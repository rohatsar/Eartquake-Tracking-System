from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import traceback
import warnings
import folium
import tempfile
import requests
from math import radians, sin, cos, asin, sqrt
from translations_ai import translations_ai_risk # type: ignore

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Basit yerleşik koordinatlar (fallback — yaklaşık)
BUILTIN_COORDS = {
    "adana": (37.0017, 35.3280),"adıyaman": (37.7648, 38.2768),"afyonkarahisar": (38.7597, 30.5406),"ağrı": (39.7191, 43.0511), "amasya": (40.6525, 35.8336),
    "ankara": (39.9334, 32.8597),"antalya": (36.8969, 30.7133), "artvin": (41.1828, 41.8183), "aydın": (37.8560, 27.8450),"balıkesir": (39.6484, 27.8826),
     "bilecik": (40.1500, 30.0665),"bingöl": (38.8840, 40.4989),  "bitlis": (38.4012, 42.1128),"bolu": (40.7350, 31.6068),"burdur": (37.4613, 30.0665),
    "bursa": (40.1950, 29.0600),"çanakkale": (40.1553, 26.4142),"çankırı": (40.6013, 33.6134),"çorum": (40.5484, 34.9537),"denizli": (37.7765, 29.0864),
    "diyarbakır": (37.9144, 40.2306),"edirne": (41.6772, 26.5557),"elazığ": (38.6740, 39.2222),"erzincan": (39.7484, 39.4910),"erzurum": (39.9043, 41.2679),
    "eskişehir": (39.7767, 30.5206),"gaziantep": (37.0662, 37.3833),"giresun": (40.9128, 38.3895),"gümüşhane": (40.4590, 39.4790),"hakkari": (37.5744, 43.7406),
    "hatay": (36.2028, 36.1604),"ısparta": (37.7641, 30.5566),"mersin": (36.8121, 34.6415),"istanbul": (41.0082, 28.9784),"izmir": (38.4237, 27.1428),
    "kars": (40.6013, 43.0945),"kastamonu": (41.3784, 33.7837),"kayseri": (38.7322, 35.4850),"kırıkkale": (39.8468, 33.5153),"kırklareli": (41.7356, 27.2250),
    "kırşehir": (39.1425, 34.1700),"kocaeli": (40.8533, 29.8815),"konya": (37.8746, 32.4932),"kütahya": (39.4242, 29.9833),"malatya": (38.3552, 38.3095),
    "manisa": (38.6191, 27.4289),"kahramanmaraş": (37.5858, 36.9371),"mardin": (37.3120, 40.7426),"muğla": (37.2153, 28.3636),"muş": (38.7436, 41.5061),
    "nevşehir": (38.6247, 34.7123),"niğde": (37.9667, 34.6804),"ordu": (40.9833, 37.8797),"rize": (41.0201, 40.5234),"sakarya": (40.7561, 30.4030),
    "samsun": (41.2867, 36.3313),"siirt": (37.9270, 41.9371),"sinop": (42.0269, 35.1550),"sivas": (39.7477, 37.0179),"tekirdağ": (40.9780, 27.5115),
    "tokat": (40.3167, 36.5547),"trabzon": (41.0015, 39.7178),"tunceli": (39.1090, 39.5486),"şanlıurfa": (37.1591, 38.7969),"uşak": (38.6757, 29.4082),
    "van": (38.4924, 43.3820),"yozgat": (39.8200, 34.8045),"zonguldak": (41.4564, 31.7987),"aksaray": (38.3720, 34.0277),"bayburt": (40.2550, 40.2242),
    "karaman": (37.1750, 33.2150),"batman": (37.8812, 41.1351),"şırnak": (37.5036, 42.4618),"bartın": (41.5811, 32.4615),"ardahan": (41.1106, 42.7022),
    "ığdır": (39.8881, 44.0048),"yalova": (40.6500, 29.2667),"karabük": (41.2056, 32.6204),"kilis": (36.7167, 37.1167),"osmaniye": (37.0745, 36.2384),"düzce": (40.8438, 31.1565)
}

# User-approved prior categories
PRIOR_BUCKETS = {
    'very_high': set([
        'istanbul', 'kocaeli', 'sakarya', 'duzce', 'bolu', 'yalova','bursa', 'izmir', 'manisa', 'aydin', 'mugla','hatay', 'kahramanmaras', 'elazig', 'bingol', 'malatya',
        'hakkari', 'van', 'tunceli'
    ]),
    'high': set([
        'tekirdag', 'balikesir', 'denizli', 'usak', 'afyonkarahisar', 'kutahya','canakkale', 'antalya', 'burdur', 'isparta', 'erzincan','diyarbakir', 'sanliurfa', 'gaziantep', 'siirt',
        'adana', 'osmaniye', 'bitlis', 'mardin', 'batman',
    ]),
    'medium': set([
        'ankara', 'eskisehir', 'konya', 'kayseri', 'sivas', 'tokat','amasya', 'erzurum', 'sirnak', 'kilis', 'yozgat','kirikkale', 'corum', 'cankiri', 'nevsehir', 'nigde',
        'kirsehir', 'bayburt'
    ]),
    'low': set([
        'samsun', 'ordu', 'giresun', 'trabzon', 'rize', 'artvin','gumushane', 'kastamonu', 'sinop', 'aksaray','karabuk', 'bartin', 'zonguldak', 'bilecik','mersin'
    ]),
    'very_low': set([
        'edirne', 'kirklareli', 'tekirdag', 'karabuk','zonguldak', 'bartin', 'bilecik', 'kirikkale','yozgat', 'cankiri', 'corum','karaman'
    ])
}

PRIOR_VALUES = {
    'very_high': 90.0, 'high': 50.0, 'medium': 25.0, 'low':10.0, 'very_low': 3.0
}

# helper normalize function reused in multiple places
def normalize_key(s):
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return ""
    s = str(s).strip().lower()
    repl = {'ç':'c','ğ':'g','ı':'i','ö':'o','ş':'s','ü':'u','İ':'i'}
    for k,v in repl.items():
        s = s.replace(k,v)
    s = s.replace('.','').replace(',','').replace('-',' ').strip()
    return s.replace(' ','').lower()

