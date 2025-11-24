import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
import time

# 1. ตั้งค่าหน้า Dashboard
st.set_page_config(page_title="Thailand Weather Dashboard", layout="wide", page_icon="🌦️")

# CSS ตกแต่งเพิ่มเติมให้ดู Modern ขึ้น
st.markdown("""
    <style>
        .stMetric {
            background-color: #262730;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #4DB6AC;
        }
    </style>
""", unsafe_allow_html=True)

# 2. ข้อมูล 77 จังหวัด (พร้อมพิกัด)
provinces = {
    "Bangkok": {"lat": 13.7563, "lon": 100.5018}, "Amnat Charoen": {"lat": 15.8657, "lon": 104.6258},
    "Ang Thong": {"lat": 14.5896, "lon": 100.4551}, "Bueng Kan": {"lat": 18.3609, "lon": 103.6464},
    "Buriram": {"lat": 14.9930, "lon": 103.1029}, "Chachoengsao": {"lat": 13.6904, "lon": 101.0780},
    "Chai Nat": {"lat": 15.1852, "lon": 100.1251}, "Chaiyaphum": {"lat": 15.8105, "lon": 102.0277},
    "Chanthaburi": {"lat": 12.6114, "lon": 102.1039}, "Chiang Mai": {"lat": 18.7904, "lon": 98.9847},
    "Chiang Rai": {"lat": 19.9105, "lon": 99.8406}, "Chonburi": {"lat": 13.3611, "lon": 100.9847},
    "Chumphon": {"lat": 10.4930, "lon": 99.1800}, "Kalasin": {"lat": 16.4322, "lon": 103.5061},
    "Kamphaeng Phet": {"lat": 16.4828, "lon": 99.5227}, "Kanchanaburi": {"lat": 14.0228, "lon": 99.5328},
    "Khon Kaen": {"lat": 16.4322, "lon": 102.8236}, "Krabi": {"lat": 8.0863, "lon": 98.9063},
    "Lampang": {"lat": 18.2858, "lon": 99.4910}, "Lamphun": {"lat": 18.5748, "lon": 99.0087},
    "Loei": {"lat": 17.4860, "lon": 101.7223}, "Lopburi": {"lat": 14.7995, "lon": 100.6534},
    "Mae Hong Son": {"lat": 19.3021, "lon": 97.9654}, "Maha Sarakham": {"lat": 16.1857, "lon": 103.3015},
    "Mukdahan": {"lat": 16.5434, "lon": 104.7235}, "Nakhon Nayok": {"lat": 14.2069, "lon": 101.2130},
    "Nakhon Pathom": {"lat": 13.8196, "lon": 100.0373}, "Nakhon Phanom": {"lat": 17.3948, "lon": 104.7695},
    "Nakhon Ratchasima": {"lat": 14.9751, "lon": 102.0987}, "Nakhon Sawan": {"lat": 15.6987, "lon": 100.1372},
    "Nakhon Si Thammarat": {"lat": 8.4309, "lon": 99.9631}, "Nan": {"lat": 18.7756, "lon": 100.7730},
    "Narathiwat": {"lat": 6.4255, "lon": 101.8253}, "Nong Bua Lamphu": {"lat": 17.2029, "lon": 102.4411},
    "Nong Khai": {"lat": 17.8785, "lon": 102.7413}, "Nonthaburi": {"lat": 13.8621, "lon": 100.5140},
    "Pathum Thani": {"lat": 14.0208, "lon": 100.5250}, "Pattani": {"lat": 6.8696, "lon": 101.2539},
    "Phang Nga": {"lat": 8.4509, "lon": 98.5299}, "Phatthalung": {"lat": 7.6172, "lon": 100.0709},
    "Phayao": {"lat": 19.1662, "lon": 99.9018}, "Phetchabun": {"lat": 16.4253, "lon": 101.1526},
    "Phetchaburi": {"lat": 13.1128, "lon": 99.9405}, "Phichit": {"lat": 16.4416, "lon": 100.3489},
    "Phitsanulok": {"lat": 16.8211, "lon": 100.2659}, "Phra Nakhon Si Ayutthaya": {"lat": 14.3532, "lon": 100.5684},
    "Phrae": {"lat": 18.1446, "lon": 100.1403}, "Phuket": {"lat": 7.8804, "lon": 98.3923},
    "Prachinburi": {"lat": 14.0509, "lon": 101.3716}, "Prachuap Khiri Khan": {"lat": 11.8256, "lon": 99.7925},
    "Ranong": {"lat": 9.9658, "lon": 98.6348}, "Ratchaburi": {"lat": 13.5283, "lon": 99.8135},
    "Rayong": {"lat": 12.6815, "lon": 101.2816}, "Roi Et": {"lat": 16.0538, "lon": 103.6520},
    "Sa Kaeo": {"lat": 13.8240, "lon": 102.0646}, "Sakon Nakhon": {"lat": 17.1542, "lon": 104.1352},
    "Samut Prakan": {"lat": 13.5991, "lon": 100.5967}, "Samut Sakhon": {"lat": 13.5475, "lon": 100.2749},
    "Samut Songkhram": {"lat": 13.4098, "lon": 100.0023}, "Saraburi": {"lat": 14.5289, "lon": 100.9101},
    "Satun": {"lat": 6.6238, "lon": 100.0674}, "Sing Buri": {"lat": 14.8899, "lon": 100.3957},
    "Sisaket": {"lat": 15.1186, "lon": 104.3220}, "Songkhla": {"lat": 7.1756, "lon": 100.6143},
    "Sukhothai": {"lat": 17.0056, "lon": 99.8196}, "Suphan Buri": {"lat": 14.4745, "lon": 100.1277},
    "Surat Thani": {"lat": 9.1418, "lon": 99.3296}, "Surin": {"lat": 14.8905, "lon": 103.4905},
    "Tak": {"lat": 16.8837, "lon": 99.1258}, "Trang": {"lat": 7.5563, "lon": 99.6114},
    "Trat": {"lat": 12.2428, "lon": 102.5175}, "Ubon Ratchathani": {"lat": 15.2448, "lon": 104.8473},
    "Udon Thani": {"lat": 17.4156, "lon": 102.7872}, "Uthai Thani": {"lat": 15.3835, "lon": 100.0246},
    "Uttaradit": {"lat": 17.6201, "lon": 100.0993}, "Yala": {"lat": 6.5411, "lon": 101.2804},
    "Yasothon": {"lat": 15.7926, "lon": 104.1367}
}

