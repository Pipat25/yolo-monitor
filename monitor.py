import pandas as pd
from flask import Flask, jsonify, send_file
import os

app = Flask(__name__)
csv_path = "results.csv"

@app.route('/metrics')
def get_metrics():
    try:
        # อ่านไฟล์ทุกครั้งที่มี request
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
            "mAP50_95": latest_data["metrics/mAP50-95(B)"].tolist()
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
    app.run(host='0.0.0.0', port=10000, debug=True)  # ใช้พอร์ต 10000 สำหรับ Render
