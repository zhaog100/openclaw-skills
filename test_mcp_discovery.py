#!/usr/bin/env python3
"""
Test suite for MCP Server Discovery
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from mcp_server_discovery import MCPDiscoveryAgent, MCPServer


class TestMCPDiscoveryAgent(unittest.TestCase):
    """Test cases for MCPDiscoveryAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self.agent = MCPDiscoveryAgent(self.config_path)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.config_path, self.config_path)
        self.assertIsNotNone(self.agent.config)
        self.assertEqual(len(self.agent.discovered_servers), 0)

    def test_load_config_default(self):
        """Test loading default configuration."""
        config = self.agent._load_config()
        self.assertIn("discovery_methods", config)
        self.assertIn("mdns_service_types", config)
        self.assertIn("registry_urls", config)
        self.assertIn("server_capabilities", config)

    def test_load_config_custom(self):
        """Test loading custom configuration."""
        # Create custom config
        custom_config = {
            "discovery_methods": ["config"],
            "custom_field": "test_value"
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(custom_config, f)

        agent = MCPDiscoveryAgent(self.config_path)
        self.assertEqual(agent.config["discovery_methods"], ["config"])
        self.assertEqual(agent.config["custom_field"], "test_value")

    def test_validate_server_success(self):
        """Test server validation success."""
        # Mock a server that accepts connections
        with patch('socket.create_connection') as mock_connect:
            mock_connect.return_value.__enter__ = MagicMock()
            mock_connect.return_value.__exit__ = MagicMock()
            
            result = self.agent._validate_server("127.0.0.1", 8080)
            self.assertTrue(result)

    def test_validate_server_failure(self):
        """Test server validation failure."""
        with patch('socket.create_connection') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            result = self.agent._validate_server("127.0.0.1", 8080)
            self.assertFalse(result)

    def test_probe_capabilities(self):
        """Test capability probing."""
        capabilities = self.agent._probe_capabilities("127.0.0.1", 8080)
        self.assertIsInstance(capabilities, list)
        self.assertIn("basic", capabilities)

    def test_save_server_to_config(self):
        """Test saving server to config."""
        server = MCPServer(
            name="test-server",
            address="127.0.0.1",
            port=8080,
            server_type="test",
            capabilities=["basic"],
            discovered_via="manual",
            last_seen="2026-05-11T19:30:45.123456",
            metadata={"test": True}
        )

        self.agent._save_server_to_config(server)

        # Verify file was created
        config_file = Path(self.agent.config["config_file"])
        self.assertTrue(config_file.exists())

        # Verify content
        with open(config_file, 'r') as f:
            data = json.load(f)

        self.assertIn("servers", data)
        self.assertEqual(len(data["servers"]), 1)
        self.assertEqual(data["servers"][0]["name"], "test-server")

    def test_output_servers_table(self):
        """Test table format output."""
        server = MCPServer(
            name="test-server",
            address="127.0.0.1",
            port=8080,
            server_type="test",
            capabilities=["basic"],
            discovered_via="manual",
            last_seen="2026-05-11T19:30:45.123456",
            metadata={}
        )
        self.agent.discovered_servers = [server]

        output_file = os.path.join(self.test_dir, "test_output.json")
        
        with patch('builtins.print'):
            self.agent._output_servers(output_file, "table")

        # Verify JSON file was created
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertIn("timestamp", data)
        self.assertIn("servers", data)
        self.assertEqual(len(data["servers"]), 1)

    def test_output_servers_json(self):
        """Test JSON format output."""
        server = MCPServer(
            name="test-server",
            address="127.0.0.1",
            port=8080,
            server_type="test",
            capabilities=["basic"],
            discovered_via="manual",
            last_seen="2026-05-11T19:30:45.123456",
            metadata={}
        )
        self.agent.discovered_servers = [server]

        output_file = os.path.join(self.test_dir, "test_output.json")
        
        with patch('builtins.print'):
            self.agent._output_servers(output_file, "json")

        # Verify file was created
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertIn("timestamp", data)
        self.assertIn("servers", data)
        self.assertEqual(len(data["servers"]), 1)

    def test_output_servers_deduplication(self):
        """Test server deduplication."""
        server1 = MCPServer(
            name="server1",
            address="127.0.0.1",
            port=8080,
            server_type="test",
            capabilities=["basic"],
            discovered_via="manual",
            last_seen="2026-05-11T19:30:45.123456",
            metadata={}
        )
        
        server2 = MCPServer(
            name="server2",  # Same address:port
            address="127.0.0.1",
            port=8080,
            server_type="test",
            capabilities=["advanced"],
            discovered_via="mDNS",
            last_seen="2026-05-11T19:30:45.123456",
            metadata={}
        )

        self.agent.discovered_servers = [server1, server2]

        output_file = os.path.join(self.test_dir, "test_output.json")
        
        with patch('builtins.print'):
            self.agent._output_servers(output_file, "json")

        # Verify only one server (deduplicated)
        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data["servers"]), 1)

    @patch('zeroconf.Zeroconf')
    def test_discover_mdns(self, mock_zeroconf):
        """Test mDNS discovery setup."""
        mock_zc = MagicMock()
        mock_zeroconf.return_value = mock_zc

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.agent._discover_mdns())
            
            # Verify zeroconf was called
            mock_zeroconf.assert_called_once()
            mock_zc.close.assert_not_called()  # Should be called later
        finally:
            loop.close()

    @patch('aiohttp.ClientSession')
    def test_discover_registry(self, mock_session):
        """Test registry discovery."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "servers": [
                {
                    "name": "registry-server",
                    "address": "192.168.1.100",
                    "port": 9090,
                    "type": "mcp",
                    "capabilities": ["data-query"]
                }
            ]
        }
        
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.agent._discover_registry())
            
            # Verify server was discovered
            self.assertEqual(len(self.agent.discovered_servers), 1)
            server = self.agent.discovered_servers[0]
            self.assertEqual(server.name, "registry-server")
            self.assertEqual(server.address, "192.168.1.100")
            self.assertEqual(server.port, 9090)
            self.assertEqual(server.discovered_via, "registry")
        finally:
            loop.close()

    def test_discover_config(self):
        """Test config-based discovery."""
        # Create config file
        config_file = Path(self.agent.config["config_file"])
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "servers": [
                {
                    "name": "config-server",
                    "address": "10.0.0.1",
                    "port": 7070,
                    "type": "mcp",
                    "capabilities": ["file-operations"]
                }
            ]
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.agent._discover_config())
            
            # Verify server was discovered
            self.assertEqual(len(self.agent.discovered_servers), 1)
            server = self.agent.discovered_servers[0]
            self.assertEqual(server.name, "config-server")
            self.assertEqual(server.address, "10.0.0.1")
            self.assertEqual(server.port, 7070)
            self.assertEqual(server.discovered_via, "config")
        finally:
            loop.close()

    def test_register_server_valid(self):
        """Test valid server registration."""
        with patch.object(self.agent, '_validate_server', return_value=True):
            with patch.object(self.agent, '_probe_capabilities', return_value=["test-capability"]):
                with patch.object(self.agent, '_save_server_to_config') as mock_save:
                    result = self.agent._register_server("test@127.0.0.1:8080")
                    
                    self.assertEqual(result, 0)
                    mock_save.assert_called_once()

    def test_register_server_invalid_format(self):
        """Test invalid server registration format."""
        result = self.agent._register_server("invalid-format")
        self.assertEqual(result, 1)

    def test_register_server_unreachable(self):
        """Test registration of unreachable server."""
        with patch.object(self.agent, '_validate_server', return_value=False):
            result = self.agent._register_server("test@127.0.0.1:8080")
            self.assertEqual(result, 1)

    def test_list_servers_empty(self):
        """Test listing when no servers discovered."""
        with patch('builtins.print') as mock_print:
            result = self.agent._list_servers("output.json", "table")
            self.assertEqual(result, 1)
            mock_print.assert_called_with("📭 No servers discovered yet. Run --discover first.")

    def test_list_servers_with_data(self):
        """Test listing with discovered servers."""
        server = MCPServer(
            name="test-server",
            address="127.0.0.1",
            port=8080,
            server_type="test",
            capabilities=["basic"],
            discovered_via="manual",
            last_seen="2026-05-11T19:30:45.123456",
            metadata={}
        )
        self.agent.discovered_servers = [server]

        output_file = os.path.join(self.test_dir, "test_output.json")
        
        with patch('builtins.print'):
            result = self.agent._list_servers(output_file, "json")
            
        self.assertEqual(result, 0)
        self.assertTrue(os.path.exists(output_file))


if __name__ == '__main__':
    unittest.main(verbosity=2)