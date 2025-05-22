# 🔧 rev_from_docker

Edge 디바이스(Ubuntu+Docker)에서 YOLO(Object Detection) 및 SED(Sound Event Detection)를 통해 추론 결과를 FastAPI 기반으로 전송하고, 노트북(Receiver, Core 역할 / Windows + Anaconda 환경)이 이를 수신하여 저장/처리하는 시스템입니다.


---

## 📦 프로젝트 구조

```
rev_from_docker/
├── main.py                  # FastAPI 수신 서버 (YOLO + SED 결과 처리)
├── requirements.txt         # Conda 환경용 패키지 목록
├── .gitignore               # Git 추적 제외 파일 목록
└── received_from_sender/
    ├── video/               # 수신된 영상 프레임 저장
    └── audio/               # 수신된 오디오 WAV 저장
```

---

## 🚀 실행 방법 (📦 Windows + Anaconda 기반 수신 서버 구성)

### 0. 네트워크 구성 및 사전 조건
FastAPI 기반 통신을 위해 다음 조건을 사전에 만족해야 합니다.

✅ 1. 동일 네트워크 연결
두 장치(Edge PC와 Notebook)는 동일 네트워크에 있어야 합니다.

가장 쉬운 방법: 스마트폰 핫스팟 공유

데스크탑(Docker 실행용)과 노트북(Receiver)를 핫스팟에 모두 연결

✅ 2. IP 확인
각 장치의 IP 주소를 확인하여 Sender 코드에 정확히 기입해야 합니다.

장치	명령어	설명
Docker PC (Ubuntu)	ifconfig 또는 ip a	실제 호스트의 IP를 확인합니다
노트북 (Windows)	ipconfig	IPv4 주소 확인 후 sender 코드에 넣습니다

✅ 3. 방화벽 해제 (Windows)
노트북에서 8000번 포트 열림 확인 (Receiver)
FastAPI는 기본적으로 8000 포트를 사용하므로 아래 설정을 반드시 확인하세요.

명령 프롬프트(CMD)를 관리자 권한으로 실행

아래 명령어 입력:

```bash
netsh advfirewall firewall add rule name="FastAPI" dir=in action=allow protocol=TCP localport=8000
```
또는 Windows Defender 방화벽 → 고급 설정 → 인바운드 규칙에서 수동 설정.

✅ 4. Docker 컨테이너 내부에서 외부 IP 접근 가능해야 함
도커 컨테이너 내부에서도 노트북의 IP로 접근이 가능해야 하며,
ping 테스트는 아래처럼 확인 가능합니다:


```bash
docker exec -it sender-api 
apt update && apt install iputils-ping -y  # ping 없을 경우
ping <노트북_IP>
```

위 항목들을 모두 만족해야 FastAPI 통신이 성공적으로 수행됩니다.


### 1. Conda 환경 생성

```bash
conda create -n rev_from_docker python=3.9
conda activate rev_from_docker
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. FastAPI 서버 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🛰️ 시스템 구성

- **Edge (Docker)**: YOLO 및 SED 결과를 FastAPI에 POST 요청으로 전송  
- **Receiver (Notebook, Core 역할)**: 해당 데이터를 `/stream`, `/sed` API 경로로 수신하고, 저장 및 후속 처리를 담당


---

## 📁 예시 데이터 경로

- 영상: `received_from_sender/video/`  
- 오디오: `received_from_sender/audio/`

---

✍️ 작성자
김민수 (2025)