from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
import requests, os
from datetime import datetime
import folium

class DepremPenceresi(QtWidgets.QDialog):
    def __init__(self, dil="Türkçe"):
        super().__init__()
        self.dil = dil
        self.ceviriler = {
            "Türkçe": {
                "title": "Deprem Bilgileri",
                "refresh_button": "Depremleri Yenile",
                "close_button": "Pencereyi Kapat",
                "error_title": "Hata",
                "error_message_prefix": "Veri çekilemedi:\n"
            },
            "İngilizce": {
                "refresh_button": "Refresh Earthquakes",
                "close_button": "Close Window",
                "error_title": "Error",
                "error_message_prefix": "Data could not be fetched:\n"
            },
            "İspanyolca": {
                "title": "Información de Terremotos",
                "refresh_button": "Actualizar Terremotos",
                "close_button": "Cerrar Ventana",
                "error_title": "Error",
                "error_message_prefix": "No se pudieron obtener los datos:\n"
            },
            "Arapça": {
                "title": "معلومات الزلازل",
                "refresh_button": "تحديث الزلازل",
                "close_button": "إغلاق النافذة",
                "error_title": "خطأ",
                "error_message_prefix": "تعذر جلب البيانات:\n"
            },
            "Fransızca": {
                "title": "Informations sur les Séismes",
                "refresh_button": "Actualiser les Séismes",
                "close_button": "Fermer la Fenêtre",
                "error_title": "Erreur",
                "error_message_prefix": "Impossible de récupérer les données:\n"
            }
        }

        ceviri = self.ceviriler.get(self.dil, self.ceviriler["Türkçe"])
        self.setWindowTitle(ceviri["title"])
        self.setGeometry(400, 200, 900, 600)

        layout = QtWidgets.QVBoxLayout(self)

        # Deprem listesi
        self.listWidget = QtWidgets.QListWidget()
        layout.addWidget(self.listWidget)

        # Harita görüntüsü
        self.webView = QtWebEngineWidgets.QWebEngineView()
        layout.addWidget(self.webView)

        # Butonlar
        butonlar = QtWidgets.QHBoxLayout()

        self.yenileBtn = QtWidgets.QPushButton(ceviri["refresh_button"])
        self.yenileBtn.clicked.connect(self.deprem_verilerini_cek)
        butonlar.addWidget(self.yenileBtn)

        self.kapatBtn = QtWidgets.QPushButton(ceviri["close_button"])
        self.kapatBtn.clicked.connect(self.close)
        butonlar.addWidget(self.kapatBtn)

        layout.addLayout(butonlar)

        # İlk veri çekimi
        self.deprem_verilerini_cek()

    def deprem_verilerini_cek(self):
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "starttime": "2025-06-01",
            "minmagnitude": 4.5,
            "orderby": "time",
            "limit": 50
        }
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            depremler = data["features"]
            self.listWidget.clear()

            # Harita oluştur
            m = folium.Map(location=[39.0, 35.0], zoom_start=5)

            for deprem in depremler:
                yer = deprem["properties"]["place"]
                buyukluk = deprem["properties"]["mag"]
                zaman_ms = deprem["properties"]["time"]
                zaman = datetime.utcfromtimestamp(zaman_ms / 1000).strftime("%Y-%m-%d %H:%M")

                # Listeye ekle
                item = QtWidgets.QListWidgetItem(f"{yer} - M {buyukluk} - {zaman}")
                if buyukluk >= 6.0:
                    item.setForeground(QtGui.QColor("red"))
                self.listWidget.addItem(item)

                # Haritaya marker ekle
                coords = deprem["geometry"]["coordinates"]
                lon, lat = coords[0], coords[1]
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5 + buyukluk,
                    popup=f"{yer}<br>Büyüklük: M{buyukluk}<br>Zaman: {zaman}",
                    color="red" if buyukluk >= 6.0 else "orange",
                    fill=True,
                    fill_color="red" if buyukluk >= 6.0 else "orange"
                ).add_to(m)

            # Haritayı kaydet ve göster
            m.save("harita.html")
            file_path = os.path.abspath("harita.html")
            self.webView.load(QtCore.QUrl.fromLocalFile(file_path))

        except requests.exceptions.RequestException as e:
            ceviri = self.ceviriler.get(self.dil, self.ceviriler["Türkçe"])
            QtWidgets.QMessageBox.warning(self, ceviri["error_title"], ceviri["error_message_prefix"] + str(e))
