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


@client.get()
def client_config(request):
    group_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession, 'group').to_dict()['values']]
    work_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession, 'work').to_dict()['values']]
    work_types.sort(key=itemgetter('label'))
    group_account_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'groupAccount').to_dict()['values']]
    person_account_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'personAccount').to_dict()['values']]
    identifier_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'identifier').to_dict()['values']]
    description_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'description').to_dict()['values']]
    description_formats = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'descriptionFormat').to_dict()['values']]
    expression_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'expression').to_dict()['values']]
    expression_formats = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'expressionFormat').to_dict()['values']]
    expression_access = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'expressionAccess').to_dict()['values']]
    relation_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'relation').to_dict()['values']]
    measure_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'measure').to_dict()['values']]
    position_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'position').to_dict()['values']]
    user_group_types = [
        {'id': 100, 'label': 'Admin'},
        {'id': 80, 'label': 'Manager'},
        {'id': 60, 'label': 'Editor'},
        {'id': 40, 'label': 'Owner'},
        {'id': 10, 'label': 'Viewer'}]

    contributor_role_types = [
        {'id': v['key'], 'label': v['label']}
        for v in TypeResource(request.dbsession,
                              'contributorRole').to_dict()['values']]

    # palette generated by http://mcg.mbitson.com
    result = {
        'status': 'ok',
        'repository': request.repository.settings,
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
    dev_user_id = request.registry.settings.get('idris.debug_dev_user')
    if dev_user_id:
        auth_context = authenticator_factory(request)
        principals = auth_context.principals(dev_user_id)
        token = request.create_jwt_token(dev_user_id, principals=principals)
        result['dev_user'] = {'user': dev_user_id, 'token': token}
    return result
