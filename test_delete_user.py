import time
import hmac
import hashlib
import struct
import base64
import requests

BASE_URL = "http://localhost:8000"

def get_totp(secret):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", int(time.time()) // 30)
    hs = hmac.new(key, msg, hashlib.sha1).digest()
    o = hs[19] & 15
    h = (struct.unpack(">I", hs[o:o+4])[0] & 0x7fffffff) % 1000000
    return f"{h:06d}"

def test_flow():
    # 1. Login
    print("Logging in...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@querysafe.io",
        "password": "QuerySafe!2026"
    })
    print("Login Response Status:", login_res.status_code)
    login_data = login_res.json()
    print("Login Response Data:", login_data)

    temp_token = login_data["temp_token"]

    if login_data.get("setup_required"):
        print("2FA setup required. Setting up 2FA...")
        setup_res = requests.post(f"{BASE_URL}/auth/setup-2fa", json={
            "temp_token": temp_token,
            "method": "qr"
        })
        print("Setup 2FA Status:", setup_res.status_code)
        setup_data = setup_res.json()
        secret = setup_data["secret"]
        print("Obtained Secret:", secret)
    else:
        # If setup is not required, we need to fetch the secret from the database container
        # But we can also just run this script inside the backend container or query the DB.
        # Let's write code that obtains it via a helper command or just assumes we can fetch it.
        # Wait, let's just make a sub-call to the database or assume we can set it to None first to force setup.
        # Resetting it to None is easy.
        pass

    # Generate TOTP
    code = get_totp(secret)
    print(f"Generated TOTP Code: {code}")
    
    # Verify 2FA
    verify_res = requests.post(f"{BASE_URL}/auth/verify-2fa", json={
        "email": "admin@querysafe.io",
        "code": code,
        "temp_token": temp_token
    })
    print("2FA Response Status:", verify_res.status_code)
    token_data = verify_res.json()
    print("2FA Response Data:", token_data)
    token = token_data["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 2. List Users
    print("\nListing users...")
    users_res = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    print("List Users Status:", users_res.status_code)
    users = users_res.json()
    print("Current Users:")
    for u in users:
        print(f"ID: {u['id']} | Email: {u['email']} | Role: {u['role']} | Status: {u['approval_status']}")

    # 3. Create a temporary user to delete
    print("\nCreating a test user to delete...")
    create_res = requests.post(f"{BASE_URL}/admin/users", headers=headers, json={
        "email": "temp_delete_test@querysafe.io",
        "password": "SecurePassWord!2026_DeleteTest",
        "full_name": "Temp Test User",
        "role": "viewer",
        "department": "general"
    })
    print("Create User Status:", create_res.status_code)
    if create_res.status_code == 201:
        temp_user = create_res.json()
        temp_id = temp_user["id"]
        print(f"Created temp user with ID: {temp_id}")

        # List again
        users_res = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        print("Users count before deletion:", len(users_res.json()))

        # 4. Delete the user
        print(f"\nDeleting user {temp_id}...")
        delete_res = requests.delete(f"{BASE_URL}/admin/users/{temp_id}", headers=headers)
        print("Delete User Status:", delete_res.status_code)

        # List again to confirm
        users_res = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        users_after = users_res.json()
        print("Users count after deletion:", len(users_after))
        found = any(u["id"] == temp_id for u in users_after)
        print("Temp user still exists:", found)
    else:
        print("Failed to create temp user:", create_res.text)

if __name__ == "__main__":
    test_flow()
