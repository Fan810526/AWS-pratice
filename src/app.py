# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request
import datetime
import sys
import random

# Load environment variables and check for AWS S3 modules
HAS_S3 = False
s3_client = None
S3_BUCKET_NAME = None
AWS_REGION = 'us-east-1'

try:
    import os
    from dotenv import load_dotenv
    import boto3
    load_dotenv()
    
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Initialize boto3 S3 client using default credential chain
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    HAS_S3 = True
except Exception as e:
    # Print error but allow app to start for backward compatibility / development without S3
    print("Warning: AWS S3 initialization disabled or failed - {}".format(str(e)))

app = Flask(__name__)

# 模擬股票基礎資料
STOCKS_DATA = {
    "AAPL": {"name": "Apple Inc.", "price": 175.40, "history": [170.1, 171.3, 169.8, 172.0, 173.5, 172.9, 174.0, 173.8, 174.5, 175.4]},
    "GOOG": {"name": "Alphabet Inc.", "price": 142.10, "history": [145.0, 144.2, 143.5, 144.0, 142.8, 143.1, 141.9, 142.5, 143.0, 142.1]},
    "MSFT": {"name": "Microsoft Corp.", "price": 415.50, "history": [400.2, 402.5, 405.0, 404.1, 408.0, 410.2, 409.5, 412.0, 413.5, 415.5]},
    "TSLA": {"name": "Tesla Inc.", "price": 178.20, "history": [195.0, 192.5, 188.0, 189.5, 185.2, 186.0, 182.1, 180.5, 182.0, 178.2]},
    "NVDA": {"name": "NVIDIA Corp.", "price": 875.00, "history": [810.0, 825.0, 820.0, 835.0, 842.0, 850.0, 848.0, 860.0, 855.0, 875.0]}
}

