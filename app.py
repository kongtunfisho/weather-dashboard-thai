import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
from io import BytesIO # จำเป็นสำหรับการโหลดไฟล์ Excel

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
        /* ปรับสี Radio Button ให้มองเห็นชัด */
        .stRadio > label {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. ข้อมูล 77 จังหวัด (ตัวอย่างบางส่วน - คุณสามารถนำรายชื่อจังหวัดเต็มๆ จากโค้ดก่อนหน้ามาใส่ตรงนี้ได้เลย)
# ข้อมูล 77 จังหวัดในประเทศไทย (ครบถ้วน)
provinces = {
    "Amnat Charoen": {"lat": 15.8657, "lon": 104.6258},
    "Ang Thong": {"lat": 14.5896, "lon": 100.4551},
    "Bangkok": {"lat": 13.7563, "lon": 100.5018},
    "Bueng Kan": {"lat": 18.3609, "lon": 103.6464},
    "Buriram": {"lat": 14.9930, "lon": 103.1029},
    "Chachoengsao": {"lat": 13.6904, "lon": 101.0780},
    "Chai Nat": {"lat": 15.1852, "lon": 100.1251},
    "Chaiyaphum": {"lat": 15.8105, "lon": 102.0277},
    "Chanthaburi": {"lat": 12.6114, "lon": 102.1039},
    "Chiang Mai": {"lat": 18.7904, "lon": 98.9847},
    "Chiang Rai": {"lat": 19.9105, "lon": 99.8406},
    "Chonburi": {"lat": 13.3611, "lon": 100.9847},
    "Chumphon": {"lat": 10.4930, "lon": 99.1800},
    "Kalasin": {"lat": 16.4322, "lon": 103.5061},
    "Kamphaeng Phet": {"lat": 16.4828, "lon": 99.5227},
    "Kanchanaburi": {"lat": 14.0228, "lon": 99.5328},
    "Khon Kaen": {"lat": 16.4322, "lon": 102.8236},
    "Krabi": {"lat": 8.0863, "lon": 98.9063},
    "Lampang": {"lat": 18.2858, "lon": 99.4910},
    "Lamphun": {"lat": 18.5748, "lon": 99.0087},
    "Loei": {"lat": 17.4860, "lon": 101.7223},
    "Lopburi": {"lat": 14.7995, "lon": 100.6534},
    "Mae Hong Son": {"lat": 19.3021, "lon": 97.9654},
    "Maha Sarakham": {"lat": 16.1857, "lon": 103.3015},
    "Mukdahan": {"lat": 16.5434, "lon": 104.7235},
    "Nakhon Nayok": {"lat": 14.2069, "lon": 101.2130},
    "Nakhon Pathom": {"lat": 13.8196, "lon": 100.0373},
    "Nakhon Phanom": {"lat": 17.3948, "lon": 104.7695},
    "Nakhon Ratchasima": {"lat": 14.9751, "lon": 102.0987},
    "Nakhon Sawan": {"lat": 15.6987, "lon": 100.1372},
    "Nakhon Si Thammarat": {"lat": 8.4309, "lon": 99.9631},
    "Nan": {"lat": 18.7756, "lon": 100.7730},
    "Narathiwat": {"lat": 6.4255, "lon": 101.8253},
    "Nong Bua Lamphu": {"lat": 17.2029, "lon": 102.4411},
    "Nong Khai": {"lat": 17.8785, "lon": 102.7413},
    "Nonthaburi": {"lat": 13.8621, "lon": 100.5140},
    "Pathum Thani": {"lat": 14.0208, "lon": 100.5250},
    "Pattani": {"lat": 6.8696, "lon": 101.2539},
    "Phang Nga": {"lat": 8.4509, "lon": 98.5299},
    "Phatthalung": {"lat": 7.6172, "lon": 100.0709},
    "Phayao": {"lat": 19.1662, "lon": 99.9018},
    "Phetchabun": {"lat": 16.4253, "lon": 101.1526},
    "Phetchaburi": {"lat": 13.1128, "lon": 99.9405},
    "Phichit": {"lat": 16.4416, "lon": 100.3489},
    "Phitsanulok": {"lat": 16.8211, "lon": 100.2659},
    "Phra Nakhon Si Ayutthaya": {"lat": 14.3532, "lon": 100.5684},
    "Phrae": {"lat": 18.1446, "lon": 100.1403},
    "Phuket": {"lat": 7.8804, "lon": 98.3923},
    "Prachinburi": {"lat": 14.0509, "lon": 101.3716},
    "Prachuap Khiri Khan": {"lat": 11.8256, "lon": 99.7925},
    "Ranong": {"lat": 9.9658, "lon": 98.6348},
    "Ratchaburi": {"lat": 13.5283, "lon": 99.8135},
    "Rayong": {"lat": 12.6815, "lon": 101.2816},
    "Roi Et": {"lat": 16.0538, "lon": 103.6520},
    "Sa Kaeo": {"lat": 13.8240, "lon": 102.0646},
    "Sakon Nakhon": {"lat": 17.1542, "lon": 104.1352},
    "Samut Prakan": {"lat": 13.5991, "lon": 100.5967},
    "Samut Sakhon": {"lat": 13.5475, "lon": 100.2749},
    "Samut Songkhram": {"lat": 13.4098, "lon": 100.0023},
    "Saraburi": {"lat": 14.5289, "lon": 100.9101},
    "Satun": {"lat": 6.6238, "lon": 100.0674},
    "Sing Buri": {"lat": 14.8899, "lon": 100.3957},
    "Sisaket": {"lat": 15.1186, "lon": 104.3220},
    "Songkhla": {"lat": 7.1756, "lon": 100.6143},
    "Sukhothai": {"lat": 17.0056, "lon": 99.8196},
    "Suphan Buri": {"lat": 14.4745, "lon": 100.1277},
    "Surat Thani": {"lat": 9.1418, "lon": 99.3296},
    "Surin": {"lat": 14.8905, "lon": 103.4905},
    "Tak": {"lat": 16.8837, "lon": 99.1258},
    "Trang": {"lat": 7.5563, "lon": 99.6114},
    "Trat": {"lat": 12.2428, "lon": 102.5175},
    "Ubon Ratchathani": {"lat": 15.2448, "lon": 104.8473},
    "Udon Thani": {"lat": 17.4156, "lon": 102.7872},
    "Uthai Thani": {"lat": 15.3835, "lon": 100.0246},
    "Uttaradit": {"lat": 17.6201, "lon": 100.0993},
    "Yala": {"lat": 6.5411, "lon": 101.2804},
    "Yasothon": {"lat": 15.7926, "lon": 104.1367}
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

# 3. อัปเกรดฟังก์ชัน API
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
        "past_days": 92
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

# --- FIX 1: แก้ปัญหาค่า None โดยหา Index ของวันปัจจุบันให้ถูกต้อง ---
today_str = datetime.now().strftime("%Y-%m-%d")

# หาตำแหน่งของ "วันนี้" ในลิสต์วันที่ที่ API ส่งมา
if today_str in daily['time']:
    today_idx = daily['time'].index(today_str)
else:
    today_idx = -1 # ถ้าไม่เจอให้เอาตัวสุดท้าย

today_max = daily['temperature_2m_max'][today_idx]
today_min = daily['temperature_2m_min'][today_idx]
uv_today = daily['uv_index_max'][today_idx]
sunrise = daily['sunrise'][today_idx][-5:]
sunset = daily['sunset'][today_idx][-5:]

# ข้อมูลรายชั่วโมง (Current)
current_hour_index = datetime.now().hour 
# เนื่องจาก hourly ข้อมูลเยอะมาก เราใช้ index ล่าสุดของ list (ซึ่งคือปัจจุบัน/อนาคตใกล้ๆ)
# วิธีที่แม่นยำคือหา index ของชั่วโมงปัจจุบันจาก Time List ทั้งหมด
all_hourly_times = hourly['time']
current_hour_iso = datetime.now().strftime("%Y-%m-%dT%H:00")
try:
    # พยายามหาข้อมูลชั่วโมงปัจจุบันเป๊ะๆ
    hourly_now_idx = all_hourly_times.index(current_hour_iso)
except:
    # ถ้าหาไม่เจอ (อาจจะเพราะเรื่อง Timezone) ให้เอา index รองสุดท้าย (ปัจจุบัน)
    hourly_now_idx = -24 + datetime.now().hour # ประมาณการคร่าวๆ จากท้ายตาราง

dew_point = hourly['dew_point_2m'][hourly_now_idx]
visibility = hourly['visibility'][hourly_now_idx] / 1000 
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
                    <div style="font-weight: bold;">{today_max}° / {today_min}°</div> 
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

# --- ส่วนกราฟและ Export (ปรับปรุงใหม่) ---
st.write("---")
st.subheader("📈 กราฟแสดงข้อมูลสภาพอากาศ")

col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    graph_metric = st.selectbox(
        "📦 เลือกข้อมูลที่ต้องการแสดง:",
        ["อุณหภูมิ (Temperature)", "ความชื้น (Humidity)", "แรงลม (Wind Speed)", "ความกดอากาศ (Pressure)", "UV Index"]
    )

with col_opt2:
    time_range = st.selectbox(
        "⏳ เลือกช่วงเวลา:",
        ["24 ชั่วโมงที่ผ่านมา (รายชั่วโมง)", "7 วันที่ผ่านมา (รายชั่วโมง)", "30 วันที่ผ่านมา (รายวัน)", "3 เดือนที่ผ่านมา (รายวัน)"]
    )

# เตรียมข้อมูล
df_full = pd.DataFrame({
    'Time': pd.to_datetime(hourly['time']),
    'Temperature': hourly['temperature_2m'],
    'Humidity': hourly['relative_humidity_2m'],
    'Wind Speed': hourly['wind_speed_10m'],
    'Pressure': hourly['surface_pressure'],
    'UV Index': hourly['uv_index']
})
df_full.set_index('Time', inplace=True)

# --- FIX 2: ตัดข้อมูลอนาคตออก (Graph Clipping) ---
now = datetime.now()
df_historical = df_full[df_full.index <= now] # กรองเอาเฉพาะเวลาที่เป็นอดีตถึงปัจจุบันเท่านั้น

df_plot = pd.DataFrame()

if "24 ชั่วโมง" in time_range:
    start_time = now - timedelta(hours=24)
    # ตัดข้อมูลตั้งแต่ 24 ชม. ที่แล้ว ถึง ปัจจุบัน (ไม่เอาอนาคต)
    df_plot = df_historical[start_time:] 

elif "7 วัน" in time_range:
    start_time = now - timedelta(days=7)
    df_plot = df_historical[start_time:]

elif "30 วัน" in time_range:
    start_time = now - timedelta(days=30)
    df_plot = df_historical[start_time:].resample('D').mean() 

elif "3 เดือน" in time_range:
    start_time = now - timedelta(days=90)
    df_plot = df_historical[start_time:].resample('D').mean()

# เลือกสี
color_hex = "#FFC107"
y_col = "Temperature"
if "ความชื้น" in graph_metric: y_col, color_hex = "Humidity", "#00B0FF"
elif "แรงลม" in graph_metric: y_col, color_hex = "Wind Speed", "#00E676"
elif "ความกดอากาศ" in graph_metric: y_col, color_hex = "Pressure", "#FF4081"
elif "UV" in graph_metric: y_col, color_hex = "UV Index", "#E040FB"

if not df_plot.empty:
    fig = px.area(df_plot, x=df_plot.index, y=y_col, 
                  title=f"แนวโน้ม{graph_metric} - {time_range}",
                  color_discrete_sequence=[color_hex])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#444"))
    st.plotly_chart(fig, use_container_width=True)

    # --- FIX 3: ส่วน Export ข้อมูล ---
    st.write("### 📥 ดาวน์โหลดข้อมูล")
    col_dl1, col_dl2 = st.columns([1, 3])
    
    with col_dl1:
        file_format = st.radio("เลือกประเภทไฟล์:", ["CSV", "Excel (.xlsx)"])
    
    with col_dl2:
        st.write("") # เว้นบรรทัด
        st.write("") 
        if file_format == "CSV":
            csv = df_plot.to_csv().encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f'weather_data_{selected_city}.csv',
                mime='text/csv',
                type="primary"
            )
        else:
            # Export เป็น Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_plot.to_excel(writer, sheet_name='Weather Data')
            
            st.download_button(
                label="Download Excel",
                data=buffer.getvalue(),
                file_name=f'weather_data_{selected_city}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                type="primary"
            )

else:
    st.warning("ไม่มีข้อมูลในช่วงเวลานี้")
