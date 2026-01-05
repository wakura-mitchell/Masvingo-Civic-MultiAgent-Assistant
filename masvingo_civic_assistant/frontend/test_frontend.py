#!/usr/bin/env python3
"""
Test script for Stage 5 Frontend Enhancements
Tests the new API endpoints and frontend functionality
"""

import requests
import json
import time
from datetime import datetime

class FrontendTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_agent_status(self):
        """Test the agent status endpoint"""
        print("🧪 Testing Agent Status Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/agent-status")
            if response.status_code == 200:
                data = response.json()
                print("✅ Agent status retrieved successfully")
                print(f"   📊 Agents: {len(data.get('agents', []))}")
                for agent in data.get('agents', []):
                    status = agent.get('status', 'unknown')
                    response_time = agent.get('response_time', 'N/A')
                    print(f"   🤖 {agent.get('name', 'Unknown')}: {status} ({response_time})")
                return True
            else:
                print(f"❌ Agent status failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Agent status error: {e}")
            return False

    def test_system_health(self):
        """Test the system health endpoint"""
        print("🧪 Testing System Health Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/system-health")
            if response.status_code == 200:
                data = response.json()
                print("✅ System health retrieved successfully")
                print(f"   💚 Status: {data.get('status', 'unknown')}")
                print(f"   ⏱️  Uptime: {data.get('uptime', 'N/A')}")
                print(f"   🧠 Memory: {data.get('memory_usage', 'N/A')}")
                return True
            else:
                print(f"❌ System health failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ System health error: {e}")
            return False

    def test_agent_query(self, query="What are the current water rates?"):
        """Test the enhanced agent query endpoint"""
        print(f"🧪 Testing Agent Query: '{query}'...")
        try:
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/agent-query", json=payload)
            if response.status_code == 200:
                data = response.json()
                print("✅ Agent query successful")
                agent = data.get('agent', 'Unknown')
                response_time = data.get('response_time', 'N/A')
                print(f"   🤖 Routed to: {agent}")
                print(f"   ⏱️  Response time: {response_time}")
                print(f"   📝 Response length: {len(data.get('response', ''))} chars")
                return True
            else:
                print(f"❌ Agent query failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Agent query error: {e}")
            return False

    def test_orchestrated_query(self, query="How do I pay my property taxes?"):
        """Test the orchestrated query endpoint"""
        print(f"🧪 Testing Orchestrated Query: '{query}'...")
        try:
            payload = {"query": query}
            response = self.session.post(f"{self.base_url}/orchestrated-query", json=payload)
            if response.status_code == 200:
                data = response.json()
                print("✅ Orchestrated query successful")
                print(f"   🎯 Classification: {data.get('classification', 'Unknown')}")
                print(f"   🤖 Agent used: {data.get('agent', 'Unknown')}")
                print(f"   ⏱️  Total time: {data.get('total_time', 'N/A')}")
                return True
            else:
                print(f"❌ Orchestrated query failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Orchestrated query error: {e}")
            return False

    def test_frontend_load(self):
        """Test that the frontend loads correctly"""
        print("🧪 Testing Frontend Load...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                content = response.text
                # Check for key features
                checks = [
                    ("Agent Status Dashboard", "agent-status" in content),
                    ("Quick Actions", "quick-actions" in content),
                    ("Theme Toggle", "theme-toggle" in content),
                    ("PWA Manifest", 'manifest.json' in content),
                    ("Tailwind CSS", "tailwindcss" in content),
                    ("Font Awesome", "fontawesome" in content),
                    ("Marked.js", "marked" in content)
                ]
                passed = 0
                for feature, found in checks:
                    if found:
                        print(f"   ✅ {feature}")
                        passed += 1
                    else:
                        print(f"   ❌ {feature} not found")
                print(f"   📊 Frontend checks: {passed}/{len(checks)} passed")
                return passed == len(checks)
            else:
                print(f"❌ Frontend load failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend load error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Stage 5 Frontend Tests")
        print("=" * 50)

        tests = [
            self.test_frontend_load,
            self.test_agent_status,
            self.test_system_health,
            self.test_agent_query,
            self.test_orchestrated_query
        ]

        results = []
        for test in tests:
            result = test()
            results.append(result)
            print()

        print("=" * 50)
        passed = sum(results)
        total = len(results)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Stage 5 frontend is ready for production.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")

        return passed == total

if __name__ == "__main__":
    tester = FrontendTester()
    success = tester.run_all_tests()

    if not success:
        exit(1)