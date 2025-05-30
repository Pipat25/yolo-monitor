import pandas as pd
from flask import Flask, jsonify, send_file
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
csv_path = "results.csv"  # ใช้ชื่อไฟล์ใน Render
latest_data = None

class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == csv_path:
            global latest_data
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ตรวจพบการเปลี่ยนแปลงที่ {csv_path}")
            time.sleep(0.5)
            try:
                latest_data = pd.read_csv(csv_path)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] อัปเดต latest_data สำเร็จ: {len(latest_data)} epoch")
            except Exception as e:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] เกิดข้อผิดพลาดในการอ่าน CSV: {e}")

@app.route('/metrics')
def get_metrics():
    global latest_data
    if latest_data is None:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] latest_data เป็น None, พยายามอ่านไฟล์โดยตรง")
        try:
            latest_data = pd.read_csv(csv_path)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] อ่านไฟล์โดยตรงสำเร็จ: {len(latest_data)} epoch")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] เกิดข้อผิดพลาดในการอ่านไฟล์โดยตรง: {e}")
            return jsonify({"error": "ไม่มีข้อมูล"})
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ส่งข้อมูลจาก latest_data: {len(latest_data)} epoch")
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

@app.route('/')
def serve_html():
    return send_file('index.html')

if __name__ == '__main__':
    if not os.path.exists(csv_path):
        print(f"⚠️ ไม่พบไฟล์ CSV ที่ {csv_path} คาดว่าจะสร้างหลัง epoch แรก")
    
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(csv_path), recursive=False)
    observer.start()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] เริ่มการตรวจสอบไฟล์ที่ {csv_path}")
    
    try:
        if os.path.exists(csv_path):
            latest_data = pd.read_csv(csv_path)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] อ่าน CSV ครั้งแรกสำเร็จ: {len(latest_data)} epoch")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] เกิดข้อผิดพลาดในการอ่าน CSV ครั้งแรก: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)