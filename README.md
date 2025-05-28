# 🔧 REV_FROM_DOCKER

Edge 디바이스(Ubuntu+Docker)에서 YOLO(Object Detection) 및 SED(Sound Event Detection)를 통해 추론 결과를 FastAPI 기반으로 전송하고, 노트북(Receiver, Core 역할 / Windows + Anaconda 환경)이 이를 수신하여 Fusion 및 실시간 팝업 알림을 제공하는 Core 시스템입니다.


---

## 📦 프로젝트 구조

```
cs_pjt_receiver_win/
├── main.py                  # FastAPI 기반 수신 서버
├── alert_watcher.py         # 실시간 알림 팝업 시스템
├── requirements.txt         # 의존성 목록
├── .gitignore               # Git 무시 파일 목록
├── README.md                # 프로젝트 설명서
├── received_from_sender/    # 수신된 데이터 저장 폴더
│   ├── audio/               # 오디오 파일 저장 (.gitkeep 포함)
│   ├── video/               # 비디오 파일 저장 (.gitkeep 포함)
│   ├── image/               # 이미지 파일 저장 (.gitkeep 포함)
│   ├── metadata/            # 메타데이터 저장 (.gitkeep 포함)
│   └── alerts/              # 알림 JSON 및 이미지 저장 (.gitkeep 포함)
└── __pycache__/             # Python 캐시 파일 (자동 생성)
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


### 4. 실시간 Pop up 알림 구동

```bash
python alert_watcher.py
```

---


## 🛰️ 시스템 구성

- **Edge (Docker)**: YOLO 및 SED 결과를 FastAPI에 POST 요청으로 전송  
- **Receiver (Notebook, Core 역할)**: 해당 데이터를 `/yolo`, `/sed` API 경로로 수신하고, 저장 및 Event Fusion, 알람 Pop Up 수행


---

## 📁 예시 데이터 경로

- 영상: `received_from_sender/image/`
- 영상 Meta data : `received_from_sender/metadata/`  
- 오디오: `received_from_sender/audio/`
- Fusion 알람 : `received_from_sender/alerts/`

---

## ⚙️ 주요 기능

### 🔹 1. FastAPI 기반 수신 서버 (`main.py`)

- **역할**: Edge Device로부터 전송된 데이터 수신 및 저장
- **지원 경로**:
  - `POST /yolo` : 이미지 + 메타데이터 수신
  - `POST /sed`  : 오디오 파일 수신
- **저장 위치**: `received_from_sender/` 하위 폴더
- **기능 요약**:
  - 전송 성공 시 수신 로그 출력 (예: 저장 경로 포함)
  - 수신된 파일은 타입별로 자동 분류되어 저장

---

### 🔸 2. 실시간 알림 팝업 시스템 (`alert_watcher.py`)

- **역할**: `received_from_sender/alerts/` 폴더를 실시간 감시하여 새 이벤트 발생 시 즉시 팝업
- **동작 방식**:
  1. `_alert.json` 파일 생성 감지
  2. 동일 이름의 `.jpg` 존재 확인 후 팝업 띄움
  3. 동일 경로 중복 알림은 무시

- **표시 정보**:
  - 📅 시점 (`timestamp`) → 없으면 파일명에서 추출
  - 📍 디바이스 ID (`device_id`)
  - 🎯 감지 클래스 (`class`)
  - ⚠️ 위험 레벨 (`level`)
  - 🖼 감지 이미지 (원본 그대로 표시)

- **UI 구성**:
  - 🪟 Tkinter 팝업 창
  - `맑은 고딕` 폰트 14pt 사용
  - 이미지 하단 표시 (320x240 리사이즈 X → 원본 표시)
  - 항상 위에 떠 있는 팝업 구성 가능 (`topmost=True` 옵션으로 확장 가능)

---


✍️ 작성자
김민수 (2025)
