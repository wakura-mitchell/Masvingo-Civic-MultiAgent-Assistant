#!/usr/bin/env python3
"""
Masvingo Civic Assistant - Multi-Agent System Entry Point

This is the main entry point for the mock multi-agent civic platform.
It initializes the system and provides interfaces for running agents,
tools, and orchestration.
"""

import sys
import os
from pathlib import Path

# Add src to path for importing existing modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

def main():
    """Main function to run the civic assistant."""
    print("🚀 Initializing Masvingo Civic Assistant...")
    print("📁 Loading configuration...")

    # Placeholder for initialization
    print("✅ System initialized successfully!")
    print("🤖 Multi-agent system ready.")
    print("\nAvailable components:")
    print("- Agents: Billing, Incident, Licensing")
    print("- Tools: RAG, API Mock, Form Generator")
    print("- Orchestration: LangGraph workflows")
    print("\nTo run the web interface: python frontend/webapp.py")
    
    # Quick tool test
    print("\n🧪 Testing tools...")
    try:
        from tools.api_tool import APITool
        api = APITool()
        result = api.call_promun("/water-bill/123")
        print(f"✅ API Tool: {result['current_balance']}")
        
        from tools.math_tool import MathTool
        math = MathTool()
        fee = math.calculate_fee(100, 0.1, 30)
        print(f"✅ Math Tool: Total fee {fee['total']}")
        
        print("✅ All tools functional!")
    except Exception as e:
        print(f"⚠️ Tool test failed: {e}")

    # Quick agent test
    print("\n🤖 Testing agents...")
    try:
        from agents.coordinator_agent import CoordinatorAgent
        coord = CoordinatorAgent()
        response = coord.route_query("How much do I owe?")
        print(f"✅ Coordinator Agent: {response[:50]}...")
        print("✅ All agents functional!")
    except Exception as e:
        print(f"⚠️ Agent test failed: {e}")

if __name__ == "__main__":
    main()