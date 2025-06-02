import os
import time
import requests

SOURCE_URL = "https://52b2-223-24-159-27.ngrok-free.app/results.csv"  # แทนด้วย URL จาก ngrok
FILE_PATH = "results.csv"


def update_csv():
    try:
        response = requests.get(SOURCE_URL, timeout=5)
        if response.status_code == 200:
            with open(FILE_PATH, 'wb') as f:
                f.write(response.content)
            print(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] อัปเดต results.csv สำเร็จ"
            )
        else:
            print(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] เกิดข้อผิดพลาด: {response.status_code}"
            )
    except Exception as e:
        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] เกิดข้อผิดพลาดในการดึงไฟล์: {e}"
        )


if __name__ == "__main__":
    update_csv()
