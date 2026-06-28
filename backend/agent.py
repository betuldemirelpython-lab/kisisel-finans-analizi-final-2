# =============================================================================
# agent.py — FinanceAgent: 4 Adımlı AI Pipeline Controller
# =============================================================================
# Bu dosya, kişisel finans asistanının ana iş mantığını içerir.
# Google Gemini (birincil) ve Groq/Llama3 (yedek) LLM'lerini kullanır.
# =============================================================================

import os
import logging
from dotenv import load_dotenv

# Google Gemini kütüphanesi
import google.generativeai as genai

# Groq kütüphanesi (fallback LLM)
from groq import Groq

# Kendi prompt şablonlarımız
from prompts import (
    SYSTEM_PROMPT,
    get_extraction_prompt,
    get_categorization_prompt,
    get_analysis_prompt,
    get_suggestion_prompt,
)

# ─────────────────────────────────────────────────────────────────────────────
# Loglama ayarları
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# .env dosyasından ortam değişkenlerini yükle
load_dotenv()


# =============================================================================
# FinanceAgent Sınıfı
# =============================================================================
class FinanceAgent:
    """
    Kişisel finans analizi yapan AI agent'ı.
    
    Google Gemini'yi birincil LLM olarak kullanır.
    Gemini başarısız olursa otomatik olarak Groq/Llama3'e geçer.
    """

    def __init__(self):
        """
        Agent'ı başlatır ve LLM bağlantılarını kurar.
        API anahtarlarını .env dosyasından okur.
        """
        # ── Gemini API ayarları ──────────────────────────────────────────────
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=SYSTEM_PROMPT,
            )
            logger.info("✅ Gemini API bağlantısı kuruldu.")
        else:
            self.gemini_model = None
            logger.warning("⚠️  GEMINI_API_KEY bulunamadı! Gemini devre dışı.")

        # ── Groq API ayarları (yedek LLM) ───────────────────────────────────
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
            logger.info("✅ Groq API bağlantısı kuruldu.")
        else:
            self.groq_client = None
            logger.warning("⚠️  GROQ_API_KEY bulunamadı! Groq devre dışı.")

        # En az bir LLM çalışmalı
        if not self.gemini_model and not self.groq_client:
            raise ValueError(
                "❌ Hiçbir API anahtarı bulunamadı! "
                ".env dosyasına GEMINI_API_KEY veya GROQ_API_KEY ekleyin."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # YARDIMCI METOT: LLM'e istek gönder
    # ─────────────────────────────────────────────────────────────────────────
    def _call_llm(self, prompt: str) -> str:
        """
        LLM'e prompt gönderir ve yanıtı döndürür.
        
        Önce Gemini'yi dener. Hata alırsa Groq'a geçer.
        Her iki LLM de başarısız olursa hata fırlatır.
        
        Args:
            prompt: LLM'e gönderilecek prompt metni
            
        Returns:
            LLM'in ürettiği metin yanıtı
            
        Raises:
            Exception: Her iki LLM de yanıt vermezse
        """
        gemini_error_msg = "Gemini API anahtarı bulunamadı veya model başlatılamadı."
        
        # ── Gemini ile dene ──────────────────────────────────────────────────
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as gemini_error:
                gemini_error_msg = str(gemini_error)
                logger.warning(
                    f"⚠️  Gemini başarısız, Groq'a geçiliyor... Hata: {gemini_error}"
                )

        # ── Groq ile dene (fallback) ─────────────────────────────────────────
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=2048,
                )
                return response.choices[0].message.content
            except Exception as groq_error:
                logger.error(f"❌ Groq da başarısız oldu. Hata: {groq_error}")
                raise Exception(
                    f"Her iki LLM de yanıt vermedi.\n"
                    f"- Gemini Hatası: {gemini_error_msg}\n"
                    f"- Groq Hatası: {groq_error}"
                )

        raise Exception(
            f"Hiçbir LLM kullanılabilir durumda değil.\n"
            f"- Gemini Hatası: {gemini_error_msg}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # ANA METOT: 4 Adımlı Analiz Pipeline'ı
    # ─────────────────────────────────────────────────────────────────────────
    def analyze(self, user_input: str) -> dict:
        """
        Kullanıcının harcama metnini 4 adımda analiz eder.
        
        Adım 1: Harcama kalemlerini ayıkla
        Adım 2: Kategorilere göre grupla
        Adım 3: Harcama analizi yap
        Adım 4: Tasarruf önerileri üret
        
        Args:
            user_input: Kullanıcının girdiği serbest metin
            
        Returns:
            Her adımın sonucunu içeren dictionary
        """
        logger.info("=" * 60)
        logger.info("🚀 Finans analizi başladı...")
        logger.info(f"📝 Girdi uzunluğu: {len(user_input)} karakter")
        logger.info("=" * 60)

        try:
            # ── ADIM 1: Harcama Ayıklama ─────────────────────────────────────
            logger.info("🔍 Adım 1 başladı: Harcamalar ayıklanıyor...")
            extraction_prompt = get_extraction_prompt(user_input)
            extracted_expenses = self._call_llm(extraction_prompt)
            logger.info("✅ Adım 1 tamamlandı: Harcamalar ayıklandı")

            # ── ADIM 2: Kategorilere Ayırma ──────────────────────────────────
            logger.info("🗂️  Adım 2 başladı: Kategorilere ayrılıyor...")
            categorization_prompt = get_categorization_prompt(extracted_expenses)
            categorized_expenses = self._call_llm(categorization_prompt)
            logger.info("✅ Adım 2 tamamlandı: Kategoriler oluşturuldu")

            # ── ADIM 3: Analiz ────────────────────────────────────────────────
            logger.info("📈 Adım 3 başladı: Harcama analizi yapılıyor...")
            analysis_prompt = get_analysis_prompt(categorized_expenses)
            analysis_result = self._call_llm(analysis_prompt)
            logger.info("✅ Adım 3 tamamlandı: Analiz raporu hazırlandı")

            # ── ADIM 4: Tasarruf Önerileri ────────────────────────────────────
            logger.info("💡 Adım 4 başladı: Tasarruf önerileri üretiliyor...")
            suggestion_prompt = get_suggestion_prompt(analysis_result)
            suggestions = self._call_llm(suggestion_prompt)
            logger.info("✅ Adım 4 tamamlandı: Öneriler hazırlandı")

            logger.info("=" * 60)
            logger.info("🎉 Analiz başarıyla tamamlandı!")
            logger.info("=" * 60)

            # Tüm sonuçları dictionary olarak döndür
            return {
                "status": "success",
                "extracted_expenses": extracted_expenses,
                "categorized_expenses": categorized_expenses,
                "analysis": analysis_result,
                "suggestions": suggestions,
            }

        except Exception as e:
            # Herhangi bir adımda hata oluşursa yakala ve raporla
            logger.error(f"❌ Analiz sırasında hata oluştu: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "extracted_expenses": "",
                "categorized_expenses": "",
                "analysis": "",
                "suggestions": "",
            }
