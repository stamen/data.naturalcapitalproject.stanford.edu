"""Cache Plugin.

app/cache.py

"""

import asyncio
import urllib
from typing import Any, Dict
import logging

import aiocache
from starlette.concurrency import run_in_threadpool
from starlette.responses import Response

from fastapi.dependencies.utils import is_coroutine_callable

from settings import cache_setting

LOGGER = logging.getLogger(__name__)

class cached(aiocache.cached):
    """Custom Cached Decorator."""

    async def get_from_cache(self, key):
        try:
            value = await self.cache.get(key)
            if isinstance(value, Response):
                value.headers["X-Cache"] = "HIT"
            return value
        except Exception:
            aiocache.logger.exception(
                "Couldn't retrieve %s, unexpected error", key
            )

    async def decorator(
        self,
        f,
        *args,
        cache_read=True,
        cache_write=True,
        aiocache_wait_for_write=True,
        **kwargs,
    ):
        key = self.get_cache_key(f, args, kwargs)

        if cache_read:
            value = await self.get_from_cache(key)
            if value is not None:
                return value

        # CUSTOM, we add support for non-async method
        if is_coroutine_callable(f):
            result = await f(*args, **kwargs)
        else:
            result = await run_in_threadpool(f, *args, **kwargs)

        if cache_write:
            if aiocache_wait_for_write:
                await self.set_in_cache(key, result)
            else:
                asyncio.ensure_future(self.set_in_cache(key, result))

        return result


def setup_cache():
    """Setup aiocache."""
    config: Dict[str, Any] = {
        'cache': "aiocache.SimpleMemoryCache",
        'serializer': {
            'class': "aiocache.serializers.PickleSerializer"
        }
    }
    if cache_setting.ttl is not None:
        config["ttl"] = cache_setting.ttl

    if cache_setting.endpoint:
        url = urllib.parse.urlparse(cache_setting.endpoint)
        ulr_config = dict(urllib.parse.parse_qsl(url.query))
        config.update(ulr_config)

        cache_class = aiocache.Cache.get_scheme_class(url.scheme)
        config.update(cache_class.parse_uri_path(url.path))
        config["endpoint"] = url.hostname
        config["port"] = str(url.port)

        # Add other configuration into config here, Example for namespace:
        """
        if cache_setting.namespace != "":
            config["namespace"] = cache_setting.namespace
        """

        if url.password:
            config["password"] = url.password

        if cache_class == aiocache.Cache.REDIS:
            config["cache"] = "aiocache.RedisCache"
        elif cache_class == aiocache.Cache.MEMCACHED:
            config["cache"] = "aiocache.MemcachedCache"

    LOGGER.info(f"Setting up cache with configuration: {config}")
    aiocache.caches.set_config({"default": config})