from typing import Literal, Optional
from mcp.server.mcpserver import Context
from ..connector import execute_mikrotik_command
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE, annotate

@mcp.tool(name="create_mangle_rule", annotations=annotate(WRITE, "Create Firewall Mangle Rule"))
async def mikrotik_create_mangle_rule(
    ctx: Context,
    chain: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"],
    action: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ],
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    src_port: Optional[str] = None,
    dst_port: Optional[str] = None,
    protocol: Optional[str] = None,
    in_interface: Optional[str] = None,
    out_interface: Optional[str] = None,
    connection_state: Optional[str] = None,
    connection_nat_state: Optional[str] = None,
    new_packet_mark: Optional[str] = None,
    new_connection_mark: Optional[str] = None,
    new_routing_mark: Optional[str] = None,
    connection_mark: Optional[str] = None,
    routing_mark: Optional[str] = None,
    packet_mark: Optional[str] = None,
    per_connection_classifier: Optional[str] = None,
    src_address_list: Optional[str] = None,
    dst_address_list: Optional[str] = None,
    limit: Optional[str] = None,
    tcp_flags: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
    log: bool = False,
    log_prefix: Optional[str] = None,
    chain_filter: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"] = None, 
    action_filter: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ] = None,
    comment_filter: Optional[str] = None,
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    in_interface_filter: Optional[str] = None,
    out_interface_filter: Optional[str] = None,
    packet_mark_filter: Optional[str] = None,
    connection_mark_filter: Optional[str] = None,
    routing_mark_filter: Optional[str] = None,
    device: Optional[str] = None
) -> str:
    """Creates a firewall mangle rule in the specified chain on the MikroTik device.

    Args:
        ctx: MCP server context
        chain: Target chain - prerouting, input, forward, output, postrouting, lanin, lanout, or lanforward
        action: Rule action - mark-packet, mark-connection, mark-routing, sniff-tzsp, change-mss, change-dscp, 
                jump, log, passthrough, return, accept, drop, fasttrack-connection, route, set-priority, 
                add-dst-to-address-list, add-src-to-address-list, change-ttl, clear-df, sniff-pc, strip-ipv4-options
        
        Matching criteria (all optional - used to match traffic):
            src_address: Source IP or CIDR, e.g. "192.168.1.0/24"
            dst_address: Destination IP or CIDR
            src_port: Source port number or range, e.g. "80" or "8000-9000"
            dst_port: Destination port number or range
            protocol: Protocol filter - tcp, udp, icmp, etc.
            in_interface: Incoming interface name
            out_interface: Outgoing interface name
            connection_state: Comma-separated connection states, e.g. "established,related,new,invalid"
            connection_nat_state: NAT connection state (dnat, snat, none)
            src_address_list: Source address list reference (by name)
            dst_address_list: Destination address list reference (by name)
        
        Actions and marks (all optional - specify what to do with matched traffic):
            new_packet_mark: Mark name for packets, e.g. "my-pack-mark"
            new_connection_mark: Mark name for connections, e.g. "my-conn-mark"
            new_routing_mark: Mark name for routing policy, e.g. "my-route-mark"
            connection_mark: Filter by existing connection mark when matching
            routing_mark: Filter by existing routing mark when matching
            packet_mark: Filter by existing packet mark when matching
            per_connection_classifier: Per-connection traffic classifier
        
        Advanced options:
            limit: RouterOS rate/burst limiter, e.g. "10,5:packet" or "10/1s:packet"
            tcp_flags: TCP flags filter, e.g. "syn,!ack"
            comment: Rule description/comment
            disabled: Set to true to create the rule in disabled state (default: false)
            log: Set to true to enable logging (default: false)
            log_prefix: Log message prefix (only used when log=true)
        
        Rule placement (optional - position the rule before a matching rule):
            chain_filter: Chain to search for placement rule
            action_filter: Action to match for placement
            comment_filter: Comment match for placement
            src_address_filter: Source address match for placement
            dst_address_filter: Destination address match for placement
            protocol_filter: Protocol match for placement
            in_interface_filter: Input interface match for placement
            out_interface_filter: Output interface match for placement
            packet_mark_filter: Packet mark match for placement
            connection_mark_filter: Connection mark match for placement
            routing_mark_filter: Routing mark match for placement
        
        device: Target device name (for multi-device management)
    
    Returns:
        Confirmation message with rule creation result
    """
    await ctx.info(f"Creating firewall mangle rule: chain={chain}, action={action}")

    # Build the command
    cmd = f"/ip firewall mangle add chain={chain} action={action}"

    # Add optional parameters
    if src_address:
        cmd += f" src-address={src_address}"

    if dst_address:
        cmd += f" dst-address={dst_address}"

    if src_port:
        cmd += f" src-port={src_port}"

    if dst_port:
        cmd += f" dst-port={dst_port}"

    if protocol:
        cmd += f" protocol={protocol}"

    if in_interface:
        cmd += f' in-interface="{in_interface}"'

    if out_interface:
        cmd += f' out-interface="{out_interface}"'

    if connection_state:
        cmd += f" connection-state={connection_state}"

    if connection_nat_state:
        cmd += f" connection-nat-state={connection_nat_state}"

    if src_address_list:
        cmd += f' src-address-list="{src_address_list}"'

    if dst_address_list:
        cmd += f' dst-address-list="{dst_address_list}"'

    if limit:
        cmd += f" limit={limit}"

    if tcp_flags:
        cmd += f" tcp-flags={tcp_flags}"

    if per_connection_classifier:
        cmd += f' per-connection-classifier="{per_connection_classifier}"'

    if new_packet_mark:
        cmd += f' new-packet-mark="{new_packet_mark}"'

    if new_connection_mark:
        cmd += f' new-connection-mark="{new_connection_mark}"'

    if new_routing_mark:
        cmd += f' new-routing-mark="{new_routing_mark}"'

    if connection_mark:
        cmd += f' connection-mark="{connection_mark}"'

    if routing_mark:
        cmd += f' routing-mark="{routing_mark}"'

    if packet_mark:
        cmd += f' packet-mark="{packet_mark}"'

    if comment:
        cmd += f' comment="{comment}"'

    if disabled:
        cmd += " disabled=yes"

    if log:
        cmd += " log=yes"
        if log_prefix:
            cmd += f' log-prefix="{log_prefix}"'


    find_parts: list[str] = []
    if comment_filter:
        find_parts.append(f'comment="{comment_filter}"')
    if action_filter:
        find_parts.append(f'action={action_filter}')
    if chain_filter:
        find_parts.append(f'chain={chain_filter}')
    if src_address_filter:
        find_parts.append(f'src-address={src_address_filter}')
    if dst_address_filter:
        find_parts.append(f'dst-address={dst_address_filter}')
    if protocol_filter:
        find_parts.append(f'protocol={protocol_filter}')
    if in_interface_filter:
        find_parts.append(f'in-interface="{in_interface_filter}"')
    if out_interface_filter:
        find_parts.append(f'out-interface="{out_interface_filter}"')
    if packet_mark_filter:
        find_parts.append(f'new-packet-mark="{packet_mark_filter}"')
    if connection_mark_filter:
        find_parts.append(f'new-connection-mark="{connection_mark_filter}"')
    if routing_mark_filter:
        find_parts.append(f'new-routing-mark="{routing_mark_filter}"')

    find_builder = "find " + " and ".join(find_parts)
    if find_parts:
        check_cmd = f"/ip firewall mangle print count-only where "+ " and ".join(find_parts)
        count = await execute_mikrotik_command(check_cmd, ctx, device=device)

        if count.strip() == "0" or not count.strip().isdigit():
            return f"No firewall mangle rules found matching the filter criteria."

        cmd += f" place-before=[{find_builder}]"

    result = await execute_mikrotik_command(cmd, ctx, device=device)

    # Check if creation was successful
    return f"Firewall mangle rule created:\n{result}"

