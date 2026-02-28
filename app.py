import streamlit as st
import requests
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="Air Quality Dashboard", page_icon="🌍", layout="wide")

# ---------------- TRAIN MODEL (NO model.pkl NEEDED) ----------------
@st.cache_resource
def train_model():
    data = pd.read_csv("data.csv")
    data = data.dropna()

    X = data[['PM2.5','PM10','NO2','CO']]
    y = data['AQI']

    model = RandomForestRegressor()
    model.fit(X, y)
    return model

model = train_model()

# ---------------- OPENWEATHER API ----------------
API_KEY = "cbffec8159e5d858ca6c988981b74dbb"

# ---------------- HEADER ----------------
st.title("🌍 Smart Air Quality Dashboard")
st.caption("Real-time Air Pollution Monitoring & Health Insights")

st.info("🔎 Select a city to view real-time air quality & health recommendations")

# ---------------- CITY SELECT ----------------
cities = ["Delhi","Mumbai","Hyderabad","Chennai","Bangalore","Kolkata","Guntur"]
city = st.selectbox("Select City", cities)

# ---------------- BUTTON ----------------
if st.button("Check Air Quality"):

    # get coordinates
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo_data = requests.get(geo_url).json()

    if len(geo_data) == 0:
        st.error("City not found")
    else:
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']

        # fetch pollution data
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        air = requests.get(air_url).json()

        pm25 = air['list'][0]['components']['pm2_5']
        pm10 = air['list'][0]['components']['pm10']
        no2 = air['list'][0]['components']['no2']
        co = air['list'][0]['components']['co']

        # predict AQI
        prediction = model.predict([[pm25, pm10, no2, co]])
        aqi = int(prediction[0])

        # emoji indicator
        if aqi <= 50:
            emoji = "😊"
            status = "Good"
            color = "green"
        elif aqi <= 100:
            emoji = "🙂"
            status = "Moderate"
            color = "blue"
        elif aqi <= 200:
            emoji = "😷"
            status = "Poor"
            color = "orange"
        else:
            emoji = "⚠️"
            status = "Very Poor / Hazardous"
            color = "red"

        # ---------------- AQI DISPLAY ----------------
        st.subheader(f"AQI: {aqi} {emoji}")
        st.markdown(f"### Status: :{color}[{status}]")

        # ---------------- HEALTH TIP ----------------
        if aqi > 200:
            st.error("⚠ Avoid outdoor exercise. Wear a mask.")
        elif aqi > 100:
            st.warning("Limit prolonged outdoor activity.")
        else:
            st.success("Air quality is safe for outdoor activities.")

        # ---------------- POLLUTION CHART ----------------
        st.write("### 📊 Pollution Levels")

        chart_data = pd.DataFrame({
            "Pollutant": ["PM2.5", "PM10", "NO2", "CO"],
            "Level": [pm25, pm10, no2, co]
        })

        st.bar_chart(chart_data.set_index("Pollutant"))

        # ---------------- LOCATION MAP ----------------
        st.write("### 📍 Location")
        map_data = pd.DataFrame({'lat':[lat],'lon':[lon]})
        st.map(map_data)

        # ---------------- AQI TABLE ----------------
        st.write("### AQI Categories")
        st.table({
            "AQI Range": ["0-50","51-100","101-200","201-300","301+"],
            "Quality": ["Good","Moderate","Poor","Very Poor","Hazardous"]
        })

        # ---------------- LAST UPDATED ----------------
        st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y | %I:%M %p')}")