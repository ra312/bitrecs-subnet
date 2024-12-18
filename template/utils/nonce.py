import string
import time
from random import SystemRandom
random = SystemRandom()

def generate_nonce() -> str:
    return f"{time.time_ns()}_{''.join(random.choices(string.ascii_letters + string.digits, k=10))}"
