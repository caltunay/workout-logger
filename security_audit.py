#!/usr/bin/env python3
"""
Security Audit Script for Workout Tracker
Run this script to check for common security issues before deployment.
"""

import os
import re
import sys
from pathlib import Path

def check_secrets_in_code():
    """Check for hardcoded secrets in code files"""
    print("🔍 Checking for hardcoded secrets...")
    
    secret_patterns = [
        (r'api[_-]?key\s*[:=]\s*["\'][^"\']{10,}["\']', 'API Key'),
        (r'password\s*[:=]\s*["\'][^"\']{3,}["\']', 'Password'),
        (r'secret\s*[:=]\s*["\'][^"\']{10,}["\']', 'Secret'),
        (r'token\s*[:=]\s*["\'][^"\']{10,}["\']', 'Token'),
        (r'sk-[a-zA-Z0-9]{32,}', 'OpenAI API Key'),
        (r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_.+/=]+', 'JWT Token'),
    ]
    
    issues = []
    
    for file_path in Path('.').rglob('*.py'):
        if 'test-workout-tracker' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern, name in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(f"  ⚠️  {file_path}:{line_num} - Potential {name} found")
        except Exception as e:
            print(f"  ⚠️  Could not read {file_path}: {e}")
    
    if issues:
        print("❌ Potential secrets found:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ No hardcoded secrets detected")
        return True

def check_env_file():
    """Check .env file configuration"""
    print("\n🔍 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    required_vars = [
        'SUPABASE_PROJECT_URL',
        'SUPABASE_ANON_PUBLIC_KEY',
        'ENVIRONMENT',
        'CORS_ORIGINS',
        'ENABLE_TEST_MODE'
    ]
    
    issues = []
    
    with open('.env', 'r') as f:
        env_content = f.read()
    
    for var in required_vars:
        if var not in env_content:
            issues.append(f"  ⚠️  Missing required variable: {var}")
    
    # Check for production safety
    if 'ENVIRONMENT=production' in env_content and 'ENABLE_TEST_MODE=true' in env_content:
        issues.append("  ⚠️  Test mode is enabled in production environment")
    
    if issues:
        print("❌ .env file issues:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ .env file looks good")
        return True

def check_gitignore():
    """Check .gitignore file"""
    print("\n🔍 Checking .gitignore...")
    
    if not os.path.exists('.gitignore'):
        print("❌ .gitignore file not found")
        return False
    
    required_entries = ['.env', '__pycache__/', '*.pyc', 'node_modules/']
    
    with open('.gitignore', 'r') as f:
        gitignore_content = f.read()
    
    missing = []
    for entry in required_entries:
        if entry not in gitignore_content:
            missing.append(entry)
    
    if missing:
        print(f"❌ Missing .gitignore entries: {', '.join(missing)}")
        return False
    else:
        print("✅ .gitignore looks good")
        return True

def check_dependencies():
    """Check for known vulnerable dependencies"""
    print("\n🔍 Checking dependencies...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    # This is a basic check - in production, use tools like safety or pip-audit
    print("✅ requirements.txt found (run 'pip install safety && safety check' for vulnerability scan)")
    return True

def check_security_headers():
    """Check if security headers are implemented"""
    print("\n🔍 Checking security headers implementation...")
    
    if not os.path.exists('main.py'):
        print("❌ main.py not found")
        return False
    
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    security_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Strict-Transport-Security'
    ]
    
    missing_headers = []
    for header in security_headers:
        if header not in main_content:
            missing_headers.append(header)
    
    if missing_headers:
        print(f"❌ Missing security headers: {', '.join(missing_headers)}")
        return False
    else:
        print("✅ Security headers implemented")
        return True

def check_input_validation():
    """Check for input validation implementation"""
    print("\n🔍 Checking input validation...")
    
    if not os.path.exists('main.py'):
        print("❌ main.py not found")
        return False
    
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    validation_indicators = ['Field(', 'validator', 'min_length', 'max_length']
    
    found_validation = any(indicator in main_content for indicator in validation_indicators)
    
    if found_validation:
        print("✅ Input validation implemented")
        return True
    else:
        print("❌ No input validation found")
        return False

def main():
    """Run all security checks"""
    print("🛡️  Security Audit for Workout Tracker")
    print("=" * 50)
    
    checks = [
        check_secrets_in_code,
        check_env_file,
        check_gitignore,
        check_dependencies,
        check_security_headers,
        check_input_validation
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Error running check: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} security checks passed! Safe to deploy.")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} of {total} security checks failed. Please fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
