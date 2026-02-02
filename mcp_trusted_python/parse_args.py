import argparse
import os
from typing import Any, Dict

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="MCP Trusted Python Agent Command-Line Interface"
    )
    parser.add_argument(
        "--transport",
        type=str,
        default=None,
        help="MCP transport to use: 'stdio' (default), 'streamable-http', etc."
    )
    # Add more shared/global options here as needed
    return parser

def parse_args(default_transport: str = "stdio") -> Dict[str, Any]:
    """
    Parse CLI arguments and environment for standard agent options.
    Returns a dict of all parsed options, including `transport`.
    """
    parser = get_parser()
    args = parser.parse_args()
    # CLI arg > ENV > default
    transport = args.transport or os.getenv("MCP_TRANSPORT") or default_transport
    opts = vars(args)
    opts["transport"] = transport
    return opts