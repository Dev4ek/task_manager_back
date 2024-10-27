from dotenv import load_dotenv
load_dotenv()

from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
from app.routers import user, task, project, chat

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import database
from app.core.config import settings
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    docs_url='/docs', 
    openapi_url='/openapi.json',
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["http://90.156.170.11", "http://localhost", "http://localhost:8082"],
  allow_methods = ["*"],
  allow_credentials=True,
  allow_headers = ["*"]
)

app.include_router(user.router_user)
app.include_router(project.router_project)
app.include_router(task.router_task)
app.include_router(chat.router_chat)


@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)

if __name__ == '__main__':
    database.create_tables()
    database.create_test_user()
    
    import os   
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    import sys
    sys.dont_write_bytecode = True

    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                full_path = os.path.join(root, d)
                os.system(f'rm -rf {full_path}')

    uvicorn.run("main:app", host="0.0.0.0", port=8082, workers=1)
    