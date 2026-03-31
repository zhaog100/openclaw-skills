#!/usr/bin/env python3
"""
Pre-Tool-Use Hook for Claude Code
Bounty: $100
Issue: #3
Repository: claude-builders-bounty/claude-builders-bounty

This hook intercepts tool calls and blocks potentially destructive operations.
"""

import sys
import json
import re
from typing import Dict, List, Optional, Tuple

class PreToolUseHook:
    """Hook that validates and filters tool calls before execution"""

    # Destructive patterns to block
    DESTRUCTIVE_PATTERNS = {
        'file_operations': [
            r'rm\s+-rf',
            r'delete\s+file',
            r'remove\s+file',
            r'truncate\s+file',
            r'overwrite\s+file',
        ],
        'system_operations': [
            r'shutdown',
            r'reboot',
            r'kill\s+-9',
            r'pkill\s+',
            r'terminate\s+system',
        ],
        'database_operations': [
            r'DROP\s+TABLE',
            r'DROP\s+DATABASE',
            r'TRUNCATE\s+TABLE',
            r'DELETE\s+FROM\s+\*',
            r'RESET\s+DATABASE',
        ],
        'network_operations': [
            r'iptables\s+-F',
            r'ufw\s+disable',
            r'shutdown\s+-h',
        ],
        'credential_operations': [
            r'revoke\s+key',
            r'delete\s+token',
            r'expire\s+credential',
            r'invalidate\s+session',
        ]
    }

    # Allowed safe patterns
    SAFE_PATTERNS = [
        r'ls\s+',
        r'cat\s+',
        r'head\s+',
        r'tail\s+',
        r'grep\s+',
        r'git\s+status',
        r'git\s+log',
        r'git\s+diff',
    ]

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the hook

        Args:
            strict_mode: If True, block anything not explicitly allowed
        """
        self.strict_mode = strict_mode
        self.blocked_count = 0

    def validate_tool_call(self, tool_name: str, tool_params: Dict) -> Tuple[bool, str]:
        """
        Validate a tool call before execution

        Args:
            tool_name: Name of the tool being called
            tool_params: Parameters passed to the tool

        Returns:
            (is_allowed, reason) tuple
        """
        # Check for destructive patterns in tool name
        if self._contains_destructive_pattern(tool_name):
            return False, f"Blocked destructive tool: {tool_name}"

        # Check parameters for destructive operations
        params_str = json.dumps(tool_params)

        # First check if it's explicitly safe
        if self._is_explicitly_safe(params_str):
            return True, "Safe operation"

        # Then check for destructive patterns
        destructive_match = self._contains_destructive_pattern(params_str)
        if destructive_match:
            return False, f"Blocked destructive pattern: {destructive_match}"

        # In strict mode, block anything not explicitly allowed
        if self.strict_mode:
            return False, "Strict mode: operation not in allowlist"

        return True, "Operation allowed"

    def _contains_destructive_pattern(self, text: str) -> Optional[str]:
        """Check if text contains any destructive pattern"""
        text_lower = text.lower()

        for category, patterns in self.DESTRUCTIVE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return f"{category}: {pattern}"

        return None

    def _is_explicitly_safe(self, text: str) -> bool:
        """Check if operation is explicitly marked as safe"""
        for pattern in self.SAFE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def filter_tool_params(self, tool_name: str, tool_params: Dict) -> Dict:
        """
        Filter sensitive information from tool parameters

        Args:
            tool_name: Name of the tool
            tool_params: Original parameters

        Returns:
            Filtered parameters
        """
        filtered = tool_params.copy()

        # Remove sensitive keys
        sensitive_keys = [
            'password', 'token', 'api_key', 'secret',
            'credential', 'auth', 'private_key'
        ]

        def remove_sensitive(obj):
            if isinstance(obj, dict):
                return {
                    k: '***REDACTED***' if any(sk in k.lower() for sk in sensitive_keys) else remove_sensitive(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [remove_sensitive(item) for item in obj]
            else:
                return obj

        return remove_sensitive(filtered)

    def process_tool_call(self, tool_name: str, tool_params: Dict) -> Dict:
        """
        Process a tool call through the hook

        Args:
            tool_name: Name of the tool
            tool_params: Parameters for the tool

        Returns:
            {
                'allowed': bool,
                'reason': str,
                'filtered_params': dict,
                'blocked': bool
            }
        """
        is_allowed, reason = self.validate_tool_call(tool_name, tool_params)
        filtered_params = self.filter_tool_params(tool_name, tool_params)

        if not is_allowed:
            self.blocked_count += 1

        return {
            'allowed': is_allowed,
            'reason': reason,
            'filtered_params': filtered_params,
            'blocked': not is_allowed
        }


def main():
    """CLI interface for the hook"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Pre-tool-use hook that blocks destructive operations'
    )
    parser.add_argument(
        '--tool-name',
        required=True,
        help='Name of the tool being called'
    )
    parser.add_argument(
        '--tool-params',
        required=True,
        help='JSON string of tool parameters'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict mode (block anything not explicitly allowed)'
    )
    parser.add_argument(
        '--json-output',
        action='store_true',
        help='Output result as JSON'
    )

    args = parser.parse_args()

    # Parse tool parameters
    try:
        tool_params = json.loads(args.tool_params)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in tool-params: {e}", file=sys.stderr)
        sys.exit(1)

    # Create hook and process
    hook = PreToolUseHook(strict_mode=args.strict)
    result = hook.process_tool_call(args.tool_name, tool_params)

    # Output result
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        if result['allowed']:
            print(f"✅ ALLOWED: {result['reason']}")
            print(f"Filtered params: {json.dumps(result['filtered_params'], indent=2)}")
        else:
            print(f"🚫 BLOCKED: {result['reason']}")
            sys.exit(2)  # Non-zero exit for blocked operations


if __name__ == '__main__':
    main()
