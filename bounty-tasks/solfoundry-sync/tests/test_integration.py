#!/usr/bin/env python3
"""集成测试"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
sys.path.insert(0, 'app')
from main import app, bounties_db

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        bounties_db.clear()
    
    def test_full_sync_flow(self):
        webhook_payload = {"action": "opened", "issue": {"id": 99999, "number": 200, "title": "[BOUNTY] Test", "body": "Test", "labels": [{"name": "tier-2"}]}, "repository": {"name": "solfoundry"}}
        response = self.client.post("/webhook/github", json=webhook_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("github-99999", bounties_db)
    
    def test_label_update(self):
        bounties_db["github-123"] = type('Bounty', (), {'id': 'github-123', 'github_issue_id': '123', 'tier': 'T2'})()
        webhook_payload = {"action": "labeled", "issue": {"id": 123}, "repository": {"name": "solfoundry"}, "label": {"name": "tier-1"}}
        response = self.client.post("/webhook/github", json=webhook_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(bounties_db["github-123"].tier, "T1")

if __name__ == '__main__':
    unittest.main()
