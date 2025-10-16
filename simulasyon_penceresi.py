from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore
import folium
from folium import Marker, Element
import math
import io
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import json
from datetime import datetime
import os

class SimulasyonPenceresi(QtWidgets.QWidget):
    def __init__(self,secili_dil):
        super().__init__()
        self.secili_dil = secili_dil
        self.setWindowTitle("Deprem Simülasyonu")
        self.stacked_widget = QtWidgets.QStackedWidget(self)
        self.resize(900, 700)
        
        self.sound_effect = QMediaPlayer()
        self.sound_effect.setMedia(QMediaContent(QUrl.fromLocalFile(r"C:\Users\Rohat\Desktop\Deprem_uygulamasi\data\eartquake_alarm_voice.mp3")))
        self.sound_effect.setVolume(50)
        
        self.kullanici_enlem = 37.0
        self.kullanici_boylam = 35.3
        self.secilen_enlem = None
        self.secilen_boylam = None

        # Layout
        self.simulasyon_sayfasi = QtWidgets.QWidget()
        ana_layout = QtWidgets.QVBoxLayout(self.simulasyon_sayfasi)


        # WebView harita
        self.webView = QtWebEngineWidgets.QWebEngineView()
        ana_layout.addWidget(self.webView)
        
       
        
        # Alt kısım (büyüklük input ve buton)
        alt_layout = QtWidgets.QHBoxLayout()
        self.buyukluk_input = QtWidgets.QLineEdit()
        # Deprem tipi seçimi
        self.deprem_tipi_combo = QtWidgets.QComboBox()
        self.deprem_tipi_combo.addItems(["Yüzey Depremi", "Derin Deprem", "Artçı"])
        self.deprem_tipi_combo.setStyleSheet("""
        QComboBox {
        border: 1.5px solid #ccc;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 16px;
        }
        """)
        alt_layout.addWidget(self.deprem_tipi_combo)
        self.buyukluk_input.setPlaceholderText("Deprem büyüklüğü (örn: 5.6)")
        self.buyukluk_input.setStyleSheet("""
            border: 1.5px solid #ccc;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 16px;
        """)
        alt_layout.addWidget(self.buyukluk_input)

        self.btn_simulasyon = QtWidgets.QPushButton("Simülasyonu Başlat")
        self.btn_simulasyon.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 16px;
              
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.btn_simulasyon.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_simulasyon.setMinimumHeight(40)
        self.btn_simulasyon.clicked.connect(self.simulasyon_baslat)
        alt_layout.addWidget(self.btn_simulasyon)
        # İşte buraya ekle:
        self.btn_gecmis = QtWidgets.QPushButton("Geçmişi Gör")
        self.btn_gecmis.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #45A049;
        }
    """)
        self.btn_gecmis.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_gecmis.setMinimumHeight(40)
        self.btn_gecmis.clicked.connect(self.guncelle_gecmis_listesi)
        self.btn_gecmis.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        alt_layout.addWidget(self.btn_gecmis)
    
    # Alt layout'u ana layout'a ekle
  

        ana_layout.addLayout(alt_layout)

        #self.setLayout(ana_layout)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)


        
        self.harita_yukle()
        # 🔽 işte tam buraya geçmiş sayfasını ekliyorsun
        self.gecmis_sayfasi = QtWidgets.QWidget()
        gecmis_layout = QtWidgets.QVBoxLayout(self.gecmis_sayfasi)

        # Liste widget'ı
        self.gecmis_listesi = QtWidgets.QListWidget()
        gecmis_layout.addWidget(self.gecmis_listesi)

        # Geri Dön butonu
        self.btn_geri = QtWidgets.QPushButton("Geri Dön")
        self.btn_geri.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        gecmis_layout.addWidget(self.btn_geri)
        self.stacked_widget.addWidget(self.simulasyon_sayfasi)
        self.stacked_widget.addWidget(self.gecmis_sayfasi)
        
        self.dil_ayarla()   
    def harita_yukle(self):
        self.map = folium.Map(location=[self.kullanici_enlem, self.kullanici_boylam], zoom_start=6)
       

        Marker([self.kullanici_enlem, self.kullanici_boylam], popup="Senin Konumun").add_to(self.map)
        self.map.add_child(folium.LatLngPopup())

        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.webView.setHtml(data.getvalue().decode())

    def simulasyon_baslat(self):
        # Deprem tipi seçimi
        deprem_tipi = self.deprem_tipi_combo.currentText()
         # Deprem tipine göre etki katsayısı belirle
        if deprem_tipi == "Yüzey Depremi":
         etki_katsayisi = 0.9   # Normal
        elif deprem_tipi == "Derin Deprem":
         etki_katsayisi = 0.6   # Daha az hissedilir
        elif deprem_tipi == "Artçı":
         etki_katsayisi = 0.4   # Zayıf
        else:
         etki_katsayisi = 1.0
        buyukluk_text = self.buyukluk_input.text()
        if not buyukluk_text:
            QtWidgets.QMessageBox.warning(self, "Uyarı", self.cevir("uyari_buyukluk"))
            return
        
    
        try:
            buyukluk = float(buyukluk_text)
        except:
            QtWidgets.QMessageBox.warning(self, "Uyarı", self.cevir("uyari_gecerli_sayi"))
            return

        secim_penceresi = QtWidgets.QInputDialog()
        enlem, ok1 = secim_penceresi.getDouble(
            self,
            self.cevir("deprem_noktasi"),
            self.cevir("enlem_girisi"),
            37.0, 36.0, 42.0, 4
        )
        if not ok1:
            return
        boylam, ok2 = secim_penceresi.getDouble(
              self,
              self.cevir("deprem_noktasi"),
              self.cevir("boylam_girisi"),
              35.0, 26.0, 45.0, 4
            )
        if not ok2:
            return
        self.sound_effect.play()  
        self.secilen_enlem = enlem
        self.secilen_boylam = boylam

        mesafe_km = self.hesapla_mesafe(self.kullanici_enlem, self.kullanici_boylam, enlem, boylam)
        gecis_suresi = mesafe_km / 6
        etki_yaricapi = buyukluk * 50000* etki_katsayisi  # 50 km * büyüklük

# Daire yarıçaplarını sırayla sakla
        halkalar = []
        for i in range(1, 10):
         yaricap = (i * etki_yaricapi / 9)
         renk = "red" if i <= 3 else "orange" if i <= 6 else "green"
         folium.Circle(
         location=[enlem, boylam],
         radius=yaricap,
         color=renk,
         fill=True,
         fill_opacity=0.15 if renk == "red" else 0.10 if renk == "orange" else 0.07
       ).add_to(self.map)
         halkalar.append(yaricap)  # ← BU SATIR for'un İÇİNDE OLMALI
         # Deprem tipi için anahtarlar
         deprem_tipi_anahtarlar = ["Yuzey_Depremi", "Derin_Deprem", "Artci"]
         tip_index = self.deprem_tipi_combo.currentIndex()
         tip_key = deprem_tipi_anahtarlar[tip_index]

# Kullanıcının mesafesini mm'ye çevir
         mesafe_metre = mesafe_km * 1000

# Sallantı belirlemesi halkalara göre
        if mesafe_metre <= halkalar[2]:
            sallanti_key = "şiddetli"
            sallanti = self.cevir("şiddetli")
        elif mesafe_metre <= halkalar[5]:
            sallanti_key = "orta"
            sallanti = self.cevir("orta")
        elif mesafe_metre <= halkalar[8]:
            sallanti_key = "hafif"
            sallanti = self.cevir("hafif")
        else:
            sallanti_key = "cok_hafif"
            sallanti = self.cevir("cok_hafif")
            

        self.map = folium.Map(location=[self.kullanici_enlem, self.kullanici_boylam], zoom_start=6)
        

        # Deprem etki yarıçapını büyüklüğe göre hesapla
        etki_yaricapi = buyukluk * 50000  # 50 km * büyüklük

    # Kırmızı bölge (şiddetli)
        for i in range(1, 4):
            folium.Circle(
            location=[enlem, boylam],
            radius=(i * etki_yaricapi / 9),  # 1/9, 2/9, 3/9 yani 1/3
            color="red",
            fill=True,
            fill_opacity=0.15
        ).add_to(self.map)

# Turuncu bölge (orta)
        for i in range(4, 7):
            folium.Circle(
            location=[enlem, boylam],
            radius=(i * etki_yaricapi / 9),
            color="orange",
            fill=True,
            fill_opacity=0.10
        ).add_to(self.map)

# Yeşil bölge (hafif)
        for i in range(7, 10):
            folium.Circle(
            location=[enlem, boylam],
            radius=(i * etki_yaricapi / 9),
            color="green",
            fill=True,
            fill_opacity=0.07
         ).add_to(self.map)

        Marker([self.kullanici_enlem, self.kullanici_boylam], popup="Senin Konumun").add_to(self.map)
        Marker([enlem, boylam], popup=f"Deprem Noktası\nM {buyukluk}").add_to(self.map)
        # 📌 İşte buraya dalga animasyonlarını ekle
 
        

        html_info = f"""
            <div style="
                position: fixed; 
                top: 15px; 
                right: 15px; 
                z-index: 9999;
                background-color: rgba(33, 150, 243, 0.9);
                color: white;
                padding: 15px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 15px;
                max-width: 220px;
                line-height: 1.4;
            ">
                <b>{self.cevir("deprem_bilgisi_baslik")}</b><br>
                {self.cevir("nokta")}: ({round(enlem, 3)}, {round(boylam, 3)})<br>
                {self.cevir("mesafe")}: {round(mesafe_km, 2)} km<br>
                {self.cevir("ulasma_suresi")}: {round(gecis_suresi, 1)} sn<br>
                {self.cevir("buyukluk")}: {buyukluk}<br>
                {self.cevir("tip")}: {deprem_tipi}<br>
                {self.cevir("sallanti")}: {sallanti}
            </div>
        """
        self.map.get_root().html.add_child(Element(html_info))
          # Sayaç (sol alt) - süreye göre dinamik geri sayım
        html_timer = f"""
        <div id="timer" style="
        position: fixed;
        bottom: 10px;
        left: 10px;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.85);
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 0 5px rgba(0,0,0,0.3);
        ">
        {self.cevir("kalan_sure")}: <span id="countdown">{int(gecis_suresi)}</span> sn
        </div>

        <script>
        var timeLeft = {int(gecis_suresi)};
        var countdownElement = document.getElementById('countdown');
        var timer = setInterval(function(){{
        timeLeft--;
        countdownElement.textContent = timeLeft;
        if(timeLeft <= 0){{
            clearInterval(timer);
            countdownElement.textContent = '{self.cevir("deprem_geldi")}';
            }}
        }}, 1000);
        </script>
        """

        self.map.get_root().html.add_child(Element(html_timer))
        
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.webView.setHtml(data.getvalue().decode())
        
        deprem_tipi = self.deprem_tipi_combo.currentText()  # varsa tip seçimini al
        self.kaydet_json(buyukluk, tip_key, round(mesafe_km, 1), sallanti_key)
        
    def hesapla_mesafe(self, lat1, lon1, lat2, lon2):
        R = 6371
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c
    def kaydet_json(self, buyukluk, tip_key, mesafe, sallanti_key):
        kayit = {
        "zaman": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "buyukluk": buyukluk,
        "tip_key": tip_key,     # Anahtar olarak sakla
        "mesafe": mesafe,
        "sallanti_key": sallanti_key      # Anahtar olarak sakla
        }

        dosya_adi = "deprem_gecmisi.json"

        if os.path.exists(dosya_adi):
         with open(dosya_adi, "r", encoding="utf-8") as file:
            try:
                veriler = json.load(file)
            except json.JSONDecodeError:
                veriler = []
        else:
          veriler = []
       
        veriler.append(kayit)
        

        if len(veriler) > 10:
         veriler = veriler[-10:]

        with open(dosya_adi, "w", encoding="utf-8") as file:
         json.dump(veriler, file, indent=4, ensure_ascii=False)
         self.guncelle_gecmis_listesi()
         
    def guncelle_gecmis_listesi(self):
     dosya_adi = "deprem_gecmisi.json"
     if os.path.exists(dosya_adi):
        with open(dosya_adi, "r", encoding="utf-8") as file:
            try:
                veriler = json.load(file)
            except json.JSONDecodeError:
                veriler = []
     else:
        veriler = []

     self.gecmis_listesi.clear()
     for kayit in veriler[::-1]:
        # Öncelikle tip_key varsa onu kullan, yoksa tip
        tip_key = kayit.get("tip_key")
        if not tip_key:
            # tip metni farklı dillerde olabilir, Türkçeye göre anahtara çevirmek için ters eşleme gerekebilir
            tip_metni = kayit.get("tip", "")
            tip_key = self.ters_cevir("deprem_tipi", tip_metni) or "Yuzey_Depremi"

        sallanti_key = kayit.get("sallanti_key")
        if not sallanti_key:
            sallanti_metni = kayit.get("sallanti", "")
            sallanti_key = self.ters_cevir("sallanti", sallanti_metni) or "hafif"

        tip_cevir = self.cevir(tip_key)
        sallanti_cevir = self.cevir(sallanti_key)

        item_text = f"{kayit['zaman']} - M{kayit['buyukluk']} {tip_cevir} ({sallanti_cevir})"
        self.gecmis_listesi.addItem(item_text)
        
    def cevir(self, metin_key):
     ceviriler = {
         "Türkçe": {
        "simulasyonu_baslat": "Simülasyonu Başlat",
        "deprem_tipi": ["Yüzey Depremi", "Derin Deprem", "Artçı"],
        "buyukluk_placeholder": "Deprem büyüklüğü (örn: 5.6)",
        "deprem_bilgisi_baslik": "Deprem Bilgisi",
        "nokta": "Nokta",
        "mesafe": "Mesafe",
        "ulasma_suresi": "Ulaşma Süresi",
        "buyukluk": "Büyüklük",
        "tip": "Tip",
        "sallanti": "Sallantı",
        "gecmisi_gor": "Geçmişi Gör",
        "geri_don": "Geri Dön",
        "uyari_buyukluk": "Lütfen büyüklüğü gir.",
        "uyari_gecerli_sayi": "Geçerli bir sayı gir.",
        "kalan_sure": "Kalan Süre",
        "deprem_geldi": "Deprem Geldi!",
        "şiddetli": "Şiddetli",
        "orta": "Orta",
        "hafif": "Hafif",
        "cok_hafif": "Çok Hafif",
        "deprem_noktasi": "Deprem Noktası",
        "enlem_girisi": "Enlem (36-42):",
        "boylam_girisi": "Boylam (26-45):",
        "Yuzey_Depremi": "Yüzey Depremi",
        "Derin_Deprem": "Derin Deprem",
        "Artci": "Artçı"
        
        
        
    },
    "İngilizce": {
        "simulasyonu_baslat": "Start Simulation",
        "deprem_tipi": ["Surface Earthquake", "Deep Earthquake", "Aftershock"],
        "buyukluk_placeholder": "Magnitude (e.g., 5.6)",
        "deprem_bilgisi_baslik": "Earthquake Info",
        "nokta": "Point",
        "mesafe": "Distance",
        "ulasma_suresi": "Arrival Time",
        "buyukluk": "Magnitude",
        "tip": "Type",
        "sallanti": "Shaking",
        "gecmisi_gor": "View History",
        "geri_don": "Go Back",
        "uyari_buyukluk": "Please enter magnitude.",
        "uyari_gecerli_sayi": "Please enter a valid number.",
        "kalan_sure": "Time Left:",
        "deprem_geldi": "Earthquake Arrived!",
        "şiddetli": "Strong",
        "orta": "Moderate",
        "hafif": "Light",
        "cok_hafif": "Very Light",
        "deprem_noktasi": "Earthquake Location",
        "enlem_girisi": "Latitude (36-42):",
        "boylam_girisi": "Longitude (26-45):",
        "Yuzey_Depremi": "Surface Earthquake",
        "Derin_Deprem": "Deep Earthquake",
        "Artci": "Aftershock"

        },
         "İspanyolca": {
        "simulasyonu_baslat": "Iniciar Simulación",
        "deprem_tipi": ["Terremoto Superficial", "Terremoto Profundo", "Réplica"],
        "buyukluk_placeholder": "Magnitud (p.ej., 5.6)",
        "deprem_bilgisi_baslik": "Información del Terremoto",
        "nokta": "Punto",
        "mesafe": "Distancia",
        "ulasma_suresi": "Tiempo de llegada",
        "buyukluk": "Magnitud",
        "tip": "Tipo",
        "sallanti": "Sacudida",
        "gecmisi_gor": "Ver Historial",
        "geri_don": "Regresar",
        "uyari_buyukluk": "Por favor ingrese la magnitud.",
        "uyari_gecerli_sayi": "Por favor ingrese un número válido.",
        "kalan_sure": "Tiempo Restante:",
        "deprem_geldi": "¡Terremoto Llegó!",
        "şiddetli": "Fuerte",
        "orta": "Moderado",
        "hafif": "Ligero",
        "cok_hafif": "Muy Ligero",
        "deprem_noktasi": "Earthquake Location",
        "enlem_girisi": "Latitude (36-42):",
        "boylam_girisi": "Longitude (26-45):",
        "Yuzey_Depremi": "Terremoto Superficial",
        "Derin_Deprem": "Terremoto Profundo",
        "Artci": "Réplica"
    },
    "Arapça": {
        "simulasyonu_baslat": "بدء المحاكاة",
        "deprem_tipi": ["زلزال سطحي", "زلزال عميق", "هزة ارتدادية"],
        "buyukluk_placeholder": "القوة (مثال: 5.6)",
        "deprem_bilgisi_baslik": "معلومات الزلزال",
        "nokta": "النقطة",
        "mesafe": "المسافة",
        "ulasma_suresi": "وقت الوصول",
        "buyukluk": "القوة",
        "tip": "النوع",
        "sallanti": "الهزة",
        "gecmisi_gor": "عرض السجل",
        "geri_don": "العودة",
        "uyari_buyukluk": "يرجى إدخال القوة.",
        "uyari_gecerli_sayi": "يرجى إدخال رقم صالح.",
        "kalan_sure": "الوقت المتبقي:",
        "deprem_geldi": "وصل الزلزال!",
        "şiddetli": "قوي",
        "orta": "متوسط",
        "hafif": "خفيف",
        "cok_hafif": "خفيف جدًا",
        "deprem_noktasi": "موقع الزلزال",
        "enlem_girisi": "خط العرض (36-42):",
        "boylam_girisi": "خط الطول (26-45):",
        "Yuzey_Depremi": "زلزال سطحي",
        "Derin_Deprem": "زلزال عميق",
        "Artci": "هزة ارتدادية"
    },
    "Fransızca": {
        "simulasyonu_baslat": "Démarrer la Simulation",
        "deprem_tipi": ["Séisme Superficiel", "Séisme Profond", "Réplique"],
        "buyukluk_placeholder": "Magnitude (ex : 5,6)",
        "deprem_bilgisi_baslik": "Informations sur le Séisme",
        "nokta": "Point",
        "mesafe": "Distance",
        "ulasma_suresi": "Temps d'arrivée",
        "buyukluk": "Magnitude",
        "tip": "Type",
        "sallanti": "Secousse",
        "gecmisi_gor": "Voir l'historique",
        "geri_don": "Retour",
        "uyari_buyukluk": "Veuillez saisir la magnitude.",
        "uyari_gecerli_sayi": "Veuillez saisir un nombre valide.",
        "kalan_sure": "Temps restant :",
        "deprem_geldi": "Séisme arrivé !",
        "şiddetli": "Fort",
        "orta": "Modéré",
        "hafif": "Léger",
        "cok_hafif": "Très Léger",
        "deprem_noktasi": "Emplacement du Séisme",
        "enlem_girisi": "Latitude (36-42) :",
        "boylam_girisi": "Longitude (26-45) :",
        "Yuzey_Depremi": "Séisme Superficiel",
        "Derin_Deprem": "Séisme Profond",
        "Artci": "Réplique"
    }
}

       
     return ceviriler.get(self.secili_dil, ceviriler["Türkçe"]).get(metin_key, metin_key)
    def dil_ayarla(self):
     self.btn_simulasyon.setText(self.cevir("simulasyonu_baslat"))
     self.btn_gecmis.setText(self.cevir("gecmisi_gor"))
     self.btn_geri.setText(self.cevir("geri_don"))
     self.setWindowTitle(self.cevir("deprem_bilgisi_baslik"))  # veya "Deprem Simülasyonu" için başka bir anahtar yapabilirsin
     
     
     # Dil değiştiğinde geçmişi güncelle
     self.guncelle_gecmis_listesi()

     # Deprem tipi comboBox dil ayarı
     self.deprem_tipi_combo.clear()
     self.deprem_tipi_combo.addItems(self.cevir("deprem_tipi"))
    
     # Büyüklük input placeholder dil ayarı
     self.buyukluk_input.setPlaceholderText(self.cevir("buyukluk_placeholder"))
    def ters_cevir(self, kategori, metin):
     ceviri_sozluk = {
        "deprem_tipi": {
            # Metin: Anahtar
            "Yüzey Depremi": "Yuzey_Depremi",
            "Derin Deprem": "Derin_Deprem",
            "Artçı": "Artci",
            "Surface Earthquake": "Yuzey_Depremi",
            "Deep Earthquake": "Derin_Deprem",
            "Aftershock": "Artci",
            "Terremoto Superficial": "Yuzey_Depremi",
            "Terremoto Profundo": "Derin_Deprem",
            "Réplica": "Artci",
            "Séisme Superficiel": "Yuzey_Depremi",
            "Séisme Profond": "Derin_Deprem",
            "Réplique": "Artci",
            "زلزال سطحي": "Yuzey_Depremi",
            "زلزال عميق": "Derin_Deprem",
            "هزة ارتدادية": "Artci",
        },
        "sallanti": {
            "Şiddetli": "siddetli",
            "Orta": "orta",
            "Hafif": "hafif",
            "Çok Hafif": "cok_hafif",
            "Strong": "siddetli",
            "Moderate": "orta",
            "Light": "hafif",
            "Very Light": "cok_hafif",
            "Fuerte": "siddetli",
            "Moderado": "orta",
            "Ligero": "hafif",
            "Muy Ligero": "cok_hafif",
            "Fort": "siddetli",
            "Modéré": "orta",
            "Léger": "hafif",
            "Très Léger": "cok_hafif",
            "قوي": "siddetli",
            "متوسط": "orta",
            "خفيف": "hafif",
            "خفيف جدًا": "cok_hafif",
        }
    }
     return ceviri_sozluk.get(kategori, {}).get(metin, None) 
