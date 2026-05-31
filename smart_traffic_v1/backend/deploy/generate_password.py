#!/usr/bin/env python3
# 生成 werkzeug pbkdf2:sha256 加密的密码
from werkzeug.security import generate_password_hash

password = 'admin123'
hashed = generate_password_hash(password, method='pbkdf2:sha256')
print(f"原始密码: {password}")
print(f"加密密码: {hashed}")