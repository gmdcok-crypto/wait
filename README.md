# 대기 호출 솔루션 (MVP)

키오스크에서 전화번호를 등록하면 대기번호를 발송하고, 호출 앱에서 카카오톡/문자로 호출하는 PWA + FastAPI 시스템입니다.

개발·배포·MySQL 모두 **Railway** 기준으로 구성합니다. (로컬 Docker/MySQL 불필요)

## 스택

- **Backend**: Python, FastAPI, SQLAlchemy
- **DB**: Railway MySQL
- **Frontend**: React + Vite PWA (`/kiosk`, `/staff`)
- **Platform**: Railway

## Railway 설정

### 1) 프로젝트

1. GitHub에 푸시 후 Railway 프로젝트 생성
2. **MySQL** 서비스 추가
3. **API** 서비스 추가 (이 저장소 연결)

### 2) API 서비스

- **Root Directory**: `backend`
- 시작 명령: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (`backend/railway.toml` / `Procfile`)
- MySQL 서비스 변수를 API에 **Variable Reference**로 연결  
  (`MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`, `MYSQLPORT`)
- 추가 환경변수:

```env
CORS_ORIGINS=https://<프론트도메인>
NOTIFY_MODE=console
DEFAULT_STORE_NAME=데모 매장
DEFAULT_STORE_SLUG=demo
```

`MYSQL*`가 있으면 `DATABASE_URL`을 자동 생성합니다 (`app/config.py`).

배포 후 확인:

- `https://<api>/health`
- `https://<api>/docs`

### 3) Frontend 서비스

별도 Railway 서비스(또는 Static)로 `frontend` 배포:

```env
VITE_API_BASE=https://<api-도메인>
VITE_STORE_SLUG=demo
```

빌드: `npm install && npm run build`  
출력: `dist`

- 키오스크: `/kiosk`
- 호출 앱: `/staff`

## 주요 API

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/tickets` | 대기 등록 + 안내 발송 |
| GET | `/api/tickets?store_slug=demo` | 오늘 대기열 |
| POST | `/api/tickets/{id}/call` | 호출 (`?recall=true` 재호출) |
| PATCH | `/api/tickets/{id}/status` | 완료/부재 등 |
| GET/POST | `/api/stores` | 매장 조회/생성 |

## 알림

- 기본: `NOTIFY_MODE=console` (Railway 로그에 출력)
- 연동: `NOTIFY_MODE=kakao_sms` + 카카오/문자 API 키  
  - 알림톡 실패 시 SMS 폴백 (`app/adapters/notify.py`)
  - 벤더 URL/페이로드는 계약사에 맞게 교체

## 다음 단계 (권장)

- 카카오 비즈메시지(알림톡) 템플릿 검수 + 벤더 연동
- SMS 발신번호 등록
- 매장 로그인/멀티 창구
- 호출 전광판 / 예상 대기시간
