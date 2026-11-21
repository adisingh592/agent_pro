"""
Comprehensive Automated Test Suite for Phase 2.2.2:
File Intelligence & Safe File Operations.
Uses isolated temporary directories to guarantee zero impact on host filesystem.
"""
import sys
import time
import os
import tempfile
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.tools import (
    default_tool_registry,
    default_tool_executor,
    FilesystemSafety,
    FilesystemSafetyError,
    PermissionLevel
)
from app.database.db import db_manager


def test_safety_and_path_restrictions():
    print("\n--- 1. Testing Filesystem Safety & Path Boundaries ---")
    
    # 1. Restricted system folders blocked
    restricted_targets = [
        "C:\\Windows",
        "C:\\Windows\\System32",
        "C:\\Program Files",
        "C:\\ProgramData"
    ]
    for target in restricted_targets:
        try:
            FilesystemSafety.validate_read_path(target, check_exists=False)
            assert False, f"Expected restricted path '{target}' to be blocked!"
        except FilesystemSafetyError as e:
            assert "restricted" in str(e).lower() or "blocked" in str(e).lower()
    print("  ✓ System32 and Program Files access strictly blocked.")

    # 2. Path traversal (.. escape attempts)
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        traversal_attempt = str(base_dir / ".." / ".." / "Windows" / "System32")
        try:
            FilesystemSafety.validate_read_path(traversal_attempt, check_exists=False)
            assert False, "Expected path traversal to Windows to be blocked!"
        except FilesystemSafetyError:
            pass
    print("  ✓ Directory traversal escape attempts blocked.")

    # 3. Non-existent read path detection
    try:
        FilesystemSafety.validate_read_path("C:\\non_existent_folder_abc_123\\test.txt", check_exists=True)
        assert False, "Expected non-existent path to raise FilesystemSafetyError"
    except FilesystemSafetyError as e:
        assert "does not exist" in str(e)
    print("  ✓ Non-existent read path safely detected.")


def test_read_only_file_tools():
    print("\n--- 2. Testing Read-Only File Tools ---")
    executor = default_tool_executor

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        
        # Create dummy directory structure
        sub1 = base / "src"
        sub1.mkdir()
        sub2 = base / "docs"
        sub2.mkdir()

        f_py1 = sub1 / "main.py"
        f_py1.write_text("print('hello world')\n", encoding="utf-8")
        f_py2 = sub1 / "helper.py"
        f_py2.write_text("def add(a, b): return a + b\n", encoding="utf-8")
        f_doc = sub2 / "report.md"
        f_doc.write_text("# Quarterly Report\nAll metrics green.\n", encoding="utf-8")
        f_bin = base / "archive.bin"
        f_bin.write_bytes(b"\x00\x01\x02\x03\xff")

        # 1. list_directory
        res_list = executor.execute("list_directory", {"directory": str(base)})
        assert res_list.success is True
        items = res_list.result["items"]
        assert len(items) >= 3
        types = {i["name"]: i["type"] for i in items}
        assert types["src"] == "directory"
        assert types["archive.bin"] == "file"
        print(f"  ✓ list_directory returned {len(items)} items correctly.")

        # 2. search_files
        res_search_all = executor.execute("search_files", {"directory": str(base), "pattern": "*.py", "recursive": True})
        assert res_search_all.success is True
        assert res_search_all.result["count"] == 2
        print(f"  ✓ search_files found {res_search_all.result['count']} Python files recursively.")

        # Non-recursive search
        res_search_flat = executor.execute("search_files", {"directory": str(base), "pattern": "*.py", "recursive": False})
        assert res_search_flat.success is True
        assert res_search_flat.result["count"] == 0
        print("  ✓ Non-recursive search correctly respected boundary.")

        # 3. get_file_info
        res_info = executor.execute("get_file_info", {"path": str(f_py1)})
        assert res_info.success is True
        info = res_info.result
        assert info["name"] == "main.py"
        assert info["extension"] == ".py"
        assert info["is_directory"] is False
        assert info["size_bytes"] > 0
        print(f"  ✓ get_file_info returned metadata for '{info['name']}' ({info['size_readable']}).")

        # 4. read_text_file
        res_read = executor.execute("read_text_file", {"path": str(f_py1), "max_characters": 1000})
        assert res_read.success is True
        assert "hello world" in res_read.result["content"]
        assert res_read.result["truncated"] is False
        print("  ✓ read_text_file read UTF-8 content accurately.")

        # Read binary file should be rejected
        res_read_bin = executor.execute("read_text_file", {"path": str(f_bin)})
        assert res_read_bin.success is False
        assert "Binary file reading is blocked" in res_read_bin.error
        print("  ✓ Binary file reading blocked safely.")

        # 5. find_recent_files
        res_recent = executor.execute("find_recent_files", {"directory": str(base), "days": 1, "recursive": True})
        assert res_recent.success is True
        assert res_recent.result["count"] >= 3
        print(f"  ✓ find_recent_files found {res_recent.result['count']} recently modified files.")

        # 6. find_large_files
        res_large = executor.execute("find_large_files", {"directory": str(base), "minimum_size_mb": 0.000001, "recursive": True})
        assert res_large.success is True
        assert res_large.result["count"] >= 3
        print(f"  ✓ find_large_files returned {res_large.result['count']} files matching threshold.")


