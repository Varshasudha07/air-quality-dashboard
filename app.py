import streamlit as st
import requests
import joblib
import pandas as pd
from datetime import datetime

# -------------------------------
# PAGE SETTINGS
# -------------------------------
st.set_page_config(page_title="Air Quality Dashboard", layout="centered")

# -------------------------------
# HERO BANNER (TOP DESIGN)
# -------------------------------
st.markdown("""
<style>
.hero {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    padding: 35px;
    border-radius: 15px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}
.hero h1 {
    margin-bottom: 5px;
}
</style>

<div class="hero">
    <h1>🌍 Smart Air Quality Dashboard</h1>
    <p>Real-time Pollution Monitoring • Health Alerts • Live Insights</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# DATE & TIME
# -------------------------------
st.write("🕒", datetime.now().strftime("%A, %d %B %Y  |  %I:%M %p"))

# -------------------------------
# SAFETY TIP
# -------------------------------
st.info("💡 Air Safety Tip: Avoid outdoor exercise when AQI exceeds 200.")

# -------------------------------
# LOAD MODEL
# -------------------------------
model = joblib.load("model.pkl")

# -------------------------------
# API KEY
# -------------------------------
API_KEY = "cbffec8159e5d858ca6c988981b74dbb"   # ← paste your API key

st.markdown("---")

# -------------------------------
# CITY SELECTION
# -------------------------------
cities = ["Delhi","Mumbai","Hyderabad","Chennai","Bangalore","Guntur","Kolkata"]
city = st.selectbox("Select City", cities)

if st.button("Check Air Quality"):

    try:
        # -------------------------------
        # GET COORDINATES
        # -------------------------------
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_data = requests.get(geo_url).json()

        if len(geo_data) == 0:
            st.error("City not found")
        else:
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']

            # -------------------------------
            # MAP
            # -------------------------------
            st.subheader("📍 Location")
            st.map(pd.DataFrame({'lat':[lat],'lon':[lon]}))

            # -------------------------------
            # AIR POLLUTION DATA
            # -------------------------------
            air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
            air = requests.get(air_url).json()

            pm25 = air['list'][0]['components']['pm2_5']
            pm10 = air['list'][0]['components']['pm10']
            no2 = air['list'][0]['components']['no2']
            co = air['list'][0]['components']['co']

            # -------------------------------
            # ML PREDICTION
            # -------------------------------
            prediction = model.predict([[pm25, pm10, no2, co]])
            aqi = int(prediction[0])

            st.markdown("## 🌍 Air Quality Result")

            col1, col2, col3 = st.columns(3)
            col1.metric("🌫 PM2.5", round(pm25,1))
            col2.metric("🌫 PM10", round(pm10,1))
            col3.metric("🌍 AQI", aqi)

            # -------------------------------
            # AQI STATUS
            # -------------------------------
            if aqi <= 50:
                emoji = "😊"
                st.success("Good Air Quality 😊")
            elif aqi <= 100:
                emoji = "🙂"
                st.info("Moderate 🙂")
            elif aqi <= 200:
                emoji = "😷"
                st.warning("Poor Air Quality 😷")
            else:
                emoji = "⚠️"
                st.error("Very Poor / Hazardous ⚠️")

            st.subheader(f"AQI: {aqi} {emoji}")

            # -------------------------------
            # POLLUTION CHART
            # -------------------------------
            st.write("### 📊 Pollution Levels")

            chart_data = pd.DataFrame({
                "Pollutant": ["PM2.5", "PM10", "NO2", "CO"],
                "Level": [pm25, pm10, no2, co]
            })

            st.bar_chart(chart_data.set_index("Pollutant"))

            # -------------------------------
            # AQI TABLE
            # -------------------------------
            st.write("### AQI Categories")

            st.table({
                "AQI Range": ["0-50","51-100","101-200","201-300","301+"],
                "Quality": ["Good","Moderate","Poor","Very Poor","Hazardous"]
            })

            # -------------------------------
            # HEALTH ADVICE
            # -------------------------------
            st.write("### 🩺 Health Advice")

            if aqi > 200:
                st.warning("⚠ Avoid outdoor activities")
                st.warning("😷 Wear mask when outside")
                st.warning("🚫 Keep windows closed")
            elif aqi > 100:
                st.info("Sensitive groups should limit outdoor exposure")
            else:
                st.success("Air quality is safe for outdoor activities")

            # -------------------------------
            # LAST UPDATED
            # -------------------------------
            st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

    except Exception as e:
        st.error(f"Error: {e}")