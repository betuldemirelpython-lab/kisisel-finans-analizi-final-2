# =============================================================================
# streamlit_app.py — AI Kişisel Finans Asistanı Kullanıcı Arayüzü
# =============================================================================
# Bu dosya, FastAPI backend'e istek atarak analiz sonuçlarını
# kullanıcı dostu bir arayüzde görüntüler.
# =============================================================================

import requests
import streamlit as st
import os
import sys

# ─────────────────────────────────────────────────────────────────────────────
# Sayfa genel ayarları (HER ZAMAN EN BAŞTA ÇALIŞMALIDIR)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="💰 AI Kişisel Finans Asistanı",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "AI destekli kişisel finans analizi ve tasarruf asistanı.",
    },
)

# Backend klasörünü arama yoluna ekle (Streamlit'in modülleri bulabilmesi için)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Ortam değişkenlerini yükle ve yerel modda olup olmadığımızı kontrol et
is_local = False
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    backend_env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
    
    if os.path.exists(env_path) or os.path.exists(backend_env_path):
        is_local = True
        load_dotenv(env_path)
        load_dotenv(backend_env_path)
except ImportError:
    pass

# Streamlit secrets (Yalnızca canlı ortamda/Streamlit Cloud'da çalıştırılır)
if not is_local:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
        if "GROQ_API_KEY" in st.secrets:
            os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# Özel CSS Stilleri — daha profesyonel görünüm için
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Ana başlık stili */
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.2rem;
        }
        /* Alt başlık stili */
        .sub-title {
            text-align: center;
            color: #6b7280;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        /* Kart stili */
        .metric-card {
            background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
            border-radius: 12px;
            padding: 1.2rem;
            border-left: 4px solid #667eea;
            margin: 0.5rem 0;
        }
        /* Tab içerik alanı */
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1.5rem;
        }
        /* Buton stili */
        .stButton > button {
            width: 100%;
            height: 3rem;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# API ÇAĞRISI FONKSİYONU (AKILLI HİBRİT MOTOR)
# =============================================================================
def call_api(user_input: str, backend_url: str) -> dict:
    """
    FastAPI backend'ine POST isteği atarak harcama analizi yaptırır.
    Eğer backend kapalıysa veya Streamlit Cloud üzerindeysek, doğrudan
    FinanceAgent nesnesini import edip çalıştırır (Sunucusuz Fallback).
    """
    endpoint = f"{backend_url.rstrip('/')}/analyze"

    # Adım 1: FastAPI API sunucusuna istek göndermeyi dene
    try:
        response = requests.post(
            url=endpoint,
            json={"user_input": user_input},
            timeout=10,  # Hızlıca karar vermek için kısa bağlantı süresi
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        # Bağlantı başarısız olduysa veya sunucu kapalıysa sessizce Adım 2'ye geç
        pass

    # Adım 2: Sunucusuz Direct Fallback Modu (Direct Python Import)
    try:
        from agent import FinanceAgent
        agent = FinanceAgent()
        return agent.analyze(user_input)
    except Exception as e:
        return {
            "status": "error",
            "message": (
                f"❌ AI Analiz Motoru çalıştırılamadı.\n\n"
                f"**Olası Neden:** API Anahtarları (.env veya Streamlit Secrets) eksik veya hatalı.\n\n"
                f"**Hata Detayı:** {str(e)}"
            ),
        }


# =============================================================================
# SIDEBAR — Yan Panel
# =============================================================================
with st.sidebar:
    # Uygulama başlığı ve açıklaması
    st.markdown("## 💰 Finans Asistanı")
    st.markdown(
        "AI destekli kişisel finans analizi. "
        "Harcamalarınızı analiz eder, tasarruf fırsatları bulur."
    )

    st.divider()

    # Backend URL ayarı
    st.markdown("### ⚙️ Bağlantı Ayarları")
    backend_url = st.text_input(
        label="Backend URL",
        value="http://localhost:8000",
        help="FastAPI backend'inin çalıştığı adres",
        placeholder="http://localhost:8000",
    )

    # Bağlantı testi
    if st.button("🔌 Bağlantıyı Test Et", use_container_width=True):
        try:
            test_response = requests.get(
                f"{backend_url.rstrip('/')}/health",
                timeout=5,
            )
            if test_response.status_code == 200:
                st.success("✅ Backend bağlantısı başarılı!")
            else:
                st.error(f"❌ Backend hata döndürdü: {test_response.status_code}")
        except Exception:
            st.error("❌ Backend'e ulaşılamıyor!")

    st.divider()

    # Kullanım kılavuzu
    st.markdown("### 📖 Nasıl Kullanılır?")
    st.markdown(
        """
        1. 💬 Harcamalarınızı serbest metin olarak yazın
        2. 🔍 **"Analiz Et"** butonuna tıklayın
        3. ⏳ AI 30-60 saniyede analiz eder
        4. 📊 Sonuçları 4 farklı sekmede inceleyin
        """
    )

    st.divider()

    # Örnek giriş metni
    with st.expander("💡 Örnek Metin Göster"):
        st.code(
            """Bu ay kira 7500 TL ödedim. 
Migros'tan alışveriş yaptım, yaklaşık 
1800 TL. Netflix 139 TL, Spotify 59 TL, 
YouTube Premium 49 TL aboneliklerim var. 
Benzin için 650 TL harcadım. İki kez 
sinemaya gittim, toplam 340 TL. 
Yemek siparişine (Yemeksepeti) bu ay 
çok para gitti, sanırım 900 TL civarı. 
Bir de elektrik faturası 420 TL geldi.""",
            language=None,
        )

    st.divider()
    st.caption("🤖 Google Gemini & Groq AI tarafından desteklenmektedir")


# =============================================================================
# ANA İÇERİK ALANI
# =============================================================================

# Büyük başlık
st.markdown(
    '<h1 class="main-title">💰 AI Kişisel Finans Asistanı</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Harcamalarınızı yapay zeka ile analiz edin, '
    'tasarruf fırsatlarını keşfedin</p>',
    unsafe_allow_html=True,
)

# Üst metrik kartları (dekoratif)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        '<div class="metric-card">🔍 <b>Akıllı Ayıklama</b><br>'
        '<small>SMS ve notlardan harcama bulur</small></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        '<div class="metric-card">🗂️ <b>Kategorileme</b><br>'
        '<small>6 ana kategoriye ayırır</small></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        '<div class="metric-card">📈 <b>Risk Analizi</b><br>'
        '<small>Gereksiz harcamaları tespit eder</small></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        '<div class="metric-card">💡 <b>Öneriler</b><br>'
        '<small>Kişisel tasarruf planı sunar</small></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Harcama Giriş Alanı
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 📝 Harcamalarınızı Girin")
st.markdown(
    "Banka SMS'lerinizi, alışveriş notlarınızı veya harcama listenizi "
    "aşağıya yapıştırın. Serbest metin yazabilirsiniz!"
)

user_input = st.text_area(
    label="Harcama metni",
    placeholder=(
        "Örnek: Bu ay kira 7500 TL, Migros 1800 TL, "
        "Spotify 59 TL, Netflix 139 TL, benzin 800 TL ödedim. "
        "Ayrıca sinemaya 2 kez gittim, toplam 350 TL. "
        "Elektrik faturası 380 TL geldi..."
    ),
    height=200,
    label_visibility="collapsed",
    key="expense_input",
)

# Karakter sayacı
if user_input:
    st.caption(f"📏 {len(user_input)} karakter | {len(user_input.split())} kelime")

st.markdown("<br>", unsafe_allow_html=True)

# Analiz butonu
analyze_btn = st.button(
    label="🔍 Analiz Et",
    type="primary",
    use_container_width=True,
    disabled=len(user_input.strip()) < 10,
    key="analyze_button",
)


# =============================================================================
# ANALİZ ÇALIŞTIRMA VE SONUÇLARI GÖSTERME
# =============================================================================
if analyze_btn:
    if len(user_input.strip()) < 10:
        st.warning("⚠️ Lütfen en az 10 karakter içeren bir metin girin.")
    else:
        # Analiz sırasında spinner göster
        with st.spinner("🤖 AI analiz yapıyor... Bu işlem 30-60 saniye sürebilir."):
            result = call_api(user_input, backend_url)

        # ── Hata durumu ──────────────────────────────────────────────────────
        if result.get("status") == "error":
            st.error("### ❌ Analiz Başarısız")
            st.markdown(result.get("message", "Bilinmeyen bir hata oluştu."))
            st.info(
                "💡 **İpucu:** Backend'in çalıştığından emin olun. "
                "Terminalde `cd backend && uvicorn app:app --reload` komutunu çalıştırın."
            )

        # ── Başarı durumu ─────────────────────────────────────────────────────
        else:
            st.success("✅ Analiz tamamlandı! Sonuçlarınız hazır.")
            st.balloons()

            st.markdown("---")
            st.markdown("## 📊 Analiz Sonuçları")

            # 4 sekme oluştur
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Harcama Listesi",
                "🗂️ Kategoriler",
                "📈 Analiz Raporu",
                "💡 Tasarruf Önerileri",
            ])

            # ── Tab 1: Harcama Listesi ────────────────────────────────────────
            with tab1:
                st.markdown("### 📊 Tespit Edilen Harcama Kalemleri")
                st.markdown(
                    "AI'ın metninizden ayıkladığı harcama kalemleri ve tutarlar:"
                )
                st.code(
                    result.get("extracted_expenses", "Veri bulunamadı."),
                    language=None,
                )

            # ── Tab 2: Kategoriler ────────────────────────────────────────────
            with tab2:
                st.markdown("### 🗂️ Kategorilere Göre Harcamalar")
                st.markdown(
                    "Harcamalarınız 6 ana kategoriye göre gruplandırıldı:"
                )
                categorized_text = result.get("categorized_expenses", "Veri bulunamadı.")
                st.markdown(categorized_text)

            # ── Tab 3: Analiz Raporu ──────────────────────────────────────────
            with tab3:
                st.markdown("### 📈 Detaylı Harcama Analizi")
                analysis_text = result.get("analysis", "Analiz bulunamadı.")
                st.info(analysis_text)

            # ── Tab 4: Tasarruf Önerileri ─────────────────────────────────────
            with tab4:
                st.markdown("### 💡 Kişiselleştirilmiş Tasarruf Önerileri")
                suggestions_text = result.get("suggestions", "Öneri bulunamadı.")
                st.success(suggestions_text)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    "> 📌 **Hatırlatma:** Bu öneriler AI tarafından üretilmektedir. "
                    "Büyük finansal kararlar için bir uzmanla görüşmenizi öneririz."
                )


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption("🤖 Google Gemini & Groq (Llama 3) tarafından desteklenmektedir")
with footer_col2:
    st.caption("💻 FastAPI + Streamlit ile geliştirildi")
with footer_col3:
    st.caption("📌 [GitHub'da Görüntüle](#) | v1.0.0")
