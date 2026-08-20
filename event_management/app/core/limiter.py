from slowapi import Limiter
from slowapi.util import get_remote_address

# Giới hạn theo địa chỉ IP của client - dùng để chống brute-force login
limiter = Limiter(key_func=get_remote_address)
