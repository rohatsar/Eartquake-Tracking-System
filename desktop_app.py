from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox
from PyQt5.QtCore import pyqtSignal
import sys, requests, threading, time, os
import folium
from datetime import datetime, timedelta
import openai
from ui_mainwindow import MainWindow as Ui_MainWindow
from deprem_penceresi import DepremPenceresi
from harita_liste_penceresi import HaritaListePenceresi 
  

openai.api_key = "."  # Kendi API anahtarını buraya koy

def request_with_retry(url, params, retries=3, delay=5):
    for i in range(retries):
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"İstek başarısız oldu ({i+1}/{retries}): {e}")
            if i < retries - 1:
                time.sleep(delay)
            else:
                raise


class MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Earthquake Information Application")
        self.setGeometry(300, 100, 900, 600)

        # ← ❷ Harita/Liste butonunu açan bağlantı artık __init__ içinde
        self.btn_harita.clicked.connect(self.harita_tiklandi)
        

      
    # ← ❸ Fonksiyon artık sınıf seviyesinde, dışarıda
    def harita_penceresini_ac(self):
        self.harita_pencere = HaritaListePenceresi()
        self.harita_pencere.show()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pencere = MainWindow()
    pencere.show()
    sys.exit(app.exec_())
