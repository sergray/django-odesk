from django.test import TestCase


class TestTeamAuthBackend(TestCase):

    def setUp(self):
        from django_odesk.auth.backends import TeamAuthBackend
        from django.contrib.auth.models import User, Group
        # create test backend
        self.auth_backend = TeamAuthBackend()
        self.suffix = self.auth_backend.GROUP_SUFFIX
        # prepare test data
        self.user = User.objects.create(username='user@odesk.com')
        user_group_titles = [
            u'django_group',
            u'users' + self.suffix
        ]
        self.user_groups = []
        for group_title in user_group_titles:
            group = Group.objects.create(name=group_title)
            self.user.groups.add(group)
            self.user_groups.append(group)
        self.user.save()
        empty_group_titles = [
            u'empty1' + self.suffix,
            u'empty2' + self.suffix,
        ]
        self.empty_groups = []
        for group_title in empty_group_titles:
            group = Group.objects.create(name=group_title)
            self.empty_groups.append(group)

    def test_clear_groups(self):
        self.assertEqual(self.user.groups.count(), len(self.user_groups))
        self.auth_backend._clear_groups(self.user)
        # test that user belongs only to django group
        self.assertEqual(self.user.groups.count(), 1)
        for group in self.user.groups.all():
            self.assertEqual(group.name, 'django_group')

    def test_bulk_groups_insert(self):
        self.assertEqual(self.user.groups.count(), len(self.user_groups))
        self.auth_backend._bulk_groups_insert(self.user.id,
            [g.id for g in self.empty_groups])
        # test that user got added to new groups
        self.assertEqual(self.user.groups.count(),
            len(self.empty_groups) + len(self.user_groups))

    def test_sync_django_groups(self):
        self.auth_backend.sync_django_groups(self.user, [u'empty1' + \
            self.suffix])
        expected_group_names = set(['django_group', 'empty1' + self.suffix])
        for group in self.user.groups.all():
            self.assertTrue(group.name in expected_group_names)
