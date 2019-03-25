import transaction

from core import BaseTest
from idris.models import User


class GroupWebTest(BaseTest):

    def test_crud_as_admin(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json('/api/v1/group/records',
                                 {'international_name': 'Corp.',
                                  'type': 'organisation'},
                                 headers=headers,
                                 status=201)
        last_id = out.json['id']
        self.api.put_json('/api/v1/group/records/%s' % last_id,
                          {'id': last_id,
                           'international_name': 'Mega Corp.',
                           'type': 'organisation'},
                          headers=headers,
                          status=200)
        out = self.api.get('/api/v1/group/records/%s' % last_id,
                          headers=headers,
                          status=200)
        assert out.json['name'] == 'Mega Corp.'
        self.api.delete('/api/v1/group/records/%s' % last_id,
                        headers=headers,
                        status=200)
        self.api.get('/api/v1/group/records/%s' % last_id,
                          headers=headers,
                          status=404)

    def test_invalid_group_type(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json('/api/v1/group/records',
                                 {'international_name': 'Corp.',
                                  'type': 'foobar'},
                                 headers=headers,
                                 status=400)
        assert out.json['errors'][0]['name'] == 'type'
        assert out.json['errors'][0]['location'] == 'body'
        assert out.json['errors'][0]['description'].startswith(
            '"foobar" is not one of')

    def test_corporate_group_name_generator(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json(
            '/api/v1/group/records',
            {'name': 'Erasmus University', 'type': 'organisation'},
            headers=headers,
            status=400)

        assert out.json['errors'][0]['name'] == 'international_name'
        assert out.json['errors'][0]['description']  == 'Required'
        out = self.api.post_json(
            '/api/v1/group/records',
            {'international_name': 'Erasmus University',
             'type': 'organisation'},
            headers=headers,
            status=201)
        assert out.json['name'] == out.json['international_name']

    def test_group_dates(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json(
            '/api/v1/group/records',
            {'international_name': 'Some Historic Faculty',
             'type': 'organisation',
             'start_date': '1970-01-01',
             'end_date': '1990-12-31'},
            headers=headers,
            status=201)
        last_id = out.json['id']
        out = self.api.get('/api/v1/group/records/%s' % last_id,
                           headers=headers,
                           status=200)

        assert out.json['start_date'] == '1970-01-01'
        assert out.json['end_date'] == '1990-12-31'

    def test_adding_group_accounts(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json(
            '/api/v1/group/records',
            {'international_name': 'Corp.',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '1234'}]},
             headers=headers,
             status=201)
        last_id = out.json['id']
        assert out.json['accounts'] == [{'type': 'local', 'value': '1234'}]
        out = self.api.get('/api/v1/group/records/%s' % last_id,
                           headers=headers)
        assert out.json['accounts'] == [{'type': 'local', 'value': '1234'}]
        out = self.api.put_json(
            '/api/v1/group/records/%s' % last_id,
            {'id': last_id,
             'international_name': 'Corp',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': 'XXXX'}]},
             headers=headers,
             status=200)
        out = self.api.get('/api/v1/group/records/%s' % last_id,
                           headers=headers)
        assert out.json['accounts'] == [{'type': 'local', 'value': 'XXXX'}]

    def test_insert_empty_account_or_no_account(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json(
            '/api/v1/group/records',
            {'international_name': 'Other Corp',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '1234'}]},
             headers=headers,
             status=201)
        last_id = out.json['id']
        # let's change a field without specifying the accounts
        out = self.api.put_json(
            '/api/v1/group/records/%s' % last_id,
            {'id': last_id,
             'international_name': 'Other Corp',
             'abbreviated_name': 'C.',
             'type': 'organisation'},
             headers=headers,
             status=200)
        # the accounts should be intact
        assert out.json['accounts'] == [{'type': 'local', 'value': '1234'}]
        # we can clear the accounts by supllying an empty list/array
        out = self.api.put_json(
            '/api/v1/group/records/%s' % last_id,
            {'id': last_id,
             'international_name': 'Other Corp',
             'abbreviated_name': 'C.',
             'type': 'organisation',
             'accounts': []},
             headers=headers,
             status=200)
        assert out.json['accounts'] == []


class GroupAuthorzationWebTest(BaseTest):
    def test_crud_groups_by_user_groups(self):
        super(GroupAuthorzationWebTest, self).setUp()
        # add some users
        test_users = [('test_admin', 100),
                      ('test_manager', 80),
                      ('test_editor',  60)]
        session = self.storage.make_session(namespace='unittest')
        for user, user_group in test_users:
            session.add(
                User(userid=user,
                     credentials=user,
                     user_created=user,
                     user_modified=user,
                     user_group=user_group))
        session.flush()
        transaction.commit()
        for user, user_group in test_users:
            token = self.api.post_json(
            '/api/v1/auth/login',
            {'user': user, 'password': user}).json['token']
            headers = dict(Authorization='Bearer %s' % token)
            out = self.api.post_json(
                '/api/v1/group/records', {'international_name': user,
                                          'type': 'organisation'},
                headers=headers,
                status=201)
            last_id = out.json['id']
            out = self.api.get('/api/v1/group/records/%s' % last_id,
                               headers=headers)
            assert out.json['international_name'] == user
            out = self.api.put_json(
                '/api/v1/group/records/%s' % last_id,
                {'id': last_id,
                 'international_name': user,
                 'abbreviated_name': 'C.',
                 'type': 'organisation'},
                headers=headers,
                status=200)
            assert out.json['abbreviated_name'] == 'C.'
            out = self.api.delete('/api/v1/group/records/%s' % last_id,
                                  headers=headers)
            self.api.get('/api/v1/group/records/%s' % last_id,
                         headers=headers,
                         status=404)

    def test_owners_can_view_and_edit(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json(
            '/api/v1/group/records',
            {'international_name': 'Corp.',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '1234'}]},
             headers=headers,
             status=201)
        group_id = out.json['id']
        out = self.api.post_json(
            '/api/v1/user/records',
            {'userid': 'john',
             'credentials': 'john',
             'user_group': 40,
             'owns': [{'group_id': group_id}]},
            headers=headers, status=201)
        assert out.json['owns'][0]['group_id'] == group_id
        token = self.api.post_json(
            '/api/v1/auth/login',
            {'user': 'john', 'password': 'john'}).json['token']
        john_headers = dict(Authorization='Bearer %s' % token)
        # we can view the metadata
        out = self.api.get('/api/v1/group/records/%s' % group_id,
                           headers=john_headers)
        # and are allowed to edit it
        self.api.put_json(
            '/api/v1/group/records/%s' % group_id,
            {'id': group_id,
             'international_name': 'Corp.',
             'abbreviated_name': 'C.',
             'type': 'organisation',
             'accounts': []},
             headers=john_headers,
             status=200)
        # but not allowed to delete
        self.api.delete(
            '/api/v1/group/records/%s' % group_id,
             headers=john_headers, status=403)

    def test_group_bulk_import(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        records = {'records': [
            {'id': 1,
             'international_name': 'Corp.',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '123'}]},
            {'id': 2,
             'international_name': 'Other Corp.',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '345'}]}
             ]}

        # Bulk add records
        out = self.api.post_json('/api/v1/group/bulk',
                                 records,
                                 headers=headers,
                                 status=201)
        assert out.json['status'] == 'ok'
        out = self.api.get('/api/v1/group/records/2', headers=headers)
        assert out.json['international_name'] == 'Other Corp.'
        records['records'][1]['international_name'] = 'Big Other Corp.'
        # bulk update records
        out = self.api.post_json('/api/v1/group/bulk',
                                 records,
                                 headers=headers,
                                 status=201)
        assert out.json['status'] == 'ok'
        out = self.api.get('/api/v1/group/records/2', headers=headers)
        assert out.json['international_name'] == 'Big Other Corp.'

    def test_group_bulk_export_record_schema(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        records = {'records': [
            {'id': 1,
             'international_name': 'Corp.',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '123'}]},
            {'id': 2,
             'international_name': 'Other Corp.',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '345'}]}
        ]}

        # Bulk add records.
        out = self.api.post_json('/api/v1/group/bulk',
                                 records,
                                 headers=headers,
                                 status=201)

        # Export records.
        out = self.api.get('/api/v1/group/bulk?limit=1', headers=headers)

        # Test the output keys.
        out_keys = sorted(['remaining', 'records', 'limit', 'cursor', 'status'])
        assert out_keys == sorted(list(out.json.keys()))

        # Test the record keys.
        record = out.json['records'][0]
        record_keys = sorted(['id', 'name', 'type',
                              'international_name', 'accounts'])
        assert record_keys == sorted(list(record.keys()))

        # Test record contents.
        assert record['id'] == 1
        assert record['type'] == 'organisation'
        assert record['name'] == 'Corp.'
        assert record['international_name'] == 'Corp.'
        assert len(record['accounts']) == 1
        assert record['accounts'][0] == {'type': 'local', 'value': '123'}

    def test_group_bulk_export_cursor(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        records = {'records': [
            {'id': 1,
             'international_name': 'Corp.',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '123'}]},
            {'id': 2,
             'international_name': 'Other Corp.',
             'type': 'organisation',
             'accounts': [{'type': 'local', 'value': '345'}]}
        ]}

        # Bulk add records.
        out = self.api.post_json('/api/v1/group/bulk',
                                 records,
                                 headers=headers,
                                 status=201)

        # Test exporting in batches. There are two records and the batch
        # limit is set at 1, so using the cursor we should be able to get one
        # record per API call.
        out = self.api.get('/api/v1/group/bulk?limit=1', headers=headers)

        assert out.json['remaining'] == 1
        assert len(out.json['records']) == 1
        cursor = out.json['cursor']
        assert cursor is not None

        # Get the second record.
        out = self.api.get(
            '/api/v1/group/bulk?limit=1&cursor={cursor}'.format(
                cursor=cursor), headers=headers)
        assert out.json['remaining'] == 0
        assert len(out.json['records']) == 1
        assert out.json['cursor'] is None
        assert out.json['records'][0]['name'] == 'Other Corp.'

