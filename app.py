from flask import Flask, jsonify,render_template, request
import requests
from datetime import datetime,timedelta
import openai
from threading import Thread
import time

app = Flask(__name__)

# OpenAI API anahtarını buraya yapıştır
openai.api_key = "."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/depremler", methods=["GET"])
def depremler():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": "2025-06-01",
        "minmagnitude": 4.5
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "API isteği başarısız oldu."}), 500

@app.route("/depremler_ozet", methods=["GET"])
def depremler_ozet():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": "2025-06-01",
        "minmagnitude": 4.5
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        depremler = data.get("features", [])

        ozet_listesi = []
        for deprem in depremler:
            yer = deprem["properties"].get("place")
            buyukluk = deprem["properties"].get("mag")
            zaman = deprem["properties"].get("time")  # ms cinsinden
            koordinatlar = deprem["geometry"].get("coordinates")  # [boylam, enlem, derinlik]

            # Zamanı okunabilir hale çevir
            dt = datetime.utcfromtimestamp(zaman / 1000) if zaman else None
            zaman_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC") if dt else None

            ozet_listesi.append({
                "yer": yer,
                "buyukluk": buyukluk,
                "zaman": zaman_str,
                "koordinatlar": {
                    "boylam": koordinatlar[0] if koordinatlar else None,
                    "enlem": koordinatlar[1] if koordinatlar else None,
                    "derinlik": koordinatlar[2] if koordinatlar else None
                }
            })

        return jsonify(ozet_listesi)
    else:
        return jsonify({"error": "API isteği başarısız oldu."}), 500
@app.route("/depremler_son30gun", methods=["GET"])
def depremler_son30gun():
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=30)

    minmagnitude = request.args.get("minmagnitude", default="4.5")

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start_date.isoformat(),
        "endtime": today.isoformat(),
        "minmagnitude": minmagnitude
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "API isteği başarısız oldu."}), 500
 
@app.route("/uyari", methods=["GET"])
def uyari():
    client = openai.OpenAI()

    prompt = "Adana'da 6.3 büyüklüğünde deprem oldu. Kullanıcıya sakinleştirici ve bilgilendirici uyarı mesajı yaz."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen sakinleştirici ve bilgilendirici bir uyarı mesajı yazan yapay zekasın."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
    )

    mesaj = response.choices[0].message.content
    return jsonify({"uyari": mesaj})

def deprem_kontrol():
    while True:
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "starttime": "2025-06-01",
            "minmagnitude": 4.5,
            "orderby": "time",
            "limit": 1
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            son_deprem = data["features"][0]
            buyukluk = son_deprem["properties"]["mag"]
            yer = son_deprem["properties"]["place"]
            print(f"Son Deprem: {yer} | Büyüklük: {buyukluk}")

            if buyukluk >= 6.0:
                print("⚠️ 6.0 Üzeri Deprem Oldu! Bildirim Gönderiliyor...")

        else:
            print("API isteği başarısız.")
        
        time.sleep(60)

Thread(target=deprem_kontrol, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
