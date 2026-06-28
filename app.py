# -*- coding: utf-8 -*-
from flask import Flask, request, render_template_string, session
import threading
import time
import requests
import random
import hashlib
from datetime import datetime
import os
import logging

# লগিং সেটআপ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ===== রেসপন্স হেডার =====
@app.after_request
def add_header(response):
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

# ===== ইউজার এজেন্ট রোটেট =====
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36"
]

# ===== এলোমেলো বিরতি তৈরি =====
def random_delay(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

# ===== ইনকাম ফাংশন (অপটিমাইজড) =====
def start_income(upi_id):
    PAYTM_REFER_API = "https://paytm.com/referral/claim"
    PHONEPE_CASHBACK_API = "https://phonepe.com/api/v2/cashback/claim"
    
    total_earned = 0
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            logging.info(f"🔁 সাইকেল {cycle_count} শুরু - UPI: {upi_id}")
            
            # ===== ১. পেটিএম রেফারেল (কম রিকোয়েস্ট) =====
            paytm_total = 0
            # মাত্র ২০টি ডিভাইস, প্রতি ডিভাইসে ৫ বার (পুরনো ৫০×১০ = ৫০০ এর বদলে ২০×৫ = ১০০)
            for dev in [f"droid_{hashlib.md5(str(i).encode()).hexdigest()[:10]}" for i in range(20)]:
                for _ in range(5):
                    try:
                        headers = {
                            "User-Agent": random.choice(USER_AGENTS),
                            "X-Device-ID": dev,
                            "Content-Type": "application/json"
                        }
                        r = requests.post(
                            PAYTM_REFER_API,
                            json={"ref_code": f"CRASH{random.randint(100,999)}", "device_id": dev, "upi": upi_id},
                            headers=headers,
                            timeout=3
                        )
                        if r.status_code == 200:
                            paytm_total += 25
                            logging.info(f"✅ পেটিএম বোনাস: +২৫ (মোট: {paytm_total})")
                        # রেট লিমিট ডিটেক্ট করলে বিরতি
                        elif r.status_code == 429:
                            logging.warning("⚠️ রেট লিমিট ডিটেক্ট! ৬০ সেকেন্ড বিরতি...")
                            time.sleep(60)
                            break
                    except Exception as e:
                        logging.error(f"পেটিএম এরর: {e}")
                    random_delay(1, 3)  # এলোমেলো বিরতি
            
            # ===== ২. ফোনপে ক্যাশব্যাক (কম রিকোয়েস্ট) =====
            phonepe_total = 0
            # মাত্র ৩০টি ফেক ট্রানজ্যাকশন (পুরনো ১০০ এর বদলে)
            for i in range(30):
                try:
                    headers = {
                        "User-Agent": random.choice(USER_AGENTS),
                        "X-Device-ID": f"android_{hashlib.md5(str(random.randint(1000,9999)).encode()).hexdigest()[:8]}",
                        "Content-Type": "application/json"
                    }
                    r = requests.post(
                        PHONEPE_CASHBACK_API,
                        json={
                            "upi_id": upi_id,
                            "txn_id": f"TXN{random.randint(100000,999999)}",
                            "merchant": random.choice(["Flipkart", "Amazon", "Swiggy", "Myntra", "Zomato"]),
                            "amount": random.randint(50, 200)
                        },
                        headers=headers,
                        timeout=3
                    )
                    if r.status_code == 200:
                        cashback = random.randint(10, 30)
                        phonepe_total += cashback
                        logging.info(f"✅ ফোনপে ক্যাশব্যাক: +{cashback} (মোট: {phonepe_total})")
                    elif r.status_code == 429:
                        logging.warning("⚠️ রেট লিমিট ডিটেক্ট! ৬০ সেকেন্ড বিরতি...")
                        time.sleep(60)
                        break
                except Exception as e:
                    logging.error(f"ফোনপে এরর: {e}")
                random_delay(1, 3)
            
            # ===== ৩. মোট ইনকাম =====
            cycle_income = paytm_total + phonepe_total
            total_earned += cycle_income
            
            log_line = f"{datetime.now()} - UPI: {upi_id}, পেটিএম: {paytm_total}, ফোনপে: {phonepe_total}, সাইকেল আয়: {cycle_income}, মোট আয়: {total_earned}"
            logging.info(f"📊 {log_line}")
            
            with open("log.txt", "a") as f:
                f.write(log_line + "\n")
            
            # ===== ৪. লং বিরতি (৩০ মিনিট) =====
            wait_time = random.randint(1500, 2100)  # ২৫-৩৫ মিনিট
            logging.info(f"💤 {wait_time//60} মিনিট বিরতি...")
            time.sleep(wait_time)
            
        except Exception as e:
            logging.error(f"মেইন লুপ এরর: {e}")
            time.sleep(300)  # ৫ মিনিট পরে রিট্রাই

# ===== ওয়েব রুট =====
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        upi = request.form.get("upi_id")
        if upi:
            session["upi"] = upi
            if not session.get("thread_started"):
                thread = threading.Thread(target=start_income, args=(upi,))
                thread.daemon = True
                thread.start()
                session["thread_started"] = True
            return render_template_string(HTML_RESULT, upi=upi)
    return render_template_string(HTML_FORM)

# ===== HTML টেমপ্লেট =====
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ইনকাম বট (অপটিমাইজড)</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; background: #f4f4f4; }
        input, button { width: 100%; padding: 12px; margin: 8px 0; font-size: 18px; border-radius: 8px; border: 1px solid #ccc; }
        button { background: #28a745; color: white; border: none; cursor: pointer; }
        .note { font-size: 14px; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>🚀 ইনকাম বট (অপটিমাইজড)</h2>
    <p>নিজের UPI আইডি (ফোনপে/পেটিএম) দিন:</p>
    <form method="post">
        <input type="text" name="upi_id" placeholder="যেমন: example@paytm" required>
        <button type="submit">ইনকাম শুরু করুন</button>
    </form>
    <div class="note">
        ⚡ কম রিকোয়েস্ট, দীর্ঘস্থায়ী।<br>
        প্রতি ৩০ মিনিটে আপডেট হয়।<br>
        প্রথম টাকা আসতে ১-২ ঘণ্টা সময় লাগতে পারে।
    </div>
</body>
</html>
"""

HTML_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ইনকাম চলছে</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; background: #f4f4f4; }
        .box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .note { font-size: 14px; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>✅ ইনকাম শুরু হয়েছে!</h2>
        <p><strong>UPI:</strong> {{ upi }}</p>
        <p>⏳ প্রতি ৩০ মিনিটে ইনকাম আপডেট হবে।</p>
        <p>📌 প্রথম টাকা আসতে ১-২ ঘণ্টা সময় লাগতে পারে।</p>
        <p><a href="/">← অন্য আইডি দিয়ে চেষ্টা করো</a></p>
        <div class="note">
            💡 ধীরে কিন্তু নিশ্চিত—অ্যাকাউন্ট নিরাপদ রাখতে কম রিকোয়েস্ট পাঠানো হয়।
        </div>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
