"""app.

app/main.py

"""

from fastapi import FastAPI
from titiler.core.errors import add_exception_handlers
from titiler.core.errors import DEFAULT_STATUS_CODES
from titiler.core.factory import TilerFactory

from .dependencies import ColorMapParams

app = FastAPI(title="My simple app with custom TMS")

cog = TilerFactory(colormap_dependency=ColorMapParams)
app.include_router(cog.router, tags=["Cloud Optimized GeoTIFF"])
add_exception_handlers(app, DEFAULT_STATUS_CODES)
