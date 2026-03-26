import os
from fastmcp import FastMCP
from fastapi import FastAPI
from app.controllers import health as health_controller
from app.mcp import tools as mcp_tools

mcp = FastMCP('Big Cat Technologies')
mcp_tools.register(mcp)

mcp_app = mcp.http_app(path='/mcp', stateless_http=True)

app = FastAPI(title='Big Cat Technologies', lifespan=mcp_app.lifespan)
health_controller.register(app)

app.mount('/', mcp_app)