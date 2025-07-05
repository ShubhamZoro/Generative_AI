#!/usr/bin/env python3
"""
Test script to verify the QA Agent setup
"""

import os
import sys
import asyncio
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment setup...\n")
    
    # Check Python version
    python_version = sys.version_info
    print(f"✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 9):
        print("❌ Python 3.9 or higher is required!")
        return False
    
    # Check required packages
    required_packages = [
        'langchain',
        'langgraph', 
        'openai',
        'google.generativeai',
        'playwright',
        'streamlit',
        'pandas',
        'plotly'
    ]
    
    print("\n📦 Checking required packages:")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('.', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check environment variables
    print("\n🔑 Checking API keys:")
    api_keys_found = True
    
    if os.getenv('OPENAI_API_KEY'):
        print("✓ OPENAI_API_KEY is set")
    else:
        print("❌ OPENAI_API_KEY is NOT set")
        api_keys_found = False
    
    if os.getenv('GOOGLE_API_KEY'):
        print("✓ GOOGLE_API_KEY is set")
    else:
        print("❌ GOOGLE_API_KEY is NOT set")
        api_keys_found = False
    
    if not api_keys_found:
        print("\n❌ Please set API keys in .env file")
        return False
    
    # Check Playwright installation
    print("\n🎭 Checking Playwright browsers:")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            if p.chromium.executable_path:
                print("✓ Chromium browser is installed")
            else:
                print("❌ Chromium browser is NOT installed")
                print("Run: playwright install chromium")
                return False
    except Exception as e:
        print(f"❌ Playwright check failed: {e}")
        print("Run: playwright install")
        return False
    
    # Create necessary directories
    print("\n📁 Creating directories:")
    directories = ['test_results', 'test_results/screenshots', 'test_results/videos']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created {dir_name}/")
    
    return True

async def test_basic_functionality():
    """Test basic functionality of the QA agent"""
    print("\n🧪 Testing basic functionality...\n")
    
    try:
        # Test imports
        from qa_agent import VideoTranscriber, TestCaseGenerator
        print("✓ Successfully imported QA agent modules")
        
        # Test video transcriber initialization
        transcriber = VideoTranscriber()
        print("✓ VideoTranscriber initialized")
        
        # Test test case generator initialization
        generator = TestCaseGenerator()
        print("✓ TestCaseGenerator initialized")
        
        print("\n✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Basic functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("QA Agent Setup Verification")
    print("=" * 50)
    
    # Load .env file if it exists
    if Path('.env').exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Loaded .env file\n")
    else:
        print("⚠️  No .env file found. Create one with your API keys.\n")
    
    # Run checks
    env_ok = check_environment()
    
    if env_ok:
        # Run basic functionality test
        func_ok = asyncio.run(test_basic_functionality())
        
        if func_ok:
            print("\n" + "=" * 50)
            print("✅ Setup verification PASSED!")
            print("=" * 50)
            print("\nYou're ready to run the QA Agent!")
            print("\nNext steps:")
            print("1. Run the main application: python qa_agent.py")
            print("2. Or launch the dashboard: streamlit run dashboard.py")
        else:
            print("\n❌ Some functionality tests failed. Please check the errors above.")
    else:
        print("\n❌ Environment setup incomplete. Please fix the issues above.")

if __name__ == "__main__":
    main()
