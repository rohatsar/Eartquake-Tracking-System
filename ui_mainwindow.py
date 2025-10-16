from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from desktop_app_functions import DepremUygulamasi
import sys
from deprem_penceresi import DepremPenceresi
from harita_liste_penceresi import HaritaListePenceresi
import requests
import os, json
from simulasyon_penceresi import SimulasyonPenceresi  # type: ignore
from deprem_risk_penceresi import DepremRiskPenceresi  # type: ignore
from toplanma_penceresi import ToplanmaPenceresi  # type: ignore
from ai_risk_penceresi import AIRiskPenceresi  # type: ignore
from translations_ai import translations_ai_risk # type: ignore

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.secili_dil = "Türkçe"
        self.setWindowTitle("Deprem Bilgi Uygulaması")
        self.setGeometry(300, 100, 1200, 700)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # === STİL GÜNCELLEMESİ BAŞLANGICI ===

        # Ana pencere için genel stil (koyu arka plan)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        # Arka plan resminiz yine de kullanılacak, bu renk resim yüklenmezse diye bir yedektir.
        self.bg_path = r"C:\Users\Rohat\Desktop\Deprem_uygulamasi\data\WhatsApp Görsel 2025-10-13 saat 11.49.49_edde0cf9.jpg"
        self.bg_label = QtWidgets.QLabel(central_widget)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()
        self._guncelle_arka_plan()

        # Başlık label (Görsele uygun metin ve stil eklendi)
        self.title_label = QtWidgets.QLabel("", central_widget)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        

        # Liste ve WebView oluştur
        self.listWidget = QtWidgets.QListWidget()
        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.listWidget.hide()
        self.webView.hide()

        self.depremApp = DepremUygulamasi(self.listWidget, self.webView)

        # Buton stilleri (Görsele uygun olarak tamamen yenilendi)
        buton_stil = """
        QPushButton {
            font-family: 'Montserrat', 'Segoe UI', sans-serif;
            font-size: 15px;
            font-weight: 600;
            color: #00d9ff;
            background-color: transparent;
            border: 2px solid #00d9ff;
            border-radius: 6px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #00d9ff;
            color: #041a29;
        }
        QPushButton:pressed {
            background-color: #00b8d4;
        }
        """
        # Dil seçimi ComboBox stili
        combobox_stil = """
        QComboBox {
            border: 1px solid #00d9ff;
            border-radius: 5px;
            padding: 5px;
            background-color: #081421;
            color: #e0f2f1;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #081421;
            color: #e0f2f1;
            selection-background-color: #00d9ff;
            selection-color: #041a29;
            border: 1px solid #00d9ff;
        }
        """

        # === STİL GÜNCELLEMESİ SONU ===

        # Butonlar
        self.btn_uyari = QtWidgets.QPushButton("Simülasyon Oluştur")
        self.btn_uyari.setStyleSheet(buton_stil)

        self.btn_risk_durumu = QtWidgets.QPushButton("Türkiye Deprem Risk Durumu")
        self.btn_risk_durumu.setStyleSheet(buton_stil)

        self.btn_harita = QtWidgets.QPushButton("Dünya Depremleri")
        self.btn_harita.setStyleSheet(buton_stil)

        self.btn_toplanma = QtWidgets.QPushButton("Toplanma Alanları")
        self.btn_toplanma.setStyleSheet(buton_stil)

        self.btn_rehber = QtWidgets.QPushButton("Acil Durum Rehberi")
        self.btn_rehber.setStyleSheet(buton_stil)

        self.btn_ai_risk = QtWidgets.QPushButton("Yapay Zeka Risk Tahmini")
        self.btn_ai_risk.setStyleSheet(buton_stil)
        self.btn_ai_risk.clicked.connect(self.ai_risk_tiklandi)

        # Dil seçimi
        self.languageCombo = QtWidgets.QComboBox()
        self.languageCombo.addItems(["Türkçe", "İngilizce", "İspanyolca", "Arapça", "Fransızca"])
        self.languageCombo.setStyleSheet(combobox_stil)
        self.languageCombo.currentIndexChanged.connect(self.dil_degisti)

        self.ceviriler = {
            "Türkçe": {
                "alert_button": "Simülasyon Oluştur",
                "risk_button": "Türkiye Deprem Risk Durumu",
                "map_button": "Dünya Depremleri",
                "alert_message": "Deprem uyarısı alındı!",
                "refresh_message": "Depremler yenilendi!",
                "gathering_button": "Toplanma Alanları",
                "map_message": "Harita ve liste gösteriliyor!",
                "guide_button": "Acil Durum Rehberi",
                "ai_button": "Yapay Zeka Risk Tahmini"
            },
            "İngilizce": {
                "alert_button": "Create Simulation",
                "risk_button": "Turkey Earthquake Risk Status",
                "map_button": "World Earthquakes",
                "alert_message": "Earthquake alert received!",
                "refresh_message": "Earthquakes refreshed!",
                "gathering_button": "Gathering Areas",
                "map_message": "Map and list displaying!",
                "guide_button": "Emergency Guide",
                "ai_button": "AI Risk Prediction"
            },
            "İspanyolca": { "alert_button": "Crear Simulación",
                            "risk_button": "Estado del Riesgo Sísmico en Turquía",
                            "map_button": "Terremotos Mundiales", 
                            "alert_message": "¡Alerta de terremoto recibida!",
                            "refresh_message": "¡Terremotos actualizados!",
                            "gathering_button": "Áreas de Reunión", 
                            "map_message": "¡Mapa y lista mostrados!",
                            "guide_button": "Guía de Emergencia", 
                            "ai_button": "Predicción de Riesgo con IA" 
                            },
            
            "Arapça": { "alert_button": "إنشاء المحاكاة",
                        "risk_button": "حالة مخاطر الزلازل في تركيا",
                        "map_button": "زلازل العالم",
                        "alert_message": "تم استلام تنبيه زلزال!",
                        "refresh_message": "تم تحديث الزلازل!",
                        "gathering_button": "مناطق التجمع",
                        "map_message": "يتم عرض الخريطة والقائمة!",
                        "guide_button": "دليل الطوارئ", 
                        "ai_button": "توقع الخطر بالذكاء الاصطناعي"
            },
            "Fransızca": { "alert_button": "Créer une simulation",
                          "risk_button": "État du Risque Sismique en Turquie",
                          "map_button": "Séismes Mondiaux",
                          "alert_message": "Alerte séisme reçue !",
                          "gathering_button": "Zones de Rassemblement",
                          "refresh_message": "Séismes actualisés !",
                          "map_message": "Carte et liste affichées !",
                          "guide_button": "Guide d'Urgence",
                          "ai_button": "Prédiction de Risque par IA" }
        }
        self.dil_degisti()

        # Butonlara tıklama bağlama
        self.btn_uyari.clicked.connect(self.simulasyon_tiklandi)
        self.btn_risk_durumu.clicked.connect(self.risk_durumu_tiklandi)
        self.btn_harita.clicked.connect(self.harita_tiklandi)
        self.btn_toplanma.clicked.connect(self.toplanma_alanlarini_ac)
        self.btn_rehber.clicked.connect(self.rehber_tiklandi)

        # Layout tasarımı
        ust_layout = QtWidgets.QHBoxLayout()
        ust_layout.addWidget(self.title_label, 1)
        ust_layout.addWidget(self.languageCombo)

        buton_layout = QtWidgets.QHBoxLayout()
        buton_layout.addWidget(self.btn_uyari)
        buton_layout.addWidget(self.btn_risk_durumu)
        buton_layout.addWidget(self.btn_harita)
        buton_layout.addWidget(self.btn_toplanma)
        buton_layout.addWidget(self.btn_ai_risk)
        buton_layout.addWidget(self.btn_rehber)

        icerik_layout = QtWidgets.QHBoxLayout()
        icerik_layout.addWidget(self.listWidget, 1)
        icerik_layout.addWidget(self.webView, 3)

        ana_layout = QtWidgets.QVBoxLayout(central_widget)
        ana_layout.addLayout(ust_layout)
        ana_layout.addLayout(icerik_layout)
        ana_layout.addSpacing(80)
        ana_layout.addLayout(buton_layout)

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon("deprem.png"))
        self.tray_icon.show()

        self.son_deprem_koordinatlar = None
        self.tray_icon.messageClicked.connect(self.bildirim_tiklandi)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.anlik_deprem_kontrol_et)
        self.timer.start(5 * 60 * 1000)

        self.son_deprem_id = None
        self.anlik_deprem_kontrol_et()

    # === DİĞER FONKSİYONLARINIZ DEĞİŞMEDEN OLDUĞU GİBİ KALIYOR... ===

    def dil_degisti(self):
        secilen_dil = self.languageCombo.currentText()
        ceviri = self.ceviriler.get(secilen_dil, self.ceviriler["Türkçe"])
        self.btn_uyari.setText(ceviri["alert_button"])
        self.btn_risk_durumu.setText(ceviri["risk_button"])
        self.btn_harita.setText(ceviri["map_button"])
        self.btn_toplanma.setText(ceviri["gathering_button"])
        self.btn_rehber.setText(ceviri["guide_button"])
        self.btn_ai_risk.setText(ceviri.get("ai_button", self.btn_ai_risk.text()))
        self.alert_message = ceviri["alert_message"]
        self.refresh_message = ceviri["refresh_message"]
        self.map_message = ceviri["map_message"]
        self.secili_dil = secilen_dil
        
    def uyari_tiklandi(self):
        QtWidgets.QMessageBox.information(self, "Uyarı", self.alert_message)

    def risk_durumu_tiklandi(self):
        secilen_dil = self.languageCombo.currentText()
        self.secili_dil = secilen_dil
        try:
            self.risk_pencere = DepremRiskPenceresi(secilen_dil=self.secili_dil)
            self.risk_pencere.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Deprem risk penceresi açılamadı:\n{str(e)}")

    def harita_tiklandi(self):
        try:
            if not hasattr(self, "harita_pencere") or self.harita_pencere is None:
                self.harita_pencere = HaritaListePenceresi(parent=self)
            self.harita_pencere.show()
            self.hide()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Pencere açılamadı:\n{str(e)}")

    def resizeEvent(self, event):
        self._guncelle_arka_plan()
        return super().resizeEvent(event)

    def _guncelle_arka_plan(self):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        pixmap = QtGui.QPixmap(self.bg_path).scaled(
            self.size(),
            QtCore.Qt.IgnoreAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self.bg_label.setPixmap(pixmap)

    def anlik_deprem_kontrol_et(self):
        print("Anlık deprem kontrolü çalıştı.")
        try:
            # doğrudan dosya yolu kullanmak daha güvenli
            dosya_yolu = r"C:\Users\Rohat\Desktop\Deprem_uygulamasi\son_depremler.json"
            with open(dosya_yolu, "r", encoding="utf-8") as dosya:
                depremler = json.load(dosya)
            for deprem in depremler:
                tarih = deprem.get("tarih", "")
                il = deprem.get("ilce", "")
                buyukluk = float(deprem.get("ml", 0))
                deprem_id = deprem.get("id")
                enlem = float(deprem.get("enlem", 0))
                boylam = float(deprem.get("boylam", 0))
                if buyukluk >= 4.0:
                    if deprem_id != self.son_deprem_id:
                        mesaj = f"{il} bölgesinde {buyukluk} büyüklüğünde deprem!\nTarih: {tarih}"
                        self.son_deprem_koordinatlar = (enlem, boylam)
                        self.tray_icon.showMessage("Deprem Bildirimi", mesaj, QtWidgets.QSystemTrayIcon.Information)
                        self.son_deprem_id = deprem_id
                        break
        except Exception as e:
            print("Deprem kontrol hatası:", e)

    def bildirim_tiklandi(self):
        if not self.son_deprem_koordinatlar:
            return
        enlem, boylam = self.son_deprem_koordinatlar
        if not hasattr(self, "harita_pencere") or self.harita_pencere is None:
            self.harita_pencere = HaritaListePenceresi(parent=self)
        self.harita_pencere.show()
        self.hide()
        # beklenen method varsa çalıştır
        if hasattr(self.harita_pencere, "zoom_to_location"):
            self.harita_pencere.zoom_to_location(enlem, boylam)

    def simulasyon_tiklandi(self):
        secilen_dil = self.languageCombo.currentText()
        self.simulasyon_pencere = SimulasyonPenceresi(secilen_dil)
        self.simulasyon_pencere.show()

    def toplanma_alanlarini_ac(self):
        try:
            self.toplanma_pencere = ToplanmaPenceresi()
            self.toplanma_pencere.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Toplanma alanları açılamadı:\n{str(e)}")

    def rehber_tiklandi(self):
        try:
            if not hasattr(self, "guide_data"):
                dosya_yolu = r"C:\Users\Rohat\Desktop\Deprem_uygulamasi\data\earthquakeGuide.json"
                with open(dosya_yolu, "r", encoding="utf-8") as f:
                    self.guide_data = json.load(f)
            lang_code = {
                "Türkçe": "tr",
                "İngilizce": "en",
                "Fransızca": "fr",
                "Arapça": "ar",
                "İspanyolca": "es"
            }.get(self.secili_dil, "tr")
            guide_title = self.guide_data.get("guide_title", {}).get(lang_code, "Acil Durum Rehberi")
            title = self.guide_data.get("drop_cover_hold", {}).get(lang_code, "")
            steps = self.guide_data.get("steps", {}).get(lang_code, [])
            dialog = RehberDialog(guide_title, title, steps, parent=self)
            dialog.setModal(True)
            dialog.exec_()
        except Exception as e:
            import traceback
            QtWidgets.QMessageBox.critical(self, "Hata", f"{traceback.format_exc()}")

    def ai_risk_tiklandi(self):
        try:
            self.ai_risk_pencere = AIRiskPenceresi(secilen_dil=self.secili_dil)
            self.ai_risk_pencere.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"AI Risk Penceresi açılamadı:\n{str(e)}")