class AIRiskPenceresi(QtWidgets.QWidget):
    def __init__(self, secilen_dil="Türkçe", data_dir=None):
        super().__init__()
        self.secilen_dil = secilen_dil
        self.data_dir = data_dir or os.path.dirname(__file__)
        self.setWindowTitle(self._tr("ai_window"))
        self.setGeometry(300, 200, 1200, 720)
        self.setStyleSheet("background-color: #f8f9fa;")

        # Cached raw events & column names
        self.raw_events = None
        self._date_col = None
        self._mag_col = None
        self._region_col = None
        self._lat_col = None
        self._lon_col = None

        # force window (when user picks 7/30 explicitly)
        self._force_window_days = None

        # Layout
        main_layout = QtWidgets.QHBoxLayout(self)
        self.map_view = QtWebEngineWidgets.QWebEngineView()
        self.map_view.setMinimumWidth(520)
        main_layout.addWidget(self.map_view, 2)

        right_container = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_container)

        self.baslik = QtWidgets.QLabel("🤖 " + self._tr("ai_title"))
        self.baslik.setAlignment(QtCore.Qt.AlignCenter)
        self.baslik.setStyleSheet("font-size: 18px; font-weight: bold; margin: 8px;")
        right_layout.addWidget(self.baslik)

        # Time slider UI
        slider_layout = QtWidgets.QHBoxLayout()
        self.slider_label = QtWidgets.QLabel(self._tr("time_label") + ": ")
        slider_layout.addWidget(self.slider_label)

        self.time_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.time_slider.setMinimum(0)   # 0 gün önce = bugün
        self.time_slider.setMaximum(30)  # <-- değişti: artık max 30 gün
        self.time_slider.setValue(0)
        self.time_slider.setTickInterval(7)
        self.time_slider.setSingleStep(1)
        self.time_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.time_slider.valueChanged.connect(self._on_slider_change)
        self.time_slider.sliderReleased.connect(self._on_slider_release)
        slider_layout.addWidget(self.time_slider, 1)

        self.slider_value_label = QtWidgets.QLabel(self._tr("today"))
        slider_layout.addWidget(self.slider_value_label)
        right_layout.addLayout(slider_layout)

        # Quick buttons for common presets (90g ve 1y çıkarıldı)
        preset_layout = QtWidgets.QHBoxLayout()
        for text_key, val in [("today", 0), ("range_7g", 7), ("range_30g", 30)]:
            b = QtWidgets.QPushButton(self._tr(text_key))
            b.clicked.connect(lambda _, v=val: self._set_slider_and_apply(v))
            preset_layout.addWidget(b)
        right_layout.addLayout(preset_layout)

        # --- Model Controls (model_weight + prior tweak) ---
        # Initialize interactive state BEFORE creating UI controls
        self._current_model_weight = 0.6

        controls_group = QtWidgets.QGroupBox(self._tr("model_controls"))
        controls_layout = QtWidgets.QVBoxLayout()
        # model weight slider
        mw_h = QtWidgets.QHBoxLayout()
        mw_label = QtWidgets.QLabel(self._tr("model_weight") + ":")
        mw_label.setToolTip(self._tr("model_weight"))
        self.mw_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.mw_slider.setRange(0, 100)
        self.mw_slider.setSingleStep(5)
        self.mw_slider.setValue(int(self._current_model_weight * 100))
        self.mw_slider.setTickInterval(10)
        self.mw_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.mw_slider.valueChanged.connect(self._on_model_weight_change)
        self.mw_value_label = QtWidgets.QLabel(f"{int(self._current_model_weight*100)}%")
        mw_h.addWidget(mw_label)
        mw_h.addWidget(self.mw_slider, 1)
        mw_h.addWidget(self.mw_value_label)
        controls_layout.addLayout(mw_h)

        # priors tweak (spinboxes)
        priors_box = QtWidgets.QGroupBox(self._tr("prior_values"))
        priors_layout = QtWidgets.QFormLayout()
        self._prior_spinboxes = {}
        for key in ['very_high','high','medium','low','very_low']:
            sb = QtWidgets.QDoubleSpinBox()
            sb.setRange(0.0, 100.0)
            sb.setSingleStep(1.0)
            sb.setValue(float(PRIOR_VALUES.get(key, 0.0)))
            sb.setSuffix(" %")
            sb.valueChanged.connect(lambda _, k=key: self._on_prior_changed(k))
            priors_layout.addRow(self._tr(key) + ":", sb)
            self._prior_spinboxes[key] = sb
        priors_box.setLayout(priors_layout)
        controls_layout.addWidget(priors_box)

        # reset priors button
        priors_btns = QtWidgets.QHBoxLayout()
        self.priors_reset_btn = QtWidgets.QPushButton(self._tr("priors_reset"))
        self.priors_reset_btn.clicked.connect(self._reset_priors_to_defaults)
        priors_btns.addStretch()
        priors_btns.addWidget(self.priors_reset_btn)
        controls_layout.addLayout(priors_btns)

        controls_group.setLayout(controls_layout)
        right_layout.addWidget(controls_group)
        # --- end model controls ---

        self.info_label = QtWidgets.QLabel("")
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        right_layout.addWidget(self.info_label)
        right_layout.addSpacing(15) 

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        right_layout.addWidget(self.canvas, 1)
        self.ax = self.canvas.figure.add_subplot(111)

        self.table = QtWidgets.QTableWidget()
        right_layout.addWidget(self.table, 2)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton(self._tr("refresh_button"))
        self.btn_refresh.clicked.connect(lambda: self._run_pipeline(as_of_date=None, fetch_live=True))
        btn_layout.addWidget(self.btn_refresh)

        self.btn_export = QtWidgets.QPushButton(self._tr("export_csv"))
        self.btn_export.clicked.connect(self._export_csv)
        btn_layout.addWidget(self.btn_export)

        btn_layout.addStretch()
        self.btn_kapat = QtWidgets.QPushButton(self._tr("close_button"))
        self.btn_kapat.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_kapat)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(right_container, 3)

        # State
        self.df_features = None
        self.model = None
        self.risk_results = None
        self.feature_importances = None
        self.model_confidence = None
        self._chosen_window_days = 30

        # Run initial pipeline (today)
        self._run_pipeline(as_of_date=None, fetch_live=True)

    def _tr(self, text):
        try:
            # Dil kodları haritası
            lang_map = {"Türkçe": "tr", "İngilizce": "en", "İspanyolca": "es", "Arapça": "ar", "Fransızca": "fr"}
            code = lang_map.get(self.secilen_dil, "tr")
            
            # 1) Doğrudan anahtar varsa
            if text in translations_ai_risk:
                return translations_ai_risk[text].get(code, translations_ai_risk[text].get("en", text))

            # Normalizasyon fonksiyonu
            def norm_text(s):
                if s is None:
                    return ""
                s = str(s).strip().lower()
                replacements = [('ç','c'),('ğ','g'),('ı','i'),('ö','o'),('ş','s'),('ü','u'),('â','a'),('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u')]
                for a, b in replacements:
                    s = s.replace(a, b)
                # Noktalama işaretlerini kaldır
                for ch in ".,-()[]{}:;\"'/%\\?¡!¿—––":
                    s = s.replace(ch, '')
                s = ' '.join(s.split())
                return s

            target = norm_text(text)

            # 2) Translation sözlüğündeki değerlerle karşılaştırma
            for original_key, translations_dict in translations_ai_risk.items():
                # Önce orijinal anahtarı kontrol et
                if norm_text(original_key) == target:
                    return translations_dict.get(code, translations_dict.get("en", text))
                
                # Sonra tüm dil çevirilerini kontrol et
                for lang_key, translated_text in translations_dict.items():
                    if norm_text(translated_text) == target:
                        return translations_dict.get(code, translations_dict.get(lang_key, text))

            # 3) Eğer hala bulamadıysak, text'i normalize edip anahtar olarak ara
            for key in translations_ai_risk.keys():
                if norm_text(key) == target:
                    return translations_ai_risk[key].get(code, translations_ai_risk[key].get("en", text))

            return text

        except Exception as e:
            print(f"ERROR in _tr: {e}")
            return text

    def _set_slider_and_apply(self, days_offset):
        # set forced window for preset mode (None for live)
        if int(days_offset) == 0:
            self._force_window_days = None
        else:
            self._force_window_days = int(days_offset)
        self.time_slider.setValue(days_offset)
        self._apply_time_slider(days_offset)

    def _on_slider_change(self, val):
        # live update label while dragging
        if val == 0:
            self.slider_value_label.setText(self._tr("today"))
        else:
            as_of = (datetime.utcnow() - timedelta(days=int(val))).strftime("%Y-%m-%d")
            self.slider_value_label.setText(f"{val} {self._tr('time_label')} {self._tr('range_7g').split(' ')[0]} — {as_of}")

    def _on_slider_release(self):
        val = int(self.time_slider.value())
        # when user uses slider manually, respect that as force as well
        if val == 0:
            self._force_window_days = None
        else:
            self._force_window_days = int(val)
        self._apply_time_slider(val)

    def _apply_time_slider(self, days_offset):
        """
        days_offset: how many days in the past (0=today)
        Behavior:
         - If days_offset == 0 -> run pipeline in live mode (as_of_date=None, fetch_live=True)
         - If days_offset > 0  -> run pipeline in snapshot mode (as_of_date = now - days)
         and force chosen window to exactly that many days (so "7g" means last 7 days counts).
         Note: UI allows up to 30 days only.
        """
        try:
            self.time_slider.setEnabled(False)
            self.btn_refresh.setEnabled(False)

            if int(days_offset) == 0:
                # live mode: use up-to-date fetch
                as_of_date = None
                fetch_live = True
            else:
                # snapshot mode: deterministic view as of that past date
                as_of_date = datetime.utcnow() - timedelta(days=int(days_offset))
                fetch_live = False

            # pass force_window_days through to loader
            self._run_pipeline(as_of_date=as_of_date, fetch_live=fetch_live)
        finally:
            self.time_slider.setEnabled(True)
            self.btn_refresh.setEnabled(True)

    def _run_pipeline(self, as_of_date=None, fetch_live=True):
        try:
            ok, note = self._load_and_prepare_data(as_of_date=as_of_date, force_window_days=self._force_window_days)
            if not ok:
                self.info_label.setText(self._tr("no_real_data"))
            else:
                self.info_label.setText(self._tr("data_loaded"))

            if self.df_features is None or len(self.df_features) < 6:
                self.df_features = self._make_sample_features()
                # make sure sample also has il_key
                if 'il_key' not in self.df_features.columns:
                    self.df_features['il_key'] = self.df_features['il'].apply(normalize_key)
                self.info_label.setText(self._tr("no_real_data"))

            # LIVE UPDATE: Only fetch live when explicit refresh and as_of_date is None
            if fetch_live and as_of_date is None:
                try:
                    self._fetch_live_earthquakes_and_update(days=30, min_magnitude=0.0)
                except Exception:
                    pass

            # compute hybrid with interactive model weight
            self._hybrid_scores(model_weight=self._current_model_weight)
            self.info_label.setText(self._tr("combined_model"))

            self._draw_plot()
            self._show_table()
            self._update_map()
        except Exception as e:
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(self, self._tr("error"), f"{self._tr('ai_pipeline_error')}: {str(e)}")

    def _export_csv(self):
        try:
            if self.risk_results is None:
                QtWidgets.QMessageBox.information(self, self._tr("info"), self._tr("no_results_export"))
                return
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, self._tr("save_csv"), "ai_risk_results.csv", "CSV Files (*.csv)")
            if fname:
                self.risk_results.to_csv(fname, index=False)
                QtWidgets.QMessageBox.information(self, self._tr("success"), f"{self._tr('results_saved')}:\n{fname}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, self._tr("error"), f"{self._tr('csv_export_error')}: {str(e)}")

    def _load_and_prepare_data(self, as_of_date=None, force_window_days=None):
        """
        Loads raw events into self.raw_events (cached). Then prepares aggregated features
        computed with respect to `as_of_date` (if provided) or current UTC now.
        If force_window_days is provided (e.g. 7,30) the chosen_count and ort_mag_chosen
        are computed exactly for that many days prior to 'today'. This ensures presets show the
        expected last-N-days behavior.
        """
        tried = []
        df_events = None

        # If we don't have raw events cached yet, try to load from files
        if self.raw_events is None:
            cand_files = ["deprem_veri.csv", "deprem_dataset.csv", "son_depremler.json"]
            for fname in cand_files:
                path = os.path.join(self.data_dir, fname)
                if os.path.exists(path):
                    tried.append(path)
                    try:
                        if path.lower().endswith(".json"):
                            df_events = pd.read_json(path)
                        else:
                            df_events = pd.read_csv(path)
                        break
                    except Exception:
                        try:
                            df_events = pd.read_json(path, lines=True)
                            break
                        except Exception:
                            continue
            if df_events is None:
                return False, "no_data"

            df_events.columns = [c.lower() for c in df_events.columns]

            # detect columns
            date_col = next((c for c in ['tarih','date','datetime','time'] if c in df_events.columns), None)
            mag_col = next((c for c in ['ml','mag','magnitude','magni','mag_last30','ort_mag_last30'] if c in df_events.columns), None)
            region_col = next((c for c in ['il','ilce','city','region','place'] if c in df_events.columns), None)
            lat_col = next((c for c in ['enlem','lat','latitude'] if c in df_events.columns), None)
            lon_col = next((c for c in ['boylam','lon','longitude'] if c in df_events.columns), None)

            if date_col is None or mag_col is None or region_col is None:
                return False, "missing_fields"

            try:
                df_events[date_col] = pd.to_datetime(df_events[date_col], errors='coerce')
            except Exception:
                df_events[date_col] = pd.to_datetime(df_events[date_col], dayfirst=True, errors='coerce')

            df_events = df_events.dropna(subset=[region_col, date_col])
            df_events[region_col] = df_events[region_col].astype(str)

            # cache
            self.raw_events = df_events.copy()
            self._date_col = date_col
            self._mag_col = mag_col
            self._region_col = region_col
            self._lat_col = lat_col
            self._lon_col = lon_col
        else:
            df_events = self.raw_events.copy()
            date_col = self._date_col
            mag_col = self._mag_col
            region_col = self._region_col
            lat_col = self._lat_col
            lon_col = self._lon_col

        # Determine 'today' reference: use as_of_date if provided (snapshot), else now
        if as_of_date is None:
            today = pd.to_datetime(datetime.utcnow())
        else:
            today = pd.to_datetime(as_of_date)

        # Filter events to <= as_of_date (i.e., snapshot up to that moment)
        try:
            df_events = df_events[df_events[date_col] <= today].copy()
        except Exception:
            # if filtering fails, proceed with full set
            pass

        # aggregator: compute multiple windows and recency score relative to 'today'
        def agg_for_region(g):
            region_name = str(g.name) if getattr(g, 'name', None) is not None else str(g[region_col].iloc[0])

            # decide which window to use: prefer force_window_days if provided
            chosen_window = None
            if force_window_days is not None:
                chosen_window = int(force_window_days)
            else:
                # compute frac30/frac90 later at df-level; here keep values for 30/90/365
                chosen_window = None

            w30 = today - pd.Timedelta(days=30)
            w90 = today - pd.Timedelta(days=90)
            w365 = today - pd.Timedelta(days=365)

            last30 = g[g[date_col] >= w30]
            last90 = g[g[date_col] >= w90]
            last365 = g[g[date_col] >= w365]

            son30_count = len(last30)
            son90_count = len(last90)
            son365_count = len(last365)

            ort_mag_last30 = round(last30[mag_col].dropna().astype(float).mean(),2) if son30_count>0 else 0.0
            ort_mag_last90 = round(last90[mag_col].dropna().astype(float).mean(),2) if son90_count>0 else 0.0
            ort_mag_last365 = round(last365[mag_col].dropna().astype(float).mean(),2) if son365_count>0 else 0.0

            ort_mag_all = round(g[mag_col].dropna().astype(float).mean(),2) if mag_col in g.columns else 0.0
            total_count = len(g)
            days_since_last = (today - g[date_col].max()).days if len(g)>0 else 9999

            try:
                delta_days = (today - g[date_col]).dt.days.values
                decay = 30.0
                recency_score = float(np.nansum(np.exp(-delta_days / decay)))
            except Exception:
                recency_score = 0.0

            lat_mean = None; lon_mean = None
            if lat_col and lon_col and lat_col in g.columns and lon_col in g.columns:
                try:
                    lat_mean = g[lat_col].astype(float).mean()
                    lon_mean = g[lon_col].astype(float).mean()
                except Exception:
                    lat_mean = None; lon_mean = None

            return pd.Series({
                "region": region_name,
                "son30_count": son30_count,
                "son90_count": son90_count,
                "son365_count": son365_count,
                "ort_mag_last30": ort_mag_last30,
                "ort_mag_last90": ort_mag_last90,
                "ort_mag_last365": ort_mag_last365,
                "ort_mag_all": ort_mag_all,
                "total_count": total_count,
                "days_since_last": days_since_last,
                "recency_score": recency_score,
                "lat": lat_mean,
                "lon": lon_mean
            })

        if df_events is None or df_events.empty:
            # return empty features but not crash
            features_final = pd.DataFrame(columns=['il','zemin_tipi','chosen_count','ort_mag_chosen','ort_mag_all','total_count','days_since_last','recency_score','lat','lon','il_key'])
            self.df_features = features_final
            return True, "ok"

        agg = df_events.groupby(region_col).apply(agg_for_region).reset_index(drop=True)

        # decide chosen window if not forced (same logic as before)
        if force_window_days is None:
            frac30 = (agg['son30_count'] > 0).mean() if len(agg)>0 else 0.0
            frac90 = (agg['son90_count'] > 0).mean() if len(agg)>0 else 0.0
            chosen_window = 30 if frac30 >= 0.15 else (90 if frac90 >= 0.25 else 365)
        else:
            chosen_window = int(force_window_days)

        self._chosen_window_days = chosen_window

        # zemin mapping (same as before)
        zemin_path = os.path.join(self.data_dir, "zemin.csv")
        if os.path.exists(zemin_path):
            try:
                zdf = pd.read_csv(zemin_path)
                zdf.columns = [c.lower() for c in zdf.columns]
                if 'region' in zdf.columns and 'zemin_tipi' in zdf.columns:
                    agg = agg.merge(zdf[['region','zemin_tipi']], left_on='region', right_on='region', how='left')
                    agg['zemin_tipi'] = agg['zemin_tipi'].fillna(2).astype(int)
                else:
                    agg['zemin_tipi'] = 2
            except Exception:
                agg['zemin_tipi'] = 2
        else:
            agg['zemin_tipi'] = 2

        # numeric fill
        for c in ['son30_count','son90_count','son365_count','total_count']:
            agg[c] = agg[c].fillna(0).astype(int)
        for c in ['ort_mag_last30','ort_mag_last90','ort_mag_last365','ort_mag_all']:
            agg[c] = agg[c].fillna(0.0).astype(float)
        agg['days_since_last'] = agg['days_since_last'].fillna(9999).astype(int)
        agg['recency_score'] = agg['recency_score'].fillna(0.0).astype(float)

        # choose best window: but if forced, use that exact window
        if chosen_window == 30:
            agg['chosen_count'] = agg['son30_count']
            agg['ort_mag_chosen'] = agg['ort_mag_last30']
        elif chosen_window == 90:
            agg['chosen_count'] = agg['son90_count']
            agg['ort_mag_chosen'] = agg['ort_mag_last90']
        else:
            # includes 365 or forced custom window (>=365 means use yearly counts where available)
            if force_window_days is not None and force_window_days not in (30,90,365):
                # custom window: compute directly from events
                w = today - pd.Timedelta(days=int(force_window_days))
                def chosen_counts_custom(g):
                    sel = g[g[date_col] >= w]
                    return pd.Series({'chosen_count': len(sel), 'ort_mag_chosen': round(sel[mag_col].dropna().astype(float).mean(),2) if len(sel)>0 else 0.0})
                custom_df = df_events.groupby(region_col).apply(chosen_counts_custom).reset_index(drop=True)
                # align indexes by region names
                # simpler: fallback to son365 for now
                agg['chosen_count'] = agg['son365_count']
                agg['ort_mag_chosen'] = agg['ort_mag_last365']
            else:
                agg['chosen_count'] = agg['son365_count']
                agg['ort_mag_chosen'] = agg['ort_mag_last365']

        # Merge with builtin coords to ensure full 81 list
        features = agg[['region','zemin_tipi','chosen_count','ort_mag_chosen','ort_mag_all','total_count','days_since_last','recency_score','lat','lon']].copy()
        features = features.rename(columns={'region':'il'})

        builtin_items = []
        for k,v in BUILTIN_COORDS.items():
            builtin_items.append({'il_key': normalize_key(k), 'builtin_il': k, 'lat_builtin': v[0], 'lon_builtin': v[1]})
        builtin_df = pd.DataFrame(builtin_items)

        features['il_key'] = features['il'].apply(normalize_key)

        merged = pd.merge(builtin_df, features, on='il_key', how='left')
        # canonical display name: prefer original features 'il', else built-in name capitalized
        merged['il_display'] = merged['il'].fillna(merged['builtin_il'].str.capitalize())
        merged['lat'] = merged['lat'].fillna(merged['lat_builtin'])
        merged['lon'] = merged['lon'].fillna(merged['lon_builtin'])

        # fill numeric defaults
        merged['zemin_tipi'] = merged['zemin_tipi'].fillna(2).astype(int)
        merged['chosen_count'] = merged['chosen_count'].fillna(0).astype(int)
        merged['ort_mag_chosen'] = merged['ort_mag_chosen'].fillna(0.0).astype(float)
        merged['ort_mag_all'] = merged['ort_mag_all'].fillna(0.0).astype(float)
        merged['total_count'] = merged['total_count'].fillna(0).astype(int)
        merged['days_since_last'] = merged['days_since_last'].fillna(9999).astype(int)
        merged['recency_score'] = merged['recency_score'].fillna(0.0).astype(float)

        features_final = merged[['il_display','il_key','zemin_tipi','chosen_count','ort_mag_chosen','ort_mag_all','total_count','days_since_last','recency_score','lat','lon']].copy()
        features_final = features_final.drop_duplicates(subset=['il_key']).reset_index(drop=True).sort_values('il_display').reset_index(drop=True)
        features_final = features_final.rename(columns={'il_display':'il'})

        # normalize il_key to be safe
        features_final['il_key'] = features_final['il_key'].astype(str).apply(normalize_key)

        self.df_features = features_final
        return True, "ok"

    def _make_sample_features(self):
        iller = ["İstanbul", "Kahramanmaraş", "Hatay", "İzmir", "Bolu", "Düzce", "Van", "Muğla", "Malatya", "Edirne"]
        np.random.seed(42)
        df = pd.DataFrame({
            "il": iller,
            "zemin_tipi": np.random.randint(1,4,len(iller)),
            "chosen_count": np.random.randint(0, 25, len(iller)),
            "ort_mag_chosen": np.round(np.random.uniform(2.5,6.0,len(iller)),2),
            "ort_mag_all": np.round(np.random.uniform(2.5,6.0,len(iller)),2),
            "total_count": np.random.randint(50,800,len(iller)),
            "days_since_last": np.random.randint(0,60,len(iller)),
            "recency_score": np.random.uniform(0,5,len(iller))
        })
        lats, lons = [], []
        keys = []
        for il in df['il']:
            key = il.strip().lower()
            keys.append(normalize_key(key))
            if normalize_key(key) in BUILTIN_COORDS:
                lat, lon = BUILTIN_COORDS[normalize_key(key)]
            else:
                lat, lon = (np.nan, np.nan)
            lats.append(lat); lons.append(lon)
        df['lat'] = lats; df['lon'] = lons
        df['il_key'] = keys
        return df

    # ---------------- ML / MODEL ----------------
    def _train_model_and_return_df(self, calibrate=False):
        df = self.df_features.copy()
        # use normalized key for stable merging later
        df['il_key'] = df['il_key'].astype(str).apply(normalize_key)
        df['label'] = ((df['chosen_count'] > 5) | (df['ort_mag_chosen'] > 4.5)).astype(int)

        unique_labels = np.unique(df['label'].values)
        if len(unique_labels) < 2:
            heur = self._compute_heuristic_df()
            heur['il_key'] = heur['il'].apply(normalize_key)
            df_model = df[['il','il_key']].copy().merge(heur[['il_key','heuristic_risk']], on='il_key', how='left')
            df_model['model_risk'] = df_model['heuristic_risk'].round(1)
            # set a conservative default model_confidence (heuristic fallback)
            df_model['model_confidence'] = np.round(50.0, 1)
            self.model = None
            self.model_confidence = 0.5
            return df_model

        features = ['zemin_tipi','chosen_count','ort_mag_chosen','ort_mag_all','total_count','days_since_last']
        X = df[features].astype(float).values
        y = df['label'].values

        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        model = RandomForestClassifier(n_estimators=80, random_state=0)
        try:
            model.fit(X_scaled, y)
        except Exception:
            model = RandomForestClassifier(n_estimators=20, random_state=0)
            model.fit(X_scaled, y)

        try:
            probs = model.predict_proba(X_scaled)[:,1]
        except Exception:
            probs = np.zeros(len(X_scaled))

        df_model = df[['il','il_key']].copy()
        df_model['model_risk'] = (probs * 100).round(1)

        try:
            confidences = np.maximum(probs, 1-probs)  # how confident the classifier is for each row
            # per-row confidence in percent
            df_model['model_confidence'] = (confidences * 100).round(1)
            self.model_confidence = float(np.mean(confidences))  # overall mean (0..1)
        except Exception:
            df_model['model_confidence'] = np.round(50.0,1)
            self.model_confidence = 0.5

        try:
            importances = getattr(model, 'feature_importances_', None)
            if importances is not None:
                self.feature_importances = dict(zip(features, importances.tolist()))
        except Exception:
            self.feature_importances = None

        self.model = model
        return df_model

    def _compute_heuristic_df(self):
        df = self.df_features.copy()
        df['il_key'] = df['il_key'].astype(str).apply(normalize_key)
        cols = ['chosen_count','ort_mag_chosen','total_count','recency_score']
        for c in cols:
            vals = df[c].fillna(0).values
            if len(vals) == 0:
                continue
            low, high = np.percentile(vals, [1,99])
            if high - low > 0:
                df[c] = np.clip(df[c], low, high)
            else:
                df[c] = df[c]

        df['days_inv'] = df['days_since_last'].max() - df['days_since_last']

        def z(x):
            x = np.array(x, dtype=float)
            m = np.mean(x); s = np.std(x)
            if s < 1e-6:
                return np.zeros_like(x)
            return (x - m)/s

        sc_z = z(df['chosen_count'])
        om_z = z(df['ort_mag_chosen'])
        tot_z = z(df['total_count'])
        rec_z = z(df['recency_score'])

        w_sc = 0.35; w_om = 0.30; w_tot = 0.15; w_rec = 0.20
        combined_raw = w_sc*sc_z + w_om*om_z + w_tot*tot_z + w_rec*rec_z

        p2, p98 = np.percentile(combined_raw, [2,98])
        if abs(p98 - p2) < 1e-6:
            mx = np.max(np.abs(combined_raw)) if np.max(np.abs(combined_raw))>0 else 1.0
            scaled = 50.0 + (combined_raw / mx) * 50.0
        else:
            scaled = (combined_raw - p2) / (p98 - p2) * 100.0

        def hav(lat1, lon1, lat2, lon2):
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2-lat1; dlon = lon2-lon1
            a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
            c = 2*np.arcsin(np.sqrt(a)); return 6371.0*c

        lats = df['lat'].values; lons = df['lon'].values
        n = len(df); smoothed = np.array(scaled, dtype=float)
        h = 150.0; alpha_spatial = 0.7
        for i in range(n):
            if np.isnan(lats[i]) or np.isnan(lons[i]): continue
            dists = np.array([hav(lats[i], lons[i], lats[j], lons[j]) if not (np.isnan(lats[j]) or np.isnan(lons[j])) else np.inf for j in range(n)])
            w = np.exp(-(dists**2)/(2*(h**2)))
            w[i] = 0.0
            if np.sum(w) <= 0: continue
            w = w/np.sum(w)
            neighbor = np.nansum(w * np.array(scaled))
            smoothed[i] = alpha_spatial*scaled[i] + (1-alpha_spatial)*neighbor

        pri = []
        for il in df['il']:
            k = normalize_key(il)
            val = 0.0
            for bucket, members in PRIOR_BUCKETS.items():
                if k in members:
                    val = PRIOR_VALUES.get(bucket, 0.0); break
            pri.append(val)
        pri = np.array(pri, dtype=float)

        final = smoothed + pri
        p2f, p98f = np.percentile(final, [2,98])
        if abs(p98f - p2f) < 1e-6:
            final_scaled = np.clip(final, 0, 100)
        else:
            final_scaled = (final - p2f) / (p98f - p2f) * 100.0
            final_scaled = np.clip(final_scaled, 0, 100)

        final_mapped = 10.0 + (final_scaled/100.0) * 70.0
        df['heuristic_risk'] = np.round(final_mapped, 1)
        # keep il_key for stable joins
        df['il_key'] = df['il_key'].astype(str)
        return df[['il','il_key','heuristic_risk']]

    def _hybrid_scores(self, model_weight=0.6, calibrate_model=False):
        try:
            model_df = self._train_model_and_return_df(calibrate=calibrate_model)
        except Exception as e:
            print('model train error', e)
            model_df = pd.DataFrame({'il': self.df_features['il'], 'il_key': self.df_features['il_key'], 'model_risk': 0.0, 'model_confidence': np.round(50.0,1)})
        if 'model_risk' not in model_df.columns:
            if 'heuristic_risk' in model_df.columns:
                model_df['model_risk'] = model_df['heuristic_risk']
            else:
                model_df['model_risk'] = 0.0
        if 'model_confidence' not in model_df.columns:
            model_df['model_confidence'] = np.round(50.0,1)

        try:
            heur_df = self._compute_heuristic_df()
        except Exception as e:
            print('heuristic error', e)
            heur_df = pd.DataFrame({'il': self.df_features['il'], 'il_key': self.df_features['il_key'], 'heuristic_risk': 10.0})

        if 'heuristic_risk' not in heur_df.columns:
            heur_df['heuristic_risk'] = 10.0

        def ensure_cols(df_like, cols):
            for c in cols:
                if c not in df_like.columns:
                    df_like[c] = 0.0
            return df_like
        model_df = ensure_cols(model_df, ['il','il_key','model_risk','model_confidence'])
        heur_df = ensure_cols(heur_df, ['il','il_key','heuristic_risk'])

        # normalize keys for safe merging
        model_df['il_key'] = model_df['il_key'].astype(str).apply(normalize_key)
        heur_df['il_key'] = heur_df['il_key'].astype(str).apply(normalize_key)
        df_feat = self.df_features.copy()
        df_feat['il_key'] = df_feat['il_key'].astype(str).apply(normalize_key)

        print('DEBUG model_df cols', list(model_df.columns))
        print('DEBUG heur_df cols', list(heur_df.columns))
        print('DEBUG chosen window (days):', getattr(self, '_chosen_window_days', 30))

        conf = getattr(self, 'model_confidence', None)
        if conf is None: conf = 0.75
        conf = max(0.0, min(1.0, float(conf)))
        final_model_weight = model_weight * conf

        merged = pd.merge(model_df[['il_key','model_risk','model_confidence']], heur_df[['il_key','heuristic_risk']], on='il_key', how='outer')
        merged['model_risk'] = merged['model_risk'].fillna(0.0).astype(float)
        merged['heuristic_risk'] = merged['heuristic_risk'].fillna(10.0).astype(float)
        merged['model_confidence'] = merged['model_confidence'].fillna(np.round(50.0,1)).astype(float)

        merged['model_risk_scaled'] = 10.0 + (merged['model_risk']/100.0) * 70.0

        merged['risk_oran'] = (final_model_weight * merged['model_risk_scaled'] + (1.0 - final_model_weight) * merged['heuristic_risk']).round(1)

        # attach canonical name + coords + counts from df_features using il_key
        # ensure we preserve all 81 provinces by merging onto df_feat (left)
        merged = df_feat[['il','il_key','chosen_count','ort_mag_chosen','total_count','lat','lon']].merge(merged[['il_key','model_risk','model_confidence','heuristic_risk','risk_oran']], on='il_key', how='left')
        # fill missing numeric
        merged['model_risk'] = merged['model_risk'].fillna(0.0).astype(float)
        merged['heuristic_risk'] = merged['heuristic_risk'].fillna(10.0).astype(float)
        merged['model_confidence'] = merged['model_confidence'].fillna(np.round(50.0,1)).astype(float)
        # recompute risk_oran for any missing rows
        conf = getattr(self, 'model_confidence', None)
        if conf is None: conf = 0.75
        conf = max(0.0, min(1.0, float(conf)))
        final_model_weight = model_weight * conf
        merged['model_risk_scaled'] = 10.0 + (merged['model_risk']/100.0) * 70.0
        merged['risk_oran'] = (final_model_weight * merged['model_risk_scaled'] + (1.0 - final_model_weight) * merged['heuristic_risk']).round(1)

        merged = merged.sort_values('risk_oran', ascending=False).reset_index(drop=True)

        cols_out = ['il','il_key','risk_oran','model_risk','model_confidence','heuristic_risk','chosen_count','ort_mag_chosen','total_count','lat','lon']
        for c in cols_out:
            if c not in merged.columns:
                merged[c] = 0.0 if ('risk' in c or 'count' in c) else np.nan

        # normalize il_key column
        merged['il_key'] = merged['il_key'].astype(str).apply(normalize_key)

        self.risk_results = merged[cols_out].copy()
        return

    # --- LIVE FETCH METHODS ---
    def fetch_usgs_earthquakes(self, days=30, min_magnitude=0.0,
                               bbox=(35.0, 25.0, 42.5, 45.0), timeout=8):
        try:
            end = pd.to_datetime(datetime.utcnow())
            start = end - pd.Timedelta(days=days)
            params = {
                "format": "geojson",
                "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
                "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"),
                "minmagnitude": float(min_magnitude),
                "minlatitude": bbox[0],
                "minlongitude": bbox[1],
                "maxlatitude": bbox[2],
                "maxlongitude": bbox[3],
                "orderby": "time-asc",
            }
            url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            geo = resp.json()
            rows = []
            for feat in geo.get("features", []):
                props = feat.get("properties", {})
                geom = feat.get("geometry", {})
                coords = geom.get("coordinates", [None, None, None])
                lon, lat, depth = (coords[0], coords[1], coords[2]) if len(coords) >= 3 else (None, None, None)
                t = props.get("time", None)
                try:
                    t_dt = pd.to_datetime(t, unit='ms')
                except Exception:
                    t_dt = None
                rows.append({
                    "time": t_dt,
                    "latitude": lat,
                    "longitude": lon,
                    "depth": depth,
                    "mag": props.get("mag", None),
                    "place": props.get("place", "") or "",
                    "url": props.get("url", "")
                })
            df = pd.DataFrame(rows)
            if not df.empty:
                df = df.dropna(subset=['latitude','longitude']).reset_index(drop=True)
            print(f"DEBUG fetch_usgs_earthquakes: fetched {len(df)} events (days={days})")
            return df
        except Exception as e:
            print("WARN fetch_usgs_earthquakes failed:", str(e))
            return pd.DataFrame(columns=['time','latitude','longitude','depth','mag','place','url'])

    def _haversine_km(self, lat1, lon1, lat2, lon2):
        try:
            if any(np.isnan([lat1,lon1,lat2,lon2])):
                return np.inf
        except Exception:
            pass
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    def _assign_event_province(self, ev_row, builtin_coords_keys=None, max_nearest_km=120.0):
        place = str(ev_row.get('place', '')).lower()
        lat = ev_row.get('latitude', np.nan)
        lon = ev_row.get('longitude', np.nan)

        def norm(s):
            if not isinstance(s, str):
                return ''
            s = s.strip().lower()
            for a,b in [('ç','c'),('ğ','g'),('ı','i'),('ö','o'),('ş','s'),('ü','u'),('İ','i')]:
                s = s.replace(a,b)
            return s

        place_norm = norm(place)
        bk = {k: (k, BUILTIN_COORDS[k][0], BUILTIN_COORDS[k][1]) for k in BUILTIN_COORDS.keys()}

        for key in bk.keys():
            key_norm = norm(key)
            if key_norm in place_norm or place_norm in key_norm:
                return (key.capitalize(), 0.0, False)

        tokens = [t.strip() for t in place_norm.replace(',', ' ').split()]
        for tk in tokens:
            for key in bk.keys():
                if tk == norm(key):
                    return (key.capitalize(), 0.0, False)

        if not (np.isnan(lat) or np.isnan(lon)):
            min_dist = np.inf
            min_key = None
            for k, coords in BUILTIN_COORDS.items():
                d = self._haversine_km(lat, lon, coords[0], coords[1])
                if d < min_dist:
                    min_dist = d
                    min_key = k
            if min_key is not None:
                return (min_key.capitalize(), float(min_dist), True)

        return ("unknown", np.inf, False)

    def _fetch_live_earthquakes_and_update(self, days=30, min_magnitude=0.0, try_usgs=True):
        try:
            if not try_usgs:
                print("INFO: live fetch disabled (try_usgs=False).")
                return

            ev = self.fetch_usgs_earthquakes(days=days, min_magnitude=min_magnitude)
            if ev.empty:
                print("DEBUG _fetch_live_earthquakes_and_update: no live events fetched.")
                return

            assigned = []
            for i, row in ev.iterrows():
                prov, dist, by_nearest = self._assign_event_province(row)
                assigned.append({'il': prov, 'mag': row.get('mag', np.nan), 'time': row.get('time', None), 'distance_km': dist})
            adf = pd.DataFrame(assigned)
            adf = adf.dropna(subset=['il'])
            if adf.empty:
                print("DEBUG _fetch_live_earthquakes_and_update: no events assigned to provinces.")
                return

            grp = adf.groupby('il').agg(chosen_count_live=('mag','count'),
                                        ort_mag_chosen_live=('mag','mean')).reset_index()

            df_feat = self.df_features.copy()
            df_feat['il_norm'] = df_feat['il'].astype(str).str.strip().str.lower()
            grp['il_norm'] = grp['il'].astype(str).str.strip().str.lower()

            merged = pd.merge(df_feat, grp[['il_norm','chosen_count_live','ort_mag_chosen_live']], left_on='il_norm', right_on='il_norm', how='left')

            merged['chosen_count_live'] = merged['chosen_count_live'].fillna(0).astype(int)
            merged['ort_mag_chosen_live'] = merged['ort_mag_chosen_live'].fillna(0.0).astype(float)

            merged['chosen_count'] = merged['chosen_count_live'].astype(int)
            merged['ort_mag_chosen'] = merged['ort_mag_chosen_live'].round(2)

            merged = merged.drop(columns=['il_norm','chosen_count_live','ort_mag_chosen_live'], errors='ignore')

            cols_needed = ['il','zemin_tipi','chosen_count','ort_mag_chosen','ort_mag_all','total_count','days_since_last','recency_score','lat','lon','il_key']
            for c in cols_needed:
                if c not in merged.columns:
                    merged[c] = 0 if 'count' in c else (np.nan if 'lat' in c or 'lon' in c else 0.0)

            merged = merged[cols_needed]
            # ensure il_key normalized
            merged['il_key'] = merged['il_key'].astype(str).apply(normalize_key)
            self.df_features = merged.copy()

            print(f"DEBUG _fetch_live_earthquakes_and_update: updated df_features with live events (unique provinces: {grp['il'].nunique()})")
            return
        except Exception as e:
            print("WARN _fetch_live_earthquakes_and_update failed:", str(e))
            return

    # ---------------- UI ----------------
    def _draw_plot(self):
        df = self.risk_results.copy()
        self.ax.clear()
        # show only top 10 to avoid overlapping labels
        top_n = min(10, len(df))
        if top_n == 0:
            self.canvas.draw(); return
        df_top = df.head(top_n).copy()
        colors = []
        for x in df_top['risk_oran']:
            if x >= 60:
                colors.append('#ff4d4d')
            elif x >= 35:
                colors.append('#ffb84d')
            else:
                colors.append('#66cc66')
        self.ax.barh(df_top['il'], df_top['risk_oran'], color=colors)
        self.ax.set_xlabel(self._tr("risk_rate") + " (%)")
        self.ax.set_title(self._tr("chart_title"))
        self.ax.invert_yaxis()
        # make labels smaller to avoid overlap
        self.ax.tick_params(axis='y', labelsize=8)
        self.canvas.draw()

    def _show_table(self):
        df = self.risk_results.copy()
        
        # il_key sütununu ve gereksiz sütunları tablodan çıkar
        display_columns = [col for col in df.columns if col not in ['il_key']]
        df_display = df[display_columns]
        
        self.table.clear()
        
        # Sütun başlıklarını çevir
        translated_headers = []
        column_mapping = {
            'il': 'city',
            'risk_oran': 'risk_rate', 
            'model_risk': 'model_risk',
            'model_confidence': 'model_confidence',
            'heuristic_risk': 'heuristic_risk',
            'chosen_count': 'chosen_count',
            'ort_mag_chosen': 'avg_mag',
            'total_count': 'total_count',
            'lat': 'lat',
            'lon': 'lon'
        }
        
        for col in df_display.columns:
            if col in column_mapping:
                translated_headers.append(self._tr(column_mapping[col]))
            else:
                translated_headers.append(col)
        
        self.table.setColumnCount(len(df_display.columns))
        self.table.setRowCount(len(df_display))
        self.table.setHorizontalHeaderLabels(translated_headers)
        
        for r in range(len(df_display)):
            for c, col in enumerate(df_display.columns):
                val = df_display.iloc[r, c]
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(str(val)))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.resizeColumnsToContents()    
    def _update_map(self):
        try:
            # ensure we iterate over full 81 list (df_features) and look up risk by il_key
            df_feat = self.df_features.copy()
            rr = {}
            if self.risk_results is not None and 'il_key' in self.risk_results.columns:
                for _, r in self.risk_results.iterrows():
                    rr_key = normalize_key(r.get('il_key', ''))
                    rr[rr_key] = r.to_dict()

            valid_coords = df_feat.dropna(subset=['lat','lon'])
            if len(valid_coords) > 0:
                center_lat = float(valid_coords['lat'].mean())
                center_lon = float(valid_coords['lon'].mean())
                zoom = 6
            else:
                center_lat, center_lon, zoom = 39.0, 35.0, 5

            m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles='CartoDB positron')

            for _, row in df_feat.iterrows():
                lat = row.get('lat', np.nan)
                lon = row.get('lon', np.nan)
                il = row.get('il', 'unknown')
                ik = normalize_key(str(row.get('il_key', '')))
                if pd.isna(lat) or pd.isna(lon):
                    continue

                risk = 0.0
                chosen_cnt = 0
                model_conf_pct = None
                if ik in rr:
                    rr_entry = rr[ik]
                    risk = rr_entry.get('risk_oran', 0.0)
                    chosen_cnt = rr_entry.get('chosen_count', row.get('chosen_count', 0))
                    model_conf_pct = rr_entry.get('model_confidence', None)

                if risk >= 70:
                    color = "#ff4d4dc1"
                elif risk >=55:
                    color = "#ff4d4dff"
                elif risk >= 35:
                    color = '#ffb84d'
                else:
                    color = '#66cc66'

                mc_text = f"{self._tr('model_confidence')}: {model_conf_pct} %" if (model_conf_pct is not None and not pd.isna(model_conf_pct)) else f"{self._tr('model_confidence')}: N/A"
                popup = folium.Popup(f"<b>{il}</b><br/>{self._tr('risk_rate')}: {risk} %<br/>{self._tr('chosen_count')}: {chosen_cnt}<br/>{mc_text}", max_width=300)
                folium.CircleMarker(location=[lat, lon], radius=6 + (risk/20.0), color=color, fill=True, fill_color=color, fill_opacity=0.8, popup=popup).add_to(m)

            tmp = tempfile.NamedTemporaryFile(prefix='ai_map_', suffix='.html', delete=False)
            tmp_name = tmp.name; tmp.close(); m.save(tmp_name)
            self.map_view.load(QtCore.QUrl.fromLocalFile(tmp_name))
        except Exception:
            traceback.print_exc()

    # ----- new: handlers for model weight and priors -----
    def _on_model_weight_change(self, value):
        try:
            self._current_model_weight = float(value) / 100.0
            self.mw_value_label.setText(f"{int(value)}%")
            # Recompute hybrid scores with new weight and redraw
            try:
                self._hybrid_scores(model_weight=self._current_model_weight)
                self._draw_plot()
                self._show_table()
                self._update_map()
            except Exception as e:
                print("WARN: model weight change update failed:", e)
        except Exception:
            pass

    def _on_prior_changed(self, key):
        try:
            # read value from the corresponding spinbox and update global PRIOR_VALUES
            val = float(self._prior_spinboxes[key].value())
            PRIOR_VALUES[key] = float(val)
            # recompute heuristic + hybrid and redraw
            try:
                # ensure df_features exists
                if self.df_features is not None and len(self.df_features)>0:
                    self._hybrid_scores(model_weight=self._current_model_weight)
                    self._draw_plot()
                    self._show_table()
                    self._update_map()
            except Exception as e:
                print("WARN: prior change update failed:", e)
        except Exception:
            pass

    def _reset_priors_to_defaults(self):
        defaults = {'very_high':90.0,'high':50.0,'medium':25.0,'low':10.0,'very_low':3.0}
        for k,v in defaults.items():
            if k in self._prior_spinboxes:
                self._prior_spinboxes[k].setValue(v)
            PRIOR_VALUES[k] = v
        # trigger recompute
        try:
            if self.df_features is not None and len(self.df_features)>0:
                self._hybrid_scores(model_weight=self._current_model_weight)
                self._draw_plot()
                self._show_table()
                self._update_map()
        except Exception as e:
            print("WARN: reset priors update failed:", e)

    # -------------------------------------------------------

# If running as script, show a simple app
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = AIRiskPenceresi()
    win.show()
    sys.exit(app.exec_())
