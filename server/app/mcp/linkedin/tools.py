from fastmcp import FastMCP

from app.db import AsyncSessionLocal
from app.services import linkedin as linkedin_service


def register(mcp: FastMCP):

    @mcp.tool
    async def post_to_linkedin(text: str, auth0_id: str) -> dict:
        """Post text to LinkedIn on behalf of the user identified by auth0_id."""
        async with AsyncSessionLocal() as db:
            post_urn = await linkedin_service.post_to_linkedin(db, auth0_id=auth0_id, text=text)
        return {"status": "ok", "post_urn": post_urn}