class GroupRetrievalWebTest(GroupWebTest):
    def setUp(self):
        super(GroupRetrievalWebTest, self).setUp()
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json('/api/v1/group/records',
                                 {'international_name': 'Corp.',
                                  'type': 'organisation'},
                                 headers=headers,
                                 status=201)
        self.corp_id = out.json['id']
        out = self.api.post_json('/api/v1/group/records',
                                 {'international_name': 'Department A',
                                  'type': 'organisation'},
                                 headers=headers,
                                 status=201)
        self.dept_id = out.json['id']
        out = self.api.post_json('/api/v1/person/records',
                                 {'family_name': 'Doe',
                                  'given_name': 'John'},
                                 headers=headers,
                                 status=201)
        self.john_id = out.json['id']
        self.api.post_json('/api/v1/membership/records',
                           {'person_id': self.john_id,
                            'group_id': self.dept_id,
                            'start_date': '2017-01-01',
                            'end_date': '2017-12-31'},
                           headers=headers,
                           status=201)

    def test_group_filtering(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.get(
            '/api/v1/group/records',
            headers=headers, status=200)
        assert out.json['total'] == 2
        out = self.api.get(
            '/api/v1/group/records?query=Department',
            headers=headers, status=200)
        assert out.json['total'] == 1

    def test_group_snippet(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.get(
            '/api/v1/group/records?query=Department&format=snippet',
            headers=headers, status=200)
        assert out.json['total'] == 1
        assert len(out.json.get('snippets', [])) == 1
        assert out.json['snippets'][0]['members'] == 1

    def test_owner_group_search(self):
        headers = dict(Authorization='Bearer %s' % self.generate_test_token('owner'))
        # all users have search permission on all groups
        out = self.api.get(
            '/api/v1/group/search?query=Department&format=snippet',
            headers=headers, status=200)
        assert out.json['total'] == 1
        assert len(out.json.get('snippets', [])) == 1

    def test_add_parent_group_and_filter_listing_on_parent(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.post_json('/api/v1/group/records',
                                 {'international_name': 'Corp.',
                                  'type': 'organisation'},
                                 headers=headers,
                                 status=201)
        corp_id = out.json['id']
        out = self.api.post_json('/api/v1/group/records',
                                 {'international_name': 'Dept.',
                                  'parent_id': corp_id,
                                  'type': 'organisation'},
                                 headers=headers,
                                 status=201)
        assert out.json.get('parent_id') == corp_id
        dept_id = out.json['id']
        # filter groups on parent id
        out = self.api.get('/api/v1/group/records?filter_parent=%s' % corp_id,
                           headers=headers, status=200)
        assert out.json['total'] == 1
        assert out.json['records'][0]['id'] == dept_id

    def test_group_id_minting(self):
        headers = dict(Authorization='Bearer %s' % self.admin_token())
        out = self.api.get('/api/v1/group/ids', headers=headers)
        id_count = out.json['current_id']
        assert id_count > 0 # there are already groups
        assert id_count == out.json['highest_observed_id']
        # let's increment the id
        out = self.api.post('/api/v1/group/ids', headers=headers)
        assert out.json['current_id'] == id_count + 1
        # note that there is no group with this id yet
        assert out.json['current_id'] == out.json['highest_observed_id'] + 1
        # now let's set the id counter to ten
        out = self.api.put('/api/v1/group/ids',
                           {'next_id': 10},
                           headers=headers)
        assert out.json['current_id'] == 10
        assert out.json['highest_observed_id'] == id_count
        # let's fetch the current sequence, just to be sure
        self.api.get('/api/v1/group/ids',
                     headers=headers).json['current_id'] == 10
        # if the id sequence is set to a number lower then the
        # highest observed id, an error is raised
        out = self.api.put('/api/v1/group/ids',
                           {'next_id': 0},
                           headers=headers,
                           status=400)
        assert out.json['errors'][0]['name'] == 'next_id'