@mcp.tool(name="list_mangle_rules", annotations=annotate(READ, "List Firewall Mangle Rules"))
async def mikrotik_list_mangle_rules(
    ctx: Context,
    action_filter: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ],    
    chain_filter: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"], 
    comment: Optional[str] = None,    
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    interface_filter: Optional[str] = None,
    packet_mark_filter: Optional[str] = None,
    connection_mark_filter: Optional[str] = None,
    routing_mark_filter: Optional[str] = None,
    disabled_only: bool = False,
    invalid_only: bool = False,
    device: Optional[str] = None
) -> str:
    """Lists firewall mangle rules on the MikroTik device with optional filters.

    Args:
        ctx: MCP server context
        action_filter: Filter by rule action (required)
        chain_filter: Filter by chain (required) - prerouting, input, forward, output, postrouting, lanin, lanout, lanforward
        comment: Partial match on rule comment/description
        src_address_filter: Partial match on source address
        dst_address_filter: Partial match on destination address
        protocol_filter: Filter by protocol
        interface_filter: Filter by interface name (checks both in-interface and out-interface)
        packet_mark_filter: Partial match on packet mark
        connection_mark_filter: Partial match on connection mark
        routing_mark_filter: Partial match on routing mark
        disabled_only: Show only disabled rules (default: false)
        invalid_only: Show only invalid rules (default: false)
        device: Target device name (for multi-device management)
    
    Returns:
        Formatted list of firewall mangle rules matching the filters
    """
    await ctx.info(f"Listing firewall mangle rules with filters: chain={chain_filter}, action={action_filter}")

    # Build the command
    cmd = "/ip firewall mangle print detail"

    # Add filters
    filters = []
    if chain_filter:
        filters.append(f"chain={chain_filter}")
    if comment:
        filters.append(f'comment="{comment}"')
    if action_filter:
        filters.append(f"action={action_filter}")
    if src_address_filter:
        filters.append(f'src-address="{src_address_filter}"')
    if dst_address_filter:
        filters.append(f'dst-address="{dst_address_filter}"')
    if protocol_filter:
        filters.append(f"protocol={protocol_filter}")
    if interface_filter:
        filters.append(f'(in-interface="{interface_filter}" or out-interface="{interface_filter}")')
    if packet_mark_filter:
        filters.append(f'new-packet-mark="{packet_mark_filter}"')
    if connection_mark_filter:
        filters.append(f'new-connection-mark="{connection_mark_filter}"')
    if routing_mark_filter:
        filters.append(f'new-routing-mark="{routing_mark_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if invalid_only:
        filters.append("invalid=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx, device=device)
    return f"FIREWALL MANGLE RULES:\n{result}"

@mcp.tool(name="update_mangle_rule", annotations=annotate(WRITE_IDEMPOTENT, "Update Firewall Mangle Rule"))
async def mikrotik_update_mangle_rule(
    ctx: Context,
    chain_filter: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"], 
    action_filter: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ],
    comment_filter: Optional[str] = None,
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    in_interface_filter: Optional[str] = None,
    out_interface_filter: Optional[str] = None,
    packet_mark_filter: Optional[str] = None,
    connection_mark_filter: Optional[str] = None,
    routing_mark_filter: Optional[str] = None,
    chain: Optional[str] = None,
    action: Optional[str] = None,
    per_connection_classifier: Optional[str] = None,
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    src_port: Optional[str] = None,
    dst_port: Optional[str] = None,
    protocol: Optional[str] = None,
    in_interface: Optional[str] = None,
    out_interface: Optional[str] = None,
    connection_state: Optional[str] = None,
    connection_nat_state: Optional[str] = None,
    new_packet_mark: Optional[str] = None,
    new_connection_mark: Optional[str] = None,
    new_routing_mark: Optional[str] = None,
    connection_mark: Optional[str] = None,
    routing_mark: Optional[str] = None,
    packet_mark: Optional[str] = None,
    src_address_list: Optional[str] = None,
    dst_address_list: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
    log: Optional[bool] = None,
    log_prefix: Optional[str] = None,
    device: Optional[str] = None
) -> str:
    """Updates an existing firewall mangle rule on the MikroTik device.

    Notes:
        Rule selection: Use filter parameters (chain_filter, action_filter, comment_filter, etc.) to find and update rules by their properties. If multiple rules match, all matching rules are updated.
        
        Selector filters (chain_filter and action_filter are required when matching; optional others are combined with AND):
            chain_filter: the chain containing the rule to update
            action_filter: the rule action to match
            comment_filter: exact or partial comment match
            src_address_filter, dst_address_filter: partial address match
            protocol_filter: filter by protocol
            in_interface_filter, out_interface_filter: interface name (partial match)
            packet_mark_filter: new-packet-mark (partial match)
            connection_mark_filter: new-connection-mark (partial match)
            routing_mark_filter: new-routing-mark (partial match)
        
        Update parameters (all optional - specify only what should change):
            chain, action: change rule chain or action
            src_address, dst_address, src_port, dst_port: update match criteria
            protocol: change protocol match
            in_interface, out_interface: change interface match
            connection_state, connection_nat_state: update state conditions
            new_packet_mark, new_connection_mark, new_routing_mark: update marks
            per_connection_classifier: set per-connection traffic classification
            connection_mark, routing_mark, packet_mark: filter by existing marks
            src_address_list, dst_address_list: update address list references
            comment: update rule description
            disabled: enable (false) or disable (true) the rule
            log: enable/disable logging
            log_prefix: set log message prefix
        
        Clearing fields: Pass empty string "" for string/optional fields to clear them.
    """
    # Build optional find selector (e.g. find comment="foo" and action=mark-packet)
    find_parts: list[str] = []
    if comment_filter:
        find_parts.append(f'comment="{comment_filter}"')
    if action_filter:
        find_parts.append(f'action={action_filter}')
    if chain_filter:
        find_parts.append(f'chain={chain_filter}')
    if src_address_filter:
        find_parts.append(f'src-address={src_address_filter}')
    if dst_address_filter:
        find_parts.append(f'dst-address={dst_address_filter}')
    if protocol_filter:
        find_parts.append(f'protocol={protocol_filter}')
    if in_interface_filter:
        find_parts.append(f'in-interface="{in_interface_filter}"')
    if out_interface_filter:
        find_parts.append(f'out-interface="{out_interface_filter}"')
    if packet_mark_filter:
        find_parts.append(f'new-packet-mark="{packet_mark_filter}"')
    if connection_mark_filter:
        find_parts.append(f'new-connection-mark="{connection_mark_filter}"')
    if routing_mark_filter:
        find_parts.append(f'new-routing-mark="{routing_mark_filter}"')

    check_cmd = f"/ip firewall mangle print count-only where "+ " and ".join(find_parts)
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0" or not count.strip().isdigit():
        return f"No firewall mangle rules found matching the filter criteria."

    find_builder = "find " + " and ".join(find_parts)
    cmd = f"/ip firewall mangle set [{find_builder}]"

    await ctx.info(f"Updating firewall mangle filter: filter={find_builder}")

    # Add parameters to update
    updates = []
    if chain:
        updates.append(f"chain={chain}")
    if action:
        updates.append(f"action={action}")
    if src_address is not None:
        if src_address == "":
            updates.append("!src-address")
        else:
            updates.append(f"src-address={src_address}")
    if dst_address is not None:
        if dst_address == "":
            updates.append("!dst-address")
        else:
            updates.append(f"dst-address={dst_address}")
    if src_port is not None:
        if src_port == "":
            updates.append("!src-port")
        else:
            updates.append(f"src-port={src_port}")
    if dst_port is not None:
        if dst_port == "":
            updates.append("!dst-port")
        else:
            updates.append(f"dst-port={dst_port}")
    if protocol is not None:
        if protocol == "":
            updates.append("!protocol")
        else:
            updates.append(f"protocol={protocol}")
    if in_interface is not None:
        if in_interface == "":
            updates.append("!in-interface")
        else:
            updates.append(f'in-interface="{in_interface}"')
    if out_interface is not None:
        if out_interface == "":
            updates.append("!out-interface")
        else:
            updates.append(f'out-interface="{out_interface}"')
    if connection_state is not None:
        if connection_state == "":
            updates.append("!connection-state")
        else:
            updates.append(f"connection-state={connection_state}")
    if connection_nat_state is not None:
        if connection_nat_state == "":
            updates.append("!connection-nat-state")
        else:
            updates.append(f"connection-nat-state={connection_nat_state}")
    if new_packet_mark is not None:
        if new_packet_mark == "":
            updates.append("!new-packet-mark")
        else:
            updates.append(f'new-packet-mark="{new_packet_mark}"')
    if new_connection_mark is not None:
        if new_connection_mark == "":
            updates.append("!new-connection-mark")
        else:
            updates.append(f'new-connection-mark="{new_connection_mark}"')
    if per_connection_classifier is not None:
        if per_connection_classifier == "":
            updates.append("!per-connection-classifier")
        else:
            updates.append(f'per-connection-classifier="{per_connection_classifier}"')
    if new_routing_mark is not None:
        if new_routing_mark == "":
            updates.append("!new-routing-mark")
        else:
            updates.append(f'new-routing-mark="{new_routing_mark}"')
    if connection_mark is not None:
        if connection_mark == "":
            updates.append("!connection-mark")
        else:
            updates.append(f'connection-mark="{connection_mark}"')
    if routing_mark is not None:
        if routing_mark == "":
            updates.append("!routing-mark")
        else:
            updates.append(f'routing-mark="{routing_mark}"')
    if packet_mark is not None:
        if packet_mark == "":
            updates.append("!packet-mark")
        else:
            updates.append(f'packet-mark="{packet_mark}"')
    if src_address_list is not None:
        if src_address_list == "":
            updates.append("!src-address-list")
        else:
            updates.append(f'src-address-list="{src_address_list}"')
    if dst_address_list is not None:
        if dst_address_list == "":
            updates.append("!dst-address-list")
        else:
            updates.append(f'dst-address-list="{dst_address_list}"')
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')
    if log is not None:
        updates.append(f'log={"yes" if log else "no"}')
        if log and log_prefix:
            updates.append(f'log-prefix="{log_prefix}"')

    if not updates:
        return "No updates specified."

    cmd += " " + " ".join(updates)

    result = await execute_mikrotik_command(cmd, ctx, device=device)
    return f"Firewall mangle rule updated:\n{result}"

@mcp.tool(name="remove_mangle_rule", annotations=annotate(DESTRUCTIVE, "Remove Firewall Mangle Rule"))
async def mikrotik_remove_mangle_rule(
    ctx: Context,
    chain_filter: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"],
    action_filter: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ],
    comment_filter: Optional[str] = None,
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    in_interface_filter: Optional[str] = None,
    out_interface_filter: Optional[str] = None,
    packet_mark_filter: Optional[str] = None,
    connection_mark_filter: Optional[str] = None,
    routing_mark_filter: Optional[str] = None,
    device: Optional[str] = None
) -> str:
    """Removes firewall mangle rule(s) matching the specified filters.

    Args:
        ctx: MCP server context
        chain_filter: Required - the chain containing the rule (prerouting, input, forward, output, postrouting, lanin, lanout, lanforward)
        action_filter: Required - the rule action to match
        comment_filter: Partial match on rule comment
        src_address_filter: Partial match on source address
        dst_address_filter: Partial match on destination address
        protocol_filter: Filter by protocol
        in_interface_filter: Filter by input interface
        out_interface_filter: Filter by output interface
        packet_mark_filter: Partial match on packet mark
        connection_mark_filter: Partial match on connection mark
        routing_mark_filter: Partial match on routing mark
        device: Target device name (for multi-device management)
    
    Notes:
        All filters are combined with AND logic - all conditions must match to remove a rule.
        If multiple rules match the criteria, all matching rules are removed.
    
    Returns:
        Confirmation message showing number of rules removed
    """
    # Build find selector
    find_parts: list[str] = []
    find_parts.append(f'chain={chain_filter}')
    find_parts.append(f'action={action_filter}')
    
    if comment_filter:
        find_parts.append(f'comment=\"{comment_filter}\"')
    if src_address_filter:
        find_parts.append(f'src-address=\"{src_address_filter}\"')
    if dst_address_filter:
        find_parts.append(f'dst-address=\"{dst_address_filter}\"')
    if protocol_filter:
        find_parts.append(f'protocol={protocol_filter}')
    if in_interface_filter:
        find_parts.append(f'in-interface=\"{in_interface_filter}\"')
    if out_interface_filter:
        find_parts.append(f'out-interface=\"{out_interface_filter}\"')
    if packet_mark_filter:
        find_parts.append(f'new-packet-mark=\"{packet_mark_filter}\"')
    if connection_mark_filter:
        find_parts.append(f'new-connection-mark=\"{connection_mark_filter}\"')
    if routing_mark_filter:
        find_parts.append(f'new-routing-mark=\"{routing_mark_filter}\"')

    find_builder = "find " + " and ".join(find_parts)
    await ctx.info(f"Removing firewall mangle rules: {find_builder}")

    # Check if rules exist
    check_cmd = f"/ip firewall mangle print count-only where "+ " and ".join(find_parts)
    count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if count.strip() == "0" or not count.strip().isdigit():
        return f"No firewall mangle rules found matching the criteria."

    # Remove matching rules
    cmd = f"/ip firewall mangle remove [{find_builder}]"
    result = await execute_mikrotik_command(cmd, ctx, device=device)
    return f"{count.strip()} firewall mangle rule(s) removed:\n{result}"

