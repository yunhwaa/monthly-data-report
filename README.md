# 월간 데이터 자동 수집 리포트

매월 1일 오전 9시(KST)에 KOSIS 통계자료 + 다우존스/나스닥 데이터를 수집해  
1개의 엑셀 파일(시트 3개)로 만들어 이메일로 자동 발송합니다.

---

## 📁 파일 구조

```
project/
├── collect_data.py              # 메인 스크립트
├── requirements.txt             # 패키지 목록
└── .github/
    └── workflows/
        └── monthly.yml          # GitHub Actions 자동화
```

---

## 🚀 설정 방법 (최초 1회만)

### 1단계 – GitHub 저장소 만들기
1. [github.com](https://github.com) 로그인
2. 우측 상단 `+` → **New repository**
3. 저장소 이름 입력 (예: `monthly-data-report`) → **Create repository**
4. 이 폴더 안의 파일 전체를 저장소에 업로드

### 2단계 – Gmail 앱 비밀번호 발급
> 일반 Gmail 비밀번호가 아닌 **앱 비밀번호**가 필요합니다.

1. [myaccount.google.com/security](https://myaccount.google.com/security) 접속
2. **2단계 인증** 활성화 (안 되어 있으면 먼저 설정)
3. 검색창에 **"앱 비밀번호"** 검색 → 생성
4. 앱: **기타(직접 입력)** → `monthly-report` 입력 → **생성**
5. 16자리 비밀번호 메모해두기 (공백 제거: `xxxxxxxxxxxx xxxx` → `xxxxxxxxxxxxxxxx`)
bytcnrnkicqazrju

### 3단계 – GitHub Secrets 등록
> 저장소 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret 이름        | 값                              |
|--------------------|--------------------------------|
| `KOSIS_API_KEY`    | `MDFhZDA5OGUxNzQ5MmM0NGMyYTM3MDM5Y2NmYjMzOGM=` |
| `GMAIL_USER`       | 보내는 Gmail 주소 (예: `yourname@gmail.com`) |
| `GMAIL_APP_PASSWORD` | 2단계에서 발급받은 16자리 앱 비밀번호 |

### 4단계 – 테스트 실행
1. 저장소 → **Actions** 탭
2. `월간 데이터 자동 수집 및 발송` 클릭
3. **Run workflow** → **Run workflow** 버튼 클릭
4. 초록색 체크 ✅ 확인 후 이메일 수신 확인

---

## 📊 생성되는 엑셀 시트

| 시트명             | 내용                        |
|--------------------|-----------------------------|
| KOSIS_미분양현황   | KOSIS 통계자료 (134 기관)   |
| DowJones           | 다우존스 월봉 종가 (연간)   |
| NASDAQ             | 나스닥 월봉 종가 (연간)     |

---

## ⏰ 실행 일정

- 자동: **매월 1일 오전 9시 (KST)**
- 수동: Actions 탭 → Run workflow
