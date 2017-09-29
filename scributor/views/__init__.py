import colander
from cornice import Service
from cornice.service import get_services
from pyramid.view import view_config

from cornice_swagger import CorniceSwagger
# Create a service to serve our OpenAPI spec
swagger = Service(name='OpenAPI',
                  path='__api__',
                  description="OpenAPI documentation")


@swagger.get()
def openAPI_v1_spec(request):
    doc = CorniceSwagger(get_services())
    my_spec = doc.generate('Scributor API', '1.0.0')
    return my_spec

@view_config(route_name='swagger_ui',
             renderer='scributor:templates/swagger.pt')
def swagger_ui_view(request):
    return {'swagger_api_url': request.route_url('OpenAPI')}

hello = Service(name='hello', path='/', description="Simplest app")

@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return {'Hello': 'World'}
