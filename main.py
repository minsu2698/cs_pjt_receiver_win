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

app = FastAPI()

# 📁 저장 경로 설정
BASE_DIR = "received_from_sender"
VIDEO_DIR = os.path.join(BASE_DIR, "video")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
Y_IMAGE_DIR = os.path.join(BASE_DIR, "image")
Y_META_DIR = os.path.join(BASE_DIR, "metadata")

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(Y_IMAGE_DIR, exist_ok=True)
os.makedirs(Y_META_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h2>📥 Receiver API is running on Notebook</h2>"

# ✅ 1. YOLO 스트리밍 수신 (Base64)
@app.post("/stream")
async def receive_stream(request: Request):
    try:
        data = await request.json()
        frame_data = data.get("frame")

        if not frame_data:
            return {"status": "error", "message": "No frame received"}

        img_bytes = base64.b64decode(frame_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return {"status": "error", "message": "Invalid image frame"}

        save_path = f"{VIDEO_DIR}/frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(save_path, frame)

        print(f"🖼️ 프레임 수신 및 저장 완료: {save_path}")
        return {"status": "success", "path": save_path}

    except Exception as e:
        print("❌ 예외 발생 (/stream):", e)
        return {"status": "error", "detail": str(e)}

# ✅ 2. SED 오디오 수신
@app.post("/sed")
async def receive_sed(file: UploadFile = File(...)):
    try:
        data = await file.read()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = f"{AUDIO_DIR}/audio_{timestamp}.wav"

        with open(save_path, "wb") as f:
            f.write(data)

        wav_buffer = io.BytesIO(data)
        with wave.open(wav_buffer, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            audio_np = np.frombuffer(frames, dtype=np.int16)

        print(f"🎧 오디오 수신 완료: {save_path} (샘플: {audio_np[:10]})")
        return {"status": "success", "path": save_path, "length": len(audio_np)}

    except Exception as e:
        print("❌ 예외 발생 (/sed):", e)
        return {"status": "error", "detail": str(e)}

# ✅ 3. YOLO Trigger 이벤트 수신 (image + json_str)
@app.post("/yolo")
async def receive_yolo(json_str: str = Form(...), image: UploadFile = File(...)):
    try:
        # JSON 문자열 파싱
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as je:
            print("❌ JSON 파싱 오류 (/yolo):", je)
            return JSONResponse(status_code=400, content={"error": "Invalid JSON format"})

        event_time = data.get("event_time", datetime.now().isoformat()).replace(":", "-").replace(".", "-")
        device_id = data.get("device_id", "unknown")
        cls = data.get("class", "unknown")
        level = data.get("level", "unknown")
        filename_prefix = f"{event_time}_{device_id}_{cls}_{level}"

        # 디바이스별 폴더 구조 생성
        img_dir = os.path.join(Y_IMAGE_DIR, device_id)
        meta_dir = os.path.join(Y_META_DIR, device_id)
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(meta_dir, exist_ok=True)

        # 이미지 저장
        img_file = os.path.join(img_dir, f"{filename_prefix}.jpg")
        image.file.seek(0)
        with open(img_file, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # 메타데이터 저장
        meta_file = os.path.join(meta_dir, f"{filename_prefix}.json")
        with open(meta_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ YOLO 이벤트 수신 완료: {img_file}, {meta_file}")
        return {"status": "success", "image": img_file, "meta": meta_file}

    except Exception as e:
        print("❌ 예외 발생 (/yolo):", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
