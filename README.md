# SAL - Simple Anthropic Launcher

A CLI tool for launching Claude Code with selective MCP server management. SAL lets you control which MCP servers are enabled at startup while keeping all servers available for on-demand use.

## Features

- **Selective MCP Enabling**: Only start the MCP servers you need, reducing startup time
- **All Servers Available**: Non-enabled servers remain available via `/mcp` in Claude Code
- **Shortcuts**: Quick codes like `gm` for Gmail, `cal` for Calendar
- **Profiles**: Launch groups of servers with one command (`sal google`)
- **Session Resume**: Continue where you left off with `-r`

## Installation

### From GitHub (Recommended)

```bash
# Install with pipx
pipx install git+https://github.com/treystegall/sal-cli.git

# Or clone and install
git clone https://github.com/treystegall/sal-cli.git
cd sal-cli
pipx install .
```

### From Local Directory

```bash
cd ~/sal/sal-cli
pipx install -e .
```

### Verify Installation

```bash
sal version
```

## Quick Start

```bash
# Launch Claude with Gmail MCP enabled
sal -m gm

# Launch with multiple MCPs
sal -m gm,cal,at

# Launch with a profile (all Google services)
sal google

# Resume last session
sal -r

# Launch with no MCPs (fastest startup)
sal
```

## Usage

```
USAGE:
  sal                       Launch Claude (no MCPs enabled)
  sal -m <mcp>              Launch with specific MCP(s) enabled
  sal -m gm,at              Launch with multiple MCPs
  sal <profile>             Launch with a profile (e.g., sal google)
  sal -r, --resume          Resume last session
  sal -l, --local           Stay in current directory
  sal --safe                Launch without --dangerously-skip-permissions

COMMANDS:
  sal update                Update Claude Code to latest version
  sal version, -v           Show version information
  sal profiles              List available MCP profiles
  sal mcp list              List all available MCPs
  sal mcp set <profile>     Set default MCP profile
  sal mcp kill              Kill orphaned MCP server processes
  sal prompt "<text>"       One-shot prompt execution
  sal help, -h              Show help
```

## MCP Shortcuts

| Shortcut | Server |
|----------|--------|
| `gm` | Gmail |
| `cal` | Google Calendar |
| `at` | Airtable |
| `gsh` | Google Sheets |
| `doc` | Google Docs |
| `drv` | Google Drive |
| `gpe` | Google People |
| `n8n` | n8n |
| `jf` | JotForm |

## MCP Profiles

| Profile | Servers |
|---------|---------|
| `start` | Gmail, Calendar, Airtable |
| `google` | Gmail, Calendar, Sheets, Docs, Drive, People |
| `dev` | n8n, Airtable, JotForm |
| `all` | All available MCPs |

## How It Works

SAL controls MCP server enabling by modifying `~/.claude.json` before launching Claude Code:

1. **All servers are configured** in `mcpServers` (making them available)
2. **Non-enabled servers** are added to `disabledMcpServers` (won't auto-start)
3. **Enabled servers** are removed from `disabledMcpServers` (will auto-start)

This means:
- Enabled servers start automatically when Claude launches
- Disabled servers are still available - use `/mcp` in Claude to enable them on-demand

## Configuration

SAL stores its configuration in `~/.sal/`:

| File | Purpose |
|------|---------|
| `config.json` | Main settings (default profile, working directory) |
| `mcp.json` | MCP server definitions |
| `shortcuts.json` | Custom shortcut overrides |
| `profiles.json` | Custom profile definitions |

### Adding MCP Servers

Edit `~/.sal/mcp.json` to add your MCP servers:

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/my_server.py"],
      "env": {}
    }
  }
}
```

### Custom Shortcuts

Create `~/.sal/shortcuts.json`:

```json
{
  "ms": "my-server"
}
```

Now use `sal -m ms` to launch with your server.

### Custom Profiles

Create `~/.sal/profiles.json`:

```json
{
  "work": ["gm", "cal", "at", "ms"]
}
```

Now use `sal work` to launch with your profile.

### Setting a Default Profile

```bash
# Set default profile
sal mcp set google

# Now just running 'sal' will use the google profile
sal

# Clear default profile
sal mcp set none
```

## Default Behavior

| Setting | Default | Override |
|---------|---------|----------|
| Working directory | `~/sal/desktop` | `-l` to stay local |
| Permissions | Skip permissions prompt | `--safe` to require approval |
| MCPs enabled | None | `-m` to specify |

## Examples

```bash
# Quick Gmail access
sal gm

# Full Google workspace
sal google

# Development setup
sal -m at,n8n,jf

# Resume with specific MCPs
sal -r -m gm,cal

# One-shot prompt
sal prompt "Summarize my recent emails"

# Stay in current project directory
sal -l -m at
```

## Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/code) installed (`claude` command available)
- [pipx](https://pypa.github.io/pipx/) for installation

## Troubleshooting

### MCP servers not starting

1. Check server definitions in `~/.sal/mcp.json`
2. Verify the server command/script exists and is executable
3. Run `sal mcp list` to see available servers

### Orphaned MCP processes

```bash
sal mcp kill
```

### Reset to defaults

```bash
rm -rf ~/.sal
```

## Uninstall

```bash
pipx uninstall sal
```

## License

MIT
