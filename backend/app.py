# =============================================================================
# app.py — FastAPI REST API: Kişisel Finans Asistanı Backend
# =============================================================================
# Bu dosya, FinanceAgent'ı dışarıya REST API olarak açar.
# Streamlit frontend bu API'ye HTTP istekleri atarak analiz yaptırır.
# =============================================================================

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Kendi agent'ımızı import et
from agent import FinanceAgent

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI uygulama örneği
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Kişisel Finans Asistanı API",
    description=(
        "Kullanıcının harcama metnini analiz eden ve "
        "kişiselleştirilmiş tasarruf önerileri sunan AI agent API'si."
    ),
    version="1.0.0",
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS Middleware — Streamlit'in farklı port'tan istek atabilmesi için
# ─────────────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Geliştirme ortamı için tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, PUT, DELETE vs. hepsine izin ver
    allow_headers=["*"],       # Tüm header'lara izin ver
)


# =============================================================================
# Pydantic Veri Modelleri — Request/Response şemaları
# =============================================================================

class AnalyzeRequest(BaseModel):
    """
    /analyze endpoint'ine gönderilecek istek gövdesi.
    """
    user_input: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Kullanıcının harcama bilgilerini içeren serbest metin",
        examples=["Bu ay kira 7500 TL, Migros 1800 TL, Netflix 139 TL ödedim."],
    )


class AnalyzeResponse(BaseModel):
    """
    /analyze endpoint'inden dönen yanıt gövdesi.
    """
    status: str = Field(description="İşlem durumu: 'success' veya 'error'")
    extracted_expenses: str = Field(description="Ayıklanan harcama kalemleri listesi")
    categorized_expenses: str = Field(description="Kategorilere ayrılmış harcamalar")
    analysis: str = Field(description="Detaylı harcama analizi raporu")
    suggestions: str = Field(description="Kişiselleştirilmiş tasarruf önerileri")


# =============================================================================
# API Endpoint'leri
# =============================================================================

@app.get("/health", summary="Sağlık Kontrolü")
async def health_check():
    """
    API'nin çalışır durumda olup olmadığını kontrol eder.
    Monitoring ve deployment doğrulaması için kullanılır.
    
    Returns:
        JSON: Durum bilgisi
    """
    return {
        "status": "ok",
        "message": "🤖 AI Finans Asistanı çalışıyor",
        "version": "1.0.0",
    }


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Harcama Analizi Yap",
    description=(
        "Kullanıcının serbest metin olarak girdiği harcama bilgilerini "
        "4 adımlı AI pipeline ile analiz eder ve tasarruf önerileri sunar."
    ),
)
async def analyze_expenses(request: AnalyzeRequest):
    """
    Harcama analizi ana endpoint'i.
    
    Alınan metni FinanceAgent'a iletir ve 4 adımlı pipeline'ı çalıştırır:
    1. Harcama kalemlerini ayıkla
    2. Kategorilere ayır
    3. Analiz yap
    4. Tasarruf önerileri üret
    
    Args:
        request: Kullanıcının harcama metnini içeren istek nesnesi
        
    Returns:
        AnalyzeResponse: Her pipeline adımının sonucunu içeren yanıt
        
    Raises:
        HTTPException 500: LLM analizi başarısız olursa
    """
    try:
        # FinanceAgent örneği oluştur ve analizi çalıştır
        agent = FinanceAgent()
        result = agent.analyze(request.user_input)

        # Hata durumunu kontrol et
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"AI analizi başarısız: {result.get('message', 'Bilinmeyen hata')}",
            )

        # Başarılı yanıtı döndür
        return AnalyzeResponse(
            status=result["status"],
            extracted_expenses=result["extracted_expenses"],
            categorized_expenses=result["categorized_expenses"],
            analysis=result["analysis"],
            suggestions=result["suggestions"],
        )

    except HTTPException:
        # HTTPException'ları tekrar fırlat (zaten işlendi)
        raise
    except Exception as e:
        # Beklenmedik hataları yakala
        raise HTTPException(
            status_code=500,
            detail=f"Sunucu hatası: {str(e)}",
        )


# =============================================================================
# Uygulamayı başlat (doğrudan çalıştırılırsa)
# =============================================================================
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,   # Geliştirme modunda otomatik yeniden başlat
    )
