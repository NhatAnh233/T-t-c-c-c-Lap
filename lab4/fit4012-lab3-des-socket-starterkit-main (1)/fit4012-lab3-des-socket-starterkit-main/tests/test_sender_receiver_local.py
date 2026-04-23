import os
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_local_sender_receiver_roundtrip():
    port = find_free_port()
    receiver_env = os.environ.copy()
    receiver_env.update({
        "PYTHONUNBUFFERED": "1",
        "RECEIVER_HOST": "127.0.0.1",
        "RECEIVER_PORT": str(port),
        "SOCKET_TIMEOUT": "5",
    })
    sender_env = os.environ.copy()
    sender_env.update({
        "PYTHONUNBUFFERED": "1",
        "SERVER_IP": "127.0.0.1",
        "SERVER_PORT": str(port),
        "MESSAGE": "Xin chao FIT4012 - local integration test",
    })

    receiver = subprocess.Popen(
        [sys.executable, "-u", "receiver.py"],
        cwd=REPO_ROOT,
        env=receiver_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        started = False
        start_time = time.time()
        collected = []
        while time.time() - start_time < 5:
            line = receiver.stdout.readline()
            if line:
                collected.append(line)
                if "Đang lắng nghe" in line:
                    started = True
                    break
        assert started, "Receiver không khởi động đúng. Output: " + "".join(collected)

        sender = subprocess.run(
            [sys.executable, "sender.py"],
            cwd=REPO_ROOT,
            env=sender_env,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        receiver_out, _ = receiver.communicate(timeout=10)
        full_receiver_output = "".join(collected) + receiver_out

        assert "[+] Đã gửi bản mã." in sender.stdout
        assert "Key:" in sender.stdout
        assert "IV:" in sender.stdout
        assert "Ciphertext:" in sender.stdout
        assert "[+] Bản tin gốc: Xin chao FIT4012 - local integration test" in full_receiver_output
    finally:
        if receiver.poll() is None:
            receiver.kill()
