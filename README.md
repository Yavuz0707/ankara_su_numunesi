# 🐜 Ankara Su Numunesi Rota Optimizasyonu (ACO)

Bu proje, **Ant Colony Optimization (Karınca Kolonisi Optimizasyonu)** algoritmasını kullanarak Ankara ve çevresindeki 10 farklı gölet/barajdan su numunesi toplamak için en kısa ve verimli rotayı belirlemeyi amaçlamaktadır.

> **Senaryo:** Çevre Bakanlığı'na ait birimler, zaman kısıtlılığı nedeniyle Ankara'daki numune noktalarını en kısa sürede gezmek zorundadır.

---

## 👤 Öğrenci Bilgileri
* **Ad Soyad:** Şükrü YAVUZ
* **Öğrenci No:** 2312729015
* **Ders:** Karınca Kolonisi Algoritması ile Yol Optimizasyonu

---

## 🚀 Proje Özellikleri
Proje, akademik standartlara uygun modüler bir yazılım mimarisi ile geliştirilmiştir:

* **Gerçek Zamanlı Veri:** Mesafeler, kuş uçuşu değil Google Maps Distance Matrix API üzerinden **gerçek yol mesafeleri (driving distance)** kullanılarak hesaplanır.
* **Dinamik Parametre Yönetimi:** Kullanıcı arayüzü üzerinden $\alpha$, $\beta$, buharlaşma oranı, karınca sayısı ve iterasyon miktarı anlık olarak değiştirilebilir.
* **Görselleştirme:** * **İnteraktif Harita:** Folium tabanlı, durakların ve rotanın animasyonlu (AntPath) gösterimi.
    * **Yakınsama Grafiği:** Algoritmanın her iterasyonda en iyi sonuca nasıl yaklaştığını gösteren Matplotlib grafiği.
* **Güvenlik:** API anahtarları `.streamlit/secrets.toml` içerisinde izole edilmiştir.

---

## 🛠️ Yazılım Mimarisi (Dosya Düzeni)
Proje, sürdürülebilirlik için parçalı (modüler) bir yapıda kurgulanmıştır:

* `main.py`: Uygulamanın ana giriş noktası ve Streamlit arayüz yönetimi.
* `core/ant_algorithm.py`: ACO mantığının ve olasılıksal seçim mekanizmasının bulunduğu hesaplama motoru.
* `data/coordinates.py`: 10 farklı lokasyonun (Mogan, Eymir, Soğuksu vb.) hassas koordinat verileri.
* `visual/`: Grafik ve harita çizim fonksiyonlarının arayüzden ayrıştırıldığı bölüm.

---

## 🧪 Algoritma Parametreleri
Algoritmanın başarısını belirleyen temel "zeka" ayarları:
1.  **Karınca Sayısı:** Her döngüde keşfe çıkan sanal karınca miktarı.
2.  **İterasyon Sayısı:** Algoritmanın kaç nesil boyunca öğrenmeye devam edeceği.
3.  **Buharlaşma Oranı (Decay):** Eski yolların unutulma hızı (Yerel minimuma takılmayı önler).
4.  **Alpha ($\alpha$):** Karıncanın feromon izine (tecrübeye) verdiği ağırlık.
5.  **Beta ($\beta$):** Karıncanın fiziksel mesafeye (açgözlülük) verdiği ağırlık.

---

## 📦 Kurulum ve Çalıştırma

1.  **Kütüphanelerin Yüklenmesi:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **API Anahtarı Yapılandırması:**
    `.streamlit/secrets.toml` dosyası oluşturulmalı ve Google API anahtarı eklenmelidir:
    ```toml
    GOOGLE_API_KEY = "BURAYA_API_ANAHTARINIZI_YAZIN"
    ```

3.  **Uygulamayı Başlatma:**
    ```bash
    streamlit run main.py
    ```

---

## 📊 Sonuç ve Değerlendirme
Bu çalışma, doğadan ilham alan optimizasyon algoritmalarının gerçek yol verileriyle birleştiğinde lojistik maliyetlerini nasıl minimize edebileceğini kanıtlamaktadır. Geliştirilen modüler yapı sayesinde sisteme yeni lokasyonlar kolayca entegre edilebilir.

---
🔗 **GitHub Repo:** [https://github.com/Yavuz0707/ankara-aco-rota-optimizasyonu.git](https://github.com/Yavuz0707/ankara-aco-rota-optimizasyonu.git)
