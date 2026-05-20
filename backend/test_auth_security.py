import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def make_request(path: str, method: str = "GET", data: dict = None, token: str = None) -> tuple[int, dict]:
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            return response.status, json.loads(res_data) if res_data else {}
    except urllib.error.HTTPError as e:
        res_data = e.read().decode("utf-8")
        try:
            return e.code, json.loads(res_data)
        except Exception:
            return e.code, {"detail": res_data}
    except Exception as e:
        return 500, {"detail": str(e)}

def run_tests():
    print("==================================================")
    print("      QuerySafe Auth & Security Test Runner       ")
    print("==================================================")
    
    # 1. Test System Health check
    print("\n[TEST 1] System Health Check...")
    status, body = make_request("/health")
    print(f"Status: {status}, Response: {body}")
    assert status == 200, "Health check failed"
    assert body.get("status") == "ok", "Invalid health status"
    
    # Generate unique email for testing
    email = f"test_{int(time.time())}@company.com"
    password = "SecurePassword123!"
    
    # 2. Test User Registration
    print("\n[TEST 2] Register New User (Role: finance)...")
    status, body = make_request("/auth/register", "POST", {
        "email": email,
        "password": password,
        "role": "finance"
    })
    print(f"Status: {status}, Response: {body}")
    assert status == 201, "Registration failed"
    assert body.get("email") == email, "Email mismatch"
    assert body.get("role") == "finance", "Role mismatch"
    
    # 3. Test Weak Password Registration Block
    print("\n[TEST 3] Register User with Weak Password...")
    status, body = make_request("/auth/register", "POST", {
        "email": f"weak_{email}",
        "password": "simple",
        "role": "finance"
    })
    print(f"Status: {status}, Response: {body}")
    assert status == 422 or status == 400, f"Allowed weak password with status {status}"
    
    # 4. Test User Login (Correct Password)
    print("\n[TEST 4] Logging In with Correct Credentials...")
    status, body = make_request("/auth/login", "POST", {
        "email": email,
        "password": password
    })
    print(f"Status: {status}, Keys in Response: {list(body.keys())}")
    assert status == 200, "Login failed"
    assert "access_token" in body, "Missing access token"
    access_token = body["access_token"]
    
    # 5. Test User Login (Incorrect Password)
    print("\n[TEST 5] Logging In with Incorrect Credentials...")
    status, body = make_request("/auth/login", "POST", {
        "email": email,
        "password": "WrongPassword1!"
    })
    print(f"Status: {status}, Response: {body}")
    assert status == 412 or status == 401, f"Expected 401 Unauthorized, got {status}"
    
    # 6. Test Security SQL Validation: Safe query
    print("\n[TEST 6] Validate Safe SQL (SELECT)...")
    status, body = make_request("/security/validate-sql", "POST", {
        "sql": "SELECT * FROM invoices WHERE amount > 5000"
    })
    print(f"Status: {status}, Safe: {body.get('is_safe')}, Cleaned SQL: {body.get('cleaned_sql')}")
    assert status == 200, "Safe SQL validation failed"
    assert body.get("is_safe") is True, "Safe query was incorrectly blocked"
    assert "LIMIT 500" in body.get("cleaned_sql"), "LIMIT 500 enforcement failed to append"
    
    # 7. Test Security SQL Validation: DDL query (DROP TABLE)
    print("\n[TEST 7] Validate Dangerous SQL (DROP TABLE)...")
    status, body = make_request("/security/validate-sql", "POST", {
        "sql": "DROP TABLE users;"
    })
    print(f"Status: {status}, Safe: {body.get('is_safe')}, Reason: {body.get('reason')}")
    assert status == 200, "Dangerous SQL validation request failed"
    assert body.get("is_safe") is False, "Dangerous query was incorrectly allowed"
    assert "DROP" in body.get("blocked_keywords"), "DROP keyword was not blocked"
    
    # 8. Test 2FA Setup
    print("\n[TEST 8] Requesting 2FA Setup...")
    status, body = make_request("/auth/setup-2fa", "POST", token=access_token)
    print(f"Status: {status}, Keys in Response: {list(body.keys())}")
    assert status == 200, "2FA setup failed"
    assert "qr_code" in body, "Missing qr_code base64"
    assert "manual_code" in body, "Missing manual code secret"
    
    # 9. Test User Logout
    print("\n[TEST 9] Logging Out...")
    status, body = make_request("/auth/logout", "POST", token=access_token)
    print(f"Status: {status}, Response: {body}")
    assert status == 200, "Logout failed"
    
    print("\n==================================================")
    print("      ALL TESTS PASSED SUCCESSFULLY! [SUCCESS]   ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
