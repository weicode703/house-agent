from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


PROJECT_DIR = Path(__file__).resolve().parent
FRONTEND_URL = "http://127.0.0.1:5500/"
BACKEND_DOCS_URL = "http://127.0.0.1:8001/docs"
PROXY_DOCS_URL = "http://127.0.0.1:5500/api/docs"


def run(command: list[str]) -> None:
    print(f"\n> {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=PROJECT_DIR, check=True)


def docker_is_ready(docker: str) -> bool:
    result = subprocess.run(
        [docker, "info"],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def ensure_docker_desktop(docker: str) -> None:
    if docker_is_ready(docker):
        return

    candidates = []
    local_app_data = os.environ.get("LOCALAPPDATA")
    program_files = os.environ.get("ProgramFiles")
    if local_app_data:
        candidates.append(Path(local_app_data) / "Programs/DockerDesktop/Docker Desktop.exe")
    if program_files:
        candidates.append(Path(program_files) / "Docker/Docker/Docker Desktop.exe")

    desktop_exe = next((path for path in candidates if path.is_file()), None)
    if desktop_exe is None:
        raise RuntimeError("Docker Engine is not running and Docker Desktop was not found.")

    print("Docker Engine is stopped; starting Docker Desktop...", flush=True)
    subprocess.Popen([str(desktop_exe)], cwd=PROJECT_DIR)
    for attempt in range(180):
        if docker_is_ready(docker):
            return
        if attempt % 15 == 0:
            print(f"Waiting for Docker Engine... {attempt * 2}s", flush=True)
        time.sleep(2)
    raise RuntimeError("Docker Desktop did not become ready within 6 minutes.")


def wait_for_http(url: str, label: str, timeout_seconds: int = 120) -> bool:
    deadline = time.monotonic() + timeout_seconds
    print(f"Waiting for {label}...", flush=True)
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=3) as response:
                if 200 <= response.status < 400:
                    print(f"{label}: ready ({response.status})", flush=True)
                    return True
        except (OSError, URLError):
            time.sleep(2)
    print(f"{label}: not ready yet: {url}", flush=True)
    return False


def main() -> int:
    if not (PROJECT_DIR / ".env").is_file():
        print("Missing .env. Copy .env.example to .env and fill in the required values.")
        return 1

    docker = shutil.which("docker")
    if docker is None:
        print("Docker CLI was not found in PATH.")
        return 1

    try:
        ensure_docker_desktop(docker)
        compose = [
            docker,
            "compose",
            "-f",
            "docker-compose.yml",
            "-f",
            "docker-compose.local.yml",
        ]
        run([*compose, "config", "--quiet"])
        run([*compose, "up", "-d", "--build"])
        run([*compose, "ps"])

        frontend_ready = wait_for_http(FRONTEND_URL, "Frontend")
        backend_ready = wait_for_http(BACKEND_DOCS_URL, "Backend API")
        proxy_ready = wait_for_http(PROXY_DOCS_URL, "Nginx API proxy")

        if frontend_ready:
            print(f"\nFrontend: {FRONTEND_URL}", flush=True)
            webbrowser.open(FRONTEND_URL)
        if not (frontend_ready and backend_ready and proxy_ready):
            print("One or more checks failed. Backend logs follow for diagnosis.", flush=True)

        print("\nFollowing house-backend logs in this PyCharm Run window.", flush=True)
        print("Press Ctrl+C to stop log viewing; containers will keep running.\n", flush=True)
        subprocess.run(
            [
                *compose,
                "logs",
                "--follow",
                "--tail=100",
                "--timestamps",
                "house-backend",
            ],
            cwd=PROJECT_DIR,
            check=False,
        )
        return 0
    except subprocess.CalledProcessError as error:
        print(f"Command failed with exit code {error.returncode}.", flush=True)
        return error.returncode or 1
    except KeyboardInterrupt:
        print("\nStopped log viewing. Docker services are still running.", flush=True)
        return 0
    except RuntimeError as error:
        print(str(error), flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
