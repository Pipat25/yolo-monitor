import pandas as pd
from flask import Flask, jsonify, send_file
import os
import threading
import subprocess
import time

app = Flask(__name__)
csv_path = "results.csv"
latest_data = None

def update_csv_periodically():
    while True:
        try:
            subprocess.run(["python", "update_csv.py"])
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] อัปเดต results.csv สำเร็จ")
            time.sleep(5)
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] เกิดข้อผิดพลาด: {e}")

@app.route('/metrics')
def get_metrics():
    global latest_data
    try:
        latest_data = pd.read_csv(csv_path)
        response = jsonify({
            "epochs": latest_data["epoch"].tolist(),
            "train_box_loss": latest_data["train/box_loss"].tolist(),
            "val_box_loss": latest_data["val/box_loss"].tolist(),
            "train_cls_loss": latest_data["train/cls_loss"].tolist(),
            "val_cls_loss": latest_data["val/cls_loss"].tolist(),
            "precision": latest_data["metrics/precision(B)"].tolist(),
            "recall": latest_data["metrics/recall(B)"].tolist(),
            "mAP50": latest_data["metrics/mAP50(B)"].tolist(),
            "mAP50_95": latest_data["metrics/mAP50-95(B)"].tolist(),
            "train_dfl_loss": latest_data.get("train/dfl_loss", pd.Series([])).tolist(),
            "val_dfl_loss": latest_data.get("val/dfl_loss", pd.Series([])).tolist(),
            # เพิ่มข้อมูลสำหรับกราฟ overfitting/underfitting
            "train_loss": (latest_data["train/box_loss"] + latest_data["train/cls_loss"]).tolist(),  # รวม Train Loss
            "val_loss": (latest_data["val/box_loss"] + latest_data["val/cls_loss"]).tolist()         # รวม Val Loss
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except Exception as e:
        return jsonify({"error": f"เกิดข้อผิดพลาด: {str(e)}"}), 500

@app.route('/')
def serve_html():
    return send_file('index.html')

if __name__ == '__main__':
    if not os.path.exists(csv_path):
        print(f"⚠️ ไม่พบไฟล์ CSV ที่ {csv_path}")
    threading.Thread(target=update_csv_periodically, daemon=True).start()
    app.run(host='0.0.0.0', port=10000, debug=True)
