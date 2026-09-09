### Container Management

#### `mikrotik_list_containers`
Lists all containers on the MikroTik device.
- Parameters:
  - `name_filter` (optional): Partial match for container name
  - `status_filter` (optional): `running`, `stopped`, or `starting`
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_list_containers()
  mikrotik_list_containers(name_filter="web", status_filter="running")
  ```

#### `mikrotik_get_container`
Gets detailed information for a specific container.
- Parameters:
  - `name` (required): Exact container name
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_get_container(name="web-app")
  ```

#### `mikrotik_create_container`
Creates a new container on the MikroTik device.
- Parameters:
  - `name` (required): Container name
  - `image` (required): Container image name
  - `interface` (required): Network interface for the container
  - `hostname` (optional): Container hostname
  - `root_dir` (optional): Root filesystem directory
  - `memory_limit` (optional): Memory limit (for example `512M` or `1G`)
  - `cpu_limit` (optional): CPU limit
  - `entrypoint` (optional): Container entrypoint
  - `cmd` (optional): Container command to execute
  - `envlist` (optional): Environment variables list such as `["DEBUG=1", "LOG_LEVEL=info"]`
  - `disabled` (optional): Create container in disabled state
  - `comment` (optional): Free-form comment
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_create_container(
    name="web-app",
    image="nginx:latest",
    interface="bridge1",
    hostname="web-app-01",
    memory_limit="512M",
    envlist=["DEBUG=1"]
  )
  ```

#### `mikrotik_update_container`
Updates an existing container configuration.
- Parameters:
  - `name` (required): Exact container name
  - `hostname` (optional): New hostname
  - `memory_limit` (optional): New memory limit
  - `cpu_limit` (optional): New CPU limit
  - `cmd` (optional): New command
  - `envlist` (optional): New environment variables list
  - `disabled` (optional): Enable or disable container
  - `comment` (optional): Update description
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_update_container(name="web-app", memory_limit="1G", disabled=false)
  ```

#### `mikrotik_remove_container`
Removes a container from the MikroTik device.
- Parameters:
  - `name` (required): Exact container name
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_remove_container(name="web-app")
  ```

#### `mikrotik_start_container`
Starts a stopped container.
- Parameters:
  - `name` (required): Exact container name
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_start_container(name="web-app")
  ```

#### `mikrotik_stop_container`
Stops a running container.
- Parameters:
  - `name` (required): Exact container name
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_stop_container(name="web-app")
  ```

#### `mikrotik_restart_container`
Restarts a container.
- Parameters:
  - `name` (required): Exact container name
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_restart_container(name="web-app")
  ```

#### `mikrotik_get_container_logs`
Reads recent logs for a specific container.
- Parameters:
  - `name` (required): Exact container name
  - `tail` (optional): Number of log lines to return, default `100`
  - `follow` (optional): Follow log stream if true
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_get_container_logs(name="web-app", tail=50)
  ```

#### `mikrotik_get_container_info`
Gets a summary of the container plus its recent logs.
- Parameters:
  - `name` (required): Exact container name
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_get_container_info(name="web-app")
  ```

#### `mikrotik_list_container_mounts`
Lists container mount points.
- Parameters:
  - `container_name` (optional): Filter by container name
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_list_container_mounts(container_name="web-app")
  ```

#### `mikrotik_create_container_mount`
Creates a host-to-container mount.
- Parameters:
  - `container` (required): Container name
  - `src` (required): Source path on the MikroTik host
  - `dst` (required): Destination path inside the container
  - `comment` (optional): Free-form comment
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_create_container_mount(container="web-app", src="/mnt/data", dst="/data")
  ```

#### `mikrotik_remove_container_mount`
Removes a container mount.
- Parameters:
  - `container` (required): Container name
  - `src` (required): Source path on the MikroTik host
  - `dst` (required): Destination path inside the container
  - `device` (optional): Device title override
- Example:
  ```
  mikrotik_remove_container_mount(container="web-app", src="/mnt/data", dst="/data")
  ```

### Common Workflows

Create a container and then inspect logs:
```python
mikrotik_create_container(
    name="web-app",
    image="nginx:latest",
    interface="bridge1",
    envlist=["TZ=UTC"]
)

mikrotik_start_container(name="web-app")
mikrotik_get_container_logs(name="web-app", tail=50)
```

Update a running container:
```python
mikrotik_update_container(name="web-app", memory_limit="1G", comment="Production web app")
```

Remove a container when it is no longer needed:
```python
mikrotik_remove_container(name="web-app")
```
