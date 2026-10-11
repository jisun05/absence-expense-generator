# 식대 청구 자동화 프로젝트 (Absence Expense Generator)

[English](README.md) | [한국어](README.ko.md)

회사 구내식당 영수증과 근무 기록을 자동으로 비교하여 식대 청구 대상 여부를 검증하고, 월별 비용 보고서를 생성하는 Python 자동화 프로젝트입니다.

이 프로젝트는 반복적인 식대 청구 업무를 자동화하여 수작업을 줄이고, 근무 기록과 영수증을 기반으로 청구 금액을 계산하는 것을 목표로 합니다.

## 프로젝트 소개

매월 식대 청구를 준비할 때는 근무 시간 확인, 영수증 정리, 금액 계산, 증빙 자료 작성 등의 반복 작업이 발생합니다.

이 프로젝트는 absence.io API, Google Drive API, OCR, PostgreSQL 및 Excel/PDF 보고서 생성을 연동하여 이러한 작업을 자동화합니다.

근무 기록과 영수증을 날짜별로 비교하고, 프로젝트의 청구 기준을 충족하는 데이터만 처리하여 월별 식대 청구 자료를 생성합니다.

## 주요 기능

- **근무 기록 연동**
  - absence.io API에서 근무 기록을 가져옵니다.
  - 날짜별 근무 시간을 정리합니다.
  - 출근 시간과 퇴근 시간을 기준으로 근무 시간을 계산합니다.

- **영수증 처리**
  - Google Drive에서 영수증 이미지를 가져옵니다.
  - OCR 처리에 필요한 영수증 데이터를 추출합니다.
  - 영수증 날짜와 결제 금액을 분석합니다.

- **OCR 데이터 추출**
  - Tesseract OCR을 사용하여 영수증 이미지에서 텍스트를 추출합니다.
  - 추출한 텍스트에서 날짜와 결제 금액을 파싱합니다.

- **청구 자격 검증**
  - 기록된 근무 시간이 8시간 이상인 날짜를 확인합니다.
  - 근무 기록과 영수증의 날짜를 비교합니다.
  - 프로젝트의 청구 기준에 맞지 않는 데이터를 제외합니다.

- **식대 계산**
  - 청구 대상 근무 기록과 영수증을 매칭합니다.
  - 청구 대상 영수증의 실제 결제 금액을 기준으로 비용을 계산합니다.
  - 청구 대상이 아닌 근무 기록과 영수증은 비용 계산에서 제외합니다.

- **Excel 보고서 생성**
  - Excel 템플릿을 기반으로 월별 식대 청구 보고서를 생성합니다.
  - 일별 비용과 최종 청구 금액을 계산합니다.
  - 기존 템플릿의 서식과 수식을 유지합니다.
  - 최대 25일의 근무 기록을 처리할 수 있습니다.

- **PDF 생성**
  - 청구 대상 영수증을 날짜순으로 정렬합니다.
  - 영수증 이미지가 포함된 PDF 보고서를 생성합니다.

- **데이터베이스 저장**
  - PostgreSQL에 근무 기록, 영수증 및 비용 정보를 저장합니다.

- **자동 테스트**
  - pytest를 사용하여 주요 기능을 검증합니다.
  - 식대 계산, 영수증 파싱, 데이터 변환 및 데이터베이스 저장소 등을 테스트합니다.

- **CI 자동화**
  - GitHub Actions를 사용하여 자동 테스트를 실행합니다.
  - Docker 이미지 빌드를 검증합니다.

## 기술 스택

