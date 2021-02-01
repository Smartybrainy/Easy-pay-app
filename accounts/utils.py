import uuid
import random


def generate_ref_code():
    code = str(uuid.uuid4()).replace("-", "")[:8]
    return code


def generate_otp_number():
    otp = str(random.randint(1000, 9999))
    return otp