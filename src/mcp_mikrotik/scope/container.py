from typing import Optional, List, Literal
from mcp.server.mcpserver import Context
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE, annotate
from ..connector import execute_mikrotik_command


@mcp.tool(name="list_containers", annotations=annotate(READ, "List Containers"))
async def mikrotik_list_containers(
    ctx: Context,
    name_filter: Optional[str] = None,
    status_filter: Optional[Literal["stopped", "running", "starting"]] = None,
    device: Optional[str] = None,
) -> str:
    """Lists all containers on the MikroTik device.

    Notes:
        name_filter: partial name match, e.g. "web" matches web-app, web-api, etc.
        status_filter: filter by container status (stopped, running, starting)
    """
    await ctx.info("Listing all containers")

    cmd = "/container print"
    filters = []

    if name_filter:
        filters.append(f'name="{name_filter}"')
    if status_filter:
        filters.append(f'status="{status_filter}"')

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if not result or result.strip() == "":
        return "No containers found matching the criteria."

    return f"CONTAINERS:\n\n{result}"


@mcp.tool(name="get_container", annotations=annotate(READ, "Get Container"))
async def mikrotik_get_container(ctx: Context, name: str, device: Optional[str] = None) -> str:
    """Gets detailed information about a specific container by name.

    Notes:
        name: exact container name
    """
    await ctx.info(f"Getting container details: name={name}")

    cmd = f'/container print detail where name="{name}"'
    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if not result or result.strip() == "":
        return f"Container '{name}' not found."

    return f"CONTAINER DETAILS:\n\n{result}"


