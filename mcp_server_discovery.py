#!/usr/bin/env python3
"""
MCP Server Discovery for claude-builders-bounty #912

A discovery system for MCP (Model Context Protocol) servers with:
- Local network discovery (mDNS/Bonjour)
- Registry-based discovery
- Configuration-based discovery
- Hybrid approach
"""

import argparse
import asyncio
import json
import socket
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set
try:
    import zeroconf
except ImportError:
    zeroconf = None

try:
    import aiohttp
except ImportError:
    aiohttp = None
from pathlib import Path


@dataclass
class MCPServer:
    """Represents a discovered MCP server."""
    name: str
    address: str
    port: int
    server_type: str
    capabilities: List[str]
    discovered_via: str
    last_seen: str
    metadata: Dict


class MCPDiscoveryAgent:
    """MCP Server Discovery Agent."""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(Path.home() / ".mcp" / "discovery.json")
        self.config = self._load_config()
        self.discovered_servers: List[MCPServer] = []
        self.zeroconf = None
        self.listener = None

    def run(self) -> int:
        """Main entry point."""
        parser = argparse.ArgumentParser(
            description="MCP Server Discovery - Find and register MCP servers"
        )
        parser.add_argument(
            "--discover", action="store_true",
            help="Discover MCP servers on the network"
        )
        parser.add_argument(
            "--register", type=str,
            help="Register a new MCP server (format: name@address:port)"
        )
        parser.add_argument(
            "--list", action="store_true",
            help="List all discovered servers"
        )
        parser.add_argument(
            "--watch", action="store_true",
            help="Watch for new servers continuously"
        )
        parser.add_argument(
            "--output", type=str, default="servers.json",
            help="Output file for server list (default: servers.json)"
        )
        parser.add_argument(
            "--format", choices=["json", "table"], default="table",
            help="Output format (default: table)"
        )
        parser.add_argument(
            "--timeout", type=int, default=30,
            help="Discovery timeout in seconds (default: 30)"
        )

        args = parser.parse_args()

        try:
            if args.register:
                return self._register_server(args.register)
            elif args.discover:
                return self._discover_servers(args.timeout, args.output, args.format)
            elif args.watch:
                return self._watch_servers()
            elif args.list:
                return self._list_servers(args.output, args.format)
            else:
                parser.print_help()
                return 1

        except KeyboardInterrupt:
            print("\n👋 Discovery interrupted by user")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    def _load_config(self) -> Dict:
        """Load discovery configuration."""
        default_config = {
            "discovery_methods": ["mdns", "registry", "config"],
            "mdns_service_types": ["_mcp._tcp.local.", "_http._tcp.local."],
            "registry_urls": [
                "https://mcp-registry.example.com/servers",
                "https://registry.claude.builders/servers"
            ],
            "config_file": str(Path.home() / ".mcp" / "servers.json"),
            "server_capabilities": [
                "text-processing",
                "code-analysis",
                "data-query",
                "file-operations",
                "network-tools"
            ]
        }

        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            print(f"⚠️  Warning: Could not load config: {e}")

        return default_config

    def _register_server(self, server_spec: str) -> int:
        """Register a new MCP server."""
        try:
            if '@' not in server_spec or ':' not in server_spec:
                print("❌ Invalid format. Use: name@address:port")
                return 1

            name, address_port = server_spec.split('@', 1)
            address, port_str = address_port.split(':', 1)
            port = int(port_str)

            # Validate server
            if not self._validate_server(address, port):
                print(f"❌ Server {address}:{port} is not reachable")
                return 1

            # Create server info
            server = MCPServer(
                name=name,
                address=address,
                port=port,
                server_type="registered",
                capabilities=self._probe_capabilities(address, port),
                discovered_via="manual",
                last_seen=datetime.now().isoformat(),
                metadata={"registered_by": "user"}
            )

            # Save to config
            self._save_server_to_config(server)

            print(f"✅ Registered server: {name} @ {address}:{port}")
            print(f"📋 Capabilities: {', '.join(server.capabilities)}")

            return 0

        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return 1

    def _discover_servers(self, timeout: int, output_file: str, format_type: str) -> int:
        """Discover MCP servers using multiple methods."""
        print(f"🔍 Discovering MCP servers (timeout: {timeout}s)...")

        # Clear previous discoveries
        self.discovered_servers = []

        # Start discovery methods concurrently
        tasks = []

        if "mdns" in self.config["discovery_methods"]:
            tasks.append(self._discover_mdns())

        if "registry" in self.config["discovery_methods"]:
            tasks.append(self._discover_registry())

        if "config" in self.config["discovery_methods"]:
            tasks.append(self._discover_config())

        # Run all discovery methods
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(asyncio.gather(*tasks))
        finally:
            loop.close()

        # Wait for discovery to complete
        print(f"⏳ Discovery in progress...")
        time.sleep(timeout)

        # Stop mDNS discovery
        if self.zeroconf:
            self.zeroconf.close()

        # Output results
        self._output_servers(output_file, format_type)

        print(f"✅ Discovery complete: {len(self.discovered_servers)} servers found")
        return 0

    async def _discover_mdns(self):
        """Discover servers using mDNS/Bonjour."""
        if zeroconf is None:
            print("  ⚠️  mDNS discovery skipped: zeroconf module not installed")
            return
            
        print("📡 Starting mDNS discovery...")

        class MCPServiceListener:
            def __init__(self, agent):
                self.agent = agent

            def add_service(self, zc, type_, name):
                info = zc.get_service_info(type_, name)
                if info:
                    server = MCPServer(
                        name=name.replace('.' + type_, ''),
                        address=socket.inet_ntoa(info.addresses[0]) if info.addresses else "unknown",
                        port=info.port,
                        server_type="mcp",
                        capabilities=self.agent._probe_capabilities(
                            socket.inet_ntoa(info.addresses[0]), info.port
                        ),
                        discovered_via="mDNS",
                        last_seen=datetime.now().isoformat(),
                        metadata={"service_type": type_, "properties": dict(info.properties)}
                    )
                    self.agent.discovered_servers.append(server)
                    print(f"  🔍 Found via mDNS: {server.name} @ {server.address}:{server.port}")

            def remove_service(self, zc, type_, name):
                pass

            def update_service(self, zc, type_, name):
                pass

        self.zeroconf = zeroconf.Zeroconf()
        self.listener = MCPServiceListener(self)

        for service_type in self.config["mdns_service_types"]:
            zeroconf.ServiceBrowser(self.zeroconf, service_type, self.listener)

    async def _discover_registry(self):
        """Discover servers from registry URLs."""
        if aiohttp is None:
            print("  ⚠️  Registry discovery skipped: aiohttp module not installed")
            return
            
        print("🌐 Checking registry servers...")

        for registry_url in self.config["registry_urls"]:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(registry_url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            for server_data in data.get('servers', []):
                                server = MCPServer(
                                    name=server_data['name'],
                                    address=server_data['address'],
                                    port=server_data['port'],
                                    server_type=server_data.get('type', 'unknown'),
                                    capabilities=server_data.get('capabilities', []),
                                    discovered_via="registry",
                                    last_seen=datetime.now().isoformat(),
                                    metadata={"registry": registry_url}
                                )
                                self.discovered_servers.append(server)
                                print(f"  🌐 Found via registry: {server.name} @ {server.address}:{server.port}")
            except Exception as e:
                print(f"  ⚠️  Registry {registry_url} failed: {e}")

    async def _discover_config(self):
        """Discover servers from configuration file."""
        config_file = Path(self.config["config_file"])
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    for server_data in data.get('servers', []):
                        server = MCPServer(
                            name=server_data['name'],
                            address=server_data['address'],
                            port=server_data['port'],
                            server_type=server_data.get('type', 'unknown'),
                            capabilities=server_data.get('capabilities', []),
                            discovered_via="config",
                            last_seen=datetime.now().isoformat(),
                            metadata={"config_file": str(config_file)}
                        )
                        self.discovered_servers.append(server)
                        print(f"  📁 Found via config: {server.name} @ {server.address}:{server.port}")
            except Exception as e:
                print(f"  ⚠️  Config file failed: {e}")

    def _list_servers(self, output_file: str, format_type: str) -> int:
        """List all discovered servers."""
        if not self.discovered_servers:
            print("📭 No servers discovered yet. Run --discover first.")
            return 1

        self._output_servers(output_file, format_type)
        return 0

    def _watch_servers(self) -> int:
        """Watch for servers continuously."""
        print("👀 Watching for MCP servers... (Ctrl+C to stop)")

        # Initial discovery
        self._discover_servers(10, "watch_servers.json", "table")

        # Continuous watching with mDNS
        if "mdns" in self.config["discovery_methods"]:
            print("📡 Starting continuous mDNS watch...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(self._discover_mdns())
                # Keep running
                loop.run_forever()
            except KeyboardInterrupt:
                pass
            finally:
                if self.zeroconf:
                    self.zeroconf.close()
                loop.close()

        return 0

    def _validate_server(self, address: str, port: int) -> bool:
        """Validate if server is reachable."""
        try:
            with socket.create_connection((address, port), timeout=5):
                return True
        except:
            return False

    def _probe_capabilities(self, address: str, port: int) -> List[str]:
        """Probe server capabilities."""
        # Default capabilities for unknown servers
        return ["basic"]

    def _save_server_to_config(self, server: MCPServer):
        """Save server to configuration file."""
        config_file = Path(self.config["config_file"])
        config_file.parent.mkdir(parents=True, exist_ok=True)

        data = {"servers": []}
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
            except:
                pass

        # Add or update server
        servers = data.get('servers', [])
        for i, s in enumerate(servers):
            if s['name'] == server.name:
                servers[i] = asdict(server)
                break
        else:
            servers.append(asdict(server))

        data['servers'] = servers

        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _output_servers(self, output_file: str, format_type: str):
        """Output servers in specified format."""
        # Remove duplicates
        unique_servers = {}
        for server in self.discovered_servers:
            key = f"{server.address}:{server.port}"
            if key not in unique_servers:
                unique_servers[key] = server

        self.discovered_servers = list(unique_servers.values())

        if format_type == "json":
            data = {
                "timestamp": datetime.now().isoformat(),
                "servers": [asdict(s) for s in self.discovered_servers]
            }
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"📝 Saved to {output_file}")

        else:  # table
            print("\n📋 Discovered MCP Servers:")
            print("=" * 80)
            if not self.discovered_servers:
                print("📭 No servers found")
            else:
                for i, server in enumerate(self.discovered_servers, 1):
                    print(f"{i}. {server.name}")
                    print(f"   📍 {server.address}:{server.port}")
                    print(f"   🔧 {', '.join(server.capabilities)}")
                    print(f"   🔍 Discovered via: {server.discovered_via}")
                    print()

            # Save to file as well
            data = {
                "timestamp": datetime.now().isoformat(),
                "servers": [asdict(s) for s in self.discovered_servers]
            }
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"📝 Saved to {output_file}")


if __name__ == "__main__":
    agent = MCPDiscoveryAgent()
    sys.exit(agent.run())