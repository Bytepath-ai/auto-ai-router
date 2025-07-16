#!/usr/bin/env python3
"""
Quick test to verify SWE-bench setup and parallelsynthetize_route integration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check all requirements are met"""
    print("Checking SWE-bench evaluation requirements...\n")
    
    all_good = True
    
    # 1. Check Python imports
    print("1. Checking Python dependencies:")
    try:
        import datasets
        print("   ✓ datasets library installed")
    except ImportError:
        print("   ✗ datasets library missing - run: pip install datasets")
        all_good = False
    
    try:
        import tqdm
        print("   ✓ tqdm library installed")
    except ImportError:
        print("   ✗ tqdm library missing - run: pip install tqdm")
        all_good = False
    
    try:
        import aisuite
        print("   ✓ aisuite library installed")
    except ImportError:
        print("   ✗ aisuite library missing - run: pip install aisuite")
        all_good = False
    
    try:
        from router import AIRouter
        print("   ✓ router.py found")
    except ImportError:
        print("   ✗ router.py not found in current directory")
        all_good = False
    
    # 2. Check environment variables
    print("\n2. Checking API keys:")
    if os.getenv("OPENAI_API_KEY"):
        print("   ✓ OPENAI_API_KEY set")
    else:
        print("   ✗ OPENAI_API_KEY missing")
        all_good = False
    
    if os.getenv("ANTHROPIC_API_KEY"):
        print("   ✓ ANTHROPIC_API_KEY set")
    else:
        print("   ✗ ANTHROPIC_API_KEY missing")
        all_good = False
    
    # Optional keys
    if os.getenv("XAI_API_KEY"):
        print("   ✓ XAI_API_KEY set (optional)")
    else:
        print("   - XAI_API_KEY not set (optional)")
    
    if os.getenv("GOOGLE_API_KEY"):
        print("   ✓ GOOGLE_API_KEY set (optional)")
    else:
        print("   - GOOGLE_API_KEY not set (optional)")
    
    # 3. Check Docker
    print("\n3. Checking Docker:")
    import subprocess
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✓ Docker installed: {result.stdout.strip()}")
        else:
            print("   ✗ Docker not properly installed")
            all_good = False
    except FileNotFoundError:
        print("   ✗ Docker command not found")
        all_good = False
    
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ Docker daemon accessible")
        else:
            print("   ✗ Docker daemon not accessible - add user to docker group:")
            print("     sudo usermod -aG docker $USER")
            print("     Then log out and back in")
            all_good = False
    except:
        print("   ✗ Cannot run docker commands")
        all_good = False
    
    # 4. Check SWE-bench installation
    print("\n4. Checking SWE-bench installation:")
    try:
        import swebench
        print("   ✓ SWE-bench package installed")
    except ImportError:
        print("   ✗ SWE-bench not installed - run from SWE-bench directory:")
        print("     cd SWE-bench && pip install .")
        all_good = False
    
    # 5. Test basic functionality
    print("\n5. Testing basic router functionality:")
    if all_good:
        try:
            from router import AIRouter
            config = {
                "openai": {"api_key": os.getenv("OPENAI_API_KEY")},
                "anthropic": {"api_key": os.getenv("ANTHROPIC_API_KEY")},
            }
            router = AIRouter(config)
            print("   ✓ AIRouter initialized successfully")
            
            # Test routing decision
            analysis = router.analyze_prompt("Write a hello world function in Python")
            print(f"   ✓ Router selected: {analysis['selected_model']} (confidence: {analysis['confidence']:.2f})")
            
        except Exception as e:
            print(f"   ✗ Router test failed: {str(e)}")
            all_good = False
    
    # Summary
    print("\n" + "="*50)
    if all_good:
        print("✓ All requirements met! You can run the evaluation:")
        print("  python3 swebench_evaluation.py --max-instances 1")
    else:
        print("✗ Some requirements missing. Please fix the issues above.")
    
    return all_good

if __name__ == "__main__":
    sys.exit(0 if check_requirements() else 1)