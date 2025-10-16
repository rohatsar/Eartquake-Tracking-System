from PyQt5 import QtWidgets, QtWebEngineWidgets, QtGui, QtCore
import folium
import io
import requests
import math
from datetime import datetime, timedelta
import json
import pandas as pd # type: ignore
import math 
import unicodedata
ceviriler = {
    "Türkçe": {
        "title": "Türkiye Deprem Risk Durumu",
        "city_search_placeholder": "İl adı giriniz...",
        "district_search_placeholder": "İlçe ara...",
        "city_search_button": "İl Ara",
        "risk_sort_button": "Risk Durumuna Göre Sırala",
        "table_headers": ["İl", "Son Deprem Sayısı", "Risk Skoru"],
        "district_table_headers": ["İlçe", "Zemin Etüdü", "Risk Durumu"],
        "filters": {
            "all": "Hepsi",
            "z1": "Z1",
            "z2": "Z2",
            "z3": "Z3",
            "good": "İyi",
            "medium": "Orta",
            "bad": "Kötü",
            "unknown": "Bilinmiyor"
        },
        "popup": {
            "recent_eq_count": "Son Deprem Sayısı",
            "historical_eq_count": "Tarihsel Deprem Sayısı",
            "total": "Toplam",
            "risk_score": "Risk Skoru"
        },
        "messages": {
            "no_city_found": "'{}' bulunamadı.",
            "info_title": "Bilgi",
            "eq_count_30_days": "Deprem sayısı (son 30 gün, ML>=4): {}"
        },
        "risk_level": {
        "good": "İyi",
        "moderate": "Orta",
        "bad": "Kötü",
        "unknown": "Bilinmiyor"
        }
    },
    "İngilizce": {
        "title": "Turkey Earthquake Risk Status",
        "city_search_placeholder": "Enter city name...",
        "district_search_placeholder": "Search district...",
        "city_search_button": "Search City",
        "risk_sort_button": "Sort by Risk Status",
        "table_headers": ["City", "Recent Earthquake Count", "Risk Score"],
        "district_table_headers": ["District", "Soil Survey", "Risk Status"],
        "filters": {
            "all": "All",
            "z1": "Z1",
            "z2": "Z2",
            "z3": "Z3",
            "good": "Good",
            "medium": "Medium",
            "bad": "Bad",
            "unknown": "Unknown"
        },
        "popup": {
            "recent_eq_count": "Recent Earthquake Count",
            "historical_eq_count": "Historical Earthquake Count",
            "total": "Total",
            "risk_score": "Risk Score"
        },
        "messages": {
            "no_city_found": "'{}' not found.",
            "info_title": "Information",
            "eq_count_30_days": "Number of earthquakes (last 30 days, ML>=4): {}"
        },
        "risk_level": {
    "good": "Good",
    "moderate": "Medium",
    "bad": "Bad",
    "unknown": "Unknown"
}

    },
    "İspanyolca": {
    "title": "Estado de Riesgo Sísmico de Turquía",
    "city_search_placeholder": "Introducir nombre de ciudad...",
    "district_search_placeholder": "Buscar distrito...",
    "city_search_button": "Buscar ciudad",
    "risk_sort_button": "Ordenar por nivel de riesgo",
    "table_headers": ["Ciudad", "Número de sismos recientes", "Evaluación de riesgo"],
    "district_table_headers": ["Distrito", "Estudio del suelo", "Estado de riesgo"],
    "filters": {
        "all": "Todos",
        "z1": "Z1",
        "z2": "Z2",
        "z3": "Z3",
        "good": "Bueno",
        "medium": "Medio",
        "bad": "Malo",
        "unknown": "Desconocido"
    },
    "popup": {
        "recent_eq_count": "Número de sismos recientes",
        "historical_eq_count": "Número de sismos históricos",
        "total": "Total",
        "risk_score": "Evaluación de riesgo"
    },
    "messages": {
        "no_city_found": "'{}' no encontrado.",
        "info_title": "Información",
        "eq_count_30_days": "Número de sismos (últimos 30 días, ML>=4): {}"
    },
    "risk_level": {
    "good": "Bueno",
    "moderate": "Medio",
    "bad": "Malo",
    "unknown": "Desconocido"
}
},
    "Fransızca": {
        "title": "Statut de Risque Sismique Turquie",
        "city_search_placeholder": "Entrez le nom de la ville...",
        "district_search_placeholder": "Rechercher un district...",
        "city_search_button": "Rechercher la ville",
        "risk_sort_button": "Trier par statut de risque",
        "table_headers": ["Ville", "Nombre récent de tremblements", "Score de risque"],
        "district_table_headers": ["District", "Étude du sol", "Statut de risque"],
        "filters": {
            "all": "Tous",
            "z1": "Z1",
            "z2": "Z2",
            "z3": "Z3",
            "good": "Bon",
            "medium": "Moyen",
            "bad": "Mauvais",
            "unknown": "Inconnu"
        },
        "popup": {
            "recent_eq_count": "Nombre récent de tremblements",
            "historical_eq_count": "Nombre historique de tremblements",
            "total": "Total",
            "risk_score": "Score de risque"
        },
        "messages": {
            "no_city_found": "'{}' introuvable.",
            "info_title": "Information",
            "eq_count_30_days": "Nombre de tremblements (30 derniers jours, ML>=4) : {}"
        },
        "risk_level": {
        "good": "Bon",
        "moderate": "Moyen",
        "bad": "Mauvais",
        "unknown": "Inconnu"
}

    },
        "Arapça": {
        "title": "حالة خطر الزلازل في تركيا",
        "city_search_placeholder": "أدخل اسم المدينة...",
        "district_search_placeholder": "ابحث عن منطقة...",
        "city_search_button": "ابحث عن المدينة",
        "risk_sort_button": "الفرز حسب حالة الخطر",
        "table_headers": ["المدينة", "عدد الزلازل الحديثة", "درجة الخطر"],
        "district_table_headers": ["المنطقة", "دراسة التربة", "حالة الخطر"],
        "filters": {
            "all": "الكل",
            "z1": "Z1",
            "z2": "Z2",
            "z3": "Z3",
            "good": "جيد",
            "medium": "متوسط",
            "bad": "سيئ",
            "unknown": "غير معروف"
        },
        "popup": {
            "recent_eq_count": "عدد الزلازل الحديثة",
            "historical_eq_count": "عدد الزلازل التاريخية",
            "total": "الإجمالي",
            "risk_score": "درجة الخطر"
        },
        "messages": {
            "no_city_found": "لم يتم العثور على '{}'.",
            "info_title": "معلومات",
            "eq_count_30_days": "عدد الزلازل (آخر 30 يومًا، ML>=4): {}"
        },
        "risk_level": {
        "good": "جيد",
        "moderate": "متوسط",
        "bad": "سيء",
        "unknown": "غير معروف"
}

    }
}
class DepremRiskPenceresi(QtWidgets.QMainWindow):  # Burada QWidget yerine QMainWindow olacak
    def __init__(self, parent=None, secilen_dil="Türkçe"):
        super().__init__(parent)
        self.secilen_dil = secilen_dil 
        
        self.setWindowTitle("Türkiye Deprem Risk Durumu")
        self.resize(900, 600)
        self.geojson_dosya =(r"C:\Users\Rohat\Desktop\Deprem_uygulamasi\data\turkey.geojson") 
        self.turkiye_koordinatlari = [39, 35]
         # Türkiye illeri ve koordinatları
        self.iller = {
            "Adana": (37.0, 35.3213),
            "Adıyaman": (37.7648, 38.2765),
            "Afyonkarahisar": (38.7561, 30.5433),
            "Ağrı": (39.7191, 43.0503),
            "Aksaray": (38.3687, 34.0378),
            "Ankara": (39.9334, 32.8597),
            "Antalya": (36.8969, 30.7133),
            "Artvin": (41.1828, 41.8183),
            "Aydın": (37.8444, 27.8454),
            "Amasya": (40.6539, 35.8330),
            "Ardahan": (41.1105, 42.7022),
            "Balıkesir": (39.6484, 27.8826),
            "Bartın": (41.5811, 32.4611),
            "Batman": (37.8825, 41.1351),
            "Bayburt": (40.2552, 40.2249),
            "Bilecik": (40.1507, 29.9824),
            "Bingöl": (38.8858, 40.4966),
            "Bitlis": (38.3931, 42.1234),
            "Bolu": (40.7398, 31.6114),
            "Burdur": (37.7203, 30.2883),
            "Bursa": (40.1828, 29.0666),
            "Çanakkale": (40.1553, 26.4142),
            "Çankırı": (40.6013, 33.6134),
            "Çorum": (40.5481, 34.9536),
            "Denizli": (37.7765, 29.0864),
            "Diyarbakır": (37.9144, 40.2306),
            "Düzce": (40.8433, 31.1565),
            "Edirne": (41.6764, 26.5557),
            "Elazığ": (38.6742, 39.2227),
            "Erzincan": (39.7500, 39.4911),
            "Erzurum": (39.9043, 41.2679),
            "Eskişehir": (39.7767, 30.5206),
            "Gaziantep": (37.0662, 37.3833),
            "Giresun": (40.9128, 38.3895),
            "Gümüşhane": (40.4601, 39.4796),
            "Hakkari": (37.5744, 43.7405),
            "Hatay": (36.2028, 36.1606),
            "Isparta": (37.7648, 30.5566),
            "Iğdır": (39.9237, 44.0450),
            "İstanbul": (41.0082, 28.9784),
            "İzmir": (38.4192, 27.1287),
            "Kahramanmaraş": (37.5753, 36.9377),
            "Karabük": (41.2040, 32.6205),
            "Karaman": (37.1810, 33.2150),
            "Kars": (40.6013, 43.0983),
            "Kastamonu": (41.3887, 33.7831),
            "Kayseri": (38.7312, 35.4787),
            "Kırıkkale": (39.8468, 33.5153),
            "Kırklareli": (41.7354, 27.2250),
            "Kırşehir": (39.1425, 34.1707),
            "Kilis": (36.7184, 37.1211),
            "Kocaeli": (40.7669, 29.9400),
            "Konya": (37.8716, 32.4849),
            "Kütahya": (39.4246, 29.9833),
            "Malatya": (38.3556, 38.3095),
            "Manisa": (38.6191, 27.4289),
            "Mardin": (37.3127, 40.7350),
            "Mersin": (36.8121, 34.6415),
            "Muğla": (37.2153, 28.3636),
            "Muş": (38.9460, 41.7544),
            "Nevşehir": (38.6249, 34.7119),
            "Niğde": (37.9667, 34.6833),
            "Ordu": (40.9833, 37.8833),
            "Osmaniye": (37.0741, 36.2384),
            "Rize": (41.0201, 40.5234),
            "Sakarya": (40.7767, 30.4033),
            "Samsun": (41.2867, 36.33),
            "Siirt": (37.9441, 41.9327),
            "Sinop": (42.0231, 35.1531),
            "Sivas": (39.7482, 37.0159),
            "Şanlıurfa": (37.1674, 38.7955),
            "Şırnak": (37.5112, 42.4615),
            "Tekirdağ": (40.9785, 27.5116),
            "Tokat": (40.3167, 36.55),
            "Trabzon": (41.0015, 39.7178),
            "Tunceli": (39.1086, 39.5489),
            "Uşak": (38.6757, 29.4061),
            "Van": (38.5019, 43.4003),
            "Yalova": (40.6561, 29.2764),
            "Yozgat": (39.8209, 34.8143),
            "Zonguldak": (41.4564, 31.7987),
        }

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        self.search_layout = QtWidgets.QHBoxLayout()
        self.main_layout.insertLayout(0, self.search_layout)  # En üste ekler

        self.il_search_edit = QtWidgets.QLineEdit()
        self.il_search_edit.setPlaceholderText("İl adı giriniz...")

        self.search_button = QtWidgets.QPushButton("İl Ara")
         
         # Stil uygulama kodlarını hemen aşağıya ekle
        self.il_search_edit.setStyleSheet("""
    QLineEdit {
        border: 2px solid #0078d7;
        border-radius: 8px;
        padding: 6px;
        font-size: 14px;
    }
    QLineEdit:focus {
        border-color: #005a9e;
    }
""")

        self.search_button.setStyleSheet("""
    QPushButton {
        background-color: #0078d7;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #005a9e;
    }
    QPushButton:pressed {
        background-color: #003f6b;
    }
""")

        self.search_layout.addWidget(self.il_search_edit)
        self.search_layout.addWidget(self.search_button)
        self.il_search_edit.returnPressed.connect(self.il_ara)
        self.search_button.clicked.connect(self.il_ara)
       
        
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["İl", "Son Deprem Sayısı", "Risk Skoru"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.main_layout.addWidget(self.tableWidget)
        
        layout = QtWidgets.QHBoxLayout()
        self.webView = QtWebEngineWidgets.QWebEngineView()
        layout.addWidget(self.webView, 3)

    # Diğer widget'lar
        self.table = QtWidgets.QTableWidget()
        self.main_layout.addWidget(self.table)

        # 🔽🔽🔽 Buraya ekleyeceksin 🔽🔽🔽
        self.filter_layout = QtWidgets.QHBoxLayout()

        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("İlçe ara...")
        self.search_box.textChanged.connect(self.filtrele)
        self.filter_layout.addWidget(self.search_box)

        self.zemin_combo = QtWidgets.QComboBox()
        self.zemin_combo.addItems(["Hepsi", "Z1", "Z2", "Z3"])
        self.zemin_combo.currentIndexChanged.connect(self.filtrele)
        self.filter_layout.addWidget(self.zemin_combo)

        self.risk_combo = QtWidgets.QComboBox()
        self.risk_combo.addItems(["Hepsi", "İyi", "Orta", "Kötü"])
        self.risk_combo.currentIndexChanged.connect(self.filtrele)
        self.filter_layout.addWidget(self.risk_combo)

        self.sort_button = QtWidgets.QPushButton("Risk Drumuna Göre Sırala")
        self.sort_button.clicked.connect(self.risk_skoru_sirala)
        self.filter_layout.addWidget(self.sort_button)
        
        self.main_layout.addLayout(self.filter_layout)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["İlçe", "Zemin Etüdü", "Risk Durumu"])
        self.dil_degistir()
        layout.addWidget(self.table, 1)

        self.main_layout.addLayout(layout)

    # Veri güncelleme vs.
        
        with open(r"C:\Users\Rohat\Desktop\Deprem_uygulamasi\data\ilce.json", "r", encoding="utf-8") as f:
            
            ilce_json = json.load(f)
            ilce_data = next(item["data"] for item in ilce_json if item["type"] == "table" and item["name"] == "ilce")
        with open(r"C:\Users\Rohat\Desktop\Deprem_uygulamasi\data\zemin_etudu.json", "r", encoding="utf-8") as f:
            self.zemin_etudu_verisi = json.load(f) 
    # İl ID'leri → İl adları sözlüğü
            il_id_to_name = {
            "1": "Adana",
            "2": "Adıyaman",
            "3": "Afyonkarahisar",
            "4": "Ağrı",
             "5": "Amasya",
            "6": "Ankara",
            "7": "Antalya",
            "8": "Artvin",
            "9": "Aydın",
            "10": "Balıkesir",
            "11": "Bilecik",
            "12": "Bingöl",
            "13": "Bitlis",
            "14": "Bolu",
            "15": "Burdur",
            "16": "Bursa",
            "17": "Çanakkale",
            "18": "Çankırı",
            "19": "Çorum",
            "20": "Denizli",
            "21": "Diyarbakır",
            "22": "Edirne",
            "23": "Elazığ",
            "24": "Erzincan",
            "25": "Erzurum",
            "26": "Eskişehir",
            "27": "Gaziantep",
            "28": "Giresun",
            "29": "Gümüşhane",
            "30": "Hakkari",
            "31": "Hatay",
            "32": "Isparta",
            "33": "Mersin",
            "34": "İstanbul",
            "35": "İzmir",
            "36": "Kars",
            "37": "Kastamonu",
            "38": "Kayseri",
            "39": "Kırklareli",
            "40": "Kırşehir",
            "41": "Kocaeli",
            "42": "Konya",
            "43": "Kütahya",
            "44": "Malatya",
            "45": "Manisa",
            "46": "Kahramanmaraş",
            "47": "Mardin",
            "48": "Muğla",
            "49": "Muş",
            "50": "Nevşehir",
            "51": "Niğde",
            "52": "Ordu",
            "53": "Rize",
            "54": "Sakarya",
            "55": "Samsun",
            "56": "Siirt",
            "57": "Sinop",
            "58": "Sivas",
            "59": "Tekirdağ",
            "60": "Tokat",
            "61": "Trabzon",
            "62": "Tunceli",
            "63": "Şanlıurfa",
            "64": "Uşak",
            "65": "Van",
            "66": "Yozgat",
            "67": "Zonguldak",
            "68": "Aksaray",
            "69": "Bayburt",
            "70": "Karaman",
            "71": "Kırıkkale",
            "72": "Batman",
            "73": "Şırnak",
            "74": "Bartın",
             "75": "Ardahan",
            "76": "Iğdır",
            "77": "Yalova",
            "78": "Karabük",
            "79": "Kilis",
            "80": "Osmaniye",
            "81": "Düzce"
        }

    # İlçe verilerini il adına göre gruplayan dict
            self.ilceler = {il_adi: [] for il_adi in il_id_to_name.values()}
            for item in ilce_data:
                il_adi = il_id_to_name.get(item["il_id"])
                if il_adi:
                    self.ilceler[il_adi].append(item["name"])
        self.tarihsel_veri = pd.read_excel(r"C:\Users\Rohat\Desktop\Deprem_uygulamasi\data\turkiye_1000yil_buyuk_depremler.xlsx")
        self.tarihsel_veri.rename(columns={"B³y³kl³k": "Büyüklük", "¦l": "İl"}, inplace=True)
        self.tarihsel_veri["Büyüklük"] = pd.to_numeric(self.tarihsel_veri["Büyüklük"], errors="coerce")
        
        self.tableWidget.cellClicked.connect(self.il_secildi)

        self.veri_guncelle()

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def son_30gun_depremler(self):
        bugun = datetime.utcnow()
        otuz_gun_once = bugun - timedelta(days=30)
        starttime = otuz_gun_once.strftime("%Y-%m-%d")
        endtime = bugun.strftime("%Y-%m-%d")

        url = (f"https://earthquake.usgs.gov/fdsnws/event/1/query?"
               f"format=geojson&starttime={starttime}&endtime={endtime}"
               f"&minlatitude=35.0&maxlatitude=43.0&minlongitude=25.0&maxlongitude=45.0"
               f"&minmagnitude=4")

        response = requests.get(url)
        data = response.json()
        ceviri = ceviriler.get(self.secilen_dil, ceviriler["Türkçe"])["messages"]
        print(ceviri["eq_count_30_days"].format(len(data['features'])))
        return data

    def il_risk_hesapla(self, depremler):
        il_veri = {il: {"sayi": 0, "toplam_buyukluk": 0, "tarihsel_buyuk": 0, "tarihsel_sayi": 0} for il in self.iller.keys()}

        for deprem in depremler['features']:
            coords = deprem['geometry']['coordinates']
            lon, lat = coords[0], coords[1]
            ml = deprem['properties']['mag']

            en_yakin_il = min(self.iller.keys(), key=lambda il: self.haversine(lat, lon, *self.iller[il]))
            il_veri[en_yakin_il]["sayi"] += 1
            if ml is not None and not math.isnan(ml):
                il_veri[en_yakin_il]["toplam_buyukluk"] += ml

        for _, row in self.tarihsel_veri.iterrows():
            il = row["İl"]
            büyüklük = row["Büyüklük"]
            if il in il_veri:
                il_veri[il]["tarihsel_sayi"] += 1
                if not pd.isna(büyüklük):
                    il_veri[il]["tarihsel_buyuk"] += büyüklük

        il_risk = {}
        for il, data in il_veri.items():
            a, b = data["sayi"], data["toplam_buyukluk"]
            c, d = data["tarihsel_sayi"], data["tarihsel_buyuk"]

            ort_guncel = (b / a) if (a > 0 and not math.isnan(b)) else 0
            ort_tarihsel = (d / c) if (c > 0 and not math.isnan(d)) else 0

            if a == 0 and c == 0:
                risk = 0
            else:
                risk = (a * ort_guncel * 0.6) + (c * ort_tarihsel * 0.4)

            il_risk[il] = {
                "risk_skoru": risk,
                "son_deprem_sayisi": a,  # sadece son 30 gün
                 "tarihsel_deprem_sayisi": c,
            }
        return il_risk
    def harita_olustur(self):
        with open(self.geojson_dosya, "r", encoding="utf-8-sig") as f:
            il_geojson = json.load(f)

        data = []
        for il, info in self.il_risk_verisi.items():
            data.append({
                "il": il,
                "risk_skoru": info["risk_skoru"]
            })
        df = pd.DataFrame(data)

        m = folium.Map(location=self.turkiye_koordinatlari, zoom_start=6)

        folium.Choropleth(
            geo_data=il_geojson,
            name="Deprem Risk Haritası",
            data=df,
            columns=["il", "risk_skoru"],
            key_on="feature.properties.name",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.5,
            legend_name="Deprem Risk Skoru",
            nan_fill_color="white",
        ).add_to(m)

        for il, info in self.il_risk_verisi.items():
            lat, lon = self.iller[il]
            toplam_deprem_sayisi = info["son_deprem_sayisi"] + info["tarihsel_deprem_sayisi"]
            ceviri = ceviriler.get(self.secilen_dil, ceviriler["Türkçe"])["popup"]

            popup_text = (f"<b>{il}</b><br>"
              f"{ceviri['recent_eq_count']}: {info['son_deprem_sayisi']}<br>"
              f"{ceviri['historical_eq_count']}: {info['tarihsel_deprem_sayisi']}<br>"
              f"{ceviri['total']}: {toplam_deprem_sayisi}<br>"
              f"{ceviri['risk_score']}: {info['risk_skoru']:.2f}")

            folium.CircleMarker(
                 location=[lat, lon],
                radius=8,
                color="blue",
                fill=True,
                fill_color="cyan",
                fill_opacity=0.7,
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)
        self.webView.setHtml(data.getvalue().decode())

    def veri_guncelle(self):
        depremler = self.son_30gun_depremler()
        self.il_risk_verisi = self.il_risk_hesapla(depremler)
        
        self.harita_olustur()
        self.tablo_guncelle()

    def tablo_guncelle(self):
        self.tableWidget.setRowCount(0)
        for i, (il, risk) in enumerate(self.il_risk_verisi.items()):
            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(il))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(risk["son_deprem_sayisi"])))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{risk['risk_skoru']:.2f}"))
    def il_secildi(self, row, column):
        il_adi = self.tableWidget.item(row, 0).text()
        ilceler = self.ilceler.get(il_adi, [])
        self.table.setRowCount(0)
        
        # Zemin etüdü verisinde ilçelerin anahtarlarını küçük harf ve strip ile normalleştir
        zemin_dict_raw = self.zemin_etudu_verisi.get(il_adi, {})
        zemin_dict = {DepremRiskPenceresi.normalize_text(k): v for k, v in zemin_dict_raw.items()}
      
        for i, ilce in enumerate(ilceler):
       
            self.table.insertRow(i)
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(ilce))

            ilce_key = DepremRiskPenceresi.normalize_text(ilce)
            zemin_etudu = zemin_dict.get(ilce_key, "Bilinmiyor")

            zemin_item = QtWidgets.QTableWidgetItem(zemin_etudu)
            self.table.setItem(i, 1, zemin_item)

            ceviri = ceviriler.get(self.secilen_dil, ceviriler["Türkçe"])["risk_level"]

            if zemin_etudu == "Z1":
                risk_durumu = ceviri["good"]
                color = QtGui.QColor(144, 238, 144)
                text_color = QtGui.QColor(0, 0, 0)
            elif zemin_etudu == "Z2":
                risk_durumu = ceviri["moderate"]
                color = QtGui.QColor(255, 165, 0)
                text_color = QtGui.QColor(0, 0, 0)
            elif zemin_etudu == "Z3":
                risk_durumu = ceviri["bad"]
                color = QtGui.QColor(255, 69, 0)
                text_color = QtGui.QColor(255, 255, 255)
            else:
                risk_durumu = ceviri["unknown"]
                color = QtGui.QColor(255, 255, 255)
                text_color = QtGui.QColor(0, 0, 0)

            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(risk_durumu))
            for col in range(3):
                item = self.table.item(i, col)
                if item:
                    item.setBackground(color)
                    item.setForeground(text_color)
    def normalize_text(text):
        replacements = {
        'ı': 'i', 'İ': 'i', 'ş': 's', 'Ş': 's', 'ğ': 'g', 'Ğ': 'g',
        'ü': 'u', 'Ü': 'u', 'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'
    }
        text = text.lower().strip()
        for k, v in replacements.items():
            text = text.replace(k, v)
        # Unicode normalizasyonu yap (NFKD formu)
            text = unicodedata.normalize('NFKD', text)
            # Harf, rakam ve boşluk dışındaki karakterleri temizle
        import re
        text = re.sub(r'[^a-z0-9\s]', '', text)
    # Fazla boşlukları tek boşluk yap
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def risk_skoru_sirala(self):
       ilceler = []
       for i in range(self.table.rowCount()):
        ilce = self.table.item(i, 0).text()
        zemin = self.table.item(i, 1).text() if self.table.item(i, 1) else "Bilinmiyor"
        risk = self.table.item(i, 2).text()
        ilceler.append((ilce, zemin, risk))

       ceviri = ceviriler.get(self.secilen_dil, ceviriler["Türkçe"])["risk_level"]
       risk_sirasi = {
            ceviri["bad"]: 3,
            ceviri["moderate"]: 2,
            ceviri["good"]: 1,
            ceviri["unknown"]: 0
        }
       ilceler.sort(key=lambda x: risk_sirasi.get(x[2], 0), reverse=True)
       
       ceviri = ceviriler.get(self.secilen_dil, ceviriler["Türkçe"])["risk_level"]
       renkler = {
        ceviri["good"]: QtGui.QColor("lightgreen"),
        ceviri["moderate"]: QtGui.QColor("orange"),
        ceviri["bad"]: QtGui.QColor("red"),
        ceviri["unknown"]: QtGui.QColor("lightgray")
        }

       self.table.setRowCount(0)
       for i, (ilce, zemin, risk) in enumerate(ilceler):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(ilce))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(zemin))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(risk))

        # Renk atama
            renk = renkler.get(risk, QtGui.QColor("white"))
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if item:
                    item.setBackground(renk)
                    item.setForeground(QtGui.QBrush(QtGui.QColor("black")))

    def filtrele(self):
        aranan = self.search_box.text().lower().strip()
        secili_zemin = self.zemin_combo.currentText()
        secili_risk = self.risk_combo.currentText()

        # Risk karşılıklarını yakala (çeviriye göre değil anahtara göre kontrol et)
        ceviri_risk = ceviriler.get(self.secilen_dil, ceviriler["Türkçe"])["risk_level"]
        ters_ceviri_risk = {v: k for k, v in ceviri_risk.items()}  # Örn: {"İyi": "good", ...}
        secili_risk_key = ters_ceviri_risk.get(secili_risk, "all")  # Good / Medium / Bad

        for i in range(self.table.rowCount()):
            ilce = self.table.item(i, 0).text().lower().strip()

            item = self.table.item(i, 1)
            zemin = item.text() if item else "Bilinmiyor"

            item2 = self.table.item(i, 2)
            risk_label = item2.text() if item2 else "Bilinmiyor"
            risk_key = ters_ceviri_risk.get(risk_label, "unknown")

            goster = True

            if aranan and aranan not in ilce:
                goster = False
            if secili_zemin != "Hepsi" and zemin != secili_zemin:
                goster = False
            if secili_risk != ceviriler[self.secilen_dil]["filters"]["all"] and risk_key != secili_risk_key:
                goster = False

            self.table.setRowHidden(i, not goster)

    def il_ara(self):
       aranan_il = self.il_search_edit.text().strip()
       if not aranan_il:
            return

       aranan_il_lower = aranan_il.lower()

       for i in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(i, 0)  # İl sütunu
            if item and item.text().lower() == aranan_il_lower:
                self.tableWidget.selectRow(i)
                self.tableWidget.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtCenter)
                return

       ceviri = ceviriler.get(self.secilen_dil, ceviriler["Türkçe"])["messages"]
       QtWidgets.QMessageBox.information(self, ceviri["info_title"], ceviri["no_city_found"].format(aranan_il))
    def dil_degistir(self):
        ceviri = ceviriler.get(self.secilen_dil, ceviriler["Türkçe"])
        self.setWindowTitle(ceviri["title"])
        self.il_search_edit.setPlaceholderText(ceviri["city_search_placeholder"])
        self.search_button.setText(ceviri["city_search_button"])
        self.tableWidget.setHorizontalHeaderLabels(ceviri["table_headers"])
        self.search_box.setPlaceholderText(ceviri["district_search_placeholder"])
        self.zemin_combo.clear()
        self.zemin_combo.addItems([ceviri["filters"]["all"], ceviri["filters"]["z1"], ceviri["filters"]["z2"], ceviri["filters"]["z3"]])
        self.risk_combo.clear()
        self.risk_combo.addItems([ceviri["filters"]["all"], ceviri["filters"]["good"], ceviri["filters"]["medium"], ceviri["filters"]["bad"]])
        self.sort_button.setText(ceviri["risk_sort_button"])
        self.table.setHorizontalHeaderLabels(ceviri["district_table_headers"])    
    def set_dil(self, yeni_dil):
        if yeni_dil in ceviriler:
            self.secilen_dil = yeni_dil
            self.dil_degistir()
            self.tablo_guncelle()  # Tablo başlıkları ve içerik güncellenebilir
    def renkleri_guncelle(self):
        for i in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(i, 2)
            if item:
                if item.text() == "Kötü":
                    item.setBackground(QtGui.QColor("red"))
                elif item.text() == "Orta":
                    item.setBackground(QtGui.QColor("yellow"))
                elif item.text() == "İyi":
                    item.setBackground(QtGui.QColor("green"))
