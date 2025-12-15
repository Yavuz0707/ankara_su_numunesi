import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import AntPath
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import time

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Ankara ACO Su Rotası",
    page_icon="🐜",
    layout="wide"
)

# --- CSS İYİLEŞTİRMELERİ ---
st.markdown("""
    <style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center;}
    </style>
    """, unsafe_allow_html=True)

# --- 1. VERİ HAZIRLIĞI (SENARYO 5) ---
LOCATIONS = {
    "Merkez (Baslangic)": (39.9079, 32.8169),
    "Mogan Golu": (39.7745, 32.7936),
    "Eymir Golu": (39.8258, 32.8317),
    "Goksu Parki": (39.9880, 32.6450),
    "Mavi Gol": (39.9272, 32.9461),
    "Cubuk-1 Baraji": (40.0053, 33.0308),
    "Kurtbogazi Baraji": (40.2458, 32.6825),
    "Karagol": (40.3011, 32.9097),
    "Soguksu Milli Parki": (40.4686, 32.6231),
    "Kesikkopru Baraji": (39.3800, 33.2980)
}

# --- 2. GOOGLE MAPS API FONKSİYONU ---
@st.cache_data # API çağrısını önbelleğe alıp hızlandırır ve maliyeti düşürür
def get_google_matrix(locations):
    # Anahtarı güvenli yerden çekiyoruz (Kriter 1)
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        st.error("Lütfen .streamlit/secrets.toml dosyasını oluşturup API anahtarını ekleyin.")
        return None

    coords = list(locations.values())
    origins = "|".join([f"{lat},{lon}" for lat, lon in coords])
    destinations = origins
    
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origins}&destinations={destinations}&key={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    if data.get('status') != 'OK':
        st.error(f"API Hatası: {data.get('error_message')}")
        return None
        
    rows = data['rows']
    num = len(coords)
    matrix = np.zeros((num, num))
    
    for i in range(num):
        elements = rows[i]['elements']
        for j in range(num):
            if elements[j]['status'] == 'OK':
                matrix[i][j] = elements[j]['distance']['value'] / 1000.0
            else:
                matrix[i][j] = 9999 
    return matrix

# --- 3. GERÇEK KARINCA KOLONİSİ ALGORİTMASI (ACO) ---
class AntColonyOptimizer:
    def __init__(self, distances, n_ants, n_best, n_iterations, decay, alpha=1, beta=1):
        self.distances = distances
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_inds = range(len(distances))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.history = [] # Grafik için geçmişi tut

    def run(self):
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)
        
        progress_bar = st.progress(0)
        
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            self.spread_pheronome(all_paths, self.n_best)
            shortest_path = min(all_paths, key=lambda x: x[1])
            
            if shortest_path[1] < all_time_shortest_path[1]:
                all_time_shortest_path = shortest_path
            
            self.pheromone *= self.decay
            self.history.append(all_time_shortest_path[1])
            
            # Progress bar güncelle
            progress_bar.progress((i + 1) / self.n_iterations)
            
        return all_time_shortest_path, self.history

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            path = self.gen_path(0)
            all_paths.append((path, self.gen_path_dist(path)))
        return all_paths

    def gen_path(self, start):
        path = [start]
        visited = set(path)
        prev = start
        for i in range(len(self.distances) - 1):
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            path.append(move)
            prev = move
            visited.add(move)
        path.append(start) # Merkeze dönüş
        return path

    def pick_move(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0

        row = pheromone ** self.alpha * ((1.0 / (dist + 0.01)) ** self.beta) # 0'a bölme hatası önlemi
        norm_row = row / row.sum()
        move = np.random.choice(self.all_inds, 1, p=norm_row)[0]
        return move

    def gen_path_dist(self, path):
        total_dist = 0
        for i in range(len(path) - 1):
            total_dist += self.distances[path[i]][path[i+1]]
        return total_dist

    def spread_pheronome(self, all_paths, n_best):
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist in sorted_paths[:n_best]:
            for i in range(len(path) - 1):
                self.pheromone[path[i]][path[i+1]] += 1.0 / dist

# --- 4. ARAYÜZ (STREAMLIT) ---
st.title("🐜 Ankara Su Numunesi ACO Optimizasyonu")
st.markdown("Bu proje, **Karınca Kolonisi Algoritması** kullanarak en kısa numune toplama rotasını belirler.")

# --- Sidebar: Parametreler (Kriter 3) ---
with st.sidebar:
    st.header("⚙️ ACO Parametreleri")
    n_ants = st.slider("Karınca Sayısı (Popülasyon)", 5, 50, 20)
    n_iterations = st.slider("İterasyon Sayısı", 10, 100, 30)
    evaporation = st.slider("Buharlaşma Oranı (Decay)", 0.1, 0.99, 0.95)
    alpha = st.slider("Feromon Etkisi (Alpha)", 0.1, 5.0, 1.0)
    beta = st.slider("Mesafe Etkisi (Beta)", 0.1, 5.0, 2.0)
    st.info("Parametreleri değiştirerek algoritmanın performansını test edebilirsiniz.")

# --- Hesaplama Butonu ---
if st.button("🚀 ACO Algoritmasını Başlat", type="primary"):
    with st.spinner("Mesafe matrisi alınıyor ve karıncalar yola çıkıyor..."):
        
        # 1. Mesafe Matrisi
        dist_matrix = get_google_matrix(LOCATIONS)
        
        if dist_matrix is not None:
            # 2. ACO Çalıştır
            optimizer = AntColonyOptimizer(
                distances=dist_matrix, 
                n_ants=n_ants, 
                n_best=5, 
                n_iterations=n_iterations, 
                decay=evaporation,
                alpha=alpha,
                beta=beta
            )
            
            (best_path, best_dist), history = optimizer.run()
            
            # Session State Kaydı
            st.session_state['aco_path'] = best_path
            st.session_state['aco_dist'] = best_dist
            st.session_state['aco_history'] = history
            st.session_state['run_done'] = True

# --- Sonuçların Gösterimi ---
if st.session_state.get('run_done'):
    path = st.session_state['aco_path']
    total_km = st.session_state['aco_dist']
    history = st.session_state['aco_history']
    
    names = list(LOCATIONS.keys())
    coords = list(LOCATIONS.values())

    # İstatistikler
    c1, c2, c3 = st.columns(3)
    c1.metric("En Kısa Mesafe", f"{total_km:.2f} km")
    c2.metric("İyileşme Oranı", f"% {((history[0]-history[-1])/history[0]*100):.1f}")
    c3.metric("Son İterasyon", n_iterations)

    st.markdown("---")
    
    # Harita ve Grafik Yan Yana
    col_map, col_graph = st.columns([1.5, 1])
    
    with col_map:
        st.subheader("🗺️ Optimum Rota")
        m = folium.Map(location=[39.95, 32.85], zoom_start=9, tiles="cartodbpositron")
        
        route_coords = [coords[i] for i in path]
        
        # Karınca Yolu Animasyonu
        AntPath(locations=route_coords, color="red", weight=4, delay=800).add_to(m)
        
        for i, idx in enumerate(path[:-1]):
            folium.Marker(
                coords[idx], 
                tooltip=f"{i}. {names[idx]}",
                icon=folium.Icon(color="blue", icon="tint", prefix="fa") if i>0 else folium.Icon(color="green", icon="flag", prefix="fa")
            ).add_to(m)
            
        st_folium(m, height=400, use_container_width=True)
        
    with col_graph:
        st.subheader("📈 Yakınsama Grafiği (Convergence)")
        # Matplotlib ile grafik çizimi (Kriter 3 - İterasyon grafiği)
        fig, ax = plt.subplots()
        ax.plot(history, marker='o', linestyle='-', color='b')
        ax.set_title("Mesafenin İterasyonlara Göre Değişimi")
        ax.set_xlabel("İterasyon")
        ax.set_ylabel("Toplam Mesafe (km)")
        ax.grid(True)
        st.pyplot(fig)

    # Rota Listesi
    with st.expander("📋 Detaylı Rota Planını Gör"):
        for i, p in enumerate(path):
            if i == 0 or i == len(path)-1:
                st.write(f"🏁 **{names[p]}**")
            else:
                st.write(f"⬇ {i}. Durak: {names[p]}")