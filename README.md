# 🧠 CS_PJT Core Receiver (Windows + Anaconda 기반)

이 저장소는 YOLO 및 SED 기반 Edge 디바이스로부터 전송된 감지 데이터를 수신하고, 이를 통합 분석하여 실시간 경보를 제공하는 **Core 수신 서버**의 코드입니다.  
Windows 환경에서 Anaconda를 활용하여 FastAPI 서버를 운영하며, 수신된 데이터를 기반으로 Fusion 분석 및 팝업 알림을 제공합니다.

---

## 🧩 서비스 개요

- **FastAPI 기반 수신 서버**를 통해 Edge 디바이스로부터 감지 데이터를 수신합니다.
- 수신된 데이터는 로컬에 저장되며, 이후 Fusion 분석을 통해 경보 판단을 수행합니다.
- 경보 발생 시, **팝업 알림**을 통해 사용자에게 실시간으로 정보를 제공합니다.

---

## 📦 📂 디렉토리 구조

```
cs_pjt_receiver_win/
├── main.py                  # FastAPI 기반 수신 서버
├── alert_watcher.py         # 실시간 알림 팝업 시스템
├── requirements.txt         # 의존성 목록
├── .gitignore               # Git 무시 파일 목록
├── README.md                # 프로젝트 설명서
├── received_from_sender/    # 수신된 데이터 저장 폴더
│   ├── audio/               # 오디오 파일 저장 (.gitkeep 포함)
│   ├── image/               # 이미지 파일 저장 (.gitkeep 포함)
│   └── alerts/              # 알림 JSON 및 이미지 저장 (.gitkeep 포함)
└── __pycache__/             # Python 캐시 파일 (자동 생성)
```

---

## 🌐 네트워크 구성 및 사전 조건

FastAPI 기반 통신을 위해 다음 조건을 반드시 사전에 충족해야 합니다.

### ✅ 1. 동일 네트워크 연결

- Docker 실행용 데스크탑과 수신용 노트북은 **같은 네트워크 (예: 스마트폰 핫스팟)** 에 연결되어야 합니다.

### ✅ 2. IP 주소 확인

| 장치                  | 명령어              | 설명                           |
|----------------------|---------------------|--------------------------------|
| 🖥️ Ubuntu (Docker PC) | `ifconfig` 또는 `ip a` | Docker 호스트의 IP 주소 확인     |
| 💻 Windows (노트북)   | `ipconfig`           | IPv4 주소 확인 후 sender 코드에 반영 |

### ✅ 3. 방화벽 해제

```bash
netsh advfirewall firewall add rule name="FastAPI" dir=in action=allow protocol=TCP localport=8000
```

또는 수동으로 Windows Defender → 고급 설정 → 인바운드 규칙에서 포트 8000 허용.

### ✅ 4. Docker 컨테이너에서 외부 접근 가능해야 함

```bash
docker exec -it sender-api bash
apt update && apt install iputils-ping -y
ping <노트북_IP>
```

---

## 🛠️ 실행 단계

### 1. 수신 서버 실행 (FastAPI)

```bash
conda create -n rev_from_docker python=3.9
conda activate rev_from_docker
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

> 💡 GUI/사운드 관련 문제 발생 시:  
> `conda install pygame -c conda-forge`

---

### 2. Fusion 알림 시스템 실행 (팝업)

```bash
python alert_watcher.py
```

- `alerts/` 폴더에서 `_alert.json` + 이미지 감지 시 팝업 자동 표시
- 표시 항목: 감지 시각, 장치 ID, 감지 클래스, 경보 Level 등
- `pygame`으로 총성 등 오디오 자동 재생
- 중복 알람 방지 (`seen_files`)
- 팝업 창은 항상 최상위 유지 (`-topmost`)

---

## 🧠 Fusion Logic 요약

- YOLO 또는 SED 중 하나라도 해당 슬롯(10초) 내에 감지되면 경보 후보로 등록됩니다.
- 감지 레벨이 일정 기준을 초과하면 경보가 확정되고 알림이 발생합니다.
- 이벤트는 `received_from_sender/alerts/` 폴더에 JSON + JPG로 저장되며, 팝업은 이 경로를 감시하여 자동 트리거됩니다.

---

## 📁 수신 데이터 저장 구조

```
received_from_sender/
├── audio/
├── image/
├── alerts/
```

각 디렉토리는 디바이스 ID 기준 자동 정렬

---

## 🧪 테스트 팁

- Swagger UI: `http://<노트북_IP>:8000/docs`
- `/yolo`, `/receive_audio` 경로 테스트 가능

---

## 📄 기타 참고 사항

- `.gitignore`: 수신 데이터는 Git에 포함 안됨
- `.gitkeep`: 폴더 구조 유지용
- Edge 송신기 코드: 👉 https://github.com/minsu2698/cs_pjt_docker

---

## ✍️ 작성자

- GitHub: [@minsu2698](https://github.com/minsu2698)
- 프로젝트 담당자: 김민수