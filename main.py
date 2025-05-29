########################################################################
###########기존 Test 수신코드(실시간 Streaming, 잘됨)######################
########################################################################

# from fastapi import FastAPI, UploadFile, File, Request
# from fastapi.responses import HTMLResponse
# import cv2
# import numpy as np
# import base64
# import os
# import time
# from datetime import datetime
# import io
# import wave

# app = FastAPI()

# # 저장 경로 설정
# VIDEO_DIR = "received_from_sender/video"
# AUDIO_DIR = "received_from_sender/audio"
# os.makedirs(VIDEO_DIR, exist_ok=True)
# os.makedirs(AUDIO_DIR, exist_ok=True)

# @app.get("/", response_class=HTMLResponse)
# async def root():
#     return "<h2>📥 Receiver API is running on Notebook</h2>"

# @app.post("/stream")
# async def receive_stream(request: Request):
#     """
#     YOLO 추론 이미지(Base64)를 수신하는 엔드포인트
#     """
#     try:
#         data = await request.json()
#         frame_data = data.get("frame")

#         if not frame_data:
#             return {"status": "error", "message": "No frame received"}

#         img_bytes = base64.b64decode(frame_data)
#         np_arr = np.frombuffer(img_bytes, np.uint8)
#         frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#         if frame is None:
#             return {"status": "error", "message": "Invalid image frame"}

#         save_path = f"{VIDEO_DIR}/frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
#         cv2.imwrite(save_path, frame)

#         print(f"🖼️ 프레임 수신 및 저장 완료: {save_path}")
#         return {"status": "success", "path": save_path}

#     except Exception as e:
#         print("❌ 예외 발생:", e)
#         return {"status": "error", "detail": str(e)}

# @app.post("/sed")
# async def receive_sed(file: UploadFile = File(...)):
#     """
#     SED 추론 WAV 파일을 수신하는 엔드포인트
#     """
#     try:
#         data = await file.read()
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         save_path = f"{AUDIO_DIR}/audio_{timestamp}.wav"

#         with open(save_path, "wb") as f:
#             f.write(data)

#         # WAV 데이터 읽기 및 로그 출력
#         wav_buffer = io.BytesIO(data)
#         with wave.open(wav_buffer, 'rb') as wf:
#             frames = wf.readframes(wf.getnframes())
#             audio_np = np.frombuffer(frames, dtype=np.int16)
#             print(f"🎧 오디오 수신 완료: {save_path} (샘플: {audio_np[:10]})")

#         return {"status": "success", "path": save_path, "length": len(audio_np)}

#     except Exception as e:
#         print("❌ 예외 발생:", e)
#         return {"status": "error", "detail": str(e)}

########################################################################
########################################################################
########################################################################



########################################################################
###########Trigger 기반 이벤트 저장 및 pytz 적용###########################
########################################################################
############## Test 완료됨###############################################

# from fastapi import FastAPI, UploadFile, File, Request, Form
# from fastapi.responses import HTMLResponse, JSONResponse
# import cv2
# import numpy as np
# import base64
# import os
# import time
# from datetime import datetime
# import io
# import wave
# import json
# import shutil

# app = FastAPI()

# # 📁 저장 경로 설정
# BASE_DIR = "received_from_sender"
# VIDEO_DIR = os.path.join(BASE_DIR, "video")
# AUDIO_DIR = os.path.join(BASE_DIR, "audio")
# Y_IMAGE_DIR = os.path.join(BASE_DIR, "image")
# Y_META_DIR = os.path.join(BASE_DIR, "metadata")

# os.makedirs(VIDEO_DIR, exist_ok=True)
# os.makedirs(AUDIO_DIR, exist_ok=True)
# os.makedirs(Y_IMAGE_DIR, exist_ok=True)
# os.makedirs(Y_META_DIR, exist_ok=True)

# @app.get("/", response_class=HTMLResponse)
# async def root():
#     return "<h2>📥 Receiver API is running on Notebook</h2>"

# # ✅ 1. YOLO 스트리밍 수신 (Base64)
# @app.post("/stream")
# async def receive_stream(request: Request):
#     try:
#         data = await request.json()
#         frame_data = data.get("frame")

#         if not frame_data:
#             return {"status": "error", "message": "No frame received"}

#         img_bytes = base64.b64decode(frame_data)
#         np_arr = np.frombuffer(img_bytes, np.uint8)
#         frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#         if frame is None:
#             return {"status": "error", "message": "Invalid image frame"}

