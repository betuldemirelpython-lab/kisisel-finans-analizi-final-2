# 💰 AI Kişisel Finans & Harcama Asistanı

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-Flash-4285F4?logo=google&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_3-F55036?logoColor=white)
![License](https://img.shields.io/badge/Lisans-MIT-green)

---

## 🎯 Ne Yapar?

Harcamalarınızı serbest metin olarak girin (banka SMS'leri, alışveriş notları, el yazısı listeler) — AI agent 4 adımlı bir pipeline ile analiz eder, kategorilere ayırır, riskli harcamaları tespit eder ve size uygulanabilir tasarruf önerileri sunar.

**Desteklenen giriş formatları:** Banka SMS'i · Alışveriş listesi · Serbest metin · Türkçe/İngilizce karışık

---

## 🏗️ Mimari

```
Kullanıcı Girdisi (Serbest Metin)
         │
         ▼
┌─────────────────────┐
│   Streamlit UI      │  ← Kullanıcı arayüzü (frontend/)
│  streamlit_app.py   │
└──────────┬──────────┘
           │ HTTP POST /analyze
           ▼
┌─────────────────────┐
│   FastAPI Backend   │  ← REST API (backend/app.py)
│     /analyze        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FinanceAgent Pipeline                    │
│                      (backend/agent.py)                     │
│                                                             │
│  [1] Harcama Ayıklama  →  [2] Kategorileme                 │
│       ↓                        ↓                            │
│  [3] Risk Analizi      →  [4] Tasarruf Önerileri           │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────┐     ┌──────────────────────┐
│   Google Gemini      │ OR  │   Groq / Llama 3     │
│  (Birincil LLM)      │────▶│  (Yedek / Fallback)  │
└──────────────────────┘     └──────────────────────┘
```

---

## ⚙️ Kurulum

### Gereksinimler

- Python **3.11+**
- **Gemini API Key** → [Google AI Studio](https://aistudio.google.com) (ücretsiz)
- **Groq API Key** → [console.groq.com](https://console.groq.com) (ücretsiz)

### Adım Adım Kurulum

**1. Projeyi klonlayın:**
```bash
git clone https://github.com/kullanici-adiniz/kisisel-finans-analizi.git
cd kisisel-finans-analizi
```

**2. Sanal ortam oluşturun (önerilir):**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Bağımlılıkları kurun:**
```bash
pip install -r requirements.txt
```

**4. API anahtarlarını ayarlayın:**
```bash
# .env.example dosyasını kopyalayın
cp .env.example .env

# .env dosyasını açıp gerçek anahtarlarınızı girin:
# GEMINI_API_KEY=AIza...
# GROQ_API_KEY=gsk_...
```

**5. FastAPI backend'i başlatın:**
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
> ✅ API şu adreste çalışıyor: http://localhost:8000
> 📖 Swagger dokümantasyonu: http://localhost:8000/docs

**6. Streamlit arayüzünü başlatın (yeni terminal):**
```bash
cd frontend
streamlit run streamlit_app.py
```
> 🌐 Uygulama şu adreste açılıyor: http://localhost:8501

---

## 🚀 Streamlit Cloud'a Deploy

### 1. GitHub'a Gönderin

```bash
git add .
git commit -m "feat: AI finans asistanı ilk sürüm"
git push origin main
```

> ⚠️ `.env` dosyası `.gitignore`'da hariç tutulmuştur. Asla commit'lemeyin!

### 2. Streamlit Cloud'da Proje Oluşturun

1. [share.streamlit.io](https://share.streamlit.io) adresine gidin
2. **"New app"** butonuna tıklayın
3. GitHub hesabınızı bağlayın
4. Repository: `kisisel-finans-analizi`
5. Main file path: `frontend/streamlit_app.py`

### 3. Secrets (API Anahtarları) Ekleyin

Streamlit Cloud panosunda → **Settings → Secrets** bölümüne şunu yapıştırın:

```toml
GEMINI_API_KEY = "AIza..."
GROQ_API_KEY = "gsk_..."
```

> 💡 **Not:** Streamlit Cloud'da FastAPI backend çalışmaz. `agent.py`'ı doğrudan Streamlit'ten çağırmak için `streamlit_app.py`'ı aşağıdaki şekilde güncelleyin:

```python
# Streamlit Cloud için agent'ı doğrudan çağırın
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import streamlit as st
from agent import FinanceAgent

# API anahtarlarını Streamlit secrets'dan alın
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
```

### 4. Deploy Edin

**"Deploy!"** butonuna tıklayın. Birkaç dakika içinde uygulamanız canlıya alınır.

---

## 📁 Dosya Yapısı

```
kisisel-finans-analizi-final-2/
│
├── backend/                    # FastAPI backend uygulaması
│   ├── app.py                  # REST API endpoint'leri (/analyze, /health)
│   ├── agent.py                # FinanceAgent sınıfı (pipeline controller)
│   └── prompts.py              # Tüm LLM prompt şablonları
│
├── frontend/                   # Streamlit kullanıcı arayüzü
│   └── streamlit_app.py        # Ana Streamlit uygulaması
│
├── .env                        # API anahtarları (gitignore'da!)
├── .env.example                # API anahtarı şablonu
├── .gitignore                  # Git dışlama listesi
├── requirements.txt            # Python bağımlılıkları
└── README.md                   # Bu dosya
```

---

## 🔄 Agent Pipeline Akışı

| Adım | İşlem | LLM Görevi |
|------|-------|-----------|
| **1** | 📝 Harcama Ayıklama | Ham metinden kalemleri ve tutarları çıkarır |
| **2** | 🗂️ Kategorileme | 6 kategoriye (kira, market, ulaşım, eğlence, abonelik, diğer) ayırır |
| **3** | 📈 Risk Analizi | Yüksek, gereksiz ve riskli harcamaları tespit eder |
| **4** | 💡 Öneri Üretimi | 4-6 somut, uygulanabilir tasarruf önerisi ve sağlık skoru verir |

**Fallback Mantığı:** Gemini başarısız → Groq/Llama3 devreye girer → Her ikisi de başarısız → Hata mesajı

---

## 📝 Örnek Kullanım

**Girdi:**
```
Bu ay kira 7500 TL ödedim. Migros'tan alışveriş yaptım, yaklaşık 1800 TL.
Netflix 139 TL, Spotify 59 TL, YouTube Premium 49 TL aboneliklerim var.
Benzin için 650 TL harcadım. İki kez sinemaya gittim, toplam 340 TL.
Yemek siparişine bu ay çok para gitti, sanırım 900 TL civarı.
Elektrik faturası 420 TL geldi.
```

**Beklenen Çıktı (Özet):**
- 🏠 Kira & Konut: 7.920 TL (%68)
- 🛒 Market & Yemek: 2.700 TL (%23)
- 📱 Abonelikler: 247 TL (%2)
- 🚗 Ulaşım: 650 TL (%5)
- 🎬 Eğlence: 340 TL (%3)

**Riskli:** Yemek siparişi 900 TL → Azaltılabilir  
**Öneri:** Yemek sipariş uygulamalarını haftada 2 gün ile sınırlayın → ~450 TL/ay tasarruf

---

## 🛠️ Teknolojiler

| Teknoloji | Kullanım |
|-----------|---------|
| 🐍 Python 3.11+ | Ana programlama dili |
| ⚡ FastAPI | REST API framework |
| 🎈 Streamlit | Kullanıcı arayüzü |
| 🤖 Google Gemini Flash | Birincil LLM |
| 🦙 Groq / Llama 3 | Yedek LLM (fallback) |
| 🔒 python-dotenv | Ortam değişkeni yönetimi |
| ✅ Pydantic | Veri doğrulama |

---

## 📄 Lisans

MIT Lisansı — Betül Altınkaynak Demirel © 2025

---

*Bu proje Google Gemini ve Groq API'leri kullanmaktadır. Finansal kararlar için profesyonel danışmanlık almanız önerilir.*
