import os
import smtplib
import pandas as pd
import yfinance as yf
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from PublicDataReader import Kosis

# ── 설정 ──────────────────────────────────────────────
KOSIS_KEY   = os.environ["KOSIS_API_KEY"]
GMAIL_USER  = os.environ["GMAIL_USER"]          # 보내는 Gmail 주소
GMAIL_PASS  = os.environ["GMAIL_APP_PASSWORD"]  # Gmail 앱 비밀번호
TO_EMAIL    = "kyhh9124@naver.com"

NOW         = datetime.now()
YEAR        = NOW.strftime("%Y")
PREV_MONTH  = (NOW.replace(day=1) - pd.DateOffset(months=1))
START_PRD   = PREV_MONTH.strftime("%Y%m")       # 전월 데이터 수집
END_PRD     = START_PRD
REPORT_NAME = f"monthly_report_{NOW.strftime('%Y%m')}.xlsx"
# ──────────────────────────────────────────────────────


def collect_kosis() -> pd.DataFrame:
    api = Kosis(KOSIS_KEY)
    df = api.get_data(
        "통계자료",
        orgId      = "134",
        tblId      = "DT_134001_001",
        itmId      = "ALL",
        objL1      = "ALL",
        prdSe      = "M",
        startPrdDe = START_PRD,
        endPrdDe   = END_PRD,
    )
    return df


def collect_yfinance() -> tuple[pd.DataFrame, pd.DataFrame]:
    start = f"{YEAR}-01-01"
    end   = NOW.strftime("%Y-%m-%d")

    dow    = yf.download("^DJI",  start=start, end=end, interval="1mo", progress=False)
    nasdaq = yf.download("^IXIC", start=start, end=end, interval="1mo", progress=False)

    dj_df = dow["Close"].reset_index().rename(columns={"^DJI": "Dow Jones Close"})
    nq_df = nasdaq["Close"].reset_index().rename(columns={"^IXIC": "NASDAQ Close"})

    return dj_df, nq_df


def style_sheet(writer: pd.ExcelWriter, sheet_name: str, df: pd.DataFrame):
    """헤더 굵게 + 열 너비 자동 조정"""
    ws = writer.sheets[sheet_name]
    from openpyxl.styles import Font, PatternFill, Alignment
    header_fill = PatternFill("solid", start_color="1F4E79")
    for cell in ws[1]:
        cell.font      = Font(bold=True, color="FFFFFF", name="Arial", size=10)
        cell.fill      = header_fill
        cell.alignment = Alignment(horizontal="center")
    for col in ws.columns:
        max_len = max(len(str(c.value)) if c.value else 0 for c in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)


def save_excel(kosis_df: pd.DataFrame, dj_df: pd.DataFrame, nq_df: pd.DataFrame) -> str:
    path = f"/tmp/{REPORT_NAME}"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        kosis_df.to_excel(writer, sheet_name="KOSIS_미분양현황", index=False)
        dj_df.to_excel(writer,    sheet_name="DowJones",         index=False)
        nq_df.to_excel(writer,    sheet_name="NASDAQ",           index=False)

        style_sheet(writer, "KOSIS_미분양현황", kosis_df)
        style_sheet(writer, "DowJones",         dj_df)
        style_sheet(writer, "NASDAQ",           nq_df)
    return path


def send_email(file_path: str):
    subject = f"[월간 자동 리포트] {NOW.strftime('%Y년 %m월')} 데이터"
    body    = (
        f"{NOW.strftime('%Y년 %m월')} 월간 데이터 리포트입니다.\n\n"
        "포함 시트:\n"
        "  1. KOSIS_미분양현황 – KOSIS 통계자료 (134 / DT_134001_001)\n"
        "  2. DowJones         – 다우존스 월봉 종가\n"
        "  3. NASDAQ           – 나스닥 월봉 종가\n\n"
        "자동 발송 메일입니다."
    )

    msg = MIMEMultipart()
    msg["From"]    = GMAIL_USER
    msg["To"]      = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with open(file_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{REPORT_NAME}"')
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())

    print(f"✅ 이메일 발송 완료 → {TO_EMAIL}")


def main():
    print("📊 KOSIS 데이터 수집 중...")
    kosis_df = collect_kosis()

    print("📈 Yahoo Finance 데이터 수집 중...")
    dj_df, nq_df = collect_yfinance()

    print("💾 엑셀 파일 저장 중...")
    file_path = save_excel(kosis_df, dj_df, nq_df)

    print("📧 이메일 발송 중...")
    send_email(file_path)


if __name__ == "__main__":
    main()
