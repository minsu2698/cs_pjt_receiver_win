import os
import json
import cv2
import time
from PIL import Image, ImageTk
import tkinter as tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 정확한 경로로 변경 (cs_test/rev_from_docker/received_from_sender/alerts)
ALERT_DIR = os.path.join("received_from_sender", "alerts")
seen_files = set()  # ✅ 중복 알람 방지용

def show_alert_popup(json_path, image_path):
    try:
        with open(json_path, 'r') as f:
            meta = json.load(f)
    except Exception as e:
        print(f"❌ JSON 파싱 실패: {e}")
        return

    root = tk.Tk()
    root.title("🚨 Fusion Alert")
    root.attributes("-topmost", True)

    try:
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            raise ValueError("이미지 로딩 실패")
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil, master=root)
    except Exception as e:
        print(f"❌ 이미지 처리 실패: {e}")
        root.destroy()
        return

    # ✅ timestamp 추출 우선순위: JSON → 파일명
    timestamp = meta.get('timestamp')
    if not timestamp:
        filename = os.path.basename(json_path)
        try:
            date_str, time_str = filename.split("_")[0:2]  # ex: 20250528, 144510
            timestamp = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
        except:
            timestamp = "Unknown"

    text = f"""🟥 총격 경보 발생

📅 시점: {timestamp}
📍 디바이스: {meta.get('device_id', 'Unknown')}
🎯 클래스: {meta.get('class', 'Unknown')}
⚠️ 레벨: {meta.get('level', 'Unknown')}"""

    label = tk.Label(root, text=text, font=("맑은 고딕", 14), justify="left")
    label.pack(pady=10)

    panel = tk.Label(root, image=img_tk)
    panel.image = img_tk
    panel.pack(pady=5)

    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()



class AlertHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".json"):  # ✅ _alert.json → .json 전체 허용
            json_path = event.src_path
            if json_path in seen_files:
                return  # ✅ 중복 방지

            base = os.path.splitext(os.path.basename(json_path))[0]
            image_path = os.path.join(ALERT_DIR, base + ".jpg")

            for i in range(10):
                if os.path.exists(image_path):
                    print(f"✅ 새 알람 감지: {json_path}")
                    seen_files.add(json_path)
                    show_alert_popup(json_path, image_path)
                    break
                else:
                    print(f"⏳ 이미지 대기 중... ({i+1}/10)")
                time.sleep(0.5)

if __name__ == "__main__":
    if not os.path.exists(ALERT_DIR):
        os.makedirs(ALERT_DIR)

    observer = Observer()
    observer.schedule(AlertHandler(), path=ALERT_DIR, recursive=False)
    observer.start()

    print(f"👀 {ALERT_DIR}/ 폴더 감시 중... 새 알람 발생 시 팝업을 띄웁니다.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

