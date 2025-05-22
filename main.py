from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
import cv2
import numpy as np
import base64
import os
import time
from datetime import datetime
import io
import wave

app = FastAPI()

# 저장 경로 설정
VIDEO_DIR = "received_from_sender/video"
AUDIO_DIR = "received_from_sender/audio"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h2>📥 Receiver API is running on Notebook</h2>"

@app.post("/stream")
async def receive_stream(request: Request):
    """
    YOLO 추론 이미지(Base64)를 수신하는 엔드포인트
    """
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
        print("❌ 예외 발생:", e)
        return {"status": "error", "detail": str(e)}

@app.post("/sed")
async def receive_sed(file: UploadFile = File(...)):
    """
    SED 추론 WAV 파일을 수신하는 엔드포인트
    """
    try:
        data = await file.read()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = f"{AUDIO_DIR}/audio_{timestamp}.wav"

        with open(save_path, "wb") as f:
            f.write(data)

        # WAV 데이터 읽기 및 로그 출력
        wav_buffer = io.BytesIO(data)
        with wave.open(wav_buffer, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            audio_np = np.frombuffer(frames, dtype=np.int16)
            print(f"🎧 오디오 수신 완료: {save_path} (샘플: {audio_np[:10]})")

        return {"status": "success", "path": save_path, "length": len(audio_np)}

    except Exception as e:
        print("❌ 예외 발생:", e)
        return {"status": "error", "detail": str(e)}
