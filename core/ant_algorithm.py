# core/ant_algorithm.py
import numpy as np
import random

class AntColonyOptimizer:
    def __init__(self, distances, n_ants, n_best, n_iterations, decay, alpha=1, beta=1):
        """
        distances: Mesafe matrisi (2D numpy array)
        n_ants: Karınca sayısı
        n_best: Her iterasyonda feromon bırakacak en iyi karınca sayısı
        n_iterations: İterasyon sayısı
        decay: Feromon buharlaşma oranı (0-1 arası)
        alpha: Feromonun önemi
        beta: Mesafenin (görünürlüğün) önemi
        """
        self.distances = distances
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_inds = range(len(distances))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        
        # Sonuçları saklamak için
        self.best_dist = float('inf')
        self.best_path = []
        self.history = [] # Grafik çizimi için iterasyon sonuçları

    def run(self):
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            self.spread_pheronome(all_paths, self.n_best)
            self.decay_pheromone() # Buharlaşma
            
            # O iterasyonun en iyisini bul
            shortest_path = min(all_paths, key=lambda x: x[1])
            
            if shortest_path[1] < self.best_dist:
                self.best_dist = shortest_path[1]
                self.best_path = shortest_path[0]
            
            self.history.append(self.best_dist)
            
        return self.best_path, self.best_dist, self.history

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            path = self.gen_path(0) # 0. indeksten (Bakanlık) başla
            path_len = self.gen_path_dist(path)
            all_paths.append((path, path_len))
        return all_paths

    def gen_path(self, start_node):
        path = [start_node]
        visited = set(path)
        prev = start_node
        
        for i in range(len(self.distances) - 1):
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            path.append(move)
            visited.add(move)
            prev = move
        
        path.append(start_node) # Başlangıça dön (TSP kuralı)
        return path

    def pick_move(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0 # Ziyaret edilenlere gitme

        # Payda kısmında 0'a bölünmeyi engellemek için küçük bir sayı ekle
        row = pheromone ** self.alpha * (( 1.0 / (dist + 0.0001)) ** self.beta)
        
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
                # Feromon güncelleme kuralı
                self.pheromone[path[i]][path[i+1]] += 1.0 / dist

    def decay_pheromone(self):
        self.pheromone = self.pheromone * (1 - self.decay)