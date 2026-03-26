from fastmcp import FastMCP

def register(mcp: FastMCP):
    @mcp.tool
    def hello_world() -> str:
        return {
            'hello': 'world'
        }