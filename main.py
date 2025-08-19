from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from controllers.web_controllers import router
import os

app = FastAPI()

# Ensure cartridge_current_working_state directory exists
state_dir = "cartridge_current_working_state"
if not os.path.exists(state_dir):
    os.makedirs(state_dir)

app.add_middleware(SessionMiddleware, secret_key="your-secret-key-here")
app.mount("/static", StaticFiles(directory="views"), name="static")

app.include_router(router)