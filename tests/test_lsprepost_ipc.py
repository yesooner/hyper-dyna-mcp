"""Tests for LS-PrePost file-queue IPC mode."""

import json
from pathlib import Path
from program.tools.lsprepost_ipc import (
    generate_bridge_journal,
    save_bridge_journal,
    write_command,
    poll_result,
    _COMMANDS_DIR,
    _RESULTS_DIR,
)


def test_generate_bridge_journal():
    cfile = generate_bridge_journal()
    assert "mcp_bridge_poll" in cfile
    assert "mcp_cmd_dir" in cfile
    assert "mcp_res_dir" in cfile


def test_generate_bridge_journal_custom_interval():
    cfile = generate_bridge_journal(poll_interval=2.0)
    assert "2000" in cfile  # 2000ms


def test_save_bridge_journal():
    path = save_bridge_journal()
    assert path.exists()
    assert path.name == "lsprepost_bridge.cfile"
    content = path.read_text(encoding="utf-8")
    assert "mcp_bridge_poll" in content


def test_write_command():
    cmd_id = write_command("open_d3plot", path="test.d3plot")
    assert len(cmd_id) == 12
    cmd_file = _COMMANDS_DIR / f"{cmd_id}.json"
    assert cmd_file.exists()
    data = json.loads(cmd_file.read_text())
    assert data["action"] == "open_d3plot"
    assert data["path"] == "test.d3plot"
    # Clean up
    cmd_file.unlink(missing_ok=True)


def test_poll_result_timeout():
    result = poll_result("nonexistent_id", timeout=0.1)
    assert result is None


def test_poll_result_found():
    # Write a result directly
    cmd_id = "test_result_123"
    res_file = _RESULTS_DIR / f"{cmd_id}.json"
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    res_file.write_text(json.dumps({"success": True, "action": "test"}))

    result = poll_result(cmd_id, timeout=1.0)
    assert result is not None
    assert result["success"] is True
    assert result["action"] == "test"
    # Clean up
    res_file.unlink(missing_ok=True)
