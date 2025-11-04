import os
import datetime
import pandas as pd
import streamlit as st
from pipeline import build_itinerary

# 1. 将 BASE 定义移到顶部，并使用 os.path.abspath 使其更健壮
#    这假设 ui.py 位于像 'src' 这样的子目录中
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. 定义一个函数来获取 CSV 路径
def get_csv_path():
    # 确保使用了正确的文件名！
    return os.path.join(BASE, "data", "pois_sample_france.csv")

# 3. 使用 st.cache_data 缓存城市列表
@st.cache_data
def load_city_list(csv_path):
    try:
        df = pd.read_csv(csv_path, encoding='windows-1252')
        cities = sorted(df['city'].unique())
        return cities
    except FileNotFoundError:
        st.error(f"错误：找不到 CSV 文件。请确保 'data/pois_sample_france.csv' 存在于项目根目录。")
        return ["Paris"] # 出错时回退

st.set_page_config(page_title="WanderWeave", layout="centered")
st.title("WanderWeave — Itinéraires & Rencontres")

# 4. 动态加载城市列表
csv_file_path = get_csv_path()
all_cities = load_city_list(csv_file_path)

# 5. 使用动态列表 all_cities 替换硬编码列表
city = st.selectbox("Ville", all_cities, index=0)

topics = st.multiselect("Topics", ["art","photo","street-art","relax","gourmet","locals","romantic","history"], default=["art","relax"])
mode = st.selectbox("Mode", ["solo","amis","rencontres"], index=0)
hidden_ratio = st.slider("Hidden gems (poids)", 0.0, 1.0, 0.3, 0.05)
start_time = st.time_input("Heure de début", datetime.time(9, 30))
end_time = st.time_input("Heure de fin", datetime.time(20, 0))


if st.button("Générer"):
    # 6. 使用前面定义的正确路径
    itin = build_itinerary(
        csv_file_path, city, topics, mode=mode, hidden_ratio=hidden_ratio,
        start_hhmm=start_time.strftime("%H:%M"),
        end_hhmm=end_time.strftime("%H:%M")
    )
    if itin.empty:
        st.warning("Aucun créneau. Essayez d'autres topics ou un hidden ratio différent.")
    else:
        st.dataframe(itin)
        st.download_button("Télécharger CSV", itin.to_csv(index=False).encode("utf-8"), "itinerary.csv", "text/csv")
        md = "# Itinéraire — WanderWeave\n\n" + "\n".join([f"- **{r['time_start']}–{r['time_end']}** — **{r['name']}** [{r['category']}{' (Hidden)' if int(r['hidden'])==1 else ''}] — tags: {r['tags']}" for _,r in itin.iterrows()])
        st.download_button("Télécharger Markdown", md.encode("utf-8"), "itinerary.md", "text/markdown")