@mcp.tool(name="move_mangle_rule", annotations=annotate(WRITE_IDEMPOTENT, "Move Firewall Mangle Rule"))
async def mikrotik_move_mangle_rule(
    ctx: Context,
    chain_filter: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"],
    action_filter: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ],
    chain_dst: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"],
    action_dst: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ],
    comment_filter: Optional[str] = None,
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    in_interface_filter: Optional[str] = None,
    out_interface_filter: Optional[str] = None,
    packet_mark_filter: Optional[str] = None,
    connection_mark_filter: Optional[str] = None,
    routing_mark_filter: Optional[str] = None,
    comment_dst: Optional[str] = None,
    src_address_dst: Optional[str] = None,
    dst_address_dst: Optional[str] = None,
    protocol_dst: Optional[str] = None,
    in_interface_dst: Optional[str] = None,
    out_interface_dst: Optional[str] = None,
    packet_mark_dst: Optional[str] = None,
    connection_mark_dst: Optional[str] = None,
    routing_mark_dst: Optional[str] = None,
    device: Optional[str] = None
) -> str:
    """Moves firewall mangle rule(s) matching the specified filters to a different position.

    Args:
        ctx: MCP server context
        
        Source rule selection (all required):
            chain_filter: Source chain (prerouting, input, forward, output, postrouting, lanin, lanout, lanforward)
            action_filter: Source rule action to match
        
        Source rule filters (all optional - combined with AND logic):
            comment_filter: Partial match on comment
            src_address_filter: Partial match on source address
            dst_address_filter: Partial match on destination address
            protocol_filter: Protocol filter
            in_interface_filter: Input interface filter
            out_interface_filter: Output interface filter
            packet_mark_filter: Partial match on packet mark
            connection_mark_filter: Partial match on connection mark
            routing_mark_filter: Partial match on routing mark
        
        Destination position (all required):
            chain_dst: Destination chain
            action_dst: Destination rule action to move before
        
        Destination filters (all optional - combined with AND logic):
            comment_dst: Partial match on destination comment
            src_address_dst: Partial match on destination source address
            dst_address_dst: Partial match on destination address
            protocol_dst: Destination protocol filter
            in_interface_dst: Destination input interface
            out_interface_dst: Destination output interface
            packet_mark_dst: Partial match on destination packet mark
            connection_mark_dst: Partial match on destination connection mark
            routing_mark_dst: Partial match on destination routing mark
        
        device: Target device name (for multi-device management)
    
    Returns:
        Confirmation message of the move operation
    """
    # Build find selector
    find_parts: list[str] = []
    find_parts.append(f'chain={chain_filter}')
    find_parts.append(f'action={action_filter}')
    
    if comment_filter:
        find_parts.append(f'comment=\"{comment_filter}\"')
    if src_address_filter:
        find_parts.append(f'src-address=\"{src_address_filter}\"')
    if dst_address_filter:
        find_parts.append(f'dst-address=\"{dst_address_filter}\"')
    if protocol_filter:
        find_parts.append(f'protocol={protocol_filter}')
    if in_interface_filter:
        find_parts.append(f'in-interface=\"{in_interface_filter}\"')
    if out_interface_filter:
        find_parts.append(f'out-interface=\"{out_interface_filter}\"')
    if packet_mark_filter:
        find_parts.append(f'new-packet-mark=\"{packet_mark_filter}\"')
    if connection_mark_filter:
        find_parts.append(f'new-connection-mark=\"{connection_mark_filter}\"')
    if routing_mark_filter:
        find_parts.append(f'new-routing-mark=\"{routing_mark_filter}\"')

    find_builder = "find " + " and ".join(find_parts)

    # Check if rules exist
    check_cmd = f"/ip firewall mangle print count-only where "+" and ".join(find_parts)
    src_count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if src_count.strip() == "0" or not src_count.strip().isdigit():
        return f"No firewall mangle rules found matching the criteria."

    dst_parts: list[str] = []
    dst_parts.append(f'chain={chain_dst}')
    dst_parts.append(f'action={action_dst}')
    
    if comment_dst:
        dst_parts.append(f'comment=\"{comment_dst}\"')
    if src_address_dst:
        dst_parts.append(f'src-address=\"{src_address_dst}\"')
    if dst_address_dst:
        dst_parts.append(f'dst-address=\"{dst_address_dst}\"')
    if protocol_dst:
        dst_parts.append(f'protocol={protocol_dst}')
    if in_interface_dst:
        dst_parts.append(f'in-interface=\"{in_interface_dst}\"')
    if out_interface_dst:
        dst_parts.append(f'out-interface=\"{out_interface_dst}\"')
    if packet_mark_dst:
        dst_parts.append(f'new-packet-mark=\"{packet_mark_dst}\"')
    if connection_mark_dst:
        dst_parts.append(f'new-connection-mark=\"{connection_mark_dst}\"')
    if routing_mark_dst:
        dst_parts.append(f'new-routing-mark=\"{routing_mark_dst}\"')

    dst_builder = "find " + " and ".join(dst_parts)

    # Check if dst rules exist
    check_cmd = f"/ip firewall mangle print count-only where "+" and ".join(dst_parts)
    dst_count = await execute_mikrotik_command(check_cmd, ctx, device=device)

    if dst_count.strip() == "0" or not dst_count.strip().isdigit():
        return f"No firewall mangle rules found matching the criteria."

    await ctx.info(f"Moving firewall mangle rules: {find_builder} to position {dst_builder}")

    # Move matching rules
    cmd = f"/ip firewall mangle move numbers=[{find_builder}] destination=[{dst_builder}]"
    result = await execute_mikrotik_command(cmd, ctx, device=device)

    return f"Firewall mangle rule(s) moved:\n{result}"

