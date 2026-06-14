from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.core.settings import ExecutionSettings
from src.shared.execution.checking.docker_executor import DockerExecutor
from src.shared.execution.checking.execution_workspace import (
    binary_path,
    isolation_shell_prefix,
    new_workspace_id,
    source_path,
    workspace_root,
)


def test_each_submit_gets_unique_workspace_directory() -> None:
    first = new_workspace_id()
    second = new_workspace_id()
    assert workspace_root(first) != workspace_root(second)
    assert workspace_root(first) == f"/tmp/home/{first}"
    assert source_path(first, ".py") == f"/tmp/home/{first}/source.py"
    assert binary_path(second) == f"/tmp/home/{second}/app"


def test_isolation_prefix_removes_workspace_on_exit() -> None:
    workspace_id = "abc123def4567890"
    prefix = isolation_shell_prefix(workspace_id)
    assert f'CT_WORKSPACE="{workspace_root(workspace_id)}"' in prefix
    assert "mkdir -p" in prefix
    assert "trap 'rm -rf \"$CT_WORKSPACE\"' EXIT INT TERM" in prefix


def test_cold_docker_run_enforces_limits_and_no_network() -> None:
    settings = ExecutionSettings(use_warm_runners=False)
    docker = DockerExecutor(settings)
    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("src.shared.execution.checking.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_find_warm_runner_container", return_value=None):
                with patch.object(docker, "_run_limited_process") as limited:
                    limited.return_value = MagicMock(stdout="", stderr="", returncode=0)
                    docker.run_raw_shell("cpp_runner", "echo hi", workspace_id="b" * 16)

    command = limited.call_args[0][0]
    joined = " ".join(command)
    assert "--network none" in joined
    assert "--user 1000:1000" in joined
    assert f"--cpus={settings.cold_run_cpus}" in joined
    assert f"--memory={settings.cold_run_memory}" in joined
    assert f"--pids-limit={settings.cold_run_pids_limit}" in joined
    assert "/tmp/home/bbbbbbbbbbbbbbbb" in command[-1]


def test_warm_runner_recycles_after_configured_exec_count() -> None:
    settings = ExecutionSettings(warm_runner_recycle_after=3)
    docker = DockerExecutor(settings)
    container = "warmcontainer01"
    docker._warm_exec_counts[container] = 3

    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("subprocess.run") as run_mock:
            docker._maybe_recycle_warm_runner(container)

    run_mock.assert_called_once()
    assert docker._warm_exec_counts[container] == 0


def test_warm_exec_wraps_user_command_with_workspace_trap() -> None:
    settings = ExecutionSettings(use_warm_runners=True)
    docker = DockerExecutor(settings)
    captured: dict[str, str] = {}

    def fake_exec(container_id, shell_cmd, timeout=None, stdin=None):
        captured["cmd"] = shell_cmd
        from src.shared.execution.checking.docker_executor import DockerRunResult

        return DockerRunResult(stdout="", stderr="", returncode=0, duration_ms=1)

    workspace_id = "cafebabecafebabe"
    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("src.shared.execution.checking.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_find_warm_runner_container", return_value="warmid"):
                with patch.object(docker, "_exec_in_container", side_effect=fake_exec):
                    with patch.object(docker, "_maybe_recycle_warm_runner"):
                        docker.run_raw_shell(
                            "python_runner",
                            "echo user-code",
                            workspace_id=workspace_id,
                        )

    assert workspace_root(workspace_id) in captured["cmd"]
    assert "trap" in captured["cmd"]
    assert "echo user-code" in captured["cmd"]


def test_warm_exec_runs_as_non_root_with_home_env() -> None:
    settings = ExecutionSettings(use_warm_runners=True)
    docker = DockerExecutor(settings)
    captured: dict[str, list[str]] = {}

    def fake_limited(command, **kwargs):
        captured["command"] = command
        from src.shared.execution.checking.docker_executor import DockerRunResult

        return DockerRunResult(stdout="", stderr="", returncode=0)

    with patch.object(docker, "_docker_binary", return_value="docker"):
        with patch("src.shared.execution.checking.docker_executor.Path.exists", return_value=True):
            with patch.object(docker, "_find_warm_runner_container", return_value="warmid"):
                with patch.object(docker, "_run_limited_process", side_effect=fake_limited):
                    with patch.object(docker, "_maybe_recycle_warm_runner"):
                        docker.run_raw_shell("csharp_runner", "dotnet-script --version", workspace_id="a" * 16)

    command = captured["command"]
    assert "-u" in command
    assert "1000:1000" in command
    assert "HOME=/tmp/home" in command
