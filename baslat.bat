@echo off
echo.
echo =====================================================
echo   AI Kisisel Finans Asistani - Baslatici
echo =====================================================
echo.

:: .env kontrolu
if not exist ".env" (
    echo [HATA] .env dosyasi bulunamadi!
    echo .env.example dosyasini kopyalayin ve API anahtarlarinizi girin:
    echo.
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

:: API key kontrolu
findstr /C:"GEMINI_API_KEY=your_" .env >nul 2>&1
if %errorlevel%==0 (
    echo [UYARI] GEMINI_API_KEY henuz guncellenmemis!
    echo .env dosyasini acin ve gercek API anahtarinizi girin.
    pause
    exit /b 1
)

echo [1/2] FastAPI backend baslatiliyor...
start "FastAPI Backend" cmd /k "cd /d %~dp0backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000"

:: Backend'in baslamasi icin bekle
timeout /t 4 /nobreak >nul

echo [2/2] Streamlit arayuzu baslatiliyor...
start "Streamlit Frontend" cmd /k "cd /d %~dp0frontend && streamlit run streamlit_app.py"

echo.
echo =====================================================
echo   Uygulama baslatildi!
echo.
echo   Backend API  : http://localhost:8000
echo   Swagger Docs : http://localhost:8000/docs
echo   Streamlit UI : http://localhost:8501
echo =====================================================
echo.
echo Tarayicinizda http://localhost:8501 adresini acin.
echo.
pause