| 분류 | 기술 |
|---|---|
| 프로그래밍 언어 | Python |
| 근무 기록 API | absence.io API |
| 인증 | Google OAuth 2.0 |
| 파일 저장소 | Google Drive API |
| OCR | Tesseract OCR, pytesseract |
| 이미지 처리 | Pillow |
| Excel 보고서 | openpyxl |
| PDF 보고서 | Python PDF 생성 라이브러리 |
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
├── database/         # 데이터베이스 연결, 스키마, 저장소
├── expense/          # 식대 계산 및 Excel 보고서 생성
├── receipts/         # 영수증 다운로드, OCR, 파싱, PDF 생성
├── templates/        # Excel 보고서 템플릿
├── tests/            # 자동화 테스트
├── utils/            # 유틸리티 함수
├── output/           # 생성된 보고서
├── main.py           # 프로그램 진입점
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── README.ko.md
```

## 처리 과정

1. 대상 월의 근무 기록을 absence.io API에서 조회합니다.
2. 날짜별 근무 시간을 정리합니다.
3. Google Drive에서 영수증 이미지를 가져옵니다.
4. OCR을 사용하여 영수증 날짜와 결제 금액을 추출합니다.
5. 영수증 날짜와 근무 기록 날짜를 비교합니다.
6. 근무 시간이 8시간 미만인 날짜의 영수증과 청구 기준을 충족하지 않는 데이터를 제외합니다.
7. 청구 대상 근무 기록, 영수증 및 비용 정보를 PostgreSQL에 저장합니다.
8. Excel 템플릿을 기반으로 월별 식대 청구 보고서를 생성합니다.
9. 청구 대상 영수증을 날짜순으로 정렬하여 PDF 보고서를 생성합니다.

## 식대 청구 기준

프로젝트에서는 다음 조건을 기준으로 식대 청구 대상을 판단합니다.

1. 기록된 근무 시간이 8시간 이상이어야 합니다.
2. 근무 기록과 영수증의 날짜가 일치해야 합니다.
3. 영수증이 프로젝트의 청구 대상 기준을 충족해야 합니다.

다음 데이터는 청구 대상에서 제외됩니다.

- 청구 기준을 충족하지 못한 근무 기록
- 해당 날짜의 영수증이 없는 근무 기록
- 청구 대상 근무 기록과 매칭되지 않는 영수증
- 프로젝트의 영수증 처리 기준을 충족하지 않는 데이터

최종 청구 금액은 청구 대상 영수증의 실제 결제 금액을 기준으로 계산합니다.

## 실행 환경

프로젝트를 실행하려면 다음 환경과 인증 정보가 필요합니다.

- Python 3.13.2
- Tesseract OCR
- PostgreSQL 16
- Google Drive API 및 OAuth 인증 정보
- absence.io API 인증 정보
- Docker Desktop 및 Docker Compose (Docker를 사용하는 경우)

Python 버전과 라이브러리 요구 사항은 프로젝트의 설정 파일을 기준으로 확인해야 합니다.

## 환경 설정

### 1. 저장소 복제

```bash
git clone https://github.com/jisun05/absence-expense-generator.git
cd absence-expense-generator
```

### 2. 가상 환경 생성

```powershell
python -m venv .venv
```

가상 환경을 활성화합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 의존성 설치

```powershell
python -m pip install -r requirements.txt
```

### 4. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.

필요한 설정 항목은 `.env.example` 파일을 참고하세요.

실제 API 인증 정보와 데이터베이스 접속 정보는 로컬 환경에 설정해야 합니다.

### 5. Google Drive 인증 설정

Google Drive API를 사용하기 위해 Google OAuth 인증을 설정합니다.

애플리케이션에서 요구하는 위치에 `credentials.json`을 배치하고, 필요한 경우 OAuth 인증 과정을 통해 `token.json`을 생성합니다.

인증 파일에는 민감한 정보가 포함될 수 있으므로 공개 저장소에 커밋하지 마세요.

### 6. Tesseract OCR 설정

Tesseract OCR을 설치하고 애플리케이션에서 실행할 수 있도록 설정합니다.

Windows에서 기본 설치 경로를 사용하는 경우 다음 경로를 사용할 수 있습니다.

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

다른 경로에 설치했다면 실제 설치 경로에 맞게 설정해야 합니다.

### 7. 데이터베이스 설정

PostgreSQL을 실행하고 `.env`에 설정한 데이터베이스 접속 정보가 올바른지 확인합니다.

Docker Compose를 사용하는 경우 다음 명령으로 서비스를 시작할 수 있습니다.

```powershell
docker compose up -d db
```

서비스 상태를 확인합니다.

```powershell
docker compose ps
```

## 로컬 실행

환경 변수, API 인증 정보 및 데이터베이스 설정을 완료한 뒤 다음 명령으로 애플리케이션을 실행합니다.

```powershell
python main.py
```

프로그램은 월별 식대 청구 워크플로를 실행하여 근무 기록 조회, 영수증 처리, 비용 계산 및 보고서 생성을 수행합니다.

생성된 보고서는 프로젝트에서 설정한 출력 디렉터리에 저장됩니다.

## Excel 템플릿

Excel 보고서는 템플릿을 기반으로 생성됩니다.

공개용 예제 템플릿은 다음 경로에 있습니다.

`templates/travel_expense_template_public.xlsx`

공개용 템플릿은 보고서 생성 기능을 확인하기 위한 예제입니다.

실제 회사 정보, 개인정보 또는 기밀 데이터가 포함된 원본 템플릿은 공개 저장소에 커밋하지 마세요.

## Docker Compose 실행

Docker Compose를 사용하여 PostgreSQL 데이터베이스와 애플리케이션을 컨테이너 환경에서 실행할 수 있습니다.

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 데이터베이스 연결에 필요한 환경 변수를 설정합니다.

필요한 변수는 `docker-compose.yml`과 애플리케이션 설정을 확인하세요.

실제 비밀번호와 인증 정보가 포함된 `.env` 파일은 GitHub에 커밋하지 마세요.

### 2. PostgreSQL 실행

데이터베이스 서비스만 실행하려면 다음 명령을 사용합니다.

```powershell
docker compose up -d db
```

컨테이너 상태를 확인합니다.

```powershell
docker compose ps
```

### 3. 전체 애플리케이션 실행

PostgreSQL과 애플리케이션을 함께 실행하려면 다음 명령을 사용합니다.

```powershell
docker compose up -d --build
```

애플리케이션 컨테이너는 데이터베이스의 상태 확인이 완료된 후 시작됩니다.

### 4. 로그 확인

전체 서비스의 로그를 확인합니다.

```powershell
docker compose logs
```

애플리케이션 로그만 확인하려면 다음 명령을 사용합니다.

```powershell
docker compose logs app
```

데이터베이스 로그를 확인하려면 다음 명령을 사용합니다.

```powershell
docker compose logs db
```

### 5. 서비스 중지

실행 중인 서비스를 중지하려면 다음 명령을 사용합니다.

```powershell
docker compose down
```

이 명령은 컨테이너를 제거하지만, 별도로 정의된 `postgres_data` 볼륨은 기본적으로 유지합니다.

## 테스트

전체 테스트를 실행하려면 다음 명령을 사용합니다.

```powershell
python -m pytest -v
```

테스트는 프로젝트의 주요 기능을 검증합니다.

- 식대 계산
- 영수증 데이터 파싱
- 영수증 처리
- 근무 시간 데이터 변환
- 데이터베이스 저장소

## 지속적 통합 (CI)

GitHub Actions를 사용하여 자동 테스트와 Docker 이미지 빌드를 검증합니다.

`main` 브랜치에 푸시하거나 해당 브랜치를 대상으로 Pull Request를 생성하면 설정된 워크플로가 실행됩니다.

워크플로 설정 파일:

`.github/workflows/ci.yml`

CI를 통해 코드 변경 후에도 주요 기능이 정상적으로 동작하는지 확인할 수 있습니다.

## 보안

다음과 같은 파일에 인증 정보, 개인정보 또는 기밀 데이터가 포함되어 있다면 공개 저장소에 커밋하지 마세요.

- `.env`
- `credentials.json`
- `token.json`
- 회사 정보가 포함된 원본 Excel 템플릿
- 개인정보가 포함된 영수증 이미지
- 개인 또는 금융 정보가 포함된 생성 보고서

Git에 추가하기 전에 `.gitignore` 설정과 변경 파일 목록을 확인하세요.

공개용 예제 템플릿을 사용하고, 실제 회사 데이터와 개인 인증 정보를 분리하여 관리하는 것을 권장합니다.

## 향후 개선 사항

- 다양한 영수증 형식에 대한 OCR 날짜 및 금액 추출 정확도 개선
- 오류 처리 및 구조화된 로깅 강화
- 월별 보고서 생성 워크플로의 자동 테스트 확장
- 설정 검증 및 초기 설치 과정 개선
- 데이터 검증 및 보고서 생성 기능 개선

## 라이선스

현재 별도의 라이선스가 지정되어 있지 않습니다.

프로젝트를 공개적으로 배포하거나 다른 사람이 재사용할 수 있도록 허용하려면 적절한 라이선스를 추가하는 것이 좋습니다.