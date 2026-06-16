#!/usr/bin/env python3
"""Convert cdn-only_plain.txt into Keenetic route add .bat files for GitHub Actions."""

import ipaddress
import sys
from pathlib import Path

def read_prefixes(path: Path) -> list:
    """Read CIDR prefixes from file (space or newline separated)."""
    prefixes = []
    content = path.read_text(encoding="utf-8")
    # Split by whitespace (spaces, newlines, tabs)
    for token in content.split():
        token = token.strip()
        if not token:
            continue
        try:
            network = ipaddress.ip_network(token, strict=False)
            if network.version == 4:
                prefixes.append(network)
        except ValueError:
            continue
    return prefixes

def build_routes(prefixes: list) -> list:
    """Convert prefixes to Keenetic route add commands."""
    lines = []
    for network in prefixes:
        lines.append(f"route add {network.network_address} mask {network.netmask} 0.0.0.0")
    return lines

def main():
    # Input file is fetched by the workflow
    input_file = Path("cdn-only_plain.txt")
    if not input_file.exists():
        print("❌ Input file not found!", file=sys.stderr)
        sys.exit(1)

    prefixes = read_prefixes(input_file)
    if not prefixes:
        print("❌ No valid IPv4 prefixes found!", file=sys.stderr)
        sys.exit(1)

    routes = build_routes(prefixes)

    # Write output (single file, no chunking for Action)
    output_file = Path("cdn-only_keenetic.bat")
    output_file.write_text("\n".join(routes) + "\n", encoding="utf-8")
    print(f"✅ Converted {len(routes)} routes to {output_file}")

if __name__ == "__main__":
    main()
