from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash(password: str):
	return password_hash.hash(password)