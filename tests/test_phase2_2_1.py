"""
Comprehensive Automated Test Suite for Phase 2.2.1: Agent Tool Engine.
Tests tool registration, validation, permissions, execution, and model-agent integration.
"""
import sys
import time
import os
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.tools import (
    PermissionLevel,
    ToolPermissionPolicy,
    ToolValidator,
    ToolDefinition,
    ToolRegistry,
    default_tool_registry,
    ToolExecutor,
    default_tool_executor,
    register_built_in_tools
)
from app.core.model_manager import ModelManager
from app.core.agent import AgentCore, OllamaChatWorker
from app.database.db import db_manager


def test_tool_registration():
    print("\n--- 1. Testing Tool Registration ---")
    registry = ToolRegistry()
    assert len(registry.list_tools()) == 0, "New registry should be empty"

    dummy_tool = ToolDefinition(
        name="test_tool",
        description="A dummy test tool",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        },
        handler=lambda message: {"echo": message},
        permission_level=PermissionLevel.SAFE_READ_ONLY
    )
    registry.register(dummy_tool)

    assert registry.has_tool("test_tool") is True, "test_tool should be registered"
    retrieved = registry.get("test_tool")
    assert retrieved is not None and retrieved.name == "test_tool", "Retrieved tool name should match"
    assert registry.get("non_existent_tool") is None, "Unknown tool should return None"

    ollama_defs = registry.get_ollama_tools()
    assert len(ollama_defs) == 1, "Should have 1 Ollama tool definition"
    assert ollama_defs[0]["type"] == "function"
    assert ollama_defs[0]["function"]["name"] == "test_tool"
    print("✓ Tool registration and retrieval tests passed.")


def test_tool_validation():
    print("\n--- 2. Testing Tool Validation ---")
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "count": {"type": "integer"},
            "flag": {"type": "boolean"}
        },
        "required": ["name", "count"]
    }

    # Valid arguments
    valid_args = {"name": "sample", "count": 5, "flag": True}
    is_valid, err = ToolValidator.validate_call("sample_tool", valid_args, schema)
    assert is_valid is True, f"Expected valid, got error: {err}"

    # Missing required argument
    missing_args = {"name": "sample"}
    is_valid, err = ToolValidator.validate_call("sample_tool", missing_args, schema)
    assert is_valid is False, "Should fail when required 'count' is missing"
    assert "Missing required parameter 'count'" in err

    # Unexpected argument
    unexpected_args = {"name": "sample", "count": 5, "extra": "forbidden"}
    is_valid, err = ToolValidator.validate_call("sample_tool", unexpected_args, schema)
    assert is_valid is False, "Should fail on unexpected parameter"
    assert "Unexpected parameter 'extra'" in err

    # Invalid type (expected integer, got string)
    invalid_type_args = {"name": "sample", "count": "five"}
    is_valid, err = ToolValidator.validate_call("sample_tool", invalid_type_args, schema)
    assert is_valid is False, "Should fail on invalid type"
    assert "expected integer" in err

    # Boolean passed for integer (Python bool is subclass of int)
    bool_for_int_args = {"name": "sample", "count": True}
    is_valid, err = ToolValidator.validate_call("sample_tool", bool_for_int_args, schema)
    assert is_valid is False, "Should reject boolean passed for integer"
    print("✓ Tool validation and type enforcement tests passed.")


def test_built_in_tools_execution():
    print("\n--- 3. Testing Built-in Tools Execution ---")
    executor = default_tool_executor

    # 1. get_current_time
    res_time = executor.execute("get_current_time")
    assert res_time.success is True, f"get_current_time failed: {res_time.error}"
    assert res_time.tool_name == "get_current_time"
    assert isinstance(res_time.result, str) and len(res_time.result) > 5
    print(f"  get_current_time returned: '{res_time.result}' ({res_time.duration_ms:.2f}ms)")

    # 2. get_system_info
    res_sys = executor.execute("get_system_info")
    assert res_sys.success is True, f"get_system_info failed: {res_sys.error}"
    sys_data = res_sys.result
    assert "os" in sys_data and "Windows" in sys_data["os"]
    assert "cpu" in sys_data
    assert "ram_total" in sys_data
    assert "cpu_usage" in sys_data
    print(f"  get_system_info returned: OS={sys_data['os']}, RAM={sys_data['ram_total']}, CPU={sys_data['cpu_usage']} ({res_sys.duration_ms:.2f}ms)")

    # 3. get_gpu_info
    res_gpu = executor.execute("get_gpu_info")
    assert res_gpu.success is True, f"get_gpu_info failed: {res_gpu.error}"
    gpu_data = res_gpu.result
    assert "status" in gpu_data or "gpu_name" in gpu_data
    print(f"  get_gpu_info returned: {gpu_data.get('gpu_name', gpu_data.get('status'))} ({res_gpu.duration_ms:.2f}ms)")

    # 4. Unknown tool execution rejection
    res_unknown = executor.execute("non_existent_tool_xyz")
    assert res_unknown.success is False
    assert "Unknown tool" in res_unknown.error
    print("✓ Built-in tools execution and unknown tool rejection tests passed.")


