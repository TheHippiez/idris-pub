import redis
from zope.interface import implementer

from idris.interfaces import ICacheService

@implementer(ICacheService)
class RedisCache(object):
    def __init__(self, uri, prefix):
        host, port = uri.replace('redis://', '').split(':')
        self._client = redis.Redis(host=host, port=port)
        self._prefix = '%s:mc' % prefix

    def get(self, key):
        result = self._client.get('%s:%s' % (self._prefix, key))
        if result is not None:
            result = result
        return result

    def set(self, key, value, expire=None):
        key = '%s:%s' % (self._prefix, key)
        if expire is None:
            return self._client.set(key, value)
        else:
            return self._client.setex(key, expire, value)

    def delete(self, *keys):
        keys = ['%s:%s' % (self._prefix, k) for k in keys]
        return self._client.delete(*keys)

    def flush(self):
        key = '%s:*' % self._prefix
        cursor = '0'
        count = 0
        while cursor is not 0:
            cursor, keys = self._client.scan(
                cursor=cursor, match=key, count=1000)
            if keys:
                count += len(keys)
                self._client.delete(*keys)
        return count


def cache_factory(registry, repository_namespace):
    config_url = registry.settings['cache.url']
    proto = config_url.split('://')[0]
    CacheImpl = registry.queryUtility(ICacheService, proto)
    prefix = '%s-%s' % (registry.settings['idris.app_prefix'],
                        repository_namespace)
    return CacheImpl(config_url, prefix)

def includeme(config):
    config.registry.registerUtility(
        RedisCache, ICacheService, 'redis')