# 模擬公司資料庫 (含上班時間時段)
COMPANIES_DATA = [
    {
        "id": 1,
        "name": u"鈦思科技 (Terasoft)",
        "shift": "afternoon",
        "hours": "13:00 - 22:00",
        "location": u"台北市信義區",
        "industry": u"軟體開發",
        "title": u"Python 後端工程師 (下午彈性班)",
        "desc": u"避開上下班通勤尖峰！適合習慣下午專注開發的夜貓子工程師，彈性下午班時段。"
    },
    {
        "id": 2,
        "name": u"微星科技 (MSI)",
        "shift": "morning",
        "hours": "09:00 - 18:00",
        "location": u"新北市中和區",
        "industry": u"硬體製造",
        "title": u"硬體測試工程師",
        "desc": u"負責微星主機板與顯示卡相容性測試與自動化指令腳本編寫。"
    },
    {
        "id": 3,
        "name": u"領航國際物流 (Navigator Logistics)",
        "shift": "afternoon",
        "hours": "14:00 - 23:00",
        "location": u"桃園市蘆竹區",
        "industry": u"物流倉儲",
        "title": u"夜間物流調度管理專員",
        "desc": u"負責下午到晚間的跨境航班物流貨件分類、進出倉調度管理，享夜班加給。"
    },
    {
        "id": 4,
        "name": u"雲端智慧科技 (Cloudfy)",
        "shift": "afternoon",
        "hours": "13:30 - 22:00",
        "location": u"台中市西屯區",
        "industry": u"雲端服務",
        "title": u"雲端架構維運工程師 (美加協作)",
        "desc": u"因應美加客戶時區協同作業，固定下午班時段，負責 AWS / GCP 雲端監控與排障。"
    },
    {
        "id": 5,
        "name": u"安防國際客服 (SecureCall)",
        "shift": "night",
        "hours": "22:00 - 07:00",
        "location": u"高雄市前鎮區",
        "industry": u"客戶服務",
        "title": u"英語客服專員 (大夜班)",
        "desc": u"處理歐美客戶緊急安全事件通報與即時線上英文對答，享優渥大夜班津貼。"
    },
    {
        "id": 6,
        "name": u"極速遊戲研發 (Speedy Games)",
        "shift": "afternoon",
        "hours": "14:00 - 22:00",
        "location": u"台北市大安區",
        "industry": u"遊戲開發",
        "title": u"Unity 遊戲前端工程師 (下午班)",
        "desc": u"適合下午到晚間開發能量最強的開發者。負責跨平台遊戲核心玩法實作與渲染優化。"
    },
    {
        "id": 7,
        "name": u"全球跨境電商 (ShopWorld)",
        "shift": "afternoon",
        "hours": "13:00 - 21:00",
        "location": u"台北市中山區",
        "industry": u"電子商務",
        "title": u"電商社群運營 / 客服專員",
        "desc": u"處理下午至晚間網購尖峰時段的客戶諮詢、社群貼文維護與訂單追蹤。"
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['GET'])
def get_info():
    python_version = sys.version
    flask_version = "1.0.4"
    return jsonify({
        "status": "success",
        "project": "Flask on Python 2.7",
        "python_version": python_version,
        "flask_version": flask_version,
        "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "port": 19191
    })

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    stocks_list = []
    for symbol, info in STOCKS_DATA.items():
        # 加上隨機微幅變動 (-1.5% 到 +1.5%)
        change_pct = random.uniform(-1.5, 1.5)
        new_price = info["price"] * (1 + change_pct / 100.0)
        
        # 更新走勢歷史 (替換最後一個為新價格)
        hist = list(info["history"])
        hist[-1] = round(new_price, 2)
        
        # 計算相較於歷史第一筆的今日漲跌幅
        daily_change = ((new_price - hist[0]) / hist[0]) * 100.0
        
        stocks_list.append({
            "symbol": symbol,
            "name": info["name"],
            "price": round(new_price, 2),
            "change_percent": round(daily_change, 2),
            "history": hist
        })
    return jsonify(stocks_list)

@app.route('/api/companies', methods=['GET'])
def get_companies():
    shift_filter = request.args.get('shift', '')
    keyword_filter = request.args.get('keyword', '')
    
    filtered = []
    for c in COMPANIES_DATA:
        # 篩選時段
        if shift_filter and c['shift'] != shift_filter:
            continue
            
        # 篩選關鍵字
        if keyword_filter:
            kw = keyword_filter.lower()
            match = (
                kw in c['name'].lower() or
                kw in c['industry'].lower() or
                kw in c['title'].lower() or
                kw in c['desc'].lower() or
                kw in c['location'].lower()
            )
            if not match:
                continue
                
        filtered.append(c)
        
    return jsonify(filtered)

@app.route('/api/s3/config', methods=['GET'])
def get_s3_config():
    aws_keys_present = False
    if HAS_S3:
        try:
            import os
            aws_keys_present = bool(os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'))
        except:
            pass
    return jsonify({
        "has_s3_module": HAS_S3,
        "bucket_name": S3_BUCKET_NAME or "",
        "region": AWS_REGION,
        "keys_configured_locally": aws_keys_present,
        "s3_client_available": s3_client is not None
    })

@app.route('/api/s3/upload', methods=['POST'])
def upload_s3_file():
    if not HAS_S3 or not s3_client:
        return jsonify({"status": "error", "message": "S3 module or client is not available"}), 500
    
    if not S3_BUCKET_NAME:
        return jsonify({"status": "error", "message": "S3_BUCKET_NAME environment variable is not configured"}), 400
        
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
        
    filename = file.filename
    logs = []
    
    # Step 1: Initialize S3 client log
    logs.append("$ Initializing boto3.client('s3', region_name='{}')...".format(AWS_REGION))
    logs.append("S3 client is initialized using AWS default credentials provider chain.")
    
    # Step 2: Upload File
    logs.append("$ s3_client.upload_fileobj(file, bucket='{}', key='{}')...".format(S3_BUCKET_NAME, filename))
    try:
        s3_client.upload_fileobj(file, S3_BUCKET_NAME, filename)
        logs.append("File uploaded successfully to S3 bucket.")
    except Exception as e:
        logs.append("Error: Upload failed - {}".format(str(e)))
        return jsonify({"status": "error", "logs": logs, "message": str(e)}), 500
        
    # Step 3: Verification (head_object)
    logs.append("$ s3_client.head_object(Bucket='{}', Key='{}')...".format(S3_BUCKET_NAME, filename))
    try:
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=filename)
        size_bytes = response.get('ContentLength', 0)
        last_mod = response.get('LastModified')
        last_mod_str = last_mod.strftime('%Y-%m-%d %H:%M:%S') if last_mod else 'unknown'
        logs.append("S3 verified: File found! ContentLength = {} bytes, LastModified = {}.".format(size_bytes, last_mod_str))
        return jsonify({
            "status": "success",
            "filename": filename,
            "logs": logs,
            "message": "File successfully uploaded and verified to exist in S3!"
        })
    except Exception as e:
        logs.append("Verification failed: head_object returned an error - {}".format(str(e)))
        return jsonify({
            "status": "warning",
            "logs": logs,
            "message": "Upload succeeded, but verification failed: {}".format(str(e))
        })

@app.route('/api/s3/list', methods=['GET'])
def list_s3_files():
    if not HAS_S3 or not s3_client or not S3_BUCKET_NAME:
        return jsonify([])
        
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, MaxKeys=50)
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                })
        # Sort by last modified descending
        files.sort(key=lambda x: x['last_modified'], reverse=True)
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("==================================================")
    print("  Starting Flask application on port 19191...     ")
    print("  Access it at http://127.0.0.1:19191/            ")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
