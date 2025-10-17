🌍 Earthquake Application (AI-Powered Disaster Risk Analysis)
📘 Project Overview

This application is designed to monitor earthquakes in Turkey and worldwide, perform AI-based risk analysis, and simulate possible earthquake scenarios through an interactive desktop interface.
Built with Python (PyQt5), it offers a multi-language interface, real-time data visualization, and machine learning-based predictions.

🚀 Features
Feature	Description
🌐 Multi-Language Support	Interface available in Turkish, English, Spanish, Arabic, and French.
🧠 AI-Powered Risk Analysis	Calculates earthquake risk scores using real data and ML models.
🗺️ Interactive Map Module	Displays global earthquake data on an interactive map.
📊 Risk Table View	Presents risk data by city with filtering and sorting options.
🔄 Simulation Mode	Generates and visualizes possible earthquake scenarios.
💾 Live Data Updates	Fetches real-time data from AFAD and USGS APIs.
🧩 Technologies Used

Python 3.11+

PyQt5 → GUI framework

QtWebEngine → For map rendering

Requests → API data fetching

Pandas / NumPy → Data processing and analysis

Scikit-learn → Machine learning models

Matplotlib / Seaborn → Data visualization

⚙️ Installation
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py


Note: Make sure PyQtWebEngine is installed.
Some map features require an active internet connection.

📁 Project Structure
📦 EarthquakeApp/
├── __pycache__/
├── data/
│   └── (earthquake and risk datasets)
├── templates/
│   └── (UI templates if used)
├── ai_risk_penceresi.py
├── app.py
├── deprem_gecmisi.json
├── deprem_harita.html
├── deprem_penceresi.py
├── deprem_risk_penceresi.py
├── depremverisi.py
├── [desktop_app.py  ← MAIN FILE]
├── desktop_app_functions.py
├── harita.html
├── harita_liste_penceresi.py
├── simulasyon_penceresi.py
├── son_depremler.json
├── toplanma_penceresi.py
├── translations_ai.py
└── ui_mainwindow.py

🤖 AI Module

The AI module analyzes earthquake-related datasets to predict the risk level for each city.
Model details:

Trained on normalized features (fault line proximity, population density, past earthquake count, etc.)

Uses Random Forest or XGBoost algorithms

Outputs: risk_score (0–1) or categorical levels (Low / Medium / High)

🧭 Future Improvements

 Real-time earthquake notification system

 Emergency meeting point recommendations based on user location

 3D simulation mode (Gazebo / ROS integration)

 Mobile version (Flutter or React Native)

👨‍💻 Developer

Rohat Sarıgül
📍 Çukurova University — Computer Engineering
💡 Interests: Artificial Intelligence, Software Development, Simulation Systems

📜 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute it.
