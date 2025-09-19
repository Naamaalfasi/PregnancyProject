import jwt
from datetime import datetime, timedelta

SECRET_KEY = "jRT4r3BOvTAb6_S5wUwjn36c9FjrHKqpq-n0cbxpvbMFVgcpcXakO1KQiNLAdxaiCpRcRof_NFSbyiYF3yjPcg"  # החלף למשהו חזק ושמור בסוד!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # יום

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
