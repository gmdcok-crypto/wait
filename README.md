# 대기 호출 솔루션 (MVP)

키오스크에서 전화번호를 등록하면 대기번호를 발송하고, 호출 앱에서 카카오톡/문자로 호출하는 PWA + FastAPI 시스템입니다.

## 스택

- **Backend**: Python, FastAPI, SQLAlchemy, MySQL
- **Frontend**: React + Vite PWA (`/kiosk`, `/staff`)
- **Deploy**: Railway (API + MySQL)

## 로컬 실행

### 1) MySQL + API (Docker)

```bash
docker compose up -d --build
```

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### 2) API만 로컬 Python

```bash
docker compose up -d mysql
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
uvicorn app.main:app --reload --port 8000
```

### 3) Frontend PWA

```bash
cd frontend
npm install
npm run dev
```

- 홈: http://127.0.0.1:5173
- 키오스크: http://127.0.0.1:5173/kiosk
- 호출 앱: http://127.0.0.1:5173/staff

로컬에서는 Vite 프록시가 `/api`를 백엔드로 넘깁니다.

## 주요 API

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/tickets` | 대기 등록 + 안내 발송 |
| GET | `/api/tickets?store_slug=demo` | 오늘 대기열 |
| POST | `/api/tickets/{id}/call` | 호출 (`?recall=true` 재호출) |
| PATCH | `/api/tickets/{id}/status` | 완료/부재 등 |
| GET/POST | `/api/stores` | 매장 조회/생성 |

## 알림

- 기본: `NOTIFY_MODE=console` (서버 로그/콘솔 출력)
- 연동: `NOTIFY_MODE=kakao_sms` + 카카오/문자 API 키  
  - 알림톡 실패 시 SMS 폴백 (`backend/app/adapters/notify.py`)
  - 실제 벤더 URL/페이로드는 계약사에 맞게 교체

## Railway 배포

1. GitHub 연결 후 새 프로젝트 생성
2. **MySQL** 플러그인/서비스 추가
3. API 서비스에 Root Directory를 저장소 루트로 두고 `backend/Dockerfile` 사용 (`railway.toml`)
4. 환경변수 설정:

```env
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DB
CORS_ORIGINS=https://your-frontend.example
NOTIFY_MODE=console
DEFAULT_STORE_NAME=데모 매장
DEFAULT_STORE_SLUG=demo
```

Railway MySQL 변수는 보통 `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`, `MYSQLPORT`로 제공됩니다.  
필요하면 이를 조합해 `DATABASE_URL`을 만들거나, `config.py`에서 개별 변수를 읽도록 확장하세요.

5. Frontend는 Railway Static / Cloudflare / Vercel 등에 배포하고:

```env
VITE_API_BASE=https://your-api.up.railway.app
VITE_STORE_SLUG=demo
```

## 다음 단계 (권장)

- 카카오 비즈메시지(알림톡) 템플릿 검수 + 벤더 SDK 연동
- SMS 발신번호 등록
- 매장 로그인/멀티 창구
- 호출 전광판 / 예상 대기시간
