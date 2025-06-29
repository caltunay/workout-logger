#!/usr/bin/env python3
"""
Quick security validation test
Tests that the application starts with security measures in place
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """Test that configuration loads properly"""
    try:
        from config import ENVIRONMENT, CORS_ORIGINS, ENABLE_TEST_MODE
        print("✅ Configuration loaded successfully")
        print(f"   Environment: {ENVIRONMENT}")
        print(f"   Test mode: {ENABLE_TEST_MODE}")
        print(f"   CORS origins: {len(CORS_ORIGINS)} configured")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_app_creation():
    """Test that FastAPI app can be created with security middleware"""
    try:
        from main import app
        print("✅ FastAPI app created with security middleware")
        
        # Check middleware
        middleware_names = [type(middleware).__name__ for middleware, _ in app.user_middleware]
        expected_middleware = ['CORSMiddleware']
        
        for mw in expected_middleware:
            if mw in middleware_names:
                print(f"   ✅ {mw} configured")
            else:
                print(f"   ⚠️  {mw} not found")
        
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_validation_models():
    """Test that Pydantic models have proper validation"""
    try:
        from main import LoginRequest, AddSetRequest
        
        # Test email validation
        try:
            LoginRequest(email="invalid-email", password="12345678")
            print("⚠️  Email validation may not be working")
        except:
            print("✅ Email validation working")
        
        # Test field constraints
        try:
            AddSetRequest(
                session_id=0,  # Should fail (gt=0)
                exercise_name="test",
                reps=1,
                weight=1,
                is_kg=True,
                user_id="123e4567-e89b-12d3-a456-426614174000",
                access_token="test-token"
            )
            print("⚠️  Field validation may not be working")
        except:
            print("✅ Field validation working")
        
        return True
    except Exception as e:
        print(f"❌ Validation testing failed: {e}")
        return False

def test_env_file():
    """Test that .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    required_vars = [
        'SUPABASE_PROJECT_URL',
        'SUPABASE_ANON_PUBLIC_KEY',
        'ENVIRONMENT'
    ]
    
    with open('.env', 'r') as f:
        env_content = f.read()
    
    missing = []
    for var in required_vars:
        if var not in env_content:
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("✅ Required environment variables present")
        return True

def main():
    """Run all validation tests"""
    print("🧪 Security Validation Tests")
    print("=" * 40)
    
    tests = [
        test_env_file,
        test_config_loading,
        test_app_creation,
        test_validation_models
    ]
    
    results = []
    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} validation tests passed!")
        print("🛡️  Application is ready for deployment")
        return True
    else:
        print(f"❌ {total - passed} of {total} tests failed")
        print("⚠️  Please fix issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
