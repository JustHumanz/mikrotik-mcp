import asyncio
import pytest

from mcp_mikrotik.scope import container as mod
from tests.conftest import FakeExecutor


class TestListContainers:
    """Tests for list_containers function."""

    def test_list_containers_no_filter(self, ctx, monkeypatch):
        """Should list all containers without filters."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_list_containers(ctx=ctx))

        assert isinstance(result, str)
        assert "CONTAINERS" in result
        assert '/container print' in fake.commands[0]

    def test_list_containers_with_name_filter(self, ctx, monkeypatch):
        """Should list containers filtered by name."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_list_containers(ctx=ctx, name_filter="web"))

        assert isinstance(result, str)
        assert 'name~"web"' in fake.commands[0]

    def test_list_containers_with_status_filter(self, ctx, monkeypatch):
        """Should list containers filtered by status."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_list_containers(ctx=ctx, status_filter="running"))

        assert isinstance(result, str)
        assert 'status="running"' in fake.commands[0]

    def test_list_containers_empty_result(self, ctx, monkeypatch):
        """Should handle empty container list."""
        async def fake_exec(command: str, _ctx, device=None):
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_list_containers(ctx=ctx))

        assert "No containers found" in result


class TestGetContainer:
    """Tests for get_container function."""

    def test_get_container_found(self, ctx, monkeypatch):
        """Should return detailed container information."""
        async def fake_exec(command: str, _ctx, device=None):
            if 'name="test-container"' in command:
                return 'name="test-container" status=running'
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_get_container(ctx=ctx, name="test-container"))

        assert isinstance(result, str)
        assert "CONTAINER DETAILS" in result

    def test_get_container_not_found(self, ctx, monkeypatch):
        """Should handle container not found."""
        async def fake_exec(command: str, _ctx, device=None):
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_get_container(ctx=ctx, name="nonexistent"))

        assert "not found" in result


class TestCreateContainer:
    """Tests for create_container function."""

    def test_create_container_minimal(self, ctx, monkeypatch):
        """Should create container with minimal parameters."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_create_container(
            ctx=ctx,
            name="test-app",
            image="ubuntu:latest",
            interface="ether1"
        ))

        assert isinstance(result, str)
        assert "created successfully" in result
        assert "test-app" in fake.commands[0]
        assert "ubuntu:latest" in fake.commands[0]

    def test_create_container_with_options(self, ctx, monkeypatch):
        """Should create container with all optional parameters."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_create_container(
            ctx=ctx,
            name="web-server",
            image="nginx:latest",
            interface="bridge1",
            hostname="web-01",
            memory_limit="512M",
            cpu_limit="2",
            comment="Production web server"
        ))

        assert isinstance(result, str)
        assert "web-server" in fake.commands[0]
        assert "hostname=web-01" in fake.commands[0]
        assert "memory-limit=512M" in fake.commands[0]

    def test_create_container_with_envlist(self, ctx, monkeypatch):
        """Should create container with environment variables."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_create_container(
            ctx=ctx,
            name="app",
            image="app:1.0",
            interface="ether1",
            envlist=["DEBUG=1", "LOG_LEVEL=info"]
        ))

        assert isinstance(result, str)
        assert "created successfully" in result

    def test_create_container_failure(self, ctx, monkeypatch):
        """Should handle creation failure."""
        async def fake_exec(command: str, _ctx, device=None):
            if "add" in command:
                return "failure: image not found"
            return "some output"

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_create_container(
            ctx=ctx,
            name="test",
            image="invalid:image",
            interface="ether1"
        ))

        assert "Failed to create container" in result


class TestUpdateContainer:
    """Tests for update_container function."""

    def test_update_container_single_field(self, ctx, monkeypatch):
        """Should update a single container field."""
        fake = FakeExecutor()

        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "1"
            return "some output"

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_update_container(
            ctx=ctx,
            name="test",
            memory_limit="1G"
        ))

        assert isinstance(result, str)
        assert "updated successfully" in result

    def test_update_container_not_found(self, ctx, monkeypatch):
        """Should handle container not found."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "0"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_update_container(
            ctx=ctx,
            name="nonexistent",
            memory_limit="1G"
        ))

        assert "not found" in result

    def test_update_container_no_parameters(self, ctx, monkeypatch):
        """Should handle update with no parameters specified."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "1"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_update_container(ctx=ctx, name="test"))

        assert "No parameters specified" in result


