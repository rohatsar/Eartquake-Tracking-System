from PyQt5 import QtWidgets, QtWebEngineWidgets
import os
import json

class ToplanmaPenceresi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toplanma Alanları")
        self.setGeometry(350, 150, 900, 600)

        self.webview = QtWebEngineWidgets.QWebEngineView(self)
        self.setCentralWidget(self.webview)

        # JSON dosya yolu
        json_path = os.path.join(os.path.dirname(__file__), "data", "toplanma_alanlari.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                alanlar = json.load(f)
        except Exception as e:
            self.webview.setHtml(f"<h2>Veri okunamadı: {str(e)}</h2>")
            return

        # HTML oluştur
        html = self._create_map_html(alanlar)
        self.webview.setHtml(html)

    def _create_map_html(self, alanlar):
        # Başlangıç merkez koordinatı (Adana civarı)
        center_lat = 37.0
        center_lon = 35.3

        # Leaflet + marker scripti oluşturuyoruz
        markers_js = ""
        for alan in alanlar:
            lat = alan.get("lat")
            lon = alan.get("lon")
            adres = alan.get("adres", "Adres bilgisi yok")
            markers_js += f"L.marker([{lat}, {lon}]).addTo(map).bindPopup('{adres}');\n"

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Toplanma Alanları</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <style>
    #map {{ height: 100vh; width: 100%; margin: 0; padding: 0; }}
    body {{ margin: 0; }}
  </style>
</head>
<body>
<div id="map"></div>
<script>
  var map = L.map('map').setView([{center_lat}, {center_lon}], 11);

  L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 15,
    attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'
  }}).addTo(map);

  {markers_js}
</script>
</body>
</html>
"""
        return html_template
