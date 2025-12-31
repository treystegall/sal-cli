"""Configuration management for SAL."""

import json
from pathlib import Path

from .shortcuts import DEFAULT_PROFILES, DEFAULT_SHORTCUTS

# Configuration directory
SAL_CONFIG_DIR = Path.home() / ".sal"
CONFIG_FILE = SAL_CONFIG_DIR / "config.json"
SHORTCUTS_FILE = SAL_CONFIG_DIR / "shortcuts.json"
PROFILES_FILE = SAL_CONFIG_DIR / "profiles.json"
MCP_CONFIG_FILE = SAL_CONFIG_DIR / "mcp.json"

# Claude Code configuration file
CLAUDE_CONFIG_FILE = Path.home() / ".claude.json"

# Default configuration values
DEFAULT_CONFIG = {
    "default_profile": None,
    "claude_dir": "~/sal/desktop",
    "skip_permissions": True,
}

# Default MCP server definitions
DEFAULT_MCP_SERVERS = {
    "mcpServers": {
        "gmail": {
            "type": "stdio",
            "command": "/Users/treystegall/tsdev/mcp_servers/.venv/bin/python",
            "args": [
                "/Users/treystegall/tsdev/mcp_servers/gmail-mcp-server/gmail_mcp_server.py"
            ],
            "env": {},
        },
        "google-calendar": {
            "type": "stdio",
            "command": "/Users/treystegall/tsdev/mcp_servers/.venv/bin/python",
            "args": [
                "/Users/treystegall/tsdev/mcp_servers/gcal-mcp-server/calendar_mcp_server.py"
            ],
            "env": {},
        },
        "airtable": {
            "type": "stdio",
            "command": "/Users/treystegall/tsdev/mcp_servers/.venv/bin/python",
            "args": [
                "/Users/treystegall/tsdev/mcp_servers/airtable-mcp-server/airtable_mcp_server.py"
            ],
            "env": {},
        },
        "google-sheets": {
            "type": "stdio",
            "command": "/Users/treystegall/tsdev/mcp_servers/.venv/bin/python",
            "args": [
                "/Users/treystegall/tsdev/mcp_servers/googlesheets-mcp-server/sheets_mcp_server.py"
            ],
            "env": {},
        },
        "google-docs": {
            "type": "stdio",
            "command": "/Users/treystegall/tsdev/mcp_servers/.venv/bin/python",
            "args": [
                "/Users/treystegall/tsdev/mcp_servers/googledocs-mcp-server/docs_mcp_server.py"
            ],
            "env": {},
        },
        "google-drive": {
            "type": "stdio",
            "command": "/Users/treystegall/tsdev/mcp_servers/.venv/bin/python",
            "args": [
                "/Users/treystegall/tsdev/mcp_servers/googledrive-mcp-server/server.py"
            ],
            "env": {},
        },
        "google-people": {
            "type": "stdio",
            "command": "/Users/treystegall/tsdev/mcp_servers/.venv/bin/python",
            "args": [
                "/Users/treystegall/tsdev/mcp_servers/people-mcp-server/people_mcp_server.py"
            ],
            "env": {},
        },
        "n8n": {
            "type": "stdio",
            "command": "npx",
            "args": ["n8n-mcp"],
            "env": {
                "MCP_MODE": "stdio",
                "LOG_LEVEL": "error",
                "DISABLE_CONSOLE_OUTPUT": "true",
                "N8N_API_URL": "https://stegall-n8n.ngrok.io/api/v1",
                "N8N_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MmU3ODIxZS1mZjhhLTQ3ZTAtODY3Yi1hOGNhYTMxNGI5YTkiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY0NTU1Mjc3LCJleHAiOjE3NjcwNzA4MDB9.wrGPfZCju7wxakOF6nfmcuck973VRrNk1lVCD3bh5kw",
            },
        },
        "jotform": {
            "type": "stdio",
            "command": "/Users/treystegall/tsdev/mcp_servers/.venv/bin/python",
            "args": [
                "/Users/treystegall/tsdev/mcp_servers/jotform-mcp-server/jotform_mcp_server.py"
            ],
            "env": {},
        },
    }
}


def ensure_config_dir() -> None:
    """Create the SAL config directory if it doesn't exist."""
    SAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_json_file(filepath: Path, default: dict | list) -> dict | list:
    """Load a JSON file, returning default if file doesn't exist."""
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return default


def save_json_file(filepath: Path, data: dict | list) -> None:
    """Save data to a JSON file."""
    ensure_config_dir()
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_config() -> dict:
    """Load the main SAL configuration."""
    config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG.copy())
    # Merge with defaults to ensure all keys exist
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
    return config


def save_config(config: dict) -> None:
    """Save the main SAL configuration."""
    save_json_file(CONFIG_FILE, config)


def load_shortcuts() -> dict[str, str]:
    """Load MCP shortcuts, merging user overrides with defaults."""
    user_shortcuts = load_json_file(SHORTCUTS_FILE, {})
    shortcuts = DEFAULT_SHORTCUTS.copy()
    shortcuts.update(user_shortcuts)
    return shortcuts


def save_shortcuts(shortcuts: dict[str, str]) -> None:
    """Save user MCP shortcuts."""
    save_json_file(SHORTCUTS_FILE, shortcuts)


