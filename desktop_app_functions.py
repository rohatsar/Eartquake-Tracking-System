# desktop_app_functions.py
import requests
import os
import tempfile
import folium
from folium.plugins import MarkerCluster
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets


class DepremUygulamasi:
    def __init__(self, list_widget, web_view):
        self.listWidget = list_widget
        self.webView = web_view
        self.deprem_data = []
        self._last_map_file = None

    def deprem_verilerini_cek(self,
                              start_date="2025-06-01",
                              end_date=None,
                              min_magnitude=0.0,
                              max_magnitude=10.0,
                              deprem_tipi="Hepsi",
                              limit=1000):
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")

        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "starttime": start_date,
            "endtime": end_date,
            "minmagnitude": min_magnitude,
            "orderby": "time",
            "limit": int(limit)
        }

        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            depremler = data.get("features", [])

            self.listWidget.clear()
            self.deprem_data = []

            # Önceki temp dosyasını temizle
            try:
                if self._last_map_file and os.path.exists(self._last_map_file):
                    try:
                        os.remove(self._last_map_file)
                    except Exception:
                        pass
                    self._last_map_file = None
            except Exception:
                pass

            harita = folium.Map(location=[39.0, 35.0], zoom_start=5, tiles='OpenStreetMap')
            use_cluster = int(limit) > 2000
            cluster = MarkerCluster(name="Depremler").add_to(harita) if use_cluster else None

            for deprem in depremler:
                props = deprem.get("properties", {})
                geom = deprem.get("geometry", {})
                buyukluk = props.get("mag")
                if buyukluk is None:
                    continue

                if buyukluk < float(min_magnitude) or buyukluk > float(max_magnitude):
                    continue

                yer = props.get("place", "Bilinmiyor")
                zaman_ms = props.get("time", 0)
                try:
                    zaman = datetime.utcfromtimestamp(zaman_ms / 1000).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    zaman = "Bilinmiyor"

                coords = geom.get("coordinates", [None, None, None])
                if len(coords) < 3:
                    continue
                lon, lat, derinlik = coords[0], coords[1], coords[2]
                if lat is None or lon is None:
                    continue

                self.deprem_data.append({
                    "place": yer,
                    "mag": buyukluk,
                    "time": zaman_ms,
                    "depth": derinlik,
                    "url": props.get("url", ""),
                    "fault": props.get("fault", "Bilinmiyor"),
                    "lon": lon,
                    "lat": lat
                })

                idx = len(self.deprem_data) - 1
                item = QtWidgets.QListWidgetItem(f"{zaman} | M{buyukluk} | {yer}")

                # Renk kodlama
                if buyukluk >= 6.0:
                    item.setForeground(QtGui.QColor("red"))
                    renk = '#d9534f'
                elif 6.0 > buyukluk >= 4.5:
                    item.setForeground(QtGui.QColor("orange"))
                    renk = '#f0ad4e'
                elif 4.5 > buyukluk >= 2.0:
                    item.setForeground(QtGui.QColor("green"))
                    renk = '#5cb85c'
                else:
                    item.setForeground(QtGui.QColor("#5bc0de"))
                    renk = '#5bc0de'

                item.setData(QtCore.Qt.UserRole, idx)
                self.listWidget.addItem(item)

                # Popup içeriği: link varsa target="_blank" ekliyoruz
                url_detay = props.get("url", "")
                if url_detay:
                    popup_html = f"<b>{yer}</b><br>M{buyukluk}<br>{zaman}<br><a href='{url_detay}' target='_blank' rel='noopener noreferrer'>Detay</a>"
                else:
                    popup_html = f"<b>{yer}</b><br>M{buyukluk}<br>{zaman}"

                target = cluster if use_cluster else harita
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=max(3, 3 + float(buyukluk) * 1.2),
                    popup=popup_html,
                    color=renk,
                    fill=True,
                    fill_opacity=0.7,
                    weight=2
                ).add_to(target)

            # Kaydet ve yükle
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
                temp_file = f.name
            harita.save(temp_file)
            self._last_map_file = temp_file
            self.webView.load(QtCore.QUrl.fromLocalFile(temp_file))

        except Exception as e:
            self.webView.setHtml(f"<h2 style='color:red;'>Hata: {str(e)}</h2>")

    def harita_goster(self):
        self.deprem_verilerini_cek()
