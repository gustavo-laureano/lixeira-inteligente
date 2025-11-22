import numpy as np
from collections import deque
from time import time


class PhysicsPredictor:
    """Prediz trajetória de queda livre considerando gravidade"""
    
    def __init__(self, history_size=10, robot_height=0.0, gravity=9.81):
        """
        Args:
            history_size: Quantos pontos guardar no histórico
            robot_height: Altura onde o robô pega o objeto (metros)
            gravity: Aceleração da gravidade (m/s²)
        """
        self.robot_height = robot_height
        self.gravity = gravity
        
        # Histórico circular
        self.positions = deque(maxlen=history_size)
        self.timestamps = deque(maxlen=history_size)
    
    def add_point(self, position_3d):
        """
        Adiciona ponto 3D ao histórico
        
        Args:
            position_3d: np.array([x, y, z]) em metros
        """
        self.positions.append(position_3d)
        self.timestamps.append(time())
    
    def clear_history(self):
        """Limpa histórico"""
        self.positions.clear()
        self.timestamps.clear()
    
    def calculate_velocity(self):
        """
        Calcula velocidade atual usando regressão linear
        
        Returns:
            np.array([vx, vy, vz]) - Velocidade em m/s
            None se dados insuficientes
        """
        if len(self.positions) < 3:
            return None
        
        # Converter para arrays numpy
        t = np.array(self.timestamps)
        pos = np.array(self.positions)
        
        # Normalizar tempo (último frame = 0)
        t_rel = t - t[-1]
        
        # Regressão linear para cada eixo
        vx = np.polyfit(t_rel, pos[:, 0], 1)[0]
        vy = np.polyfit(t_rel, pos[:, 1], 1)[0]
        vz = np.polyfit(t_rel, pos[:, 2], 1)[0]
        
        return np.array([vx, vy, vz])
    
    def predict_landing(self):
        """
        Prediz ponto de impacto no chão
        
        Returns:
            landing_point: np.array([x, y, z]) - Ponto de chegada
            None se não puder calcular
        """
        if len(self.positions) < 3:
            return None
        
        # Posição e velocidade atuais
        current_pos = self.positions[-1]
        velocity = self.calculate_velocity()
        
        if velocity is None:
            return None
        
        x0, y0, z0 = current_pos
        vx, vy, vz = velocity
        
        # Resolver equação de queda livre
        # z(t) = z0 + vz*t - 0.5*g*t²
        # Queremos z(t) = robot_height
        
        a = -0.5 * self.gravity
        b = vz
        c = z0 - self.robot_height
        
        # Bhaskara
        delta = b**2 - 4*a*c
        
        if delta < 0:
            return None  # Não atinge o chão
        
        t1 = (-b + np.sqrt(delta)) / (2*a)
        t2 = (-b - np.sqrt(delta)) / (2*a)
        
        # Tempo futuro (positivo)
        time_to_impact = max(t1, t2)
        
        if time_to_impact <= 0:
            return None
        
        # Posição de impacto
        x_final = x0 + vx * time_to_impact
        y_final = y0 + vy * time_to_impact
        z_final = self.robot_height
        
        return np.array([x_final, y_final, z_final])
    
    def predict_trajectory(self, step=0.05):
        """
        Gera pontos da trajetória completa
        
        Args:
            step: Intervalo de tempo entre pontos (segundos)
        
        Returns:
            list[np.array([x, y, z])] - Lista de pontos da trajetória
        """
        landing = self.predict_landing()
        
        if landing is None:
            return []
        
        # Posição e velocidade atuais
        current_pos = self.positions[-1]
        velocity = self.calculate_velocity()
        
        x0, y0, z0 = current_pos
        vx, vy, vz = velocity
        
        # Calcular tempo até impacto
        time_to_impact = self._calculate_impact_time(z0, vz)
        
        if time_to_impact <= 0:
            return []
        
        # Gerar pontos
        trajectory = []
        t = 0
        
        while t <= time_to_impact:
            x = x0 + vx * t
            y = y0 + vy * t
            z = z0 + vz * t - 0.5 * self.gravity * t**2
            
            trajectory.append(np.array([x, y, z]))
            t += step
        
        # Adicionar ponto final exato
        trajectory.append(landing)
        
        return trajectory
    
    def _calculate_impact_time(self, z0, vz):
        """Calcula tempo até objeto atingir robot_height"""
        a = -0.5 * self.gravity
        b = vz
        c = z0 - self.robot_height
        
        delta = b**2 - 4*a*c
        
        if delta < 0:
            return -1
        
        t1 = (-b + np.sqrt(delta)) / (2*a)
        t2 = (-b - np.sqrt(delta)) / (2*a)
        
        return max(t1, t2)
