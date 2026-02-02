import argparse
import os

def select_transport(default: str = "stdio") -> str:
    """
    Decide which transport to use, preferring:
    1. Command-line argument --transport
    2. MCP_TRANSPORT environment variable
    3. Provided default

    Args:
        default: The fallback transport to use

    Returns:
        Name of the transport method as a string
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--transport",
        type=str,
        default=None,
        help="MCP transport to use ('stdio', 'streamable-http', etc.)"
    )
    # Parse ONLY known args to avoid interfering with other CLI args
    args, _ = parser.parse_known_args()
    return args.transport or os.getenv("MCP_TRANSPORT") or default