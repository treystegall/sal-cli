"""MCP shortcut definitions and profile mappings."""

# Default shortcut mappings: short code -> full MCP server name
DEFAULT_SHORTCUTS: dict[str, str] = {
    "gm": "gmail",
    "cal": "google-calendar",
    "at": "airtable",
    "gsh": "google-sheets",
    "doc": "google-docs",
    "drv": "google-drive",
    "gpe": "google-people",
    "n8n": "n8n",
    "jf": "jotform",
}

# Default profile definitions: profile name -> list of shortcuts
DEFAULT_PROFILES: dict[str, list[str]] = {
    "start": ["at", "gm", "cal"],
    "google": ["gm", "cal", "gsh", "doc", "drv", "gpe"],
    "dev": ["n8n", "at", "jf"],
    "all": ["gm", "cal", "at", "gsh", "doc", "drv", "gpe", "n8n", "jf"],
}


def get_shortcut_help() -> str:
    """Generate help text for MCP shortcuts."""
    lines = ["MCP SHORTCUTS:"]
    for shortcut, server in DEFAULT_SHORTCUTS.items():
        lines.append(f"  {shortcut:<20} {server}")
    return "\n".join(lines)


def get_profile_help() -> str:
    """Generate help text for MCP profiles."""
    lines = ["MCP PROFILES:"]
    for profile, shortcuts in DEFAULT_PROFILES.items():
        mcps = ", ".join(shortcuts)
        lines.append(f"  {profile:<20} {mcps}")
    return "\n".join(lines)
