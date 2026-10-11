# 식대 청구 자동화 프로젝트 (Absence Expense Generator)

[English](README.md) | [한국어](README.ko.md)

회사 구내식당 영수증과 근무 기록을 자동으로 비교하여 식대 청구 대상 여부를 검증하고, 월별 비용 보고서를 생성하는 Python 자동화 프로젝트입니다.

## 프로젝트 소개

매월 식대 청구를 준비할 때 근무 시간 확인, 영수증 정리, 금액 계산, 증빙 자료 작성 등의 반복 작업이 발생합니다.

이 프로젝트는 출퇴근 기록, 영수증 이미지, OCR 기반 데이터 추출, PostgreSQL 데이터베이스를 연동하여 이러한 작업을 자동화합니다.

## 주요 기능

- **근무 기록 연동** — absence.io API에서 근무 기록을 가져옵니다.
- **영수증 처리** — Google Drive에서 영수증 이미지를 다운로드합니다.
- **OCR 데이터 추출** — Tesseract OCR을 사용해 영수증 날짜와 결제 금액을 추출합니다.
- **청구 자격 검증** — 영수증 날짜와 근무 기록 날짜가 일치하고, 기록된 근무 시간이 8시간 이상인 경우에만 청구 대상으로 처리합니다.
- **식대 계산** — 청구 대상 영수증의 실제 결제 금액을 기준으로 금액을 계산합니다.
- **PDF 생성** — 청구 대상 영수증을 날짜순으로 정렬하여 PDF를 생성합니다.
- **데이터베이스 저장** — 근무 기록, 영수증, 비용 정보를 PostgreSQL에 저장합니다.
- **자동 테스트** — pytest로 주요 기능을 검증합니다.
- **CI 자동화** — GitHub Actions로 테스트 실행과 Docker 이미지 빌드를 검증합니다.

## 기술 스택

| 분류 | 기술 |
|---|---|
| 프로그래밍 언어 | Python |
| OCR | Tesseract OCR, pytesseract |
| 이미지 처리 | Pillow |
| 근무 기록 API | absence.io API |
| 파일 저장소 | Google Drive API |
| 데이터베이스 | PostgreSQL |
| 테스트 | pytest |
| 컨테이너 | Docker, Docker Compose |
| CI | GitHub Actions |

## 프로젝트 구조

```text
absence-expense-generator/
├── absence_io/       # absence.io API 연동
├── batch/            # 월별 식대 청구 워크플로
├── config/           # 애플리케이션 설정
├── database/         # DB 연결, 스키마, 저장소
├── expense/          # 식대 계산 및 보고서 데이터 변환
├── receipts/         # 영수증 다운로드, OCR, 처리, PDF 생성
├── tests/             # 자동화 테스트
├── utils/             # 유틸리티 함수
├── output/            # 생성된 보고서
├── main.py            # 프로그램 진입점
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── README.ko.md
```

## 처리 과정

1. 대상 월의 근무 기록을 조회합니다.
2. 날짜별 근무 시간을 정리합니다.
3. Google Drive에서 영수증 이미지를 가져옵니다.
4. OCR로 영수증 날짜와 결제 금액을 추출합니다.
5. 영수증 날짜와 근무 기록 날짜를 비교합니다.
6. 일치하는 근무 기록이 없는 영수증, 대상 월이 아닌 영수증, 근무 시간이 8시간 미만인 날짜의 영수증을 제외합니다.
7. 청구 대상 근무 기록, 영수증, 비용 정보를 PostgreSQL에 저장합니다.
8. 청구 대상 영수증을 날짜순으로 정렬하여 PDF 보고서를 생성합니다.

## 실행 환경

- Python 3.12 이상
- Tesseract OCR
- PostgreSQL
- Google Drive API 인증 정보
- absence.io API 인증 정보

Docker와 Docker Compose를 사용해 컨테이너 환경에서 실행할 수도 있습니다.

## 환경 설정

프로젝트 루트에 `.env` 파일을 만들고 필요한 환경 변수를 설정합니다.

필요한 설정 항목은 `.env.example` 파일을 참고하세요.

`.env`, `credentials.json`, `token.json`과 같은 인증 정보가 포함된 파일은 Git에 커밋하지 마세요.

전체 워크플로를 실행하려면 Google Drive API와 absence.io API의 인증 설정이 필요합니다.

## 로컬 실행

가상 환경을 만들고 활성화한 다음 의존성을 설치합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Tesseract OCR을 설치하고 필요한 API 인증 정보를 설정합니다.

월별 식대 청구 프로그램을 실행합니다.

```powershell
python main.py
```

## Docker Compose 실행

PostgreSQL 서비스를 시작합니다.

```powershell
docker compose up -d db
```

실행 상태를 확인합니다.

```powershell
docker compose ps
```

전체 애플리케이션을 실행하기 전에 환경 변수와 API 인증 정보가 올바르게 설정되어 있는지 확인하세요.

## 테스트

전체 테스트를 실행합니다.

```powershell
python -m pytest -v
```

테스트는 식대 계산, 영수증 파싱, 영수증 처리, 데이터베이스 저장소, 근무 시간 변환 기능을 검증합니다.

## 지속적 통합 (CI)

`main` 브랜치에 푸시하거나 해당 브랜치를 대상으로 Pull Request를 생성하면 GitHub Actions가 다음 작업을 실행합니다.

- Python 자동 테스트
- Docker 이미지 빌드 검증

워크플로 설정 파일:

`.github/workflows/ci.yml`

## 향후 개선 사항

- 다양한 영수증 형식에 대한 OCR 날짜 추출 개선
- 오류 처리 및 구조화된 로깅 강화
- 예외 상황에 대한 자동 테스트 확장
- 배포 및 운영 문서 개선

## 라이선스

아직 별도의 라이선스가 지정되지 않았습니다.