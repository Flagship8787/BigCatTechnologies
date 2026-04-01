import os
from fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import health as health_controller
from app.controllers import blogs as blogs_controller
from app.controllers import posts as posts_controller

from app.mcp import tools as mcp_tools
from app.mcp.auth import auth

mcp = FastMCP('Big Cat Technologies', auth=auth)
mcp_tools.register(mcp)

mcp_app = mcp.http_app(path='/mcp', stateless_http=True)

app = FastAPI(title='Big Cat Technologies', lifespan=mcp_app.lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bigcattechnologies.com", "https://www.bigcattechnologies.com"],
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

health_controller.register(app)
blogs_controller.register(app)
posts_controller.register(app)

app.mount('/', mcp_app)