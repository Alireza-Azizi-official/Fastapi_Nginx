from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as starlette_HTTPException

from app.db import lifespan
from app.routes import router

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(
    directory=r"app\template"
)


@app.exception_handler(starlette_HTTPException)
async def custom_http_exception_handler(request: Request, exc: starlette_HTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "path": request.url},
            status_code=404,
        )
    return HTMLResponse(str(exc.detail), status_code=exc.status_code)