class TestContainerLifecycle:
    """Tests for container start/stop/restart operations."""

    def test_start_container(self, ctx, monkeypatch):
        """Should start a stopped container."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_start_container(ctx=ctx, name="test"))

        assert isinstance(result, str)
        assert "started successfully" in result
        assert '/container start "test"' in fake.commands[1]

    def test_stop_container(self, ctx, monkeypatch):
        """Should stop a running container."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_stop_container(ctx=ctx, name="test"))

        assert isinstance(result, str)
        assert "stopped successfully" in result
        assert '/container stop "test"' in fake.commands[1]

    def test_restart_container(self, ctx, monkeypatch):
        """Should restart a container."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_restart_container(ctx=ctx, name="test"))

        assert isinstance(result, str)
        assert "restarted successfully" in result
        assert '/container stop "test"' in fake.commands[1]
        assert '/container start "test"' in fake.commands[2]

    def test_start_container_not_found(self, ctx, monkeypatch):
        """Should handle start on non-existent container."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "0"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_start_container(ctx=ctx, name="nonexistent"))

        assert "not found" in result


class TestRemoveContainer:
    """Tests for remove_container function."""

    def test_remove_container_success(self, ctx, monkeypatch):
        """Should remove a container successfully."""
        fake = FakeExecutor()

        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "1"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_remove_container(ctx=ctx, name="test"))

        assert isinstance(result, str)
        assert "removed successfully" in result

    def test_remove_container_not_found(self, ctx, monkeypatch):
        """Should handle removal of non-existent container."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "0"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_remove_container(ctx=ctx, name="nonexistent"))

        assert "not found" in result


class TestContainerLogs:
    """Tests for container logging functions."""

    def test_get_container_logs_success(self, ctx, monkeypatch):
        """Should retrieve container logs."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "1"
            if "log" in command:
                return "Line 1\nLine 2\nLine 3"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_get_container_logs(
            ctx=ctx,
            name="test",
            tail=10
        ))

        assert isinstance(result, str)
        assert "CONTAINER LOGS" in result
        assert "Line 1" in result

    def test_get_container_logs_empty(self, ctx, monkeypatch):
        """Should handle container with no logs."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "1"
            if "log" in command:
                return ""
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_get_container_logs(ctx=ctx, name="test"))

        assert "No logs available" in result

    def test_get_container_logs_not_found(self, ctx, monkeypatch):
        """Should handle logs for non-existent container."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "0"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_get_container_logs(ctx=ctx, name="nonexistent"))

        assert "not found" in result

    def test_get_container_info_success(self, ctx, monkeypatch):
        """Should retrieve comprehensive container information."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "1"
            if "detail" in command:
                return 'name="test" status=running'
            if "log" in command:
                return "Setup log line\nStartup log line"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_get_container_info(ctx=ctx, name="test"))

        assert isinstance(result, str)
        assert "CONTAINER INFO" in result
        assert "DETAILS" in result
        assert "RECENT LOGS" in result


class TestContainerMounts:
    """Tests for container mount operations."""

    def test_list_container_mounts_all(self, ctx, monkeypatch):
        """Should list all container mounts."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_list_container_mounts(ctx=ctx))

        assert isinstance(result, str)
        assert "CONTAINER MOUNTS" in result
        assert '/container mounts print' in fake.commands[0]

    def test_list_container_mounts_filtered(self, ctx, monkeypatch):
        """Should list mounts filtered by container name."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_list_container_mounts(
            ctx=ctx,
            container_name="test"
        ))

        assert isinstance(result, str)
        assert 'container="test"' in fake.commands[0]

    def test_create_container_mount(self, ctx, monkeypatch):
        """Should create a container mount."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_create_container_mount(
            ctx=ctx,
            container="test",
            src="/var/data",
            dst="/data"
        ))

        assert isinstance(result, str)
        assert '/container mounts add' in fake.commands[0]
        assert 'container="test"' in fake.commands[0]

    def test_create_container_mount_with_comment(self, ctx, monkeypatch):
        """Should create a mount with comment."""
        fake = FakeExecutor()
        monkeypatch.setattr(mod, "execute_mikrotik_command", fake, raising=True)

        result = asyncio.run(mod.mikrotik_create_container_mount(
            ctx=ctx,
            container="test",
            src="/var/data",
            dst="/data",
            comment="Data volume"
        ))

        assert "comment=" in fake.commands[0]

    def test_remove_container_mount_success(self, ctx, monkeypatch):
        """Should remove a container mount."""
        fake = FakeExecutor()

        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "1"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_remove_container_mount(
            ctx=ctx,
            container="test",
            src="/var/data",
            dst="/data"
        ))

        assert isinstance(result, str)
        assert "removed successfully" in result

    def test_remove_container_mount_not_found(self, ctx, monkeypatch):
        """Should handle removal of non-existent mount."""
        async def fake_exec(command: str, _ctx, device=None):
            if "count-only" in command:
                return "0"
            return ""

        monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec)

        result = asyncio.run(mod.mikrotik_remove_container_mount(
            ctx=ctx,
            container="test",
            src="/var/data",
            dst="/data"
        ))

        assert "not found" in result