#         save_path = f"{VIDEO_DIR}/frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
#         cv2.imwrite(save_path, frame)

#         print(f"🖼️ 프레임 수신 및 저장 완료: {save_path}")
#         return {"status": "success", "path": save_path}

#     except Exception as e:
#         print("❌ 예외 발생 (/stream):", e)
#         return {"status": "error", "detail": str(e)}

# # ✅ 2. SED 오디오 수신
# @app.post("/sed")
# async def receive_sed(file: UploadFile = File(...)):
#     try:
#         data = await file.read()
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         save_path = f"{AUDIO_DIR}/audio_{timestamp}.wav"

#         with open(save_path, "wb") as f:
#             f.write(data)

#         wav_buffer = io.BytesIO(data)
#         with wave.open(wav_buffer, 'rb') as wf:
#             frames = wf.readframes(wf.getnframes())
#             audio_np = np.frombuffer(frames, dtype=np.int16)

#         print(f"🎧 오디오 수신 완료: {save_path} (샘플: {audio_np[:10]})")
#         return {"status": "success", "path": save_path, "length": len(audio_np)}

#     except Exception as e:
#         print("❌ 예외 발생 (/sed):", e)
#         return {"status": "error", "detail": str(e)}

# # ✅ 3. YOLO Trigger 이벤트 수신 (image + json_str)
# @app.post("/yolo")
# async def receive_yolo(json_str: str = Form(...), image: UploadFile = File(...)):
#     try:
#         # JSON 문자열 파싱
#         try:
#             data = json.loads(json_str)
#         except json.JSONDecodeError as je:
#             print("❌ JSON 파싱 오류 (/yolo):", je)
#             return JSONResponse(status_code=400, content={"error": "Invalid JSON format"})

#         event_time = data.get("event_time", datetime.now().isoformat()).replace(":", "-").replace(".", "-")
#         device_id = data.get("device_id", "unknown")
#         cls = data.get("class", "unknown")
#         level = data.get("level", "unknown")
#         filename_prefix = f"{event_time}_{device_id}_{cls}_{level}"

#         # 디바이스별 폴더 구조 생성
#         img_dir = os.path.join(Y_IMAGE_DIR, device_id)
#         meta_dir = os.path.join(Y_META_DIR, device_id)
#         os.makedirs(img_dir, exist_ok=True)
#         os.makedirs(meta_dir, exist_ok=True)

#         # 이미지 저장
#         img_file = os.path.join(img_dir, f"{filename_prefix}.jpg")
#         image.file.seek(0)
#         with open(img_file, "wb") as f:
#             shutil.copyfileobj(image.file, f)

#         # 메타데이터 저장
#         meta_file = os.path.join(meta_dir, f"{filename_prefix}.json")
#         with open(meta_file, "w") as f:
#             json.dump(data, f, indent=2)

#         print(f"✅ YOLO 이벤트 수신 완료: {img_file}, {meta_file}")
#         return {"status": "success", "image": img_file, "meta": meta_file}

#     except Exception as e:
#         print("❌ 예외 발생 (/yolo):", e)
#         return JSONResponse(status_code=500, content={"error": str(e)})


########################################################################
############ Event Fusion 및 알람 저장 기능 추가 ##########################
##### 아직까지는 Test 실패 ###########################################
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import cv2
import numpy as np
import base64
import os
import time
from datetime import datetime
import io
import wave
import json
import shutil
from collections import defaultdict

app = FastAPI()

# # 📁 저장 경로 설정
# BASE_DIR = "received_from_sender"
# #VIDEO_DIR = os.path.join(BASE_DIR, "video")       # 스트리밍 프레임 저장 경로
# AUDIO_DIR = os.path.join(BASE_DIR, "audio")       # SED 오디오 저장 경로
# Y_IMAGE_DIR = os.path.join(BASE_DIR, "image")     # YOLO 이미지 저장 경로
# Y_META_DIR = os.path.join(BASE_DIR, "metadata")   # YOLO 메타 저장 경로
# ALERT_DIR = os.path.join(BASE_DIR, "alerts")      # Fusion 후 알람 저장 경로

# #os.makedirs(VIDEO_DIR, exist_ok=True)
# os.makedirs(AUDIO_DIR, exist_ok=True)
# os.makedirs(Y_IMAGE_DIR, exist_ok=True)
# os.makedirs(Y_META_DIR, exist_ok=True)
# os.makedirs(ALERT_DIR, exist_ok=True)

