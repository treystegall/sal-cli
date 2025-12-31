# SAL - Claude Code Launcher CLI

A lightweight CLI launcher for Claude Code with MCP server management, session control, and convenience features.

## Installation

### Using pipx (Recommended)

```bash
# Install pipx if you don't have it
brew install pipx
pipx ensurepath

# Install SAL
cd ~/sal/sal-cli
pipx install -e .
```

### Using pip with virtual environment

```bash
cd ~/sal/sal-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Verify Installation

```bash
sal version
```

## Usage

```
USAGE:
  sal                       Launch Claude (no MCPs, max performance)
  sal -m <mcp>              Launch with specific MCP(s)
  sal -m gm,at              Launch with multiple MCPs
  sal -r, --resume          Resume last session
  sal -l, --local           Stay in current directory (don't cd to ~/sal/desktop)
  sal --safe                Launch without --dangerously-skip-permissions

COMMANDS:
  sal update                Update Claude Code to latest version
  sal version, -v           Show version information
  sal profiles              List available MCP profiles
  sal mcp list              List all available MCPs
  sal mcp set <profile>     Set MCP profile permanently
  sal prompt "<text>"       One-shot prompt execution
  sal help, -h              Show this help
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
| `n8n` | n8n MCP |
| `jf` | JotForm |

## MCP Profiles

| Profile | MCPs |
|---------|------|
| `google` | gm, cal, gsh, doc, drv, gpe |
| `dev` | n8n, at, jf |
| `all` | All available MCPs |

## Examples

```bash
# Launch Claude with no MCPs (fastest startup)
sal

# Launch with Gmail MCP
sal -m gm

# Launch with multiple MCPs
sal -m gm,at,n8n

# Launch using a profile
sal -m google
# Or use the profile name directly
sal google

# Resume last session
sal -r

# Resume with specific MCPs
sal -r -m gm

# Stay in current directory instead of ~/sal/desktop
sal -l

# Launch without --dangerously-skip-permissions
sal --safe

# One-shot prompt execution
sal prompt "What files are in this directory?"

# Set a default profile
sal mcp set google

# Clear default profile
sal mcp set none
```

## Configuration

SAL stores configuration in `~/.sal/`:

- `config.json` - Main settings (default profile, paths)
- `shortcuts.json` - Custom shortcut overrides
- `profiles.json` - Custom profile definitions

### Default Behavior

- **No MCPs by default**: Launches Claude with no MCP servers for maximum performance
- **Working directory**: Changes to `~/sal/desktop` before launching (use `-l` to stay local)
- **Permissions**: Uses `--dangerously-skip-permissions` by default (use `--safe` to disable)

### Custom Shortcuts

Add custom shortcuts by creating `~/.sal/shortcuts.json`:

```json
{
  "myshortcut": "my-mcp-server-name"
}
```

### Custom Profiles

Add custom profiles by creating `~/.sal/profiles.json`:

```json
{
  "myprofile": ["gm", "at", "myshortcut"]
}
```

## Requirements

- Python 3.10+
- Claude Code CLI installed (`claude` command available)
- MCP servers configured in `~/.sal/mcp.json`

## Uninstall

```bash
pipx uninstall sal
```
