#!/usr/bin/env python3
"""
Quick Requirements Checker
Verifies all prerequisites are installed
"""

import sys
import subprocess

def check_python_version():
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False

def check_pip():
    print("\nChecking pip...")
    try:
        result = subprocess.run(['pip', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {result.stdout.strip()}")
            return True
        else:
            print(f"  ✗ pip not found")
            return False
    except:
        print(f"  ✗ pip not found")
        return False

def check_ollama():
    print("\nChecking Ollama...")
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {result.stdout.strip()}")
            
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if 'llama3' in result.stdout or 'mistral' in result.stdout:
                print(f"  ✓ Model installed")
                return True
            else:
                print(f"  ⚠ No models found. Run: ollama pull llama3")
                return False
        else:
            print(f"  ✗ Ollama not found")
            return False
    except:
        print(f"  ✗ Ollama not installed")
        print(f"    Download from: https://ollama.ai")
        return False

def check_env_file():
    print("\nChecking .env file...")
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_bot_token_here' in content:
                print(f"  ⚠ .env exists but not configured")
                return False
            else:
                print(f"  ✓ .env configured")
                return True
    except FileNotFoundError:
        print(f"  ✗ .env not found")
        print(f"    Run: cp .env.example .env")
        return False

def check_dependencies():
    print("\nChecking Python dependencies...")
    try:
        import telegram
        print(f"  ✓ python-telegram-bot")
    except:
        print(f"  ✗ python-telegram-bot")
        return False
    
    try:
        import apscheduler
        print(f"  ✓ APScheduler")
    except:
        print(f"  ✗ APScheduler")
        return False
    
    try:
        import PIL
        print(f"  ✓ Pillow")
    except:
        print(f"  ✗ Pillow")
        return False
    
    try:
        import flask
        print(f"  ✓ Flask")
    except:
        print(f"  ✗ Flask")
        return False
    
    try:
        import ollama
        print(f"  ✓ ollama")
    except:
        print(f"  ✗ ollama")
        return False
    
    return True

def main():
    print("="*60)
    print("TELEGRAM AUTOMATION - REQUIREMENTS CHECK")
    print("="*60)
    
    results = []
    
    results.append(("Python 3.10+", check_python_version()))
    results.append(("pip", check_pip()))
    results.append(("Ollama", check_ollama()))
    results.append(("Dependencies", check_dependencies()))
    results.append((".env file", check_env_file()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, status in results:
        symbol = "✓" if status else "✗"
        print(f"{symbol} {name}")
    
    passed = sum(1 for _, status in results if status)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All requirements met! Ready to install.")
        print("\nNext steps:")
        print("  1. pip install -r requirements.txt")
        print("  2. Configure .env file")
        print("  3. python test_system.py")
        print("  4. python main.py")
    else:
        print("\n⚠ Some requirements missing. Please install them first.")
        print("\nInstallation guide:")
        print("  - Python 3.10+: https://www.python.org/downloads/")
        print("  - Ollama: https://ollama.ai")
        print("  - Dependencies: pip install -r requirements.txt")
        print("  - Configuration: cp .env.example .env")
    
    print("\n")

if __name__ == "__main__":
    main()
