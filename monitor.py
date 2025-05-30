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
        # คำนวณ Train Loss และ Val Loss รวม
        train_loss = latest_data["train/box_loss"] + latest_data["train/cls_loss"]
        val_loss = latest_data["val/box_loss"] + latest_data["val/cls_loss"]
        # ใช้ค่า epoch ล่าสุด
        latest_train_loss = train_loss.iloc[-1]
        latest_val_loss = val_loss.iloc[-1]

        # คำนวณเปอร์เซ็นต์ Overfitting
        overfitting_pct = 0
        if latest_val_loss > latest_train_loss:
            overfitting_pct = ((latest_val_loss - latest_train_loss) / latest_train_loss) * 100 if latest_train_loss > 0 else 0

        # คำนวณเปอร์เซ็นต์ Underfitting
        underfitting_pct = 0
        if latest_train_loss > 1.0:
            underfitting_pct = ((latest_train_loss - 1.0) / latest_train_loss) * 100

        # คำนวณเปอร์เซ็นต์ Fit ที่ดี
        fit_pct = max(0, 100 - (overfitting_pct + underfitting_pct))

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
            "train_loss": train_loss.tolist(),
            "val_loss": val_loss.tolist(),
            "overfitting_pct": overfitting_pct,
            "underfitting_pct": underfitting_pct,
            "fit_pct": fit_pct
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
