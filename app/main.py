import time
from fastapi import FastAPI
from pydantic import BaseModel
import json
from pathlib import Path
from datetime import datetime

app = FastAPI()

DB_FILE = Path("data/otp_store.json")
MEMORY_DB = {}
@app.on_event("startup")
def load_db():
    global MEMORY_DB

    if DB_FILE.exists():
        with open(DB_FILE, "r") as f:
            MEMORY_DB = json.load(f)
    else:
        MEMORY_DB = {}

@app.on_event("shutdown")
def save_db():
    DB_FILE.parent.mkdir(exist_ok=True)

    with open(DB_FILE, "w") as f:
        json.dump(MEMORY_DB, f)

@app.get("/")
def read_root():
    return {"Hello": "Macarious Version 1.0.3"}

class OTPRequest(BaseModel):
    email: str

class OTPValidateRequest(BaseModel):
    email: str
    otp: str

class OTPManager:
    def can_request_otp(email):
        if not MEMORY_DB.get(email):
            print(f"No OTP found for {email}.")
            return True
        
        now = time.time()
        expires_at = MEMORY_DB[email]["expires_at"]

        print(f"Now      : {datetime.fromtimestamp(now)}")
        print(f"Expires  : {datetime.fromtimestamp(expires_at)}")
        print(f"Expired? : {now >= expires_at}")
        return now >= expires_at
    
    def create(email, otp):        
        MEMORY_DB[email] = {
            "otp": otp,
            "expires_at": time.time() + 30  # OTP expires in 0.5 minutes
        }
        return {"status": "success", "message": "OTP created successfully, expires in 0.5 minutes"}

    def validate(email, otp):
        otp_data = MEMORY_DB.get(email)
        if otp_data and otp_data["otp"] == otp:
            if time.time() < otp_data["expires_at"]:
                print(f"OTP for {email} is valid and not expired.")
                return True
            else:
                print(f"OTP for {email} has expired.")
                OTPManager.delete(email)
                return False
        else:
            print(f"Invalid OTP for {email}.")
            return False

    def delete(email):
        MEMORY_DB.pop(email, None)

def generate_otp():
    import random
    return str(random.randint(100000, 999999))

def send_email(email, otp):
    # Placeholder for sending email logic
    print(f"Sending OTP {otp} to email {email}")

@app.post("/otprequest")
def request_otp(request: OTPRequest):
    if OTPManager.can_request_otp(request.email):
        otp = generate_otp()
        send_email(request.email, otp)
        OTPManager.create(request.email, otp)
        return {
            "status": "success",
            "message": "OTP sent to email"
        }
    else:
        return {
            "status": "error",
            "message": "Too many requests or OTP still valid"
        }

@app.post("/otpvalidate")
def validate_otp(request: OTPValidateRequest):
    if OTPManager.validate(request.email, request.otp):
        OTPManager.delete(request.email)
        return {"status": "success", "message": "OTP is valid"}
    else:
        return {"status": "error", "message": "Invalid OTP or OTP has expired or does not exist"}
    
@app.get("/allotps/")
def get_all_otps():
    return MEMORY_DB