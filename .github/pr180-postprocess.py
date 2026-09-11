from __future__ import annotations

from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one {label} match, found {count}")
    return text.replace(old, new)


mcp_path = Path("src/neo4j_agent_memory/mcp/_tools.py")
mcp_text = mcp_path.read_text(encoding="utf-8")
mcp_text = replace_once(
    mcp_text,
    "from typing import TYPE_CHECKING, Annotated, Any, Literal, cast",
    "from typing import TYPE_CHECKING, Any, Literal, cast",
    "typing import",
)
mcp_text = replace_once(
    mcp_text,
    "from pydantic import Field\n",
    "",
    "pydantic import",
)
mcp_text = replace_once(
    mcp_text,
    "limit: Annotated[int, Field(ge=1)] = 50",
    "limit: int = 50",
    "history signature",
)
mcp_text = replace_once(
    mcp_text,
    "limit: Annotated[int, Field(ge=1)] = 20",
    "limit: int = 20",
    "reflections signature",
)
mcp_text = replace_once(
    mcp_text,
    "            history = (await client.long_term.get_entity_history(entity_id))[:limit]",
    """            if limit < 1:
                raise ValueError("limit must be at least 1")
            history = (await client.long_term.get_entity_history(entity_id))[:limit]""",
    "history validation",
)
mcp_text = replace_once(
    mcp_text,
    "            reflections = (await client.short_term.get_reflections(session_id))[:limit]",
    """            if limit < 1:
                raise ValueError("limit must be at least 1")
            reflections = (await client.short_term.get_reflections(session_id))[:limit]""",
    "reflections validation",
)
mcp_path.write_text(mcp_text, encoding="utf-8")


test_path = Path("tests/unit/nams/test_mcp_platinum.py")
test_text = test_path.read_text(encoding="utf-8")
test_text = replace_once(
    test_text,
    """        assert history_limit["default"] == 50
        assert history_limit["minimum"] == 1

        reflections_limit = tools["memory_get_reflections"].inputSchema["properties"]["limit"]
        assert reflections_limit["default"] == 20
        assert reflections_limit["minimum"] == 1

    @pytest.mark.asyncio
    async def test_get_entity_history(self, server, mock_client):
""",
    """        assert history_limit["default"] == 50

        reflections_limit = tools["memory_get_reflections"].inputSchema["properties"]["limit"]
        assert reflections_limit["default"] == 20

    @pytest.mark.asyncio
    async def test_non_positive_limits_are_rejected_before_backend_access(
        self, server, mock_client
    ):
        async with Client(server) as client:
            history_result = await client.call_tool(
                "memory_get_entity_history", {"entity_id": "e1", "limit": 0}
            )
            reflections_result = await client.call_tool(
                "memory_get_reflections", {"session_id": "s1", "limit": -1}
            )

        assert json.loads(history_result.content[0].text) == {
            "error": "limit must be at least 1"
        }
        assert json.loads(reflections_result.content[0].text) == {
            "error": "limit must be at least 1"
        }
        mock_client.long_term.get_entity_history.assert_not_awaited()
        mock_client.short_term.get_reflections.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_entity_history(self, server, mock_client):
""",
    "MCP limit tests",
)
test_path.write_text(test_text, encoding="utf-8")

print("PR180_POSTPROCESS_APPLIED")
