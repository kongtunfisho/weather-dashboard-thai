import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Thailand Weather Center", layout="wide", page_icon="🌤️")

# CSS ปรับแต่ง Theme
st.markdown("""
    <style>
        .main-card {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 15px;
            color: white;
            margin-bottom: 20px;
        }
        .big-temp {
            font-size: 60px;
            font-weight: bold;
        }
        .metric-box {
            background-color: #2B2B2B;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            height: 100%;
        }
        .metric-label {
            font-size: 14px;
            color: #AAAAAA;
        }
        .metric-value {
            font-size: 20px;
            font-weight: bold;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# 2. ข้อมูลจังหวัด (ตัวอย่างบางส่วน)
provinces = {
    "Bangkok": {"lat": 13.7563, "lon": 100.5018}, "Chiang Mai": {"lat": 18.7904, "lon": 98.9847},
    "Phuket": {"lat": 7.8804, "lon": 98.3923}, "Khon Kaen": {"lat": 16.4322, "lon": 102.8236},
    "Nakhon Ratchasima": {"lat": 14.9751, "lon": 102.0987}, "Pattaya": {"lat": 12.9236, "lon": 100.8824},
    "Hat Yai": {"lat": 7.0084, "lon": 100.4747}, "Ayutthaya": {"lat": 14.3532, "lon": 100.5684},
    "Ubon Ratchathani": {"lat": 15.2448, "lon": 104.8473}, "Surat Thani": {"lat": 9.1418, "lon": 99.3296}
}

def get_moon_phase(date):
    diff = date - datetime(2000, 1, 6)
    days = diff.days
    lunation = 29.53059
    phase_index = (days % lunation) / lunation
    if phase_index < 0.03: return "🌑 เดือนดับ"
    elif phase_index < 0.25: return "🌒 ข้างขึ้น"
    elif phase_index < 0.28: return "🌓 จันทร์ครึ่งดวงแรก"
    elif phase_index < 0.50: return "🌔 ข้างขึ้นแก่"
    elif phase_index < 0.53: return "🌕 จันทร์เพ็ญ"
    elif phase_index < 0.75: return "🌖 ข้างแรมแก่"
    elif phase_index < 0.78: return "🌗 จันทร์ครึ่งดวงหลัง"
    else: return "🌘 ข้างแรม"

# 3. อัปเกรดฟังก์ชัน API ให้ดึงข้อมูลย้อนหลัง (past_days)
@st.cache_data(ttl=1800)
def get_weather_full(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,surface_pressure,wind_speed_10m",
        "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,uv_index,visibility,wind_speed_10m,surface_pressure",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max",
        "timezone": "Asia/Bangkok",
        "past_days": 92  # ดึงข้อมูลย้อนหลังได้สูงสุด 92 วันสำหรับ Free Tier
    }
    response = requests.get(url, params=params)
    return response.json()

# --- UI ส่วน Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1163/1163661.png", width=50)
    st.header("Weather Settings")
    selected_city = st.selectbox("เลือกพื้นที่:", list(provinces.keys()))

coords = provinces[selected_city]
data = get_weather_full(coords['lat'], coords['lon'])

current = data['current']
daily = data['daily']
hourly = data['hourly']

# เตรียมตัวแปร UI
today_max = daily['temperature_2m_max'][0] if daily['temperature_2m_max'] else "-"
today_min = daily['temperature_2m_min'][0] if daily['temperature_2m_min'] else "-"
uv_today = daily['uv_index_max'][0] if daily['uv_index_max'] else "-"
sunrise = daily['sunrise'][0][-5:]
sunset = daily['sunset'][0][-5:]
current_hour_index = datetime.now().hour 
# หมายเหตุ: index อาจคลาดเคลื่อนเล็กน้อยในข้อมูลผสม past_days แต่ใช้เพื่อแสดงผลคร่าวๆได้
dew_point = hourly['dew_point_2m'][-24:][current_hour_index] if len(hourly['dew_point_2m']) > 0 else 0
visibility = hourly['visibility'][-24:][current_hour_index] / 1000 
moon_phase_text = get_moon_phase(datetime.now())

# --- ส่วนแสดงผล Card ด้านบน ---
st.title(f"📍 สภาพอากาศ: {selected_city}")

col_main, col_radar = st.columns([1, 1.5])

with col_main:
    st.markdown(f"""
        <div class="main-card">
            <div style="font-size: 24px;">{selected_city}, Thailand</div>
            <div style="display: flex; align-items: center;">
                <div class="big-temp">{current['temperature_2m']}°</div>
                <div style="margin-left: 20px;">
                    <div style="font-size: 18px; color: #ccc;">รู้สึกเหมือน {current['apparent_temperature']}°</div>
                    <div style="font-weight: bold;">-- / {today_min}°</div> 
                </div>
            </div>
            <div style="margin-top: 10px;">
                สูงสุด: {today_max}° • ต่ำสุด: {today_min}°
            </div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class="metric-box"><div class="metric-label">💨 ลม</div><div class="metric-value">{current['wind_speed_10m']} km/h</div></div><br>
            <div class="metric-box"><div class="metric-label">💧 ความชื้น</div><div class="metric-value">{current['relative_humidity_2m']}%</div></div><br>
            <div class="metric-box"><div class="metric-label">🌡️ จุดน้ำค้าง</div><div class="metric-value">{dew_point}°</div></div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-box"><div class="metric-label">🏋️ ความดัน</div><div class="metric-value">{current['surface_pressure']} hPa</div></div><br>
            <div class="metric-box"><div class="metric-label">☀️ UV Index</div><div class="metric-value">{uv_today}</div></div><br>
            <div class="metric-box"><div class="metric-label">🌔 ดวงจันทร์</div><div class="metric-value" style="font-size:16px;">{moon_phase_text}</div></div>
        """, unsafe_allow_html=True)

with col_radar:
    st.subheader("📡 เรดาร์สภาพอากาศ")
    windy_url = f"https://embed.windy.com/embed2.html?lat={coords['lat']}&lon={coords['lon']}&detailLat={coords['lat']}&detailLon={coords['lon']}&width=650&height=450&zoom=10&level=surface&overlay=radar&product=radar&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=km%2Fh&metricTemp=%C2%B0C&radarRange=-1"
    st.components.v1.iframe(windy_url, height=500, scrolling=False)

# --- 🔥 ส่วนกราฟที่ปรับปรุงใหม่ (The New Graph Section) ---
st.write("---")
st.subheader("📈 กราฟแสดงข้อมูลสภาพอากาศ")

# 1. สร้าง Dropdown สำหรับเลือก
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    # เลือกตัวแปรที่จะดู
    graph_metric = st.selectbox(
        "📦 เลือกข้อมูลที่ต้องการแสดง:",
        ["อุณหภูมิ (Temperature)", "ความชื้น (Humidity)", "แรงลม (Wind Speed)", "ความกดอากาศ (Pressure)", "UV Index"]
    )

with col_opt2:
    # เลือกช่วงเวลา (Time Range)
    time_range = st.selectbox(
        "⏳ เลือกช่วงเวลา:",
        ["24 ชั่วโมงที่ผ่านมา (รายชั่วโมง)", "7 วันที่ผ่านมา (รายชั่วโมง)", "30 วันที่ผ่านมา (รายวัน)", "3 เดือนที่ผ่านมา (รายวัน)"]
    )

# 2. เตรียมข้อมูลดิบทั้งหมดใส่ DataFrame
df_full = pd.DataFrame({
    'Time': pd.to_datetime(hourly['time']),
    'Temperature': hourly['temperature_2m'],
    'Humidity': hourly['relative_humidity_2m'],
    'Wind Speed': hourly['wind_speed_10m'],
    'Pressure': hourly['surface_pressure'],
    'UV Index': hourly['uv_index']
})
df_full.set_index('Time', inplace=True) # ตั้ง Time เป็น Index เพื่อให้ตัดต่อเวลาได้ง่าย

# 3. Logic การกรองข้อมูลตาม
