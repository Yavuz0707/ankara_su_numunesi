# core/matrix_utils.py
import googlemaps
import pandas as pd
import numpy as np
import streamlit as st
import os

def get_distance_matrix(locations, api_key):
    """
    Google Maps API kullanarak lokasyonlar arası sürüş mesafesini (km) ve süresini çeker.
    """
    gmaps = googlemaps.Client(key=api_key)
    
    names = list(locations.keys())
    coords = list(locations.values())
    n = len(names)
    
    # Matrisleri başlat
    dist_matrix = np.zeros((n, n))
    
    # Google Maps Distance Matrix API limitleri nedeniyle (maks 100 eleman/sorgu)
    # Büyük setlerde parçalı göndermek gerekebilir ama 10 nokta için (10x10=100) tam sınırdadır.
    # Güvenli olması için döngü ile yapıyoruz (biraz yavaş ama güvenli).
    
    try:
        # Not: Gerçek projede API request sayısını düşürmek için bu veriyi bir kez çekip
        # CSV veya JSON olarak kaydetmek en iyisidir.
        
        # Koordinatları string formatına çevir (lat,lng)
        origins = [f"{lat},{lng}" for lat, lng in coords]
        destinations = origins
        
        # API Çağrısı
        response = gmaps.distance_matrix(origins, destinations, mode="driving")
        
        if response['status'] != 'OK':
            st.error("Google Maps API Hatası!")
            return None

        rows = response['rows']
        for i in range(n):
            elements = rows[i]['elements']
            for j in range(n):
                if i == j:
                    dist_matrix[i][j] = 0
                else:
                    # distance -> text: "15 km", value: 15000 (metre)
                    # duration -> text: "20 mins", value: 1200 (saniye)
                    try:
                        meters = elements[j]['distance']['value']
                        dist_matrix[i][j] = meters / 1000.0 # km cinsinden
                    except KeyError:
                        # Rota bulunamazsa çok yüksek değer ata
                        dist_matrix[i][j] = 9999.0
                        
        return dist_matrix

    except Exception as e:
        st.error(f"Matris oluşturulurken hata: {e}")
        return None