@mcp.tool(name="enable_mangle_rule", annotations=annotate(WRITE_IDEMPOTENT, "Enable Firewall Mangle Rule"))
async def mikrotik_enable_mangle_rule(
    ctx: Context,
    chain_filter: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"],
    action_filter: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ],
    comment_filter: Optional[str] = None,
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    in_interface_filter: Optional[str] = None,
    out_interface_filter: Optional[str] = None,
    packet_mark_filter: Optional[str] = None,
    connection_mark_filter: Optional[str] = None,
    routing_mark_filter: Optional[str] = None,
    device: Optional[str] = None
) -> str:

    # Build find selector
    find_parts: list[str] = []
    find_parts.append(f'chain={chain_filter}')
    find_parts.append(f'action={action_filter}')
    
    if comment_filter:
        find_parts.append(f'comment=\"{comment_filter}\"')
    if src_address_filter:
        find_parts.append(f'src-address=\"{src_address_filter}\"')
    if dst_address_filter:
        find_parts.append(f'dst-address=\"{dst_address_filter}\"')
    if protocol_filter:
        find_parts.append(f'protocol={protocol_filter}')
    if in_interface_filter:
        find_parts.append(f'in-interface=\"{in_interface_filter}\"')
    if out_interface_filter:
        find_parts.append(f'out-interface=\"{out_interface_filter}\"')
    if packet_mark_filter:
        find_parts.append(f'new-packet-mark=\"{packet_mark_filter}\"')
    if connection_mark_filter:
        find_parts.append(f'new-connection-mark=\"{connection_mark_filter}\"')
    if routing_mark_filter:
        find_parts.append(f'new-routing-mark=\"{routing_mark_filter}\"')

    find_builder = "find " + " and ".join(find_parts)
    """Enables a firewall mangle rule matching the specified filters.
    
    Args:
        ctx: MCP server context
        chain_filter: Required - the chain containing the rule (prerouting, input, forward, output, postrouting, lanin, lanout, lanforward)
        action_filter: Required - the rule action to match
        comment_filter: Partial match on rule comment
        src_address_filter: Partial match on source address
        dst_address_filter: Partial match on destination address
        protocol_filter: Filter by protocol
        in_interface_filter: Filter by input interface
        out_interface_filter: Filter by output interface
        packet_mark_filter: Partial match on packet mark
        connection_mark_filter: Partial match on connection mark
        routing_mark_filter: Partial match on routing mark
        device: Target device name (for multi-device management)
    
    Returns:
        Confirmation message from the MikroTik device
    """

    cmd = f"/ip firewall mangle enable numbers=[{find_builder}]"
    return await execute_mikrotik_command(cmd, ctx, device=device)

