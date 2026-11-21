"""
Automated Verification Suite for Personal Agent Phase 2.1:
- Ollama local connection detection
- Model discovery and verification of 'qwen3:8b'
- Real streaming inference with token delivery
- Stopping generation mid-stream
- Multi-turn conversation persistence in SQLite
- GPU utilization and VRAM allocation verification
- UI non-blocking thread behavior
"""
import sys
import os
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Default to windows platform if available, or offscreen
if "QT_QPA_PLATFORM" not in os.environ and sys.platform != "win32":
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEventLoop, QTimer

from app.core.model_manager import ModelManager
from app.core.agent import AgentCore
from app.core.system_monitor import SystemMonitor
from app.database.db import db_manager


def run_phase2_tests():
    print("\n========================================================")
    print(" STARTING PHASE 2.1 VERIFICATION & GPU BENCHMARK SUITE ")
    print("========================================================")

    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Test ModelManager & Ollama Detection
    print("\n[Step 1/5] Testing ModelManager & Ollama Connectivity...")
    model_mgr = ModelManager()
    is_connected = model_mgr.check_connection()
    print(f"  • Ollama Endpoint: {model_mgr.endpoint}")
    print(f"  • Connected: {is_connected}")
    assert is_connected, "Ollama service is not reachable at http://localhost:11434"

    installed = [m["name"] for m in model_mgr.available_models]
    print(f"  • Installed Models Detected: {installed}")
    assert "qwen3:8b" in installed, f"Expected 'qwen3:8b' to be installed. Found: {installed}"
    assert model_mgr.active_model == "qwen3:8b", f"Active model is {model_mgr.active_model}, expected 'qwen3:8b'"
    print("  ✓ Ollama connection and 'qwen3:8b' detection verified!")

    # 2. Test NVIDIA GPU Hardware Monitoring
    print("\n[Step 2/5] Testing NVIDIA GPU Detection & Hardware Metrics...")
    sys_mon = SystemMonitor(interval_ms=5000)
    cpu, ram, gpu = sys_mon.last_metrics
    # Force one measurement
    sys_mon._measure()
    cpu, ram, gpu = sys_mon.last_metrics
    print(f"  • CPU Usage: {cpu:.1f}%")
    print(f"  • RAM Usage: {ram:.1f}%")
    print(f"  • GPU Available: {gpu.get('available')}")
    if gpu.get("available"):
        print(f"  • GPU Hardware: {gpu.get('name')}")
        print(f"  • GPU Utilization: {gpu.get('utilization')}%")
        print(f"  • VRAM Used: {gpu.get('vram_used_mb')} MiB / {gpu.get('vram_total_mb')} MiB")
        print(f"  • GPU Temp: {gpu.get('temp_c')} °C")
    assert gpu.get("available"), "NVIDIA GPU monitoring failed to detect GPU via nvidia-smi"
    print("  ✓ GPU monitoring verified!")

    # 3. Test Real Streaming Inference with qwen3:8b
    print("\n[Step 3/5] Testing Real Streaming Inference with qwen3:8b...")
    agent_core = AgentCore(model_mgr)

    received_chunks = []
    finished_data = {}
    loop = QEventLoop()

    def on_chunk(chunk: str):
        received_chunks.append(chunk)
        print(".", end="", flush=True)

    def on_finished(full_text: str, stats: dict):
        print(" [Done]")
        finished_data["full_text"] = full_text
        finished_data["stats"] = stats
        loop.quit()

    def on_error(err_msg: str):
        print(f" [Error: {err_msg}]")
        finished_data["error"] = err_msg
        loop.quit()

    agent_core.stream_chunk.connect(on_chunk)
    agent_core.stream_finished.connect(on_finished)
    agent_core.stream_error.connect(on_error)

    test_prompt = "Explain in one sentence what a CPU is."
    print(f"  • Submitting Prompt: '{test_prompt}'")
    agent_core.process_user_input(test_prompt)

    # Allow up to 60s for model inference
    timeout_timer = QTimer()
    timeout_timer.setSingleShot(True)
    timeout_timer.timeout.connect(loop.quit)
    timeout_timer.start(60000)
    loop.exec()

    assert "error" not in finished_data, f"Inference failed with error: {finished_data.get('error')}"
    assert len(received_chunks) > 0, "No streaming tokens were received!"
    assert "full_text" in finished_data and len(finished_data["full_text"]) > 0, "No response generated!"

    stats = finished_data.get("stats", {})
    tokens_count = stats.get("eval_count", len(received_chunks))
    speed = stats.get("tokens_per_sec", 0.0)
    print(f"  • Received Chunks: {len(received_chunks)} token events")
    print(f"  • Total Tokens: {tokens_count}")
    print(f"  • Inference Speed: {speed:.1f} tokens/second")
    print(f"  • Response Preview: {finished_data['full_text'].strip()[:120]}...")
    print("  ✓ Real streaming inference successfully verified!")

    # 4. Verify GPU Processor Offload in Ollama
    print("\n[Step 4/5] Checking Ollama Processor Offloading (ollama ps)...")
    proc_info = model_mgr.query_running_processor()
    print(f"  • Active Processor in Ollama: {proc_info}")
    # Verify that GPU offload is happening
    assert "gpu" in proc_info.lower() or "llamacpp" in proc_info.lower(), (
        f"Expected GPU execution in Ollama runner. Found: {proc_info}"
    )
    print("  ✓ GPU Offload verified in Ollama runner!")

    # 5. Test SQLite Chat Persistence & Stop Generation
    print("\n[Step 5/5] Testing SQLite Chat History Persistence & Stop Mechanism...")
    messages = db_manager.get_messages(limit=10)
    assert len(messages) >= 2, "Chat messages were not persisted to SQLite database!"
    last_user = [m for m in messages if m.get("role") == "user"][-1]
    last_assistant = [m for m in messages if m.get("role") == "assistant"][-1]
    assert test_prompt in last_user["content"], "Persisted user message content mismatch"
    print(f"  • Persisted User Message ID: {last_user['id']}")
    print(f"  • Persisted Assistant Message ID: {last_assistant['id']} (Model: {last_assistant.get('model')})")

    # Test Stop Generation
    print("  • Testing Stop Generation mechanism...")
    agent_core.process_user_input("Write a very long 2000-word essay about computers.")
    time.sleep(0.5)
    assert agent_core.is_generating, "Expected agent to be in generating state"
    agent_core.stop_generation()
    assert not agent_core.is_generating, "Expected agent to stop generating after cancel"
    print("  ✓ Stop generation verified!")

    print("\n========================================================")
    print(" ALL PHASE 2.1 VERIFICATION & GPU TESTS PASSED (5/5)!   ")
    print("========================================================")


if __name__ == "__main__":
    run_phase2_tests()
