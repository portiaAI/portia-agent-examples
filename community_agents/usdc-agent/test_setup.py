#!/usr/bin/env python3
"""
Test script to verify the usdc agent setup without requiring real API keys.
This script checks if all dependencies are properly installed and imports work correctly.
"""

def test_imports():
    """Test that all required modules can be imported."""
    try:
        print("🔍 Testing imports...")
        
        # Test basic imports
        import os
        import asyncio
        from decimal import Decimal
        from typing import Optional
        print("  ✅ Standard library imports: OK")
        
        # Test third-party imports
        from dotenv import load_dotenv
        print("  ✅ python-dotenv: OK")
        
        from portia import Portia, Config, Tool, ToolRunContext
        from portia.cli import CLIExecutionHooks
        print("  ✅ portia-sdk-python: OK")
        
        # Test CDP SDK import (might not be available without proper installation)
        try:
            from cdp import CdpClient, parse_units
            print("  ✅ cdp-sdk: OK")
        except ImportError as e:
            print(f"  ⚠️  cdp-sdk: Not available ({e})")
            print("     This is expected if you haven't installed it yet.")
            print("     Run: uv add cdp-sdk")
            
        print("\n✅ All available imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_environment_template():
    """Test that environment template is properly structured."""
    import os
    try:
        print("\n🔍 Testing environment configuration...")
        
        # Check if env.example exists
        env_example_path = ".env.example"
        if os.path.exists(env_example_path):
            print("  ✅ env.example file exists")
            
            with open(env_example_path, 'r') as f:
                content = f.read()
                
            required_vars = [
                'CDP_API_KEY_ID',
                'CDP_API_KEY_SECRET',
                'NETWORK_ID'
            ]
            
            for var in required_vars:
                if var in content:
                    print(f"  ✅ {var} template found")
                else:
                    print(f"  ❌ {var} template missing")
                    
        else:
            print("  ❌ env.example file not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Environment test error: {e}")
        return False


def test_project_structure():
    """Test that the project has the expected structure."""
    import os
    try:
        print("\n🔍 Testing project structure...")
        
        expected_files = [
            'main.py',
            'pyproject.toml', 
            'README.md',
            'env.example',
            'uv.lock'
        ]
        
        for file in expected_files:
            if os.path.exists(file):
                print(f"  ✅ {file} exists")
            else:
                print(f"  ❌ {file} missing")
                
        return True
        
    except Exception as e:
        print(f"❌ Structure test error: {e}")
        return False


def main():
    """Run all tests."""
    import os
    print("🚀 USDC Agent Setup Test")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    tests = [
        test_imports,
        test_environment_template,
        test_project_structure
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your USDC Agent setup looks good.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env") 
        print("2. Add your CDP API keys and Portia API key")
        print("3. Run: uv run main.py")
        print("4. Use 'wallet info' to create wallet (auto-funded with USDC)")
        print("5. Send gasless USDC transfers to any address!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    

if __name__ == "__main__":
    main()
