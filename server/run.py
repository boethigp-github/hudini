import os
import asyncio
from fastapi import FastAPI
from app.factory.fast_api_app_factory import FastAPIAppFactory
from app.utils.hudini_logger import hudini_logger  # Import the global hudini_logger
from app.config.settings import Settings

# Initialize settings
settings = Settings()

# Initialize FastAPIAppFactory with the global logger
app_factory = FastAPIAppFactory(settings)

# Initialize the app asynchronously
async def get_application() -> FastAPI:
    return await app_factory.create_app()

# Use asyncio.create_task() to initialize the app if an event loop is already running
if __name__ != "__main__":
    app = asyncio.create_task(get_application())
else:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = loop.run_until_complete(get_application())

if __name__ == "__main__":
    import uvicorn

    port = int(settings.get('APP_PORT', 5000))
    hudini_logger.info(f"Starting Uvicorn server on port {port}")
    uvicorn.run("run:app", host="0.0.0.0", port=port, reload=True)