def load_profiles() -> dict[str, list[str]]:
    """Load MCP profiles, merging user overrides with defaults."""
    user_profiles = load_json_file(PROFILES_FILE, {})
    profiles = DEFAULT_PROFILES.copy()
    profiles.update(user_profiles)
    return profiles


def save_profiles(profiles: dict[str, list[str]]) -> None:
    """Save user MCP profiles."""
    save_json_file(PROFILES_FILE, profiles)


def init_mcp_config() -> None:
    """Initialize the MCP config file with defaults if it doesn't exist."""
    if not MCP_CONFIG_FILE.exists():
        save_json_file(MCP_CONFIG_FILE, DEFAULT_MCP_SERVERS)


def load_mcp_config() -> dict:
    """Load the MCP configuration, initializing with defaults if needed."""
    init_mcp_config()
    return load_json_file(MCP_CONFIG_FILE, DEFAULT_MCP_SERVERS)


def save_mcp_config(config: dict) -> None:
    """Save the MCP configuration."""
    save_json_file(MCP_CONFIG_FILE, config)


def get_mcp_config_path() -> Path:
    """Get the path to the MCP configuration file."""
    init_mcp_config()
    return MCP_CONFIG_FILE


def get_claude_dir() -> Path:
    """Get the Claude working directory."""
    config = load_config()
    return Path(config["claude_dir"]).expanduser()


def get_default_profile() -> str | None:
    """Get the default MCP profile, if set."""
    config = load_config()
    return config.get("default_profile")


def set_default_profile(profile: str | None) -> None:
    """Set the default MCP profile."""
    config = load_config()
    config["default_profile"] = profile
    save_config(config)


def should_skip_permissions() -> bool:
    """Check if we should use --dangerously-skip-permissions by default."""
    config = load_config()
    return config.get("skip_permissions", True)


def get_report_email() -> str | None:
    """Get configured email for morning reports."""
    config = load_config()
    return config.get("report_email")


def set_report_email(email: str) -> None:
    """Set email address for morning reports."""
    config = load_config()
    config["report_email"] = email
    save_config(config)


def load_claude_config() -> dict:
    """Load the Claude Code configuration from ~/.claude.json."""
    if CLAUDE_CONFIG_FILE.exists():
        try:
            with open(CLAUDE_CONFIG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_claude_config(config: dict) -> None:
    """Save the Claude Code configuration to ~/.claude.json."""
    with open(CLAUDE_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def set_project_mcp_servers(project_path: Path, enabled_servers: list[str]) -> None:
    """
    Set the enabled MCP servers for a project in ~/.claude.json.

    This modifies the project entry in ~/.claude.json to:
    1. Make ALL servers AVAILABLE by putting them in mcpServers
    2. Control which servers AUTO-START via disabledMcpServers list

    Servers in enabled_servers will auto-start (not in disabledMcpServers).
    All other servers will be available but disabled (in disabledMcpServers).

    Args:
        project_path: The project directory path
        enabled_servers: List of server names to enable (auto-start).
    """
    # Load the master MCP config to get ALL server definitions
    mcp_config = load_mcp_config()
    all_servers = mcp_config.get("mcpServers", {})

    # ALL servers go into mcpServers (makes them all AVAILABLE)
    all_server_configs = {}
    for server_name, server_config in all_servers.items():
        all_server_configs[server_name] = server_config.copy()

    # Load and update Claude config
    claude_config = load_claude_config()

    # Ensure projects dict exists
    if "projects" not in claude_config:
        claude_config["projects"] = {}

    # Get absolute path as string (how Claude stores project keys)
    project_key = str(project_path.expanduser().resolve())

    # Initialize project entry if it doesn't exist
    if project_key not in claude_config["projects"]:
        claude_config["projects"][project_key] = {
            "allowedTools": [],
            "mcpContextUris": [],
            "mcpServers": {},
            "enabledMcpjsonServers": [],
            "disabledMcpjsonServers": [],
            "hasTrustDialogAccepted": True,
            "ignorePatterns": [],
        }

    project = claude_config["projects"][project_key]

    # Put ALL servers in mcpServers (all are AVAILABLE)
    project["mcpServers"] = all_server_configs

    # Build disabledMcpServers list:
    # - Servers NOT in enabled_servers go here (available but won't auto-start)
    # - Servers IN enabled_servers are removed (will auto-start)
    enabled_set = set(enabled_servers)

    # Start with existing disabled servers (preserve plugin servers etc.)
    disabled_servers = set(project.get("disabledMcpServers", []))

    # Remove all our known servers first, then add back the disabled ones
    for server_name in all_servers:
        disabled_servers.discard(server_name)

    # Add back only the servers that should be DISABLED (not in enabled list)
    for server_name in all_servers:
        if server_name not in enabled_set:
            disabled_servers.add(server_name)

    project["disabledMcpServers"] = list(disabled_servers)

    # Save the updated config
    save_claude_config(claude_config)


def get_project_mcp_servers(project_path: Path) -> dict:
    """
    Get the current MCP servers configured for a project.

    Args:
        project_path: The project directory path

    Returns:
        Dict of server name -> server config
    """
    claude_config = load_claude_config()
    project_key = str(project_path.expanduser().resolve())
    projects = claude_config.get("projects", {})
    project = projects.get(project_key, {})
    return project.get("mcpServers", {})
