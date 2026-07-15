# 대기 호출 솔루션 (MVP)

키오스크에서 전화번호를 등록하면 대기번호를 발송하고, 호출 앱에서 카카오톡/문자로 호출하는 PWA + FastAPI 시스템입니다.

개발·배포·MySQL 모두 **Railway** 기준입니다.

## 스택

- **API**: Python FastAPI (레포 루트)
- **DB**: Railway MySQL
- **Frontend**: React + Vite PWA (`frontend/`)
- **Platform**: Railway

## Railway 설정 (기존과 동일)

1. GitHub 레포 연결 (Root Directory 설정 불필요)
2. 프로젝트에 **MySQL** 서비스 추가
3. **API 서비스 Variables**에서 MySQL을 연결 (중요)  
   - MySQL 서비스 → Variables → 각 값을 API 서비스에 **Add Reference**  
   - 또는 API에 `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`, `MYSQLPORT`  
   - `DATABASE_URL` / `MYSQL_URL` 하나만 넣어도 됩니다 (`mysql://`도 자동 변환)
4. 변수 개수가 MySQL 관련으로 여러 개여야 합니다. **Variables가 1개면 DB 미연결**이라 Healthcheck가 실패합니다.
5. 선택 환경변수:

```env
CORS_ORIGINS=*
NOTIFY_MODE=console
DEFAULT_STORE_NAME=데모 매장
DEFAULT_STORE_SLUG=demo
```

확인:

- 앱 홈: `https://<서비스>/`
- 키오스크: `https://<서비스>/kiosk`
- 호출 앱: `https://<서비스>/staff`
- API 문서: `https://<서비스>/docs`
- 상태: `https://<서비스>/health` , `/ready`

프론트는 Docker 빌드 시 `frontend`를 묶어서 같은 서비스에서 제공합니다.

## 주요 API

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/tickets` | 대기 등록 + 안내 발송 |
| GET | `/api/tickets?store_slug=demo` | 오늘 대기열 |
| POST | `/api/tickets/{id}/call` | 호출 (`?recall=true` 재호출) |
| PATCH | `/api/tickets/{id}/status` | 완료/부재 등 |
| GET/POST | `/api/stores` | 매장 조회/생성 |

## 알림

- 기본: `NOTIFY_MODE=console` (Railway 로그 출력)
- 연동: `NOTIFY_MODE=kakao_sms` + 카카오/문자 키 (`app/adapters/notify.py`)
