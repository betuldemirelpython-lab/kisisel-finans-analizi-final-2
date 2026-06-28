# =============================================================================
# prompts.py — AI Kişisel Finans Asistanı Prompt Şablonları
# =============================================================================
# Bu dosya, FinanceAgent pipeline'ının her adımında kullanılan
# prompt şablonlarını içermektedir.
# Her fonksiyon, ilgili adım için LLM'e gönderilecek metni döndürür.
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# SİSTEM PROMPT — LLM'in genel davranışını belirler
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Sen deneyimli bir kişisel finans danışmanısın.
Kullanıcıların harcama alışkanlıklarını analiz eder,
gereksiz giderleri tespit eder
ve net, uygulanabilir tasarruf önerileri sunarsın.
Cevapların açık, maddeli ve sade olmalıdır.
Türkçe yanıt ver. Para birimlerini TL olarak ifade et."""


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 1: HARCAMA AYIKLAMA PROMPT'U
# Kullanıcının serbest metninden harcama kalemlerini ve tutarları çıkarır
# ─────────────────────────────────────────────────────────────────────────────
def get_extraction_prompt(user_input: str) -> str:
    """
    Kullanıcının ham metin girdisinden harcama kalemlerini ayıklar.
    
    Args:
        user_input: Kullanıcının girdiği serbest metin (SMS, not vb.)
    
    Returns:
        LLM'e gönderilecek prompt metni
    """
    return f"""Aşağıdaki metni dikkatle oku ve içindeki tüm harcama kalemlerini ayıkla.

KURALLAR:
- Tutar açıkça belirtilmemişse "belirtilmemiş" yaz, asla tahmin etme
- Her kalemi ayrı bir satırda yaz
- Kalem isimlerini kısa ve net tut (örn: "Netflix aboneliği" değil "Netflix")
- Tekrar eden aynı kalemi birleştir, tutarlarını topla
- Para birimini TL olarak normalleştir (lira, ₺ → TL)
- SADECE aşağıdaki formatı kullan, başka hiçbir şey yazma:

FORMAT:
Kalem: [isim] | Tutar: [sayısal değer TL veya "belirtilmemiş"]

METİN:
{user_input}

Harcama listesi:"""


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 2: KATEGORİLEŞTİRME PROMPT'U
# Ayıklanan harcamaları belirlenen kategorilere atar
# ─────────────────────────────────────────────────────────────────────────────
def get_categorization_prompt(expense_list: str) -> str:
    """
    Ayıklanan harcama listesini kategorilere göre gruplar.
    
    Args:
        expense_list: Adım 1'den gelen pipe-separated harcama listesi
    
    Returns:
        LLM'e gönderilecek prompt metni
    """
    return f"""Aşağıdaki harcama listesini belirlenen kategorilere göre sınıflandır.

KATEGORİLER (yalnızca bu 6 kategoriyi kullan):
1. 🏠 Kira & Konut (kira, aidat, elektrik, su, doğalgaz, internet)
2. 🛒 Market & Yemek (market, restoran, kafe, yemek siparişi, kahve)
3. 🚗 Ulaşım (benzin, otobüs, metro, taksi, araç bakım, otopark)
4. 🎬 Eğlence & Kültür (sinema, konser, oyun, kitap, hobi)
5. 📱 Abonelikler (Netflix, Spotify, YouTube, dergi, yazılım, dijital)
6. 📦 Diğer (yukarıdaki kategorilere girmeyen her şey)

HARCAMA LİSTESİ:
{expense_list}

ÇIKTI FORMATI (tam olarak bu formatta yaz):
Kategori: [kategori adı ve emojisi]
- [kalem 1]: [tutar]
- [kalem 2]: [tutar]
TOPLAM: [kategori toplam tutarı veya "hesaplanamadı"]

Her kategori için ayrı blok oluştur. Sadece harcama olan kategorileri göster."""


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 3: ANALİZ PROMPT'U
# Kategorilere göre harcama örüntülerini ve riskleri değerlendirir
# ─────────────────────────────────────────────────────────────────────────────
def get_analysis_prompt(categorized_data: str) -> str:
    """
    Kategorilere ayrılmış harcama verisini analiz eder.
    
    Args:
        categorized_data: Adım 2'den gelen kategorili harcama verisi
    
    Returns:
        LLM'e gönderilecek prompt metni
    """
    return f"""Aşağıdaki kategorilere ayrılmış harcama verisini detaylı analiz et.

KATEGORİLİ HARCAMA VERİSİ:
{categorized_data}

ANALİZ RAPORU YAZ (aşağıdaki başlıkları kullan):

## 📊 Genel Harcama Tablosu
- Toplam harcama miktarını hesapla
- Her kategorinin toplam içindeki yüzdesini göster (örn: "Market: %23")
- En yüksekten en düşüğe sırala

## 🔴 Riskli / Dikkat Gerektiren Harcamalar
- Oransal olarak yüksek veya beklenmedik kalemleri tespit et
- Her risk için kısa bir açıklama yap

## 🟡 Gereksiz Görünen Harcamalar
- Kolayca kesilebilecek veya azaltılabilecek kalemleri listele
- Neden gereksiz göründüğünü açıkla

## 💡 Genel Harcama Yorumu
- 2-3 cümle ile genel harcama örüntüsünü değerlendir
- Kullanıcının finansal alışkanlığı hakkında gözlem yap

Net, maddeli ve anlaşılır bir dil kullan. Türkçe yaz."""


# ─────────────────────────────────────────────────────────────────────────────
# ADIM 4: TASARRUF ÖNERİLERİ PROMPT'U
# Analize göre somut ve uygulanabilir öneriler üretir
# ─────────────────────────────────────────────────────────────────────────────
def get_suggestion_prompt(analysis_result: str) -> str:
    """
    Analiz sonucuna göre kişiselleştirilmiş tasarruf önerileri üretir.
    
    Args:
        analysis_result: Adım 3'ten gelen analiz raporu
    
    Returns:
        LLM'e gönderilecek prompt metni
    """
    return f"""Aşağıdaki harcama analizine dayanarak kişiselleştirilmiş tasarruf önerileri sun.

ANALİZ SONUCU:
{analysis_result}

TASARRUF ÖNERİLERİ YAZ:
- 4 ile 6 arasında somut öneri yaz (ne çok az, ne çok fazla)
- Her öneri GERÇEKÇI ve UYGULANABILIR olsun
- Her önerinin başına bu emojilerden birini koy: 💰🔄✂️📉🎯🛡️
- Her önerinin ardından kısa bir gerekçe ekle (1 cümle, neden önemli)
- Mümkünse aylık tahmini tasarruf miktarını belirt

FORMAT:
💰 **Öneri Başlığı**
→ Açıklama ve gerekçe. Tahmini tasarruf: ~X TL/ay

---

Son olarak şunu ekle:
## 🏆 Harcama Sağlık Skoru: X/100
Skoru şu kriterlere göre ver:
- 80-100: Çok iyi finansal alışkanlıklar
- 60-79: Ortalama, iyileştirme alanları var  
- 40-59: Dikkat, bazı riskli harcamalar var
- 0-39: Acil finansal düzenleme gerekiyor
Skoru neden bu şekilde verdiğini 1-2 cümleyle açıkla."""
