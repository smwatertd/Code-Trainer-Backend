from __future__ import annotations

import base64
import logging
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from shutil import which

from src.core.settings import ExecutionSettings
from src.shared.execution.checking.execution_workspace import (
    binary_path,
    isolation_shell_prefix,
    new_workspace_id,
    source_path,
)
from src.shared.execution.checking.student_execution_errors import (
    GENERIC_COMPILE_FAILED,
    filter_student_compiler_lines,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DockerRunResult:
    stdout: str
    stderr: str
    returncode: int
    duration_ms: int = 0
    workspace_id: str = ""

    @property
    def combined_output(self) -> str:
        return f"{self.stderr}\n{self.stdout}".strip()


class DockerExecutor:
    DEFAULT_TIMEOUT = 5

    def __init__(self, settings: ExecutionSettings | None = None) -> None:
        self._settings = settings or ExecutionSettings()
        self._warm_exec_counts: dict[str, int] = {}

    def is_available(self) -> bool:
        if self._docker_binary() is None:
            return False
        return Path("/var/run/docker.sock").exists()

    def run_shell(
        self,
        image: str,
        command: str,
        code: str,
        ext: str,
        timeout: int | None = None,
        stdin: str | None = None,
        *,
        workspace_id: str | None = None,
    ) -> DockerRunResult:
        ws_id = workspace_id or new_workspace_id()
        container_path = source_path(ws_id, ext)
        app_path = binary_path(ws_id)
        shell_cmd = command.format(
            filename=container_path,
            source=container_path,
            binary=app_path,
            output=app_path,
        )
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
        inner = f"echo {code_b64} | base64 -d > {container_path} && ({shell_cmd})"
        return self.run_raw_shell(
            image,
            inner,
            timeout=timeout,
            stdin=stdin,
            workspace_id=ws_id,
        )

    def run_raw_shell(
        self,
        image: str,
        shell_cmd: str,
        timeout: int | None = None,
        stdin: str | None = None,
        *,
        workspace_id: str | None = None,
    ) -> DockerRunResult:
        docker_bin = self._docker_binary()
        if not docker_bin or not Path("/var/run/docker.sock").exists():
            raise RuntimeError("Docker is not available")

        ws_id = workspace_id or new_workspace_id()
        isolated_cmd = isolation_shell_prefix(ws_id) + shell_cmd

        if self._settings.use_warm_runners:
            warm_id = self._find_warm_runner_container(image)
            if warm_id:
                result = self._exec_in_container(
                    warm_id,
                    isolated_cmd,
                    timeout=timeout,
                    stdin=stdin,
                )
                self._maybe_recycle_warm_runner(warm_id)
                return DockerRunResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    returncode=result.returncode,
                    duration_ms=result.duration_ms,
                    workspace_id=ws_id,
                )

        container_name = f"runner_{uuid.uuid4().hex[:8]}"
        logger.warning(
            "Cold docker run for image=%s (warm runner unavailable)",
            image,
        )
        docker_run = [
            docker_bin,
            "run",
            "--rm",
            "--name",
            container_name,
            "-i",
            "--network",
            "none",
            f"--cpus={self._settings.cold_run_cpus}",
            f"--memory={self._settings.cold_run_memory}",
            f"--pids-limit={self._settings.cold_run_pids_limit}",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,noexec,size=50m",
            "--tmpfs",
            "/runner:rw,nosuid,nodev,size=50m",
            "--tmpfs",
            "/tmp/home:rw,exec,size=50m",
            "--env",
            "HOME=/tmp/home",
            "--user",
            "1000:1000",
            "--cap-drop=ALL",
            "--security-opt",
            "no-new-privileges",
            image,
            "sh",
            "-c",
            isolated_cmd,
        ]

        started = time.monotonic()
        try:
            result = self._run_limited_process(
                docker_run,
                container_name=container_name,
                timeout=timeout or self.DEFAULT_TIMEOUT,
                stdin=stdin,
            )
            duration_ms = int((time.monotonic() - started) * 1000)
            return DockerRunResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                duration_ms=duration_ms,
                workspace_id=ws_id,
            )
        except subprocess.TimeoutExpired:
            self._kill_container(container_name)
            raise

    def run_diagnostics(
        self,
        image: str,
        command: str,
        code: str,
        ext: str,
        timeout: int | None = None,
    ) -> list[str]:
        result = self.run_shell(image, command, code, ext, timeout=timeout)
        if result.returncode == 0:
            return []
        lines = filter_student_compiler_lines(
            [line.strip() for line in result.combined_output.splitlines() if line.strip()]
        )
        return lines or [GENERIC_COMPILE_FAILED]

    def _use_warm_runners(self) -> bool:
        return self._settings.use_warm_runners

    def _find_warm_runner_container(self, image: str) -> str | None:
        docker_bin = self._docker_binary()
        if not docker_bin:
            return None
        for selector in (f"ancestor={image}", f"name={image}"):
            try:
                proc = subprocess.run(
                    [
                        docker_bin,
                        "ps",
                        "--filter",
                        selector,
                        "--filter",
                        "status=running",
                        "--format",
                        "{{.ID}}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )
            except Exception:
                continue
            for line in proc.stdout.splitlines():
                container_id = line.strip()
                if container_id:
                    return container_id
        return None

    def _maybe_recycle_warm_runner(self, container_id: str) -> None:
        limit = self._settings.warm_runner_recycle_after
        count = self._warm_exec_counts.get(container_id, 0) + 1
        self._warm_exec_counts[container_id] = count
        if count < limit:
            return
        docker_bin = self._docker_binary()
        if not docker_bin:
            return
        logger.info("Recycling warm runner container=%s after %s execs", container_id[:12], count)
        try:
            subprocess.run(
                [docker_bin, "restart", container_id],
                capture_output=True,
                timeout=30,
                check=False,
            )
        except Exception:
            logger.exception("Failed to recycle warm runner %s", container_id[:12])
        self._warm_exec_counts[container_id] = 0

    def _exec_in_container(
        self,
        container_id: str,
        shell_cmd: str,
        timeout: int | None = None,
        stdin: str | None = None,
    ) -> DockerRunResult:
        docker_bin = self._docker_binary()
        if not docker_bin:
            raise RuntimeError("Docker is not available")
        command = [
            docker_bin,
            "exec",
            "-i",
            "-u",
            "1000:1000",
            "-e",
            "HOME=/tmp/home",
            container_id,
            "sh",
            "-c",
            shell_cmd,
        ]
        started = time.monotonic()
        result = self._run_limited_process(
            command,
            container_name=None,
            timeout=timeout or self.DEFAULT_TIMEOUT,
            stdin=stdin,
        )
        duration_ms = int((time.monotonic() - started) * 1000)
        return DockerRunResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            duration_ms=duration_ms,
        )

    def _kill_container(self, name: str | None) -> None:
        if not name:
            return
        try:
            docker_bin = self._docker_binary() or "docker"
            subprocess.run(
                [docker_bin, "kill", name],
                capture_output=True,
                timeout=3,
                check=False,
            )
        except Exception:
            pass

    def _run_limited_process(
        self,
        command: list[str],
        *,
        container_name: str | None,
        timeout: int,
        stdin: str | None = None,
    ) -> DockerRunResult:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE if stdin is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert process.stdout is not None
        assert process.stderr is not None

        stdout_buffer = bytearray()
        stderr_buffer = bytearray()
        lock = threading.Lock()
        total_bytes = 0
        output_truncated = False
        max_output_bytes = self._settings.execution_output_max_bytes

        if stdin is not None and process.stdin is not None:
            process.stdin.write(stdin.encode("utf-8"))
            process.stdin.close()

        def reader(stream, target: bytearray) -> None:
            nonlocal total_bytes, output_truncated
            try:
                while True:
                    chunk = stream.read(4096)
                    if not chunk:
                        break
                    with lock:
                        remaining = max_output_bytes - total_bytes
                        if remaining > 0:
                            accepted = chunk[:remaining]
                            target.extend(accepted)
                            total_bytes += len(accepted)
                        if len(chunk) > max(remaining, 0) or total_bytes >= max_output_bytes:
                            output_truncated = True
                    if output_truncated:
                        self._kill_container(container_name)
                        process.kill()
                        break
            finally:
                stream.close()

        stdout_thread = threading.Thread(
            target=reader,
            args=(process.stdout, stdout_buffer),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=reader,
            args=(process.stderr, stderr_buffer),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._kill_container(container_name)
            process.kill()
            raise
        finally:
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

        stderr = stderr_buffer.decode("utf-8", errors="replace")
        stdout = stdout_buffer.decode("utf-8", errors="replace")
        if output_truncated:
            marker = f"\n[output truncated after {max_output_bytes} bytes]"
            stderr = (stderr + marker).strip()
        return DockerRunResult(
            stdout=stdout,
            stderr=stderr,
            returncode=process.returncode if process.returncode is not None else 1,
        )

    @staticmethod
    def _docker_binary() -> str | None:
        for candidate in ("docker", "/usr/local/bin/docker", "/usr/bin/docker"):
            if candidate == "docker":
                found = which("docker")
                if found:
                    return found
            if Path(candidate).is_file():
                return candidate
        return None