@mcp.tool(name="disable_mangle_rule", annotations=annotate(WRITE_IDEMPOTENT, "Disable Firewall Mangle Rule"))
async def mikrotik_disable_mangle_rule(
    ctx: Context,
    chain_filter: Literal["prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward"],
    action_filter: Literal[
        "accept", "add-dst-to-address-list", "add-src-to-address-list",
        "change-dscp", "change-mss", "change-ttl", "clear-df",
        "drop", "fasttrack-connection", "jump", "log",
        "mark-connection", "mark-packet", "mark-routing", "passthrough",
        "return", "route", "set-priority", "sniff-pc", "sniff-tzsp",
        "strip-ipv4-options"
    ],
    comment_filter: Optional[str] = None,
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    in_interface_filter: Optional[str] = None,
    out_interface_filter: Optional[str] = None,
    packet_mark_filter: Optional[str] = None,
    connection_mark_filter: Optional[str] = None,
    routing_mark_filter: Optional[str] = None,
    device: Optional[str] = None

) -> str:

    # Build find selector
    find_parts: list[str] = []
    find_parts.append(f'chain={chain_filter}')
    find_parts.append(f'action={action_filter}')
    
    if comment_filter:
        find_parts.append(f'comment=\"{comment_filter}\"')
    if src_address_filter:
        find_parts.append(f'src-address=\"{src_address_filter}\"')
    if dst_address_filter:
        find_parts.append(f'dst-address=\"{dst_address_filter}\"')
    if protocol_filter:
        find_parts.append(f'protocol={protocol_filter}')
    if in_interface_filter:
        find_parts.append(f'in-interface=\"{in_interface_filter}\"')
    if out_interface_filter:
        find_parts.append(f'out-interface=\"{out_interface_filter}\"')
    if packet_mark_filter:
        find_parts.append(f'new-packet-mark=\"{packet_mark_filter}\"')
    if connection_mark_filter:
        find_parts.append(f'new-connection-mark=\"{connection_mark_filter}\"')
    if routing_mark_filter:
        find_parts.append(f'new-routing-mark=\"{routing_mark_filter}\"')

    find_builder = "find " + " and ".join(find_parts)
    """Disables a firewall mangle rule matching the specified filters.
    
    Args:
        ctx: MCP server context
        chain_filter: Required - the chain containing the rule (prerouting, input, forward, output, postrouting, lanin, lanout, lanforward)
        action_filter: Required - the rule action to match
        comment_filter: Partial match on rule comment
        src_address_filter: Partial match on source address
        dst_address_filter: Partial match on destination address
        protocol_filter: Filter by protocol
        in_interface_filter: Filter by input interface
        out_interface_filter: Filter by output interface
        packet_mark_filter: Partial match on packet mark
        connection_mark_filter: Partial match on connection mark
        routing_mark_filter: Partial match on routing mark
        device: Target device name (for multi-device management)
    
    Returns:
        Confirmation message from the MikroTik device
    """

    cmd = f"/ip firewall mangle disable numbers=[{find_builder}]"
    return await execute_mikrotik_command(cmd, ctx, device=device)