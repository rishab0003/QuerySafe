#!/usr/bin/env bash
# Live API test for OAuth + admin approval flow
set -euo pipefail
BASE="${1:-http://127.0.0.1:8765}"
ADMIN_EMAIL="${BOOTSTRAP_ADMIN_EMAIL:-admin@querysafe.io}"
ADMIN_PASSWORD="${BOOTSTRAP_ADMIN_PASSWORD:-QsBootstrap9!}"
EMP_PASS="S3cure!Passw0rd"
EMP_EMAIL="live-$(date +%s)@example.com"

echo "== Health =="
curl -sf "$BASE/health" | head -c 80
echo ""

echo "== OAuth providers =="
curl -sf "$BASE/auth/oauth/providers"
echo ""

echo "== Register employee (pending) =="
REG=$(curl -sf -X POST "$BASE/auth/register" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMP_EMAIL\",\"password\":\"$EMP_PASS\",\"full_name\":\"Live User\",\"department\":\"finance\"}")
echo "$REG" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['approval_status']=='pending', d; print('OK pending', d['email'])"

echo "== Pending login blocked =="
LOGIN=$(curl -sf -X POST "$BASE/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMP_EMAIL\",\"password\":\"$EMP_PASS\"}")
echo "$LOGIN" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('approval_pending'), d; print('OK approval_pending')"

echo "== Admin login + 2FA =="
TEMP=$(curl -sf -X POST "$BASE/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['temp_token'])")
SECRET=$(curl -sf -X POST "$BASE/auth/setup-2fa" -H 'Content-Type: application/json' \
  -d "{\"temp_token\":\"$TEMP\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['secret'])")
CODE=$(python3 -c "import pyotp; print(pyotp.TOTP('$SECRET').now())")
TOKENS=$(curl -sf -X POST "$BASE/auth/verify-2fa" -H 'Content-Type: application/json' \
  -d "{\"temp_token\":\"$TEMP\",\"code\":\"$CODE\"}")
ACCESS=$(echo "$TOKENS" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "OK admin token"

echo "== Admin approve employee =="
USER_ID=$(curl -sf "$BASE/admin/users?status_filter=pending" -H "Authorization: Bearer $ACCESS" \
  | python3 -c "import sys,json; u=[x for x in json.load(sys.stdin) if x['email']=='$EMP_EMAIL'][0]; print(u['id'])")
curl -sf -X POST "$BASE/admin/users/$USER_ID/approve" -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' -d '{"role":"finance","department":"finance"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['approval_status']=='approved' and d['role']=='finance'; print('OK approved', d['role'])"

echo "== Employee login after approval =="
TEMP2=$(curl -sf -X POST "$BASE/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMP_EMAIL\",\"password\":\"$EMP_PASS\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('temp_token'), d; print(d['temp_token'])")
SECRET2=$(curl -sf -X POST "$BASE/auth/setup-2fa" -H 'Content-Type: application/json' \
  -d "{\"temp_token\":\"$TEMP2\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['secret'])")
CODE2=$(python3 -c "import pyotp; print(pyotp.TOTP('$SECRET2').now())")
EMP_ACCESS=$(curl -sf -X POST "$BASE/auth/verify-2fa" -H 'Content-Type: application/json' \
  -d "{\"temp_token\":\"$TEMP2\",\"code\":\"$CODE2\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
ME=$(curl -sf "$BASE/auth/me" -H "Authorization: Bearer $EMP_ACCESS")
echo "$ME" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['role']=='finance'; print('OK /auth/me role=', d['role'])"

echo "== Non-admin denied =="
STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/admin/users" -H "Authorization: Bearer $EMP_ACCESS")
test "$STATUS" = "403" && echo "OK 403 for non-admin"

echo ""
echo "All live API tests passed."