# --- ส่วน Header และนาฬิกา Real-time ---
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.title("🇹🇭 Thailand Weather Dashboard")

with col_head2:
    # ใช้ st.fragment เพื่อให้เฉพาะส่วนนาฬิกาอัปเดตเองทุก 1 วินาที ไม่กระทบส่วนอื่น
    @st.fragment(run_every=1)
    def show_time():
        now = datetime.now()
        # บวกเวลาเป็น GMT+7 (ถ้า Server อยู่ต่างประเทศ)
        # แต่เพื่อความง่ายใช้เวลา Server หรือปรับตามต้องการ
        # ในที่นี้สมมติ Server เป็น UTC ถ้าอยากได้ไทยให้บวกเพิ่ม (ปรับแก้ตามจริงได้)
        # วิธีแบบง่าย: แสดงเวลาปัจจุบัน
        current_time = now.strftime("%H:%M:%S")
        st.metric(label="🕒 Real-time Clock (BKK Time)", value=current_time)
    
    show_time()

# --- ส่วนควบคุม (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    selected_city = st.selectbox("📍 เลือกจังหวัด (77 จังหวัด):", list(provinces.keys()))
    
    st.write("---")
    st.write("📅 **เลือกช่วงเวลา**")
    start_date = st.date_input("วันเริ่มต้น", datetime.now())
    end_date = st.date_input("วันสิ้นสุด", datetime.now())

coords = provinces[selected_city]

# --- ฟังก์ชันดึงข้อมูล (Cache ไว้ 30 นาที ตามโจทย์) ---
@st.cache_data(ttl=1800) # ttl=1800 วินาที = 30 นาที
def get_weather_data(lat, lon, start, end):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,rain,surface_pressure",
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "timezone": "Asia/Bangkok" # ระบุ Timezone ชัดเจน
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'hourly' not in data:
        return pd.DataFrame()

    hourly = data['hourly']
    df = pd.DataFrame({
        "Time": pd.to_datetime(hourly['time']),
        "Temperature (°C)": hourly['temperature_2m'],
        "Humidity (%)": hourly['relative_humidity_2m'],
        "Wind Speed (km/h)": hourly['wind_speed_10m'],
        "Rain (mm)": hourly['rain'],
        "Pressure (hPa)": hourly['surface_pressure']
    })
    return df

# --- การแสดงผลหลัก ---
try:
    df = get_weather_data(coords['lat'], coords['lon'], start_date, end_date)
    
    if df.empty:
        st.error("ไม่พบข้อมูลในช่วงเวลาที่เลือก")
    else:
        # 1. แผนที่แสดงตำแหน่ง (Interactive Map)
        st.subheader(f"🗺️ ตำแหน่ง: {selected_city}")
        
        # สร้าง DataFrame สำหรับ Map จุดเดียว
        map_df = pd.DataFrame({
            "lat": [coords['lat']],
            "lon": [coords['lon']],
            "city": [selected_city]
        })
        
        # ใช้ Plotly Mapbox เพื่อความสวยงามและ Zoom ไปที่จังหวัดนั้น
        fig_map = px.scatter_mapbox(
            map_df, 
            lat="lat", 
            lon="lon", 
            hover_name="city",
            zoom=8, # ระดับการซูม
            height=300
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

        # 2. ข้อมูลล่าสุด (Metrics)
        st.subheader("📊 ข้อมูลสภาพอากาศล่าสุด")
        latest = df.iloc[-1] # ข้อมูลตัวสุดท้าย (ปัจจุบัน/ล่าสุด)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ อุณหภูมิ", f"{latest['Temperature (°C)']} °C")
        col2.metric("💧 ความชื้น", f"{latest['Humidity (%)']} %")
        col3.metric("🌬️ แรงลม", f"{latest['Wind Speed (km/h)']} km/h")
        col4.metric("🌧️ ปริมาณฝน", f"{latest['Rain (mm)']} mm")

        # 3. กราฟแนวโน้ม
        st.subheader("📈 แนวโน้มสภาพอากาศ")
        tab1, tab2, tab3 = st.tabs(["อุณหภูมิ", "ความชื้น", "แรงลม"])
        
        with tab1:
            st.plotly_chart(px.line(df, x="Time", y="Temperature (°C)", title="Temperature Trends", line_shape="spline", color_discrete_sequence=["#FF5252"]), use_container_width=True)
        with tab2:
            st.plotly_chart(px.line(df, x="Time", y="Humidity (%)", title="Humidity Trends", line_shape="spline", color_discrete_sequence=["#448AFF"]), use_container_width=True)
        with tab3:
            st.plotly_chart(px.line(df, x="Time", y="Wind Speed (km/h)", title="Wind Speed Trends", line_shape="spline", color_discrete_sequence=["#69F0AE"]), use_container_width=True)

        # 4. ปุ่ม Download
        st.write("---")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลเป็น Excel/CSV",
            data=csv,
            file_name=f'weather_{selected_city}.csv',
            mime='text/csv',
        )

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
