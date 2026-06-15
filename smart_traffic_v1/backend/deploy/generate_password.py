#!/usr/bin/env python3
import sys
from werkzeug.security import generate_password_hash

if len(sys.argv) < 2:
    print('用法: python generate_password.py <密码>')
    print('示例: python generate_password.py MySecurePassword123')
    sys.exit(1)

password = sys.argv[1]
hashed = generate_password_hash(password, method='pbkdf2:sha256')
print(f'原始密码: {password}')
print(f'加密密码: {hashed}')