def test_tool_permissions():
    print("\n--- 4. Testing Tool Permissions ---")
    policy = ToolPermissionPolicy(allow_auto_execution=True)

    # Safe read-only
    allowed, reason = policy.is_tool_allowed("get_current_time", PermissionLevel.SAFE_READ_ONLY)
    assert allowed is True

    # Destructive without auto-approval
    allowed, reason = policy.is_tool_allowed("delete_hard_drive", PermissionLevel.DESTRUCTIVE)
    assert allowed is False
    assert "destructive" in reason.lower()

    # Disabled auto execution
    strict_policy = ToolPermissionPolicy(allow_auto_execution=False)
    allowed, reason = strict_policy.is_tool_allowed("get_current_time", PermissionLevel.SAFE_READ_ONLY)
    assert allowed is False
    print("✓ Tool permission and safety policy tests passed.")


def test_sqlite_tool_history():
    print("\n--- 5. Testing SQLite Tool Execution Logging ---")
    test_tool = "get_current_time"
    test_args = {}
    test_result = {"result": "November 21, 2026, 01:00 PM"}
    row_id = db_manager.save_tool_execution(
        tool_name=test_tool,
        arguments=test_args,
        result=test_result,
        status="success",
        duration_ms=4.5,
        conversation_id="test_suite"
    )
    assert row_id > 0, "Tool execution row id should be positive"

    records = db_manager.get_tool_executions(conversation_id="test_suite", limit=5)
    assert len(records) > 0, "Should retrieve saved tool execution record"
    assert records[0]["tool_name"] == test_tool
    assert records[0]["status"] == "success"
    print("✓ SQLite tool execution persistence tests passed.")


def test_live_agent_tool_inference():
    print("\n--- 6. Testing Live Agent Tool Calling Round-Trip ---")
    mm = ModelManager()
    if not mm.is_connected:
        print("  [SKIP] Ollama is offline. Skipping live LLM tool invocation.")
        return

    from PySide6.QtCore import QCoreApplication
    app = QCoreApplication.instance() or QCoreApplication([])

    agent = AgentCore(model_manager=mm)
    tool_invoked = []
    response_tokens = []
    finished_event = [False]

    def on_tool_started(name, args):
        print(f"  [SIGNAL] Tool Started: '{name}' with args {args}")
        tool_invoked.append(name)

    def on_tool_completed(name, result, duration, success):
        print(f"  [SIGNAL] Tool Completed: '{name}' in {duration:.1f}ms (success={success})")

    def on_chunk(chunk):
        response_tokens.append(chunk)

    def on_finished(full_text, stats):
        print(f"  [SIGNAL] Generation Finished ({stats.get('eval_count')} tokens, rounds={stats.get('rounds')})")
        finished_event[0] = True

    def on_error(err):
        print(f"  [SIGNAL ERROR] {err}")
        finished_event[0] = True

    agent.tool_call_started.connect(on_tool_started)
    agent.tool_call_finished.connect(on_tool_completed)
    agent.stream_chunk.connect(on_chunk)
    agent.stream_finished.connect(on_finished)
    agent.stream_error.connect(on_error)

    # Ask a tool-requiring question
    print("  Sending prompt: 'Please check and tell me the current time using the get_current_time tool.'")
    agent.process_user_input("Please check and tell me the current time using the get_current_time tool.")

    start = time.time()
    while not finished_event[0] and (time.time() - start) < 60:
        app.processEvents()
        time.sleep(0.05)

    assert finished_event[0] is True, "Inference did not complete in time"
    assert len(tool_invoked) > 0, f"Expected at least 1 tool to be called, got {tool_invoked}"
    assert "get_current_time" in tool_invoked, f"Expected 'get_current_time' in {tool_invoked}"
    full_output = "".join(response_tokens)
    assert len(full_output) > 10, "Model did not formulate a final natural language response"
    print(f"  Final model answer sample: '{full_output[:120].strip()}...'")
    print("✓ Live Agent Tool Calling round-trip test passed.")


if __name__ == "__main__":
    print("========================================================")
    print(" RUNNING PHASE 2.2.1 AGENT TOOL ENGINE TEST SUITE       ")
    print("========================================================")
    test_tool_registration()
    test_tool_validation()
    test_built_in_tools_execution()
    test_tool_permissions()
    test_sqlite_tool_history()
    test_live_agent_tool_inference()
    print("\n========================================================")
    print(" ALL PHASE 2.2.1 TESTS PASSED SUCCESSFULLY! (6/6)       ")
    print("========================================================")
