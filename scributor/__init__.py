from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from scributor.security import add_role_principals


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('cornice')
    config.include('cornice_swagger')
    config.include('pyramid_chameleon')
    config.include('pyramid_jwt')
    config.include('scributor.storage')

    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_jwt_authentication_policy(settings['scributor.secret'],
                                         http_header='Authorization',
                                         auth_type='Bearer',
                                         expiration=3600,
                                         callback=add_role_principals)
    
    config.add_route('swagger_ui', '/api/swagger.html')
    config.scan("scributor.views")
    config.add_static_view('api', path='scributor:static/dist/swagger')

    return config.make_wsgi_app()

