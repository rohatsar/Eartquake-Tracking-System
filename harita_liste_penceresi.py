
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore, QtGui
from desktop_app_functions import DepremUygulamasi
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime

# --- Custom page: link tıklamalarını yakala ve sistem tarayıcısında aç ---
class CustomWebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def acceptNavigationRequest(self, url, nav_type, isMainFrame):
        # Eğer linke tıklanmışsa (NavigationTypeLinkClicked), sistem tarayıcısında aç
        if nav_type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeLinkClicked:
            try:
                QtGui.QDesktopServices.openUrl(url)
            except Exception:
                pass
            return False
        # Diğer tüm istekleri normal işleme bırak
        return super().acceptNavigationRequest(url, nav_type, isMainFrame)


class HaritaListePenceresi(QtWidgets.QMainWindow):
    def __init__(self, parent=None, secili_dil=None):
        super().__init__(parent)
        self.parent_window = parent
        # --- Açık detay/popup referansını saklamak için ---
        self.detail_dialog = None
        # Tema durumu başlangıçta kapalı
        self.dark_mode_active = False

        # Maksimum getirilecek kayıt sayısı (isteğe göre 5000 yaptık)
        self.max_results = 5000

        # --- Esnek dil eşlemesi: hem gösterim adını hem kısa kodu kabul eder ---
        self._lang_map = {
            "Türkçe": "tr", "İngilizce": "en", "İspanyolca": "es",
            "Arapça": "ar", "Fransızca": "fr",
            "tr": "tr", "en": "en", "es": "es", "ar": "ar", "fr": "fr"
        }

        # --- Çeviri sözlükleri (aynı anahtarlar kullandığınız şekilde) ---
        self.translations = {
            "tr": {
                "Tarih Aralığı:": "Tarih Aralığı:",
                "Büyüklük Aralığı:": "Büyüklük Aralığı:",
                "Deprem Tipi:": "Deprem Tipi:",
                "Filtrele": "Filtrele",
                "Koyu Tema": "Koyu Tema",
                "Son 24 saat:": "Son 24 saat",
                "Son 7 gün:": "Son 7 gün",
                "Son 30 gün:": "Son 30 gün",
                "Ortalama Büyüklük:": "Ortalama Büyüklük",
                "Hatalı Giriş": "Hatalı Giriş",
                "BaslangicBuyukBitis": "Başlangıç tarihi bitiş tarihinden büyük olamaz.",
                "MinBuyukMaxBuyuk": "Minimum büyüklük, maksimumdan büyük olamaz.",
                "Deprem Detayları": "Deprem Detayları",
                "Grafik Baslik": "Deprem Sıklığı",
                "Adet": "adet",
                "all": "Hepsi",
                "shallow": "Sığ (<70 km)",
                "deep": "Derin (>300 km)"
            },
            "en": {
                "Tarih Aralığı:": "Date Range:",
                "Büyüklük Aralığı:": "Magnitude Range:",
                "Deprem Tipi:": "Earthquake Type:",
                "Filtrele": "Filter",
                "Koyu Tema": "Dark Theme",
                "Son 24 saat:": "Last 24h",
                "Son 7 gün:": "Last 7d",
                "Son 30 gün:": "Last 30d",
                "Ortalama Büyüklük:": "Average Magnitude",
                "Hatalı Giriş": "Invalid Input",
                "BaslangicBuyukBitis": "Start date cannot be after end date.",
                "MinBuyukMaxBuyuk": "Minimum magnitude cannot be greater than maximum.",
                "Deprem Detayları": "Earthquake Details",
                "Grafik Baslik": "Earthquake Frequency",
                "Adet": "events",
                "all": "All",
                "shallow": "Shallow (<70 km)",
                "deep": "Deep (>300 km)"
            },
            "es": {
                "Tarih Aralığı:": "Rango de Fechas:",
                "Büyüklük Aralığı:": "Rango de Magnitud:",
                "Deprem Tipi:": "Tipo de Terremoto:",
                "Filtrele": "Filtrar",
                "Koyu Tema": "Tema Oscuro",
                "Son 24 saat:": "Últimas 24h",
                "Son 7 gün:": "Últimos 7d",
                "Son 30 gün:": "Últimos 30d",
                "Ortalama Büyüklük:": "Magnitud Promedio",
                "Hatalı Giriş": "Entrada Inválida",
                "BaslangicBuyukBitis": "La fecha de inicio no puede ser posterior a la fecha de fin.",
                "MinBuyukMaxBuyuk": "La magnitud mínima no puede ser mayor que la máxima.",
                "Deprem Detayları": "Detalles del Terremoto",
                "Grafik Baslik": "Frecuencia de Terremotos",
                "Adet": "cantidad",
                "all": "Todos",
                "shallow": "Superficiales (<70 km)",
                "deep": "Profundos (>300 km)"
            },
            "fr": {
                "Tarih Aralığı:": "Plage de Dates:",
                "Büyüklük Aralığı:": "Plage de Magnitude:",
                "Deprem Tipi:": "Type de Séisme:",
                "Filtrele": "Filtrer",
                "Koyu Tema": "Thème Sombre",
                "Son 24 saat:": "Dernières 24h",
                "Son 7 gün:": "Derniers 7j",
                "Son 30 gün:": "Derniers 30j",
                "Ortalama Büyüklük:": "Magnitude Moyenne",
                "Hatalı Giriş": "Entrée Invalide",
                "BaslangicBuyukBitis": "La date de début ne peut pas être après la date de fin.",
                "MinBuyukMaxBuyuk": "La magnitude minimale ne peut pas être supérieure à la maximale.",
                "Deprem Detayları": "Détails du Séisme",
                "Grafik Baslik": "Fréquence des Séismes",
                "Adet": "nombre",
                "all": "Tous",
                "shallow": "Peu Profonds (<70 km)",
                "deep": "Profonds (>300 km)"
            },
            "ar": {
                "Tarih Aralığı:": "نطاق التاريخ:",
                "Büyüklük Aralığı:": "نطاق القوة:",
                "Deprem Tipi:": "نوع الزلزال:",
                "Filtrele": "تصفية",
                "Koyu Tema": "الوضع الداكن",
                "Son 24 saat:": "آخر 24 ساعة",
                "Son 7 gün:": "آخر 7 أيام",
                "Son 30 gün:": "آخر 30 يومًا",
                "Ortalama Büyüklük:": "متوسط القوة",
                "Hatalı Giriş": "إدخال غير صالح",
                "BaslangicBuyukBitis": "لا يمكن أن يكون تاريخ البدء بعد تاريخ الانتهاء.",
                "MinBuyukMaxBuyuk": "لا يمكن أن تكون القوة الدنيا أكبر من الحد الأقصى.",
                "Deprem Detayları": "تفاصيل الزلزال",
                "Grafik Baslik": "تكرار الزلازل",
                "Adet": "العدد",
                "all": "الكل",
                "shallow": "سطحية (<70 كم)",
                "deep": "عميقة (>300 كم)"
            }
        }

        # --- Deprem tipi eşleştirmesi (her dil için güncellenecek) ---
        self.deprem_tipi_eslestirme = {}
        # --- Dark style ---
        self.dark_style = """
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QListWidget {
                background-color: #3c3f41; color: #ffffff; border: 1px solid #555555;
            }
            QPushButton { background-color: #444444; color: #ffffff; border: 1px solid #5a5a5a; padding: 5px; }
            QPushButton:hover { background-color: #5a5a5a; }
            QTableWidget { background-color: #2b2b2b; color: #ffffff; gridline-color: #555555; }
            QHeaderView::section { background-color: #3c3f41; color: #ffffff; border: 1px solid #444; }
            QMessageBox { background-color: #2b2b2b; color: #ffffff; }
        """

        # --- Dil çözümü: parametre veya parent'tan al ---
        incoming = secili_dil if secili_dil is not None else (parent.secili_dil if parent and hasattr(parent, "secili_dil") else "Türkçe")
        self.secili_dil = self._lang_map.get(incoming, incoming if incoming in self._lang_map else "tr")

        # --- UI başlangıcı ---
        self.setWindowTitle("Deprem Harita ve Liste")
        self.setGeometry(350, 150, 1200, 750)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        ana_layout = QtWidgets.QVBoxLayout(central_widget)

        # Filtreler
        filtre_layout = QtWidgets.QHBoxLayout()
        self.labelTarih = QtWidgets.QLabel()
        self.dateEditBaslangic = QtWidgets.QDateEdit(self)
        self.dateEditBaslangic.setCalendarPopup(True)
        self.dateEditBaslangic.setDate(QtCore.QDate.currentDate().addDays(-7))
        self.dateEditBitis = QtWidgets.QDateEdit(self)
        self.dateEditBitis.setCalendarPopup(True)
        self.dateEditBitis.setDate(QtCore.QDate.currentDate())

        self.labelBuyukluk = QtWidgets.QLabel()
        self.spinMinMag = QtWidgets.QDoubleSpinBox()
        self.spinMinMag.setRange(0.0, 10.0)
        self.spinMinMag.setSingleStep(0.1)
        self.spinMinMag.setValue(0.0)
        self.spinMaxMag = QtWidgets.QDoubleSpinBox()
        self.spinMaxMag.setRange(0.0, 10.0)
        self.spinMaxMag.setSingleStep(0.1)
        self.spinMaxMag.setValue(10.0)

        self.labelDerinlik = QtWidgets.QLabel()
        self.comboDerinlik = QtWidgets.QComboBox()

        self.tarihFiltreleBtn = QtWidgets.QPushButton()
        self.tarihFiltreleBtn.clicked.connect(self.tarih_filtrele)

        filtre_layout.addWidget(self.labelTarih)
        filtre_layout.addWidget(self.dateEditBaslangic)
        filtre_layout.addWidget(QtWidgets.QLabel(" - "))
        filtre_layout.addWidget(self.dateEditBitis)
        filtre_layout.addSpacing(20)
        filtre_layout.addWidget(self.labelBuyukluk)
        filtre_layout.addWidget(self.spinMinMag)
        filtre_layout.addWidget(QtWidgets.QLabel(" - "))
        filtre_layout.addWidget(self.spinMaxMag)
        filtre_layout.addSpacing(20)
        filtre_layout.addWidget(self.labelDerinlik)
        filtre_layout.addWidget(self.comboDerinlik)
        filtre_layout.addSpacing(20)
        filtre_layout.addWidget(self.tarihFiltreleBtn)

        self.tema_toggle = QtWidgets.QCheckBox()
        self.tema_toggle.stateChanged.connect(self.temayi_degistir)
        filtre_layout.addWidget(self.tema_toggle)

        ana_layout.addLayout(filtre_layout)

        # Harita ve liste
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.listWidget = QtWidgets.QListWidget()
        splitter.addWidget(self.listWidget)

        # WebView: özel page atayıp linkleri yakala
        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.webView.setPage(CustomWebEnginePage(self.webView))
        

 
        splitter.addWidget(self.webView)
        splitter.setSizes([300, 900])
        ana_layout.addWidget(splitter)

        # Deprem uygulaması
        self.depremApp = DepremUygulamasi(self.listWidget, self.webView)
        try:
            self.depremApp.harita_goster()
        except Exception:
            pass
        self.listWidget.itemClicked.connect(self.deprem_detay_goster)

        # İstatistik paneli
        self.istatistik_paneli_olustur()
        ana_layout.addWidget(self.istatistik_widget)

        # Deprem tipi eşleştirmeyi ilk defa oluştur
        self._guncelle_deprem_tipi_eslestirme()

        # Parent dil bağlantıları ve ilk dil uygulama
        if parent is not None:
            if hasattr(parent, "languageCombo") and isinstance(parent.languageCombo, QtWidgets.QComboBox):
                parent.languageCombo.currentIndexChanged.connect(self._on_parent_language_changed)
            if hasattr(parent, "secili_dil"):
                resolved = self._lang_map.get(parent.secili_dil, parent.secili_dil)
                self.dili_degistir(resolved)
            else:
                self.dili_degistir(self.secili_dil)
        else:
            self.dili_degistir(self.secili_dil)
        
        
        # Başlangıçta veriyi çek
        self.tarih_filtrele()
        
        
    # -------------------------
    # Parent dil değişimini yakalayıcı
    # -------------------------
    def _on_parent_language_changed(self, index):
        parent = self.parent_window
        if not parent:
            return
        text = parent.languageCombo.currentText()
        kod = self._lang_map.get(text, text)
        self.dili_degistir(kod)

    # -------------------------
    # Deprem tipi eşleştirme
    # -------------------------
    def _guncelle_deprem_tipi_eslestirme(self):
        t = self.translations.get(self.secili_dil, self.translations["tr"])
        self.deprem_tipi_eslestirme = {
            t["all"]: "all",
            t["shallow"]: "shallow",
            t["deep"]: "deep"
        }

    # -------------------------
    # Dil değiştirme
    # -------------------------
    def dili_degistir(self, yeni_dil):
        if yeni_dil in self._lang_map:
            yeni_dil = self._lang_map[yeni_dil]
        self.secili_dil = yeni_dil
        t = self.translations.get(self.secili_dil, self.translations["tr"])

        # Metin yönü
        if self.secili_dil == "ar":
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
            align = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)
            align = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

        # Etiketleri güncelle
        self.labelTarih.setText(t["Tarih Aralığı:"])
        self.labelTarih.setAlignment(align)
        self.labelBuyukluk.setText(t["Büyüklük Aralığı:"])
        self.labelBuyukluk.setAlignment(align)
        self.labelDerinlik.setText(t["Deprem Tipi:"])
        self.labelDerinlik.setAlignment(align)
        self.tarihFiltreleBtn.setText(t["Filtrele"])
        self.tema_toggle.setText(t["Koyu Tema"])

        # Deprem tipi eşleştirmeyi güncelle ve combobox içeriğini yenile
        self._guncelle_deprem_tipi_eslestirme()
        current_api_value = self.get_deprem_tipi_api_degeri()
        self.comboDerinlik.clear()
        deprem_tipleri = [t["all"], t["shallow"], t["deep"]]
        self.comboDerinlik.addItems(deprem_tipleri)

        # Arapça için hizalama (görünüm)
        if self.secili_dil == "ar":
            self.comboDerinlik.setEditable(True)
            self.comboDerinlik.lineEdit().setAlignment(QtCore.Qt.AlignRight)
            self.comboDerinlik.setEditable(False)

        # Mevcut API değerini koru (çözüm: önceki eşleştirmeden api değeri al)
        yeni_metin = next((metin for metin, api_val in self.deprem_tipi_eslestirme.items()
                           if api_val == current_api_value), deprem_tipleri[0])
        index = self.comboDerinlik.findText(yeni_metin)
        if index >= 0:
            self.comboDerinlik.setCurrentIndex(index)

        # İstatistikleri güncelle
        self.istatistikleri_guncelle()

    # Public, ana pencereden çağrılabilir
    def manuel_dil_degistir(self, yeni_dil):
        kod = self._lang_map.get(yeni_dil, yeni_dil)
        self.dili_degistir(kod)

    # -------------------------
    # Filtreleme ve veri çekme
    # -------------------------
    def get_deprem_tipi_api_degeri(self):
        current_text = self.comboDerinlik.currentText() if hasattr(self, "comboDerinlik") else ""
        return self.deprem_tipi_eslestirme.get(current_text, "all")

    def tarih_filtrele(self):
        t = self.translations.get(self.secili_dil, self.translations["tr"])
        baslangic = self.dateEditBaslangic.date()
        bitis = self.dateEditBitis.date()
        if baslangic > bitis:
            QtWidgets.QMessageBox.warning(self, t["Hatalı Giriş"], t["BaslangicBuyukBitis"])
            return
        min_mag = self.spinMinMag.value()
        max_mag = self.spinMaxMag.value()
        if min_mag > max_mag:
            QtWidgets.QMessageBox.warning(self, t["Hatalı Giriş"], t["MinBuyukMaxBuyuk"])
            return

        deprem_tipi = self.get_deprem_tipi_api_degeri()
        # Deprem verilerini çek (DepremUygulamasi içinde beklenen imza)
        try:
            self.depremApp.deprem_verilerini_cek(
                start_date=baslangic.toString("yyyy-MM-dd"),
                end_date=bitis.toString("yyyy-MM-dd"),
                min_magnitude=min_mag,
                max_magnitude=max_mag,
                deprem_tipi=deprem_tipi,
                limit=self.max_results    # <-- limit eklendi
            )
        except Exception as e:
            print("deprem_verilerini_cek hata:", e)

        # İstatistikleri güncelle
        self.istatistikleri_guncelle()

        # --- DEBUG: kaç kayıt geldiğini kontrol et (isteğe bağlı) ---
        toplam = len(getattr(self.depremApp, 'deprem_data', []))
        print(f"[DEBUG] İstek limit: {self.max_results} — Çekilen kayıt sayısı: {toplam}")

    # -------------------------
    # Deprem detayları
    # -------------------------
    def deprem_detay_goster(self, item):
        t = self.translations.get(self.secili_dil, self.translations["tr"])
        index = item.data(QtCore.Qt.UserRole)
        if not isinstance(index, int):
            return

        # Güvenli şekilde detay al
        try:
            detay = self.depremApp.deprem_data[index]
        except Exception:
            return

        lokasyon = detay.get("place", "Bilinmiyor")
        buyukluk = detay.get("mag", "Bilinmiyor")
        derinlik = detay.get("depth", "Bilinmiyor")
        try:
            saat = datetime.datetime.utcfromtimestamp(detay.get("time", 0) / 1000).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            saat = "Bilinmiyor"
        fay_hatti = detay.get("fault", "Bilinmiyor")
        link = detay.get("url", "Yok")
        detay_mesaji = f"""Lokasyon: {lokasyon}
Büyüklük: {buyukluk}
Derinlik: {derinlik} km
Saat: {saat}
Fay Hattı: {fay_hatti}
Link: {link}
"""

        # Eğer önceki dialog açıksa önce kapat/temizle (çift kapanma hatalarını önlemek için)
        try:
            if getattr(self, "detail_dialog", None) is not None:
                try:
                    if self.detail_dialog.isVisible():
                        self.detail_dialog.close()
                except Exception:
                    pass
                try:
                    self.c.deleteLater()
                except Exception:
                    pass
                self.detail_dialog = None
        except Exception:
            pass

        # Yeni dialog oluştur
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(t["Deprem Detayları"])
        layout = QtWidgets.QVBoxLayout(dialog)

        text_widget = QtWidgets.QTextEdit(dialog)
        text_widget.setReadOnly(True)
        text_widget.setPlainText(detay_mesaji)
        layout.addWidget(text_widget)

        btn_close = QtWidgets.QPushButton(self.tr("Kapat"), dialog)
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)

        if getattr(self, "dark_mode_active", False):
            dialog.setStyleSheet(self.dark_style)

        # Referansı sakla ve kapandığında temizle
        self.detail_dialog = dialog
        dialog.finished.connect(self._cleanup_detail_dialog)

        # Modal olarak göster
        dialog.exec_()

    def _cleanup_detail_dialog(self, result=None):
        try:
            if getattr(self, "detail_dialog", None) is not None:
                try:
                    self.detail_dialog.deleteLater()
                except Exception:
                    pass
        finally:
            self.detail_dialog = None

    def closeEvent(self, event):
        # Eğer detay dialog açıksa önce kapat/temizle
        try:
            if getattr(self, "detail_dialog", None) is not None:
                try:
                    if self.detail_dialog.isVisible():
                        self.detail_dialog.close()
                except Exception:
                    pass
                try:
                    self.detail_dialog.deleteLater()
                except Exception:
                    pass
                self.detail_dialog = None
        except Exception:
            pass

        if self.parent():
            # parent üzerinde referans varsa temizle
            if hasattr(self.parent(), "harita_pencere"):
                self.parent().harita_pencere = None
            self.parent().show()
        event.accept()

    # -------------------------
    # İstatistik paneli
    # -------------------------
    def istatistik_paneli_olustur(self):
        self.figure = Figure(figsize=(4, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.stats_layout = QtWidgets.QVBoxLayout()
        self.labelIst1 = QtWidgets.QLabel()
        self.labelIst2 = QtWidgets.QLabel()
        self.labelIst3 = QtWidgets.QLabel()
        self.labelOrtalama = QtWidgets.QLabel()
        self.stats_layout.addWidget(self.labelIst1)
        self.stats_layout.addWidget(self.labelIst2)
        self.stats_layout.addWidget(self.labelIst3)
        self.stats_layout.addWidget(self.labelOrtalama)
        self.stats_layout.addWidget(self.canvas)
        self.istatistik_widget = QtWidgets.QWidget()
        self.istatistik_widget.setLayout(self.stats_layout)

    def istatistikleri_guncelle(self):
        t = self.translations.get(self.secili_dil, self.translations["tr"])
        now = datetime.datetime.utcnow()
        son24saat, son7gun, son30gun, toplam_mag, adet = 0, 0, 0, 0, 0
        for d in getattr(self.depremApp, 'deprem_data', []):
            try:
                zaman = datetime.datetime.utcfromtimestamp(d["time"] / 1000)
                fark = (now - zaman).total_seconds()
                mag = float(d["mag"])
                if fark <= 86400: son24saat += 1
                if fark <= 604800: son7gun += 1
                if fark <= 2592000: son30gun += 1
                toplam_mag += mag
                adet += 1
            except (KeyError, ValueError, TypeError):
                continue
        ortalama = round(toplam_mag / adet, 2) if adet > 0 else 0.0
        self.labelIst1.setText(f"{t['Son 24 saat:']}: {son24saat} {t['Adet']}")
        self.labelIst2.setText(f"{t['Son 7 gün:']}: {son7gun} {t['Adet']}")
        self.labelIst3.setText(f"{t['Son 30 gün:']}: {son30gun} {t['Adet']}")
        self.labelOrtalama.setText(f"{t['Ortalama Büyüklük:']}: {ortalama}")

        # Grafik
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if getattr(self, "dark_mode_active", False):
            bg_color = '#2b2b2b'
            text_color = 'white'
            grid_color = '#555555'
        else:
            bg_color = 'white'
            text_color = 'black'
            grid_color = '#cccccc'
        ax.set_facecolor(bg_color)
        self.figure.patch.set_facecolor(bg_color)
        periods = [t['Son 24 saat:'], t['Son 7 gün:'], t['Son 30 gün:']]
        values = [son24saat, son7gun, son30gun]

        # Her bar için farklı renkler
        colors = ['#3498db', '#2ecc71', '#e67e22']  # mavi, yeşil, turuncu
        bars = ax.bar(periods, values, color=colors, edgecolor='black')

        ax.set_title(t["Grafik Baslik"], color=text_color)
        ax.set_ylabel(t["Adet"], color=text_color)
        ax.tick_params(axis='x', colors=text_color, rotation=15)
        ax.tick_params(axis='y', colors=text_color)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7, color=grid_color)
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1, f'{value}', ha='center', va='bottom', color=text_color)
        self.figure.tight_layout()
        try:
            self.canvas.draw()
        except Exception:
            pass

    # -------------------------
    # Tema
    # -------------------------
    def temayi_degistir(self, state):
        if state == QtCore.Qt.Checked:
            self.setStyleSheet(self.dark_style)
            self.dark_mode_active = True
        else:
            self.setStyleSheet("")
            self.dark_mode_active = False
        self.istatistikleri_guncelle()   

    # -------------------------
    # Zoom (MainWindow bildirim tıklaması kullanıyor)
    # -------------------------
    def zoom_to_location(self, lat, lon, zoom=8):
        try:
            if hasattr(self.depremApp, "zoom_to_location"):
                self.depremApp.zoom_to_location(lat, lon, zoom=zoom)
            else:
                pass
        except Exception:
            pass
