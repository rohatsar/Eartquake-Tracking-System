import requests

def deprem_verilerini_cek():
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
        for d in depremler:
            yer = d["properties"]["place"]
            buyukluk = d["properties"]["mag"]
            print(f"Yer: {yer} - Büyüklük: {buyukluk}")
    else:
        print("API isteği başarısız oldu.")

# Fonksiyonu çalıştır
deprem_verilerini_cek()
