"""Claude Code launcher logic."""

import os
import subprocess
import sys
from pathlib import Path

from .config import get_claude_dir, set_project_mcp_servers, should_skip_permissions
from .mcp import parse_mcp_arg, validate_servers


def build_claude_command(
    mcp_arg: str | None = None,
    resume: bool = False,
    safe_mode: bool = False,
    prompt: str | None = None,
) -> tuple[list[str], list[str], str | None]:
    """
    Build the claude command with appropriate flags.

    Args:
        mcp_arg: Comma-separated MCPs or profile name (None for no MCPs)
        resume: Whether to resume last session
        safe_mode: If True, don't use --dangerously-skip-permissions
        prompt: One-shot prompt text

    Returns:
        Tuple of (command_list, enabled_servers, error_message)
    """
    cmd = ["claude"]
    enabled_servers: list[str] = []

    # Handle resume flag
    if resume:
        cmd.append("--resume")

    # Handle MCP configuration
    # Parse and validate requested servers - these will be set in ~/.claude.json
    if mcp_arg:
        servers = parse_mcp_arg(mcp_arg)
        valid, invalid = validate_servers(servers)

        if invalid:
            return [], [], f"Unknown MCP servers: {', '.join(invalid)}"

        enabled_servers = valid

    # Handle permissions flag
    if not safe_mode and should_skip_permissions():
        cmd.append("--dangerously-skip-permissions")

    # Handle one-shot prompt
    if prompt:
        cmd.extend(["--print", "-p", prompt])

    return cmd, enabled_servers, None


def launch_claude(
    mcp_arg: str | None = None,
    resume: bool = False,
    local_mode: bool = False,
    safe_mode: bool = False,
    prompt: str | None = None,
) -> int:
    """
    Launch Claude Code with the specified options.

    Args:
        mcp_arg: Comma-separated MCPs or profile name
        resume: Whether to resume last session
        local_mode: If True, stay in current directory
        safe_mode: If True, don't use --dangerously-skip-permissions
        prompt: One-shot prompt text

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Determine the working directory
    if local_mode:
        claude_dir = Path.cwd()
    else:
        claude_dir = get_claude_dir()
        claude_dir.mkdir(parents=True, exist_ok=True)

    # Build command and get enabled servers
    cmd, enabled_servers, error = build_claude_command(
        mcp_arg=mcp_arg,
        resume=resume,
        safe_mode=safe_mode,
        prompt=prompt,
    )

    if error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    # Update ~/.claude.json with the enabled MCP servers for this project
    # This is how Claude Code determines which servers to start
    set_project_mcp_servers(claude_dir, enabled_servers)

    # Change to the target directory
    if not local_mode:
        os.chdir(claude_dir)

    # For one-shot prompts, use subprocess to capture output
    if prompt:
        try:
            result = subprocess.run(cmd, check=False)
            return result.returncode
        except FileNotFoundError:
            print("Error: 'claude' command not found. Is Claude Code installed?", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            return 130

    # For interactive mode, replace current process
    try:
        os.execvp("claude", cmd)
    except FileNotFoundError:
        print("Error: 'claude' command not found. Is Claude Code installed?", file=sys.stderr)
        return 1

    return 0  # This line is never reached if execvp succeeds


def update_claude() -> int:
    """Update Claude Code to the latest version."""
    print("Updating Claude Code...")
    try:
        result = subprocess.run(
            ["npm", "update", "-g", "@anthropic-ai/claude-code"],
            check=False,
        )
        if result.returncode == 0:
            print("Claude Code updated successfully.")
        return result.returncode
    except FileNotFoundError:
        print("Error: 'npm' not found. Is Node.js installed?", file=sys.stderr)
        return 1


def get_claude_version() -> str | None:
    """Get the installed Claude Code version."""
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except FileNotFoundError:
        return None


def launch_claude_oneshot(
    prompt: str,
    mcps: list[str] | None = None,
    safe_mode: bool = False,
) -> subprocess.CompletedProcess:
    """
    Run Claude in one-shot mode with specified MCPs, capturing output.

    Args:
        prompt: The prompt text to send to Claude
        mcps: List of MCP shortcuts/names to enable (e.g., ["gm", "cal"])
        safe_mode: If True, don't use --dangerously-skip-permissions

    Returns:
        subprocess.CompletedProcess with stdout/stderr captured
    """
    # Get working directory
    claude_dir = get_claude_dir()
    claude_dir.mkdir(parents=True, exist_ok=True)

    # Build MCP argument if provided
    mcp_arg = ",".join(mcps) if mcps else None

    # Build command and get enabled servers
    cmd, enabled_servers, error = build_claude_command(
        mcp_arg=mcp_arg,
        resume=False,
        safe_mode=safe_mode,
        prompt=prompt,
    )

    if error:
        # Return a failed result with the error message
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=1,
            stdout="",
            stderr=error,
        )

    # Configure MCPs in ~/.claude.json
    set_project_mcp_servers(claude_dir, enabled_servers)

    # Execute and capture output
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=claude_dir,
            check=False,
        )
        return result
    except FileNotFoundError:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=1,
            stdout="",
            stderr="Error: 'claude' command not found. Is Claude Code installed?",
        )
