import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import math

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Thailand Weather Center", layout="wide", page_icon="🌤️")

# CSS ปรับแต่งให้เหมือน Weather.com (การ์ดสีขาว/ดำ ตัวเลขใหญ่)
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
        .sub-text {
            font-size: 18px;
            color: #CCCCCC;
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

# 2. ข้อมูลจังหวัด
provinces = {
    "Bangkok": {"lat": 13.7563, "lon": 100.5018}, "Chiang Mai": {"lat": 18.7904, "lon": 98.9847},
    "Phuket": {"lat": 7.8804, "lon": 98.3923}, "Khon Kaen": {"lat": 16.4322, "lon": 102.8236},
    "Nakhon Ratchasima": {"lat": 14.9751, "lon": 102.0987}, "Pattaya": {"lat": 12.9236, "lon": 100.8824},
    "Hat Yai": {"lat": 7.0084, "lon": 100.4747}, "Ayutthaya": {"lat": 14.3532, "lon": 100.5684},
    "Ubon Ratchathani": {"lat": 15.2448, "lon": 104.8473}, "Surat Thani": {"lat": 9.1418, "lon": 99.3296}
    # (สามารถเพิ่มจังหวัดอื่นต่อได้ตรงนี้ครับ)
}

# 3. ฟังก์ชันคำนวณข้างขึ้นข้างแรม (Moon Phase)
def get_moon_phase(date):
    # คำนวณแบบง่ายโดยนับจากวันที่รู้จัก
    diff = date - datetime(2000, 1, 6)
    days = diff.days
    lunation = 29.53059
    phase_index = (days % lunation) / lunation
    
    if phase_index < 0.03: return "🌑 เดือนดับ (New Moon)"
    elif phase_index < 0.25: return "🌒 ข้างขึ้น (Waxing Crescent)"
    elif phase_index < 0.28: return "🌓 จันทร์ครึ่งดวงแรก (First Quarter)"
    elif phase_index < 0.50: return "🌔 ข้างขึ้นแก่ (Waxing Gibbous)"
    elif phase_index < 0.53: return "🌕 จันทร์เพ็ญ (Full Moon)"
    elif phase_index < 0.75: return "🌖 ข้างแรมแก่ (Waning Gibbous)"
    elif phase_index < 0.78: return "🌗 จันทร์ครึ่งดวงหลัง (Last Quarter)"
    else: return "🌘 ข้างแรม (Waning Crescent)"

# 4. ฟังก์ชันดึงข้อมูล API (เพิ่มตัวแปรเยอะขึ้น)
@st.cache_data(ttl=1800)
def get_weather_full(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m",
        "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,uv_index,visibility,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max",
        "timezone": "Asia/Bangkok"
    }
    response = requests.get(url, params=params)
    return response.json()

# --- ส่วน UI หลัก ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1163/1163661.png", width=50)
    st.header("Weather Settings")
    selected_city = st.selectbox("เลือกพื้นที่:", list(provinces.keys()))

coords = provinces[selected_city]
data = get_weather_full(coords['lat'], coords['lon'])

# แปลงข้อมูล
current = data['current']
daily = data['daily']
hourly = data['hourly'] # เอาไว้ทำกราฟ

# วันนี้
today_max = daily['temperature_2m_max'][0]
today_min = daily['temperature_2m_min'][0]
uv_today = daily['uv_index_max'][0]
sunrise = daily['sunrise'][0][-5:]
sunset = daily['sunset'][0][-5:]

# คำนวณค่าที่ API ไม่มีโดยตรงในโหมด Current (ดึงจาก Hourly ชั่วโมงปัจจุบัน)
current_hour_index = datetime.now().hour
dew_point = hourly['dew_point_2m'][current_hour_index]
visibility = hourly['visibility'][current_hour_index] / 1000 # แปลง m เป็น km
moon_phase_text = get_moon_phase(datetime.now())

# --- ส่วนแสดงผลแบบ Weather.com ---

st.title(f"📍 สภาพอากาศ: {selected_city}")

# ส่วน Header ใหญ่ (อุณหภูมิ + สูง/ต่ำ)
col_main, col_radar = st.columns([1, 1.5])

with col_main:
    st.markdown(f"""
        <div class="main-card">
            <div style="font-size: 24px;">{selected_city}, Thailand</div>
            <div style="display: flex; align-items: center;">
                <div class="big-temp">{current['temperature_2m']}°</div>
                <div style="margin-left: 20px;">
                    <div class="sub-text">รู้สึกเหมือน {current['apparent_temperature']}°</div>
                    <div style="font-size: 20px; font-weight: bold;">-- / {today_min}°</div> 
                    </div>
            </div>
            <div style="margin-top: 10px;">
                สูงสุด: {today_max}° • ต่ำสุด: {today_min}°
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Grid รายละเอียด (4 บรรทัด เหมือนเว็บต้นแบบ)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">💨 ลม</div>
                <div class="metric-value">{current['wind_speed_10m']} km/h</div>
            </div>
            <br>
            <div class="metric-box">
                <div class="metric-label">💧 ความชื้น</div>
                <div class="metric-value">{current['relative_humidity_2m']}%</div>
            </div>
            <br>
            <div class="metric-box">
                <div class="metric-label">🌡️ จุดน้ำค้าง</div>
                <div class="metric-value">{dew_point}°</div>
            </div>
             <br>
            <div class="metric-box">
                <div class="metric-label">👁️ ทัศนวิสัย</div>
                <div class="metric-value">{visibility:.1f} km</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">🏋️ ความดัน</div>
                <div class="metric-value">{current['surface_pressure']} mb</div>
            </div>
            <br>
            <div class="metric-box">
                <div class="metric-label">☀️ ดัชนี UV</div>
                <div class="metric-value">{uv_today} ของ 11</div>
            </div>
            <br>
            <div class="metric-box">
                <div class="metric-label">🌔 ดวงจันทร์</div>
                <div class="metric-value" style="font-size: 16px;">{moon_phase_text}</div>
            </div>
            <br>
            <div class="metric-box">
                <div class="metric-label">🌅 ดวงอาทิตย์</div>
                <div class="metric-value" style="font-size: 16px;">ขึ้น {sunrise} / ตก {sunset}</div>
            </div>
        """, unsafe_allow_html=True)

# --- ส่วน Radar Map (Embed Windy) ---
with col_radar:
    st.subheader("📡 เรดาร์สภาพอากาศ (Live Radar)")
    # ใช้ Windy.com Widget เพราะสวยและเหมือนเรดาร์จริงที่สุด
    # ปรับ URL ให้ Focus ไปที่ Lat/Lon ของเมืองที่เลือก
    windy_url = f"https://embed.windy.com/embed2.html?lat={coords['lat']}&lon={coords['lon']}&detailLat={coords['lat']}&detailLon={coords['lon']}&width=650&height=450&zoom=10&level=surface&overlay=radar&product=radar&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=km%2Fh&metricTemp=%C2%B0C&radarRange=-1"
    
    st.components.v1.iframe(windy_url, height=500, scrolling=False)

# --- ส่วนพยากรณ์รายชั่วโมง (กราฟ) ---
st.write("---")
st.subheader("พยากรณ์รายชั่วโมง (24 ชม. ถัดไป)")
df_hourly = pd.DataFrame({
    'Time': pd.to_datetime(hourly['time'][:24]),
    'Temp': hourly['temperature_2m'][:24],
    'Rain': hourly['uv_index'][:24] # ตัวอย่าง
})

# กราฟสวยๆ
fig = px.area(df_hourly, x='Time', y='Temp', title="อุณหภูมิรายชั่วโมง", 
              color_discrete_sequence=['#FFC107'])
fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
st.plotly_chart(fig, use_container_width=True)
