"""SAL - Claude Code Launcher CLI."""

import argparse
import sys

from . import __version__
from .config import get_default_profile, set_default_profile
from .launcher import get_claude_version, launch_claude, update_claude
from .mcp import kill_orphan_mcps, list_mcps_formatted, list_profiles_formatted
from .shortcuts import DEFAULT_PROFILES, DEFAULT_SHORTCUTS

HELP_TEXT = """
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
  sal mcp kill              Kill orphan MCP server processes
  sal -p "<text>"           One-shot prompt execution
  sal prompt "<text>"       One-shot prompt execution (alt)
  sal help, -h              Show this help

MCP SHORTCUTS:
  gm                        Gmail
  cal                       Google Calendar
  at                        Airtable
  gsh                       Google Sheets
  doc                       Google Docs
  drv                       Google Drive
  gpe                       Google People
  n8n                       n8n MCP
  jf                        JotForm

MCP PROFILES:
  start                     Daily startup (at, gm, cal)
  google                    All Google services (gm, cal, gsh, doc, drv, gpe)
  dev                       Development tools (n8n, at, jf)
  all                       All available MCPs
"""


def cmd_version() -> int:
    """Show version information."""
    print(f"SAL version: {__version__}")
    claude_version = get_claude_version()
    if claude_version:
        print(f"Claude Code: {claude_version}")
    else:
        print("Claude Code: not found")
    return 0


def cmd_update() -> int:
    """Update Claude Code."""
    return update_claude()


def cmd_profiles() -> int:
    """List available MCP profiles."""
    print(list_profiles_formatted())
    return 0


def cmd_mcp_list() -> int:
    """List all available MCPs."""
    print(list_mcps_formatted())
    return 0


def cmd_mcp_set(profile: str) -> int:
    """Set MCP profile permanently."""
    profiles = DEFAULT_PROFILES.copy()
    if profile not in profiles and profile != "none":
        print(f"Error: Unknown profile '{profile}'")
        print(f"Available profiles: {', '.join(profiles.keys())}, none")
        return 1

    if profile == "none":
        set_default_profile(None)
        print("Default profile cleared. SAL will launch with no MCPs.")
    else:
        set_default_profile(profile)
        print(f"Default profile set to '{profile}'.")
    return 0


def cmd_mcp_kill() -> int:
    """Kill orphan MCP server processes."""
    killed, messages = kill_orphan_mcps()
    for msg in messages:
        print(msg)
    return 0


def cmd_prompt(text: str, safe_mode: bool = False) -> int:
    """Execute one-shot prompt."""
    return launch_claude(prompt=text, safe_mode=safe_mode)


def cmd_help() -> int:
    """Show help."""
    print(HELP_TEXT.strip())
    return 0


def cmd_launch(
    mcp_arg: str | None = None,
    resume: bool = False,
    local_mode: bool = False,
    safe_mode: bool = False,
) -> int:
    """Launch Claude Code."""
    # If no MCPs specified, check for default profile
    if mcp_arg is None:
        default_profile = get_default_profile()
        if default_profile:
            mcp_arg = default_profile

    return launch_claude(
        mcp_arg=mcp_arg,
        resume=resume,
        local_mode=local_mode,
        safe_mode=safe_mode,
    )


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="sal",
        description="SAL - Claude Code Launcher CLI",
        add_help=False,
    )

    # Launch options
    parser.add_argument(
        "-m", "--mcp",
        dest="mcp",
        metavar="MCP",
        help="Launch with specific MCP(s), comma-separated",
    )
    parser.add_argument(
        "-r", "--resume",
        action="store_true",
        help="Resume last session",
    )
    parser.add_argument(
        "-l", "--local",
        action="store_true",
        help="Stay in current directory",
    )
    parser.add_argument(
        "--safe",
        action="store_true",
        help="Launch without --dangerously-skip-permissions",
    )
    parser.add_argument(
        "-p", "--prompt",
        dest="prompt_text",
        metavar="TEXT",
        help="One-shot prompt execution",
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information",
    )
    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show this help",
    )

    # Subcommands as positional arguments
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to run",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Command arguments",
    )

    args = parser.parse_args()

    # Handle help flag
    if args.help:
        return cmd_help()

    # Handle version flag
    if args.version:
        return cmd_version()

    # Handle -p prompt flag
    if args.prompt_text:
        return cmd_prompt(args.prompt_text, safe_mode=args.safe)

    # Handle commands
    if args.command:
        cmd = args.command.lower()

        if cmd == "help":
            return cmd_help()

        if cmd == "version":
            return cmd_version()

        if cmd == "update":
            return cmd_update()

        if cmd == "profiles":
            return cmd_profiles()

        if cmd == "mcp":
            if not args.args:
                return cmd_mcp_list()
            subcmd = args.args[0].lower()
            if subcmd == "list":
                return cmd_mcp_list()
            if subcmd == "set":
                if len(args.args) < 2:
                    print("Error: 'mcp set' requires a profile name")
                    return 1
                return cmd_mcp_set(args.args[1])
            if subcmd == "kill":
                return cmd_mcp_kill()
            print(f"Error: Unknown mcp subcommand '{subcmd}'")
            return 1

        if cmd == "prompt":
            if not args.args:
                print("Error: 'prompt' requires text argument")
                return 1
            text = " ".join(args.args)
            return cmd_prompt(text, safe_mode=args.safe)

        # Unknown command - treat as potential MCP shortcut or profile
        shortcuts = DEFAULT_SHORTCUTS.copy()
        profiles = DEFAULT_PROFILES.copy()

        if cmd in shortcuts or cmd in profiles:
            # User typed a shortcut/profile directly: sal gm
            return cmd_launch(
                mcp_arg=cmd,
                resume=args.resume,
                local_mode=args.local,
                safe_mode=args.safe,
            )

        print(f"Error: Unknown command '{cmd}'")
        print("Run 'sal help' for usage information.")
        return 1

    # Default: launch claude
    return cmd_launch(
        mcp_arg=args.mcp,
        resume=args.resume,
        local_mode=args.local,
        safe_mode=args.safe,
    )


if __name__ == "__main__":
    sys.exit(main())
