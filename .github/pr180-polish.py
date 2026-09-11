from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one match in {path}, found {count}: {old[:80]!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


replace_once(
    "CHANGELOG.md",
    """### Changed

- `strands` extra requires `strands-agents>=1.44.0` (was `>=0.1.0`).
""",
    """### Changed

- **BREAKING: NAMS feedback wrappers no longer accept the ignored
  `user_identifier` / `user_id` arguments.** The MCP, Pydantic AI, and Strands
  surfaces now match the backend contract; callers should stop passing these
  keywords. MCP entity-history and reflection limits and the Pydantic AI
  entity-history limit are now enforced locally and must be at least 1. This
  does not change backend or multi-tenant isolation semantics.
- `strands` extra requires `strands-agents>=1.44.0` (was `>=0.1.0`).
""",
)

replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    "from typing import TYPE_CHECKING, Any, Literal, cast\n\nfrom fastmcp import Context\n",
    "from typing import TYPE_CHECKING, Annotated, Any, Literal, cast\n\nfrom fastmcp import Context\nfrom pydantic import Field\n",
)
replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    """    async def memory_set_entity_feedback(
        ctx: Context,
        entity_id: str,
        feedback: str,
        user_identifier: str | None = None,
    ) -> str:
""",
    """    async def memory_set_entity_feedback(
        ctx: Context,
        entity_id: str,
        feedback: str,
    ) -> str:
""",
)
replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    "            user_identifier: Optional per-user scoping (multi-tenant).\n",
    "",
)
replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    """    async def memory_get_entity_history(
        ctx: Context,
        entity_id: str,
        limit: int = 50,
    ) -> str:
""",
    """    async def memory_get_entity_history(
        ctx: Context,
        entity_id: str,
        limit: Annotated[int, Field(ge=1)] = 50,
    ) -> str:
""",
)
replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    "            limit: Maximum history entries to return (default: 50).\n",
    "            limit: Maximum history entries to return (default: 50; minimum: 1).\n",
)
replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    """            history = await client.long_term.get_entity_history(entity_id)
            return json.dumps({"entity_id": entity_id, "history": history}, default=str)
""",
    """            history = (await client.long_term.get_entity_history(entity_id))[:limit]
            return json.dumps({"entity_id": entity_id, "history": history}, default=str)
""",
)
replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    """    async def memory_get_reflections(
        ctx: Context,
        session_id: str,
        limit: int = 20,
    ) -> str:
""",
    """    async def memory_get_reflections(
        ctx: Context,
        session_id: str,
        limit: Annotated[int, Field(ge=1)] = 20,
    ) -> str:
""",
)
replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    "            limit: Maximum reflections to return (default: 20).\n",
    "            limit: Maximum reflections to return (default: 20; minimum: 1).\n",
)
replace_once(
    "src/neo4j_agent_memory/mcp/_tools.py",
    """            reflections = await client.short_term.get_reflections(session_id)
            return json.dumps({"session_id": session_id, "reflections": reflections}, default=str)
""",
    """            reflections = (await client.short_term.get_reflections(session_id))[:limit]
            return json.dumps({"session_id": session_id, "reflections": reflections}, default=str)
""",
)

replace_once(
    "src/neo4j_agent_memory/integrations/pydantic_ai/memory.py",
    """    async def set_entity_feedback(
        entity_id: str,
        feedback: str,
        user_identifier: str | None = None,
    ) -> str:
""",
    """    async def set_entity_feedback(
        entity_id: str,
        feedback: str,
    ) -> str:
""",
)
replace_once(
    "src/neo4j_agent_memory/integrations/pydantic_ai/memory.py",
    "            user_identifier: Optional per-user scoping.\n",
    "",
)
replace_once(
    "src/neo4j_agent_memory/integrations/pydantic_ai/memory.py",
    "            limit: Maximum history entries to return.\n",
    "            limit: Maximum history entries to return. Must be at least 1.\n",
)
replace_once(
    "src/neo4j_agent_memory/integrations/pydantic_ai/memory.py",
    "        entries = await memory.long_term.get_entity_history(entity_id)\n",
    """        if limit < 1:
            raise ValueError("limit must be at least 1")
        entries = (await memory.long_term.get_entity_history(entity_id))[:limit]
""",
)

replace_once(
    "src/neo4j_agent_memory/integrations/strands/tools.py",
    "    def set_entity_feedback(entity_id: str, feedback: str, user_id: str | None = None) -> str:\n",
    "    def set_entity_feedback(entity_id: str, feedback: str) -> str:\n",
)
replace_once(
    "src/neo4j_agent_memory/integrations/strands/tools.py",
    "            user_id: Optional per-user scoping.\n",
    "",
)

replace_once(
    "tests/unit/integrations/test_strands.py",
    """            assert "include_relationships" in params

    def test_get_entity_graph_tool_signature(self, mock_strands: MagicMock) -> None:
""",
    """            assert "include_relationships" in params

    def test_nams_feedback_tool_does_not_expose_ignored_user_id(
        self, mock_strands: MagicMock
    ) -> None:
        """NAMS feedback exposes only arguments honored by the backend."""
        with patch.dict("sys.modules", {"strands": mock_strands}):
            from neo4j_agent_memory.integrations.strands.tools import (
                _nams_set_entity_feedback_tool,
            )

            tool = _nams_set_entity_feedback_tool(
                endpoint="https://memory.test/v1",
                api_key="test-key",
                transport_mode="rest",
            )

            import inspect

            assert list(inspect.signature(tool).parameters) == ["entity_id", "feedback"]

    def test_get_entity_graph_tool_signature(self, mock_strands: MagicMock) -> None:
""",
)

