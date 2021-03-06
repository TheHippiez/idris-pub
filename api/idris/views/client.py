from operator import itemgetter

import colander
from cornice import Service

from idris.security import authenticator_factory
from idris.utils import OKStatus
from idris.resources import TypeResource


class ClientSchema(colander.MappingSchema):
    status = OKStatus

    @colander.instantiate(missing=colander.drop)
    class dev_user(colander.MappingSchema):
        user = colander.SchemaNode(colander.String())
        token = colander.SchemaNode(colander.String())

    @colander.instantiate()
    class types(colander.SequenceSchema):
        @colander.instantiate()
        class type(colander.MappingSchema):
            id = colander.SchemaNode(colander.String())
            label = colander.SchemaNode(colander.String())

            @colander.instantiate()
            class fields(colander.SequenceSchema):
                @colander.instantiate()
                class field(colander.MappingSchema):
                    id = colander.SchemaNode(colander.String())
                    label = colander.SchemaNode(colander.String())
                    type = colander.SchemaNode(colander.String())

            @colander.instantiate()
            class filters(colander.SequenceSchema):
                @colander.instantiate()
                class filter(colander.MappingSchema):
                    label = colander.SchemaNode(colander.String())
                    id = colander.SchemaNode(colander.String())

                    @colander.instantiate()
                    class values(colander.SequenceSchema):
                        @colander.instantiate()
                        class value(colander.MappingSchema):
                            id = colander.SchemaNode(colander.String())
                            label = colander.SchemaNode(colander.String())

            @colander.instantiate()
            class types(colander.SequenceSchema):
                @colander.instantiate()
                class type(colander.MappingSchema):
                    id = colander.SchemaNode(colander.String())
                    label = colander.SchemaNode(colander.String())


class ClientResponseSchema(colander.MappingSchema):
    body = ClientSchema()


client = Service(
    name='Client',
    path='/api/v1/client',
    tags=['config'],
    cors_origins=('*', ),
    response_schemas={
        '200': ClientResponseSchema(description='Ok')})

def generate_client_config(repo):
    group_types = repo.type_config('group_type')
    work_types = repo.type_config('work_type')
    work_types.sort(key=itemgetter('label'))
    group_account_types = repo.type_config('group_account_type')
    person_account_types = repo.type_config('person_account_type')
    identifier_types = repo.type_config('identifier_type')
    description_types = repo.type_config('description_type')
    description_formats = repo.type_config('description_format')
    expression_types = repo.type_config('expression_type')
    expression_formats = repo.type_config('expression_format')
    expression_access = repo.type_config('expression_access')
    relation_types = repo.type_config('relation_type')
    measure_types = repo.type_config('measure_type')
    position_types = repo.type_config('position_type')
    contributor_role_types = repo.type_config('contributor_role')

    user_group_types = [
        {'id': 100, 'label': 'Admin'},
        {'id': 80, 'label': 'Manager'},
        {'id': 60, 'label': 'Editor'},
        {'id': 40, 'label': 'Owner'},
        {'id': 10, 'label': 'Viewer'}]

    # palette generated by http://mcg.mbitson.com
    return {
        'status': 'ok',
        'repository': {
            'title': repo.settings['title'],
            'theme': repo.settings.get('theme')},
        'settings': {'person': {'account_types': person_account_types,
                                'position_types': position_types},
                     'group': {'account_types': group_account_types,
                               'type': group_types},
                     'work': {'type': work_types,
                              'contributor_role': contributor_role_types,
                              'identifier_types': identifier_types,
                              'description_types': description_types,
                              'description_formats': description_formats,
                              'expression_types': expression_types,
                              'expression_formats': expression_formats,
                              'expression_access': expression_access,
                              'relation_types': relation_types,
                              'measure_types': measure_types},
                     'user': {'type': user_group_types},
        },

        'types': [{'id': 'person',
                   'types': []},
                  {'id': 'group',
                   'types': group_types,
                   'account_types': group_account_types},
                  {'id': 'user',
                   'types': []},
        ]
    }




@client.get()
def client_config(request):
    result = generate_client_config(request.repository)
    dev_user_id = request.registry.settings.get('idris.debug_dev_user')
    if dev_user_id:
        auth_context = authenticator_factory(request)
        principals = auth_context.principals(dev_user_id)
        token = request.create_jwt_token(dev_user_id, principals=principals)
        result['dev_user'] = {'user': dev_user_id, 'token': token}
    return result