# 📁 저장 경로 설정
BASE_DIR = "received_from_sender"

# YOLO
IMAGE_DIR = os.path.join(BASE_DIR, "image")
IMAGE_META_DIR = os.path.join(IMAGE_DIR, "metadata_image")

# SED
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
AUDIO_META_DIR = os.path.join(AUDIO_DIR, "meta_audio")

#ALERT_DIR
ALERT_DIR = os.path.join(BASE_DIR, "alerts")

# 폴더 생성
for folder in [IMAGE_DIR, IMAGE_META_DIR, AUDIO_DIR, AUDIO_META_DIR, ALERT_DIR]:
    os.makedirs(folder, exist_ok=True)


# 🧠 Fusion Dictionary: 슬롯 단위로 YOLO/SED 이벤트 수집
fusion_dict = defaultdict(lambda: {"yolo": [], "sed": None})

# 슬롯 단위 기준 계산 함수 (10초 단위 → 테스트용으로 3초로 조정 가능)
def get_time_slot_key(event_time: datetime) -> str:
    slot_start = event_time.replace(second=(event_time.second // 10) * 10, microsecond=0)  # ← 여기서 10 → 3 으로 수정 가능
    return slot_start.strftime("%Y%m%d_%H%M%S")

# 알람 저장 함수: 가장 높은 Level의 이벤트만 기록
def save_alert(image_path: str, metadata: dict):
    fname = os.path.basename(image_path)
    alert_img = os.path.join(ALERT_DIR, fname)
    alert_json = os.path.join(ALERT_DIR, fname.replace(".jpg", ".json"))

    # 필수 Fusion 필드 추가
    metadata["fusion_device_id"] = metadata.get("device_id", "unknown")
    metadata["fusion_level"] = metadata.get("level", -1)
    metadata["fusion_time"] = metadata.get("event_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    shutil.copy(image_path, alert_img)
    with open(alert_json, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n🚨 [ALERT 발생] Level {metadata['fusion_level']} 이상")
    print(f"📸 Image : {alert_img}")
    print(f"📄 Meta  : {alert_json}\n")

# Fusion 판단 함수: 슬롯 내 가장 높은 Level 이벤트만 알람으로 저장
def try_fusion(slot_key: str):
    entry = fusion_dict[slot_key]
    yolo_events = entry["yolo"]

    if not yolo_events:
        return  # YOLO 이벤트 없음

    # Level이 가장 높은 이벤트 선택
    top_event = max(yolo_events, key=lambda x: x["level"])

    if top_event["level"] >= 3:
        save_alert(top_event["img_path"], top_event["meta"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h2>📥 Receiver API is running on Notebook</h2>"

# #     
# @app.post("/stream")
# async def receive_stream(request: Request):
#     try:
#         data = await request.json()
#         frame_data = data.get("frame")

#         if not frame_data:
#             return {"status": "error", "message": "No frame received"}

#         img_bytes = base64.b64decode(frame_data)
#         np_arr = np.frombuffer(img_bytes, np.uint8)
#         frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#         if frame is None:
#             return {"status": "error", "message": "Invalid image frame"}

#         save_path = f"{VIDEO_DIR}/frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
#         cv2.imwrite(save_path, frame)

#         print(f"🖼️ 프레임 수신 및 저장 완료: {save_path}")
#         return {"status": "success", "path": save_path}

#     except Exception as e:
#         print("❌ 예외 발생 (/stream):", e)
#         return {"status": "error", "detail": str(e)}

# ✅ 2. SED 오디오 수신
@app.post("/sed")
# async def receive_sed(file: UploadFile = File(...)):
#     try:
#         data = await file.read()
#         timestamp = datetime.now()
#         slot_key = get_time_slot_key(timestamp)
#         fname = f"audio_{slot_key}.wav"
#         save_path = os.path.join(AUDIO_DIR, fname)

#         with open(save_path, "wb") as f:
#             f.write(data)

#         # Fusion 기록 (Level은 placeholder)
#         fusion_dict[slot_key]["sed"] = {
#             "audio_path": save_path,
#             "level": 0
#         }
#         try_fusion(slot_key)

#         print(f"🎧 오디오 수신 완료: {save_path}")
#         return {"status": "success", "path": save_path, "length": len(data)}

#     except Exception as e:
#         print("❌ 예외 발생 (/sed):", e)
#         return {"status": "error", "detail": str(e)}
async def receive_sed(json_str: str = Form(...), file: UploadFile = File(...)):
    try:
        # 1️⃣ 메타데이터 파싱
        payload = json.loads(json_str.strip())
        event_time = datetime.fromisoformat(payload.get("event_time"))
        slot_key = get_time_slot_key(event_time)

        device_id = payload.get("device_id", "unknown")
        cls = payload.get("class", "unknown")
        level_raw = str(payload.get("level", "Level0")).strip()

        # 2️⃣ level 파싱 ("Level3" → 3)
        if level_raw.lower().startswith("level") and level_raw[5:].isdigit():
            level = int(level_raw[5:])
        else:
            level = int(level_raw)

        # 3️⃣ 파일 저장 경로 정의
        now_str = datetime.now().strftime('%H%M%S%f')[:-3]
        filename_prefix = f"{slot_key}_{device_id}_{cls}_lv{level}_{now_str}"

        # 2️⃣ 디바이스별 디렉토리 생성
        audio_dir = os.path.join(AUDIO_DIR, device_id)
        meta_dir = os.path.join(AUDIO_META_DIR, device_id)
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(meta_dir, exist_ok=True)

        # 4️⃣ 저장 경로 구성
        audio_path = os.path.join(audio_dir, f"{filename_prefix}.wav")
        meta_path = os.path.join(meta_dir, f"{filename_prefix}.json")

        # 5️⃣ 오디오 파일 저장
        file.file.seek(0)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 6️⃣ 메타데이터 저장
        with open(meta_path, "w") as f:
            json.dump(payload, f, indent=2)

        # 7️⃣ Fusion 등록
        fusion_dict[slot_key]["sed"] = {
            "audio_path": audio_path,
            "level": level,
            "meta": payload
        }
        try_fusion(slot_key)

        print(f"✅ SED 이벤트 수신 완료: {audio_path}, {meta_path}")
        return {"status": "success", "audio": audio_path, "meta": meta_path}

    except Exception as e:
        print(f"❌ 예외 발생 (/sed): {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# ✅ 3. YOLO Trigger 이벤트 수신
@app.post("/yolo")
async def receive_yolo(json_str: str = Form(...), image: UploadFile = File(...)):
    #print("📩 [YOLO] /yolo 요청 수신됨")  # ✅ 이 로그 반드시 확인
    try:
        data = json.loads(json_str)
        #event_time = datetime.strptime(data["event_time"], "%Y-%m-%d %H:%M:%S")
        event_time = datetime.fromisoformat(data["event_time"])
        slot_key = get_time_slot_key(event_time)

        device_id = data.get("device_id", "unknown")
        cls = data.get("class", "unknown")
        #level = int(data.get("level", -1))
        # 🔁 level 값 문자열 대응 포함
        level_raw = str(data.get("level", "Level0")).strip()
        if level_raw.lower().startswith("level") and level_raw[5:].isdigit():
            level = int(level_raw[5:])
        else:
            level = int(level_raw)
        
        # filename_prefix = f"{slot_key}_{device_id}_{cls}_lv{level}"
        now_str = datetime.now().strftime('%H%M%S%f')[:-3]
        filename_prefix = f"{slot_key}_{device_id}_{cls}_lv{level}_{now_str}"

        img_dir = os.path.join(IMAGE_DIR, device_id)
        meta_dir = os.path.join(IMAGE_META_DIR, device_id)
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(meta_dir, exist_ok=True)

        img_file = os.path.join(img_dir, f"{filename_prefix}.jpg")
        meta_file = os.path.join(meta_dir, f"{filename_prefix}.json")

        image.file.seek(0)
        with open(img_file, "wb") as f:
            shutil.copyfileobj(image.file, f)
        with open(meta_file, "w") as f:
            json.dump(data, f, indent=2)

        # Fusion 기록
        fusion_dict[slot_key]["yolo"].append({
            "img_path": img_file,
            "level": level,
            "meta": data
        })
        try_fusion(slot_key)

        print(f"✅ YOLO 이벤트 수신 완료: {img_file}, {meta_file}")
        return {"status": "success", "image": img_file, "meta": meta_file}

    except Exception as e:
        print("❌ 예외 발생 (/yolo):", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