replace_once(
    "tests/unit/nams/test_mcp_platinum.py",
    """        client.long_term.get_entity_history = AsyncMock(
            return_value=[{"conversation_id": "c1", "mention_count": 3}]
        )
""",
    """        client.long_term.get_entity_history = AsyncMock(
            return_value=[
                {"conversation_id": "c1", "mention_count": 3},
                {"conversation_id": "c2", "mention_count": 1},
            ]
        )
""",
)
replace_once(
    "tests/unit/nams/test_mcp_platinum.py",
    "        client.short_term.get_reflections = AsyncMock(return_value=[{\"text\": \"reflection one\"}])\n",
    """        client.short_term.get_reflections = AsyncMock(
            return_value=[{"text": "reflection one"}, {"text": "reflection two"}]
        )
""",
)
replace_once(
    "tests/unit/nams/test_mcp_platinum.py",
    """        mock_client.long_term.set_entity_feedback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_entity_history(self, server, mock_client):
""",
    """        mock_client.long_term.set_entity_feedback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_platinum_schema_matches_supported_arguments(self, server):
        async with Client(server) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}

        feedback_properties = tools["memory_set_entity_feedback"].inputSchema.get(
            "properties", {}
        )
        assert "user_identifier" not in feedback_properties

        history_limit = tools["memory_get_entity_history"].inputSchema["properties"]["limit"]
        assert history_limit["default"] == 50
        assert history_limit["minimum"] == 1

        reflections_limit = tools["memory_get_reflections"].inputSchema["properties"]["limit"]
        assert reflections_limit["default"] == 20
        assert reflections_limit["minimum"] == 1

    @pytest.mark.asyncio
    async def test_get_entity_history(self, server, mock_client):
""",
)
replace_once(
    "tests/unit/nams/test_mcp_platinum.py",
    "            result = await client.call_tool(\"memory_get_entity_history\", {\"entity_id\": \"e1\"})\n",
    """            result = await client.call_tool(
                "memory_get_entity_history", {"entity_id": "e1", "limit": 1}
            )
""",
)
replace_once(
    "tests/unit/nams/test_mcp_platinum.py",
    "            result = await client.call_tool(\"memory_get_reflections\", {\"session_id\": \"s1\"})\n",
    """            result = await client.call_tool(
                "memory_get_reflections", {"session_id": "s1", "limit": 1}
            )
""",
)

replace_once(
    "tests/unit/nams/test_pydantic_ai_nams.py",
    "        result = await set_feedback(entity_id=\"e1\", feedback=\"positive\", user_identifier=\"alice\")\n",
    "        result = await set_feedback(entity_id=\"e1\", feedback=\"positive\")\n",
)
replace_once(
    "tests/unit/nams/test_pydantic_ai_nams.py",
    """        assert "positive" in result
        assert "e1" in result


class TestGetEntityHistory:
""",
    """        assert "positive" in result
        assert "e1" in result

    def test_signature_does_not_expose_ignored_user_identifier(self, mock_client):
        import inspect

        tools = nams_memory_tools(mock_client)
        set_feedback = next(t for t in tools if t.__name__ == "set_entity_feedback")
        assert list(inspect.signature(set_feedback).parameters) == ["entity_id", "feedback"]

    async def test_rejects_ignored_user_identifier(self, mock_client):
        tools = nams_memory_tools(mock_client)
        set_feedback = next(t for t in tools if t.__name__ == "set_entity_feedback")

        with pytest.raises(TypeError, match="unexpected keyword argument 'user_identifier'"):
            await set_feedback(entity_id="e1", feedback="positive", user_identifier="alice")

        mock_client.long_term.set_entity_feedback.assert_not_awaited()


class TestGetEntityHistory:
""",
)
replace_once(
    "tests/unit/nams/test_pydantic_ai_nams.py",
    "        result = await get_history(\"e1\", limit=10)\n",
    "        result = await get_history(\"e1\", limit=1)\n",
)
replace_once(
    "tests/unit/nams/test_pydantic_ai_nams.py",
    """        assert "c1" in result
        assert "mentions=5" in result

    async def test_empty_history(self, mock_client):
""",
    """        assert "c1" in result
        assert "mentions=5" in result
        assert "c2" not in result

    async def test_empty_history(self, mock_client):
""",
)
replace_once(
    "tests/unit/nams/test_pydantic_ai_nams.py",
    """        result = await get_history("e1")
        assert "No history" in result


class TestGetEntityProvenance:
""",
    """        result = await get_history("e1")
        assert "No history" in result

    @pytest.mark.parametrize("limit", [0, -1])
    async def test_rejects_non_positive_limit(self, mock_client, limit):
        tools = nams_memory_tools(mock_client)
        get_history = next(t for t in tools if t.__name__ == "get_entity_history")

        with pytest.raises(ValueError, match="limit must be at least 1"):
            await get_history("e1", limit=limit)

        mock_client.long_term.get_entity_history.assert_not_awaited()


class TestGetEntityProvenance:
""",
)

print("PR180_POLISH_APPLIED")