# RehberDialog sınıfı da temaya uygun olarak güncellendi
class RehberDialog(QtWidgets.QDialog):
    def __init__(self, guide_title, title, steps, parent=None):
        super().__init__(parent)
        self.setWindowTitle(guide_title)
        self.setMinimumSize(500, 600)

        # Genel stil
        self.setStyleSheet("""
            QDialog {
                background-color: #081421;
                border-radius: 12px;
            }
            QLabel {
                font-family: "Segoe UI";
                color: #e0f2f1;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        # Başlık
        label_title = QtWidgets.QLabel(f"📖 <b>{title}</b>")
        label_title.setAlignment(QtCore.Qt.AlignCenter)
        label_title.setStyleSheet("font-size:18px; margin:10px; color:#00d9ff;")
        layout.addWidget(label_title)

        # Adımlar için liste
        list_widget = QtWidgets.QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background: #041a29;
                border: 1px solid #00d9ff;
                border-radius: 8px;
                padding: 10px;
                color: #e0f2f1;
            }
            QListWidget::item {
                font-size: 14px;
                padding: 8px;
                border-bottom: 1px solid #1a2b3c;
            }
            QListWidget::item:selected {
                background: #00d9ff;
                color: #041a29;
                border-radius: 6px;
            }
        """)

        icons = ["✔", "⚠", "⛑", "🚪", "🚗", "💡", "🔥", "📡", "📍", "🏞", "✅"]
        for i, step in enumerate(steps):
            item = QtWidgets.QListWidgetItem(f"{icons[i % len(icons)]}  {i+1}. {step}")
            list_widget.addItem(item)

        layout.addWidget(list_widget)

        # Kapat butonu
        btn_ok = QtWidgets.QPushButton("❌")
        btn_ok.setStyleSheet("""
            QPushButton {
                background: #00d9ff;
                color: #041a29;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: #33eaff;
            }
        """)
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok, alignment=QtCore.Qt.AlignCenter)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pencere = MainWindow()
    pencere.show()
    sys.exit(app.exec_()) 
