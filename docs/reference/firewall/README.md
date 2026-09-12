### Firewall Filter Rules Management

#### `mikrotik_create_filter_rule`
Creates a firewall filter rule on MikroTik device.
- Parameters:
  - `chain` (required): Chain type ("input", "forward", "output")
  - `action` (required): Action type
  - `src_address` (optional): Source address
  - `dst_address` (optional): Destination address
  - `src_port` (optional): Source port
  - `dst_port` (optional): Destination port
  - `protocol` (optional): Protocol
  - `in_interface` (optional): Input interface
  - `out_interface` (optional): Output interface
  - `connection_state` (optional): Connection state
  - `connection_nat_state` (optional): Connection NAT state
  - `src_address_list` (optional): Source address list
  - `dst_address_list` (optional): Destination address list
  - `limit` (optional): Rate limit
  - `tcp_flags` (optional): TCP flags
  - `comment` (optional): Description
  - `disabled` (optional): Disable rule
  - `log` (optional): Enable logging
  - `log_prefix` (optional): Log prefix
  - `place_before` (optional): Rule placement
- Example:
  ```
  mikrotik_create_filter_rule(chain="input", action="accept", protocol="tcp", dst_port="22", src_address="192.168.1.0/24")
  ```

#### `mikrotik_list_filter_rules`
Lists firewall filter rules on MikroTik device.
- Parameters:
  - `chain_filter` (optional): Filter by chain
  - `action_filter` (optional): Filter by action
  - `src_address_filter` (optional): Filter by source address
  - `dst_address_filter` (optional): Filter by destination address
  - `protocol_filter` (optional): Filter by protocol
  - `interface_filter` (optional): Filter by interface
  - `disabled_only` (optional): Show only disabled rules
  - `invalid_only` (optional): Show only invalid rules
  - `dynamic_only` (optional): Show only dynamic rules
- Example:
  ```
  mikrotik_list_filter_rules(chain_filter="input")
  ```

#### `mikrotik_get_filter_rule`
Gets detailed information about a specific firewall filter rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_get_filter_rule(rule_id="*1")
  ```

#### `mikrotik_update_filter_rule`
Updates an existing firewall filter rule.
- Parameters:
  - `rule_id` (required): Rule ID
  - All parameters from `create_filter_rule` (optional)
- Example:
  ```
  mikrotik_update_filter_rule(rule_id="*1", comment="Updated rule")
  ```

#### `mikrotik_remove_filter_rule`
Removes a firewall filter rule from MikroTik device.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_remove_filter_rule(rule_id="*1")
  ```

#### `mikrotik_move_filter_rule`
Moves a firewall filter rule to a different position.
- Parameters:
  - `rule_id` (required): Rule ID
  - `destination` (required): New position
- Example:
  ```
  mikrotik_move_filter_rule(rule_id="*1", destination=0)
  ```

#### `mikrotik_enable_filter_rule`
Enables a firewall filter rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_enable_filter_rule(rule_id="*1")
  ```

#### `mikrotik_disable_filter_rule`
Disables a firewall filter rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_disable_filter_rule(rule_id="*1")
  ```

#### `mikrotik_create_basic_firewall_setup`
Creates a basic firewall setup with common security rules.
- Parameters: None
- Example:
  ```
  mikrotik_create_basic_firewall_setup()
  ```

---

### Firewall Mangle Rules Management

Mangle rules are used for packet modification: marking packets/connections, changing TTL, DSCP, MSS, routing decisions, and traffic classification.

#### `mikrotik_create_mangle_rule`
Creates a firewall mangle rule in the specified chain.
- Parameters:
  - `chain` (required): Chain type ("prerouting", "input", "forward", "output", "postrouting", "lanin", "lanout", "lanforward")
  - `action` (required): Action type (mark-packet, mark-connection, mark-routing, change-dscp, change-mss, change-ttl, sniff-tzsp, fasttrack-connection, jump, log, return, accept, drop, route, strip-ipv4-options, etc.)
  - `src_address` (optional): Source address (CIDR or IP), e.g. "192.168.1.0/24"
  - `dst_address` (optional): Destination address
  - `src_port` (optional): Source port or range, e.g. "80" or "8000-9000"
  - `dst_port` (optional): Destination port or range
  - `protocol` (optional): Protocol (tcp, udp, icmp, etc.)
  - `in_interface` (optional): Input interface name
  - `out_interface` (optional): Output interface name
  - `connection_state` (optional): Connection state (established, related, new, invalid, etc.)
  - `connection_nat_state` (optional): NAT connection state
  - `src_address_list` (optional): Source address list name
  - `dst_address_list` (optional): Destination address list name
  - `new_packet_mark` (optional): Mark name for packets, e.g. "priority-high"
  - `new_connection_mark` (optional): Mark name for connections
  - `new_routing_mark` (optional): Mark name for routing table selection
  - `connection_mark` (optional): Match on existing connection mark
  - `routing_mark` (optional): Match on existing routing mark
  - `packet_mark` (optional): Match on existing packet mark
  - `per_connection_classifier` (optional): Per-connection traffic classifier (e.g. "src-address,dst-port:16" for src/dst classification)
  - `limit` (optional): Rate limit (e.g. "10,5:packet" or "10/1s:packet")
  - `tcp_flags` (optional): TCP flags matching (e.g. "syn,!ack")
  - `comment` (optional): Rule description
  - `disabled` (optional): Create rule in disabled state
  - `log` (optional): Enable logging for this rule
  - `log_prefix` (optional): Log message prefix
  - `place_before` (optional): Insert before rule ID (from unfiltered list)
- Example:
  ```
  mikrotik_create_mangle_rule(
    chain="prerouting",
    action="mark-packet",
    src_address="192.168.1.0/24",
    protocol="tcp",
    dst_port="80",
    new_packet_mark="http-traffic"
  )
  ```

#### `mikrotik_list_mangle_rules`
Lists firewall mangle rules with optional filters.
- Parameters:
  - `chain_filter` (optional): Filter by chain
  - `action_filter` (optional): Filter by action
  - `comment_filter` (optional): Partial match on comment
  - `src_address_filter` (optional): Partial match on source address
  - `dst_address_filter` (optional): Partial match on destination address
  - `protocol_filter` (optional): Filter by protocol
  - `in_interface_filter` (optional): Partial match on input interface
  - `out_interface_filter` (optional): Partial match on output interface
  - `packet_mark_filter` (optional): Partial match on new-packet-mark
  - `connection_mark_filter` (optional): Partial match on new-connection-mark
  - `routing_mark_filter` (optional): Partial match on new-routing-mark
  - `disabled_only` (optional): Show only disabled rules
  - `invalid_only` (optional): Show only invalid rules
- Example:
  ```
  mikrotik_list_mangle_rules(chain_filter="prerouting", action_filter="mark-packet")
  ```

#### `mikrotik_get_mangle_rule`
Gets detailed information about a specific mangle rule.
- Parameters:
  - `rule_id` (required): Rule ID from list output (e.g. "*1" or "0")
- Example:
  ```
  mikrotik_get_mangle_rule(rule_id="*1")
  ```

#### `mikrotik_update_mangle_rule`
Updates an existing mangle rule. Use selector filters to identify rules by their properties.
- Parameters (selectors - identify which rule to update):
  - `chain_filter` (required): The chain containing the rule
  - `action_filter` (required): The rule action
  - `comment_filter` (optional): Match by comment
  - `src_address_filter` (optional): Match by source address
  - `dst_address_filter` (optional): Match by destination address
  - `protocol_filter` (optional): Match by protocol
  - `in_interface_filter` (optional): Match by input interface
  - `out_interface_filter` (optional): Match by output interface
  - `packet_mark_filter` (optional): Match by packet mark
  - `connection_mark_filter` (optional): Match by connection mark
  - `routing_mark_filter` (optional): Match by routing mark
- Parameters (updates - fields to modify):
  - `chain` (optional): New chain
  - `action` (optional): New action
  - `src_address` (optional): New source address
  - `dst_address` (optional): New destination address
  - `src_port` (optional): New source port
  - `dst_port` (optional): New destination port
  - `protocol` (optional): New protocol
  - `in_interface` (optional): New input interface
  - `out_interface` (optional): New output interface
  - `connection_state` (optional): New connection state
  - `new_packet_mark` (optional): New packet mark
  - `new_connection_mark` (optional): New connection mark
  - `new_routing_mark` (optional): New routing mark
  - `per_connection_classifier` (optional): New per-connection classifier
  - `comment` (optional): Update description
  - `disabled` (optional): Enable/disable the rule
  - `log` (optional): Enable/disable logging
- Notes:
  - Pass empty string "" to clear optional fields
  - Multiple rules matching selectors will all be updated
- Example:
  ```
  mikrotik_update_mangle_rule(
    chain_filter="prerouting",
    action_filter="mark-packet",
    comment_filter="old-comment",
    comment="updated-comment",
    new_packet_mark="priority-medium"
  )
  ```

#### `mikrotik_remove_mangle_rule`
Removes a mangle rule from the MikroTik device.
- Parameters:
  - `rule_id` (required): Rule ID from list output
- Example:
  ```
  mikrotik_remove_mangle_rule(rule_id="*1")
  ```

#### `mikrotik_move_mangle_rule`
Moves a mangle rule to a different position in the chain.
- Parameters:
  - `rule_id` (required): Rule ID to move
  - `destination` (required): 0-based target position
- Example:
  ```
  mikrotik_move_mangle_rule(rule_id="*1", destination=0)
  ```

#### `mikrotik_enable_mangle_rule`
Enables a disabled mangle rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_enable_mangle_rule(rule_id="*1")
  ```

#### `mikrotik_disable_mangle_rule`
Disables an enabled mangle rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_disable_mangle_rule(rule_id="*1")
  ```

---

### Common Mangle Workflows

**Mark traffic by source subnet:**
```python
mikrotik_create_mangle_rule(
  chain="prerouting",
  action="mark-packet",
  src_address="192.168.1.0/24",
  new_packet_mark="internal-traffic"
)
```

**Limit bandwidth for specific ports:**
```python
mikrotik_create_mangle_rule(
  chain="forward",
  action="mark-connection",
  protocol="tcp",
  dst_port="80",
  new_connection_mark="web-connections",
  limit="100/1s"
)
```

**Per-connection classification:**
```python
mikrotik_create_mangle_rule(
  chain="prerouting",
  action="mark-connection",
  src_address="192.168.1.0/24",
  per_connection_classifier="src-address,dst-port:16",
  new_connection_mark="classified"
)
```

**Change DSCP for video traffic:**
```python
mikrotik_create_mangle_rule(
  chain="output",
  action="change-dscp",
  protocol="tcp",
  dst_port="1935",
  new_dscp="48",
  comment="Video streaming DSCP"
)
```

