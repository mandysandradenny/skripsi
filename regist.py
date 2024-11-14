from db import insert_users
import hashlib

def hashed(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username:str, password:str):
    password_hashed = hashed(password)
    insert_users(username, password_hashed)

# Untuk mendaftarkan user
# register_user('admin', 'admin')