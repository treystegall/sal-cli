"""MCP server configuration handling."""

import json
import os
import signal
import subprocess
import tempfile
from pathlib import Path

from .config import load_mcp_config, load_profiles, load_shortcuts


def get_available_servers() -> list[str]:
    """Get list of available MCP server names from config."""
    config = load_mcp_config()
    return list(config.get("mcpServers", {}).keys())


def resolve_shortcut(shortcut: str) -> str:
    """Resolve a shortcut to its full server name."""
    shortcuts = load_shortcuts()
    return shortcuts.get(shortcut, shortcut)


def resolve_profile(profile_name: str) -> list[str]:
    """Resolve a profile name to list of server names."""
    profiles = load_profiles()
    shortcuts = profiles.get(profile_name, [])
    return [resolve_shortcut(s) for s in shortcuts]


def parse_mcp_arg(mcp_arg: str) -> list[str]:
    """
    Parse the -m argument into a list of server names.

    Handles:
    - Single shortcut: "gm" -> ["gmail"]
    - Multiple shortcuts: "gm,at" -> ["gmail", "airtable"]
    - Profile names: "google" -> ["gmail", "google-calendar", ...]
    - Full server names: "gmail" -> ["gmail"]
    """
    profiles = load_profiles()
    servers = []

    for item in mcp_arg.split(","):
        item = item.strip()
        if not item:
            continue

        # Check if it's a profile name
        if item in profiles:
            servers.extend(resolve_profile(item))
        else:
            # Resolve as shortcut or use as-is
            servers.append(resolve_shortcut(item))

    # Remove duplicates while preserving order
    seen = set()
    unique_servers = []
    for s in servers:
        if s not in seen:
            seen.add(s)
            unique_servers.append(s)

    return unique_servers


def validate_servers(server_names: list[str]) -> tuple[list[str], list[str]]:
    """
    Validate that requested servers exist in the MCP config.

    Returns:
        Tuple of (valid_servers, invalid_servers)
    """
    available = set(get_available_servers())
    valid = []
    invalid = []

    for server in server_names:
        if server in available:
            valid.append(server)
        else:
            invalid.append(server)

    return valid, invalid


def generate_mcp_config(enabled_servers: list[str] | None = None) -> Path:
    """
    Generate a temporary MCP config file with all servers available.

    Servers in enabled_servers list will be started automatically.
    All other servers will be available but disabled (not auto-started).

    Args:
        enabled_servers: List of server names to enable. If None or empty,
                        all servers are available but disabled.

    Returns:
        Path to the temporary config file
    """
    master_config = load_mcp_config()
    all_servers = master_config.get("mcpServers", {})

    if enabled_servers is None:
        enabled_servers = []

    enabled_set = set(enabled_servers)

    # Build config with all servers, marking non-enabled as disabled
    configured_servers = {}
    for name, config in all_servers.items():
        server_config = config.copy()
        if name not in enabled_set:
            # Mark as disabled - available but not auto-started
            server_config["disabled"] = True
        else:
            # Ensure enabled servers don't have disabled flag
            server_config.pop("disabled", None)
        configured_servers[name] = server_config

    full_config = {"mcpServers": configured_servers}

    # Write to temporary file
    temp_dir = Path(tempfile.gettempdir()) / "sal"
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / "mcp_config.json"

    with open(temp_file, "w") as f:
        json.dump(full_config, f, indent=2)

    return temp_file


def list_mcps_formatted() -> str:
    """Generate formatted list of available MCPs."""
    shortcuts = load_shortcuts()
    available = set(get_available_servers())

    # Build reverse mapping: server name -> shortcut
    reverse_shortcuts = {v: k for k, v in shortcuts.items()}

    lines = ["Available MCP Servers:", ""]

    for server in sorted(available):
        shortcut = reverse_shortcuts.get(server, "")
        if shortcut:
            lines.append(f"  {shortcut:<8} {server}")
        else:
            lines.append(f"  {'':8} {server}")

    return "\n".join(lines)


def list_profiles_formatted() -> str:
    """Generate formatted list of MCP profiles."""
    profiles = load_profiles()

    lines = ["MCP Profiles:", ""]

    for profile, shortcuts in sorted(profiles.items()):
        servers = ", ".join(shortcuts)
        lines.append(f"  {profile}")
        lines.append(f"    {servers}")
        lines.append("")

    return "\n".join(lines)


def get_mcp_server_paths() -> list[str]:
    """Get all MCP server script paths from config."""
    config = load_mcp_config()
    servers = config.get("mcpServers", {})
    paths = []
    for server_config in servers.values():
        args = server_config.get("args", [])
        if args:
            paths.append(args[0])
    return paths


def find_orphan_mcp_processes() -> list[tuple[int, str]]:
    """
    Find running MCP server processes.

    Returns:
        List of (pid, command) tuples for running MCP processes.
    """
    orphans = []
    server_paths = get_mcp_server_paths()

    for path in server_paths:
        try:
            result = subprocess.run(
                ["pgrep", "-f", path],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                for pid_str in result.stdout.strip().split("\n"):
                    if pid_str:
                        pid = int(pid_str)
                        # Get the command for display
                        ps_result = subprocess.run(
                            ["ps", "-p", str(pid), "-o", "command="],
                            capture_output=True,
                            text=True,
                        )
                        cmd = ps_result.stdout.strip() if ps_result.returncode == 0 else path
                        orphans.append((pid, cmd))
        except (subprocess.SubprocessError, ValueError):
            continue

    # Remove duplicates (same PID might match multiple patterns)
    seen_pids = set()
    unique_orphans = []
    for pid, cmd in orphans:
        if pid not in seen_pids:
            seen_pids.add(pid)
            unique_orphans.append((pid, cmd))

    return unique_orphans


def kill_orphan_mcps() -> tuple[int, list[str]]:
    """
    Kill all orphan MCP server processes.

    Returns:
        Tuple of (killed_count, list of status messages).
    """
    orphans = find_orphan_mcp_processes()

    if not orphans:
        return 0, ["No orphan MCP processes found."]

    messages = []
    killed = 0

    for pid, cmd in orphans:
        try:
            os.kill(pid, signal.SIGTERM)
            # Extract just the script name for cleaner output
            script_name = Path(cmd.split()[-1]).name if cmd else f"PID {pid}"
            messages.append(f"  Killed: {script_name} (PID {pid})")
            killed += 1
        except OSError as e:
            messages.append(f"  Failed to kill PID {pid}: {e}")

    messages.insert(0, f"Killed {killed} orphan MCP process(es):")
    return killed, messages