@mcp.tool(name="create_container", annotations=annotate(WRITE, "Create Container"))
async def mikrotik_create_container(
    ctx: Context,
    name: str,
    image: str,
    interface: str,
    hostname: Optional[str] = None,
    root_dir: Optional[str] = None,
    memory_limit: Optional[str] = None,
    cpu_limit: Optional[str] = None,
    entrypoint: Optional[str] = None,
    cmd: Optional[str] = None,
    envlist: Optional[List[str]] = None,
    disabled: bool = False,
    comment: Optional[str] = None,
    device: Optional[str] = None,
) -> str:
    """Creates a new container on the MikroTik device.

    Notes:
        name: container name
        image: container image name
        interface: interface name for container networking
        hostname: hostname for the container (optional)
        root_dir: optional directory for container root filesystem
        memory_limit: memory limit (e.g., "512M", "1G")
        cpu_limit: CPU limit (number of cores)
        entrypoint: container entrypoint
        cmd: command to run
        envlist: environment variables as list (e.g., ["VAR=value", "DEBUG=1"])
        disabled: create container in disabled state
    """
    await ctx.info(f"Creating container: name={name}, remote-image={image}, interface={interface}")

    cmd_parts = [f"/container add name={name} remote-image={image} interface={interface}"]

    if hostname:
        cmd_parts.append(f' hostname={hostname}')
    if root_dir:
        cmd_parts.append(f' root-dir={root_dir}')
    if memory_limit:
        cmd_parts.append(f' memory-limit={memory_limit}')
    if cpu_limit:
        cmd_parts.append(f' cpu-limit={cpu_limit}')
    if entrypoint:
        cmd_parts.append(f' entrypoint={entrypoint}')
    if cmd:
        cmd_parts.append(f' cmd={cmd}')
    if envlist:
        env_str = ' '.join(envlist)
        cmd_parts.append(f' envlist="{env_str}"')
    if disabled:
        cmd_parts.append(' disabled=yes')
    if comment:
        cmd_parts.append(f' comment="{comment}"')

    full_cmd = "".join(cmd_parts)
    result = await execute_mikrotik_command(full_cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create container: {result}"

    # Verify the creation
    check_cmd = f'/container print detail where name="{name}"'
    details = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if not details.strip():
        return f"Container '{name}' was created but details could not be retrieved."

    return f"Container '{name}' created successfully:\n\n{details}"


@mcp.tool(name="update_container", annotations=annotate(WRITE_IDEMPOTENT, "Update Container"))
async def mikrotik_update_container(
    ctx: Context,
    name: str,
    hostname: Optional[str] = None,
    memory_limit: Optional[str] = None,
    cpu_limit: Optional[str] = None,
    cmd: Optional[str] = None,
    envlist: Optional[List[str]] = None,
    disabled: Optional[bool] = None,
    comment: Optional[str] = None,
    device: Optional[str] = None,
) -> str:
    """Updates configuration of an existing container.

    Notes:
        name: exact container name
        All other parameters are optional; only specified parameters will be updated
    """
    await ctx.info(f"Updating container: name={name}")

    # Check if container exists
    check_cmd = f'/container print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Container '{name}' not found."

    # Build update command
    cmd_parts = [f"/container set [find name=\"{name}\"]"]

    if hostname is not None:
        cmd_parts.append(f' hostname={hostname}')
    if memory_limit is not None:
        cmd_parts.append(f' memory-limit={memory_limit}')
    if cpu_limit is not None:
        cmd_parts.append(f' cpu-limit={cpu_limit}')
    if cmd is not None:
        cmd_parts.append(f' cmd={cmd}')
    if envlist is not None:
        env_str = ' '.join(envlist)
        cmd_parts.append(f' envlist="{env_str}"')
    if disabled is not None:
        disabled_val = "yes" if disabled else "no"
        cmd_parts.append(f' disabled={disabled_val}')
    if comment is not None:
        cmd_parts.append(f' comment="{comment}"')

    # If no parameters specified, return early
    if len(cmd_parts) == 1:
        return "No parameters specified for update."

    full_cmd = "".join(cmd_parts)
    result = await execute_mikrotik_command(full_cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update container: {result}"

    # Get updated details
    details_cmd = f'/container print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx, device=device)

    return f"Container '{name}' updated successfully:\n\n{details}"


@mcp.tool(name="remove_container", annotations=annotate(DESTRUCTIVE, "Remove Container"))
async def mikrotik_remove_container(ctx: Context, name: str, device: Optional[str] = None) -> str:
    """Removes a container from the MikroTik device.

    Notes:
        name: exact container name
        The container will be stopped and deleted
    """
    await ctx.info(f"Removing container: name={name}")

    # Check if container exists
    check_cmd = f'/container print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Container '{name}' not found."

    # Remove the container
    cmd = f'/container remove [find name="{name}"]'
    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove container: {result}"

    return f"Container '{name}' removed successfully."


@mcp.tool(name="start_container", annotations=annotate(WRITE_IDEMPOTENT, "Start Container"))
async def mikrotik_start_container(ctx: Context, name: str, device: Optional[str] = None) -> str:
    """Starts a stopped container on the MikroTik device.

    Notes:
        name: exact container name
    """
    await ctx.info(f"Starting container: name={name}")

    # Check if container exists
    check_cmd = f'/container print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Container '{name}' not found."

    # Start the container
    cmd = f'/container start "{name}"'
    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to start container: {result}"

    # Verify status
    status_cmd = f'/container print where name="{name}"'
    status = await execute_mikrotik_command(status_cmd, ctx, device=device)

    return f"Container '{name}' started successfully:\n\n{status}"

@mcp.tool(name="repull_container", annotations=annotate(WRITE_IDEMPOTENT, "Repull Container"))
async def mikrotik_repull_container(ctx: Context, name: str, image: str, device: Optional[str] = None) -> str:
    """Repulls a container on the MikroTik device.

    Notes:
        name: exact container name
        image: the image to repull
    """
    await ctx.info(f"Repulling container: name={name}")

    # Check if container exists
    check_cmd = f'/container print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Container '{name}' not found."

    # Start the container
    cmd = f'/container repull remote-image={image} number=\"{name}\"'
    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to repull container: {result}"

    # Verify status
    status_cmd = f'/container print where name="{name}"'
    status = await execute_mikrotik_command(status_cmd, ctx, device=device)

    return f"Container '{name}' repulled successfully:\n\n{status}"

@mcp.tool(name="stop_container", annotations=annotate(WRITE_IDEMPOTENT, "Stop Container"))
async def mikrotik_stop_container(ctx: Context, name: str, device: Optional[str] = None) -> str:
    """Stops a running container on the MikroTik device.

    Notes:
        name: exact container name
    """
    await ctx.info(f"Stopping container: name={name}")

    # Check if container exists
    check_cmd = f'/container print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Container '{name}' not found."

    # Stop the container
    cmd = f'/container stop "{name}"'
    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to stop container: {result}"

    # Verify status
    status_cmd = f'/container print where name="{name}"'
    status = await execute_mikrotik_command(status_cmd, ctx, device=device)

    return f"Container '{name}' stopped successfully:\n\n{status}"


@mcp.tool(name="restart_container", annotations=annotate(WRITE_IDEMPOTENT, "Restart Container"))
async def mikrotik_restart_container(ctx: Context, name: str, device: Optional[str] = None) -> str:
    """Restarts a container on the MikroTik device (stops then starts).

    Notes:
        name: exact container name
    """
    await ctx.info(f"Restarting container: name={name}")

    # Check if container exists
    check_cmd = f'/container print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Container '{name}' not found."

    # Stop the container
    stop_cmd = f'/container stop "{name}"'
    await execute_mikrotik_command(stop_cmd, ctx, device=device)

    # Start the container
    start_cmd = f'/container start "{name}"'
    result = await execute_mikrotik_command(start_cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to restart container: {result}"

    # Verify status
    status_cmd = f'/container print where name="{name}"'
    status = await execute_mikrotik_command(status_cmd, ctx, device=device)

    return f"Container '{name}' restarted successfully:\n\n{status}"


@mcp.tool(name="get_container_logs", annotations=annotate(READ, "Get Container Logs"))
async def mikrotik_get_container_logs(
    ctx: Context,
    name: str,
    device: Optional[str] = None,
) -> str:
    """Gets logs from a specific container on the MikroTik device.

    Notes:
        name: exact container name
    """
    await ctx.info(f"Getting container logs: name={name}")

    # Check if container exists
    check_cmd = f'/container print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Container '{name}' not found."

    # Get container logs
    cmd = f'/container log print where container "{name}"'
    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if not result or result.strip() == "":
        return f"No logs available for container '{name}'."

    # Limit to tail lines
    lines = result.strip().split('\n')
    log_lines = lines[-20:] if len(lines) > 20 else lines
    return f"CONTAINER LOGS (last {len(log_lines)} lines) - Container: {name}\n\n" + "\n".join(log_lines)


@mcp.tool(name="get_container_info", annotations=annotate(READ, "Get Container Info"))
async def mikrotik_get_container_info(
    ctx: Context,
    name: str,
    device: Optional[str] = None,
) -> str:
    """Gets comprehensive information about a container including status, resources, and logs.

    Notes:
        name: exact container name
        Returns status, uptime, memory usage, and recent logs
    """
    await ctx.info(f"Getting comprehensive container info: name={name}")

    # Check if container exists
    check_cmd = f'/container print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Container '{name}' not found."

    # Get detailed container info
    details_cmd = f'/container print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx, device=device)

    # Get container logs (last 20 lines)
    log_cmd = f'/container log print where container "{name}"'
    logs = await execute_mikrotik_command(log_cmd, ctx, device=device)

    log_output = "No logs available"
    if logs and logs.strip():
        lines = logs.strip().split('\n')
        log_lines = lines[-20:] if len(lines) > 20 else lines
        log_output = "\n".join(log_lines)

    return f"CONTAINER INFO - {name}\n\n--- DETAILS ---\n{details}\n\n--- RECENT LOGS (last 20 lines) ---\n{log_output}"


@mcp.tool(name="list_container_mounts", annotations=annotate(READ, "List Container Mounts"))
async def mikrotik_list_container_mounts(
    ctx: Context,
    container_name: Optional[str] = None,
    device: Optional[str] = None,
) -> str:
    """Lists all container mount points, optionally filtered by container name.

    Notes:
        container_name: optional container name to filter mounts
    """
    await ctx.info(f"Listing container mounts: container_name={container_name}")

    cmd = "/container mounts print"
    if container_name:
        cmd += f' where container="{container_name}"'

    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if not result or result.strip() == "":
        return "No container mounts found."

    return f"CONTAINER MOUNTS:\n\n{result}"


@mcp.tool(name="create_container_mount", annotations=annotate(WRITE, "Create Container Mount"))
async def mikrotik_create_container_mount(
    ctx: Context,
    container: str,
    src: str,
    dst: str,
    comment: Optional[str] = None,
    device: Optional[str] = None,
) -> str:
    """Creates a mount point for a container (mounts host directory into container).

    Notes:
        container: container name
        src: source path on host
        dst: destination path inside container
    """
    await ctx.info(f"Creating mount for container: container={container}, src={src}, dst={dst}")

    cmd = f'/container mounts add container="{container}" src={src} dst={dst}'

    if comment:
        cmd += f' comment="{comment}"'

    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create container mount: {result}"

    # Get mount details
    details_cmd = f'/container mounts print where container="{container}" and src={src} and dst={dst}'
    details = await execute_mikrotik_command(details_cmd, ctx, device=device)

    return f"Container mount created successfully:\n\n{details}"


@mcp.tool(name="remove_container_mount", annotations=annotate(DESTRUCTIVE, "Remove Container Mount"))
async def mikrotik_remove_container_mount(
    ctx: Context,
    container: str,
    src: str,
    dst: str,
    device: Optional[str] = None,
) -> str:
    """Removes a mount point from a container.

    Notes:
        container: container name
        src: source path on host (must match exactly)
        dst: destination path inside container (must match exactly)
    """
    await ctx.info(f"Removing mount from container: container={container}, src={src}, dst={dst}")

    # Check if mount exists
    check_cmd = f'/container mounts print count-only where container="{container}" and src={src} and dst={dst}'
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0":
        return f"Mount not found for container '{container}' with src={src} and dst={dst}."

    # Remove the mount
    cmd = f'/container mounts remove [find container="{container}" and src={src} and dst={dst}]'
    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove container mount: {result}"

    return f"Container mount (src={src}, dst={dst}) removed successfully from container '{container}'."