def test_file_modification_and_verification():
    print("\n--- 3. Testing File Modification Tools with Confirmation & Verification ---")
    executor = default_tool_executor

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        src_file = base / "original.txt"
        src_file.write_text("Crucial personal agent content.", encoding="utf-8")
        src_size = src_file.stat().st_size

        # 1. copy_file without confirmation -> should require confirmation
        copy_dest = base / "backup.txt"
        res_copy_unconf = executor.execute("copy_file", {"source": str(src_file), "destination": str(copy_dest)})
        assert res_copy_unconf.requires_confirmation is True
        assert not copy_dest.exists(), "File should not be copied without confirmation"
        print("  ✓ copy_file unconfirmed safely staged confirmation card.")

        # copy_file with confirmed=True -> should execute and verify
        res_copy_conf = executor.execute("copy_file", {"source": str(src_file), "destination": str(copy_dest), "confirmed": True})
        assert res_copy_conf.success is True
        assert copy_dest.exists()
        assert copy_dest.stat().st_size == src_size
        assert res_copy_conf.result["verified"] is True
        print("  ✓ copy_file executed and verified (destination exists and size matches).")

        # 2. rename_file without confirmation
        res_ren_unconf = executor.execute("rename_file", {"path": str(copy_dest), "new_name": "renamed_backup.txt"})
        assert res_ren_unconf.requires_confirmation is True
        renamed_file = base / "renamed_backup.txt"
        assert not renamed_file.exists()

        # Path injection in rename_file must be rejected
        res_ren_inj = executor.execute("rename_file", {"path": str(copy_dest), "new_name": "../illegal.txt", "confirmed": True})
        assert res_ren_inj.success is False
        assert "path separators" in res_ren_inj.error

        # Confirmed rename_file
        res_ren_conf = executor.execute("rename_file", {"path": str(copy_dest), "new_name": "renamed_backup.txt", "confirmed": True})
        assert res_ren_conf.success is True
        assert renamed_file.exists()
        assert not copy_dest.exists()
        assert res_ren_conf.result["verified"] is True
        print("  ✓ rename_file executed and verified (old path removed, new path created).")

        # 3. create_directory
        new_dir = base / "archived_folder"
        res_mkdir_unconf = executor.execute("create_directory", {"path": str(new_dir)})
        assert res_mkdir_unconf.requires_confirmation is True

        res_mkdir_conf = executor.execute("create_directory", {"path": str(new_dir), "confirmed": True})
        assert res_mkdir_conf.success is True
        assert new_dir.exists() and new_dir.is_dir()
        assert res_mkdir_conf.result["verified"] is True
        print("  ✓ create_directory executed and verified.")

        # 4. move_file
        res_move_unconf = executor.execute("move_file", {"source": str(renamed_file), "destination": str(new_dir)})
        assert res_move_unconf.requires_confirmation is True
        target_in_new_dir = new_dir / "renamed_backup.txt"
        assert not target_in_new_dir.exists()

        res_move_conf = executor.execute("move_file", {"source": str(renamed_file), "destination": str(new_dir), "confirmed": True})
        assert res_move_conf.success is True
        assert target_in_new_dir.exists()
        assert not renamed_file.exists()
        assert res_move_conf.result["verified"] is True
        print("  ✓ move_file executed and verified (source removed, destination verified).")


def test_smart_file_organization():
    print("\n--- 4. Testing Smart File Organization (Preview & Execution) ---")
    executor = default_tool_executor

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        
        # Populate various extensions
        (base / "doc1.pdf").write_text("PDF", encoding="utf-8")
        (base / "doc2.docx").write_text("DOCX", encoding="utf-8")
        (base / "photo1.png").write_text("PNG", encoding="utf-8")
        (base / "photo2.jpg").write_text("JPG", encoding="utf-8")
        (base / "script.py").write_text("PY", encoding="utf-8")
        (base / "archive.zip").write_text("ZIP", encoding="utf-8")

        # 1. organize_files_preview
        res_prev = executor.execute("organize_files_preview", {"directory": str(base)})
        assert res_prev.success is True
        prev_data = res_prev.result
        assert prev_data["total_files"] == 6
        cats = prev_data["category_summary"]
        assert cats.get("Documents") == 2
        assert cats.get("Images") == 2
        assert cats.get("Code") == 1
        assert cats.get("Archives") == 1
        print("  ✓ organize_files_preview categorized all files correctly.")

        # 2. organize_files unconfirmed
        res_org_unconf = executor.execute("organize_files", {"directory": str(base)})
        assert res_org_unconf.requires_confirmation is True
        print("  ✓ organize_files staged confirmation request for batch relocation.")

        # 3. organize_files confirmed
        res_org_conf = executor.execute("organize_files", {"directory": str(base), "confirmed": True})
        assert res_org_conf.success is True
        assert res_org_conf.result["total_organized"] == 6

        # Verify folders exist and contain the files
        assert (base / "Documents" / "doc1.pdf").exists()
        assert (base / "Documents" / "doc2.docx").exists()
        assert (base / "Images" / "photo1.png").exists()
        assert (base / "Code" / "script.py").exists()
        assert (base / "Archives" / "archive.zip").exists()
        print("  ✓ organize_files successfully created typed subfolders and moved files without conflicts.")


def test_database_audit_logging():
    print("\n--- 5. Testing Database Audit Logging for File Operations ---")
    row_id = db_manager.save_tool_execution(
        tool_name="move_file",
        arguments={"source": "C:/fake/a.txt", "destination": "C:/fake/b.txt", "confirmed": True},
        result={"verified": True, "status": "Moved and verified"},
        status="confirmed_success",
        duration_ms=12.4,
        conversation_id="test_suite"
    )
    assert row_id > 0
    records = db_manager.get_tool_executions(conversation_id="test_suite", limit=1)
    assert len(records) > 0
    rec = records[0]
    assert rec["tool_name"] == "move_file"
    assert rec["status"] == "confirmed_success"
    print("  ✓ SQLite database successfully audited file operation with status and duration.")


if __name__ == "__main__":
    print("========================================================")
    print(" RUNNING PHASE 2.2.2 FILE OPERATIONS TEST SUITE         ")
    print("========================================================")
    test_safety_and_path_restrictions()
    test_read_only_file_tools()
    test_file_modification_and_verification()
    test_smart_file_organization()
    test_database_audit_logging()
    print("\n========================================================")
    print(" ALL PHASE 2.2.2 TESTS PASSED SUCCESSFULLY! (5/5)       ")
    print("========================================================")
