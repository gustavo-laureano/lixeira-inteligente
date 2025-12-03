import numpy as np
from collections import deque
from time import time
from scipy.integrate import odeint

class PhysicsPredictor:
    """
    Prediz trajetória usando EDO (Equações Diferenciais Ordinárias)
    para considerar gravidade e resistência do ar.
    """
    
    def __init__(self, history_size=10, robot_height=0.0, gravity=9.81, drag_coeff=0.01):
        """
        Args:
            history_size: Quantos pontos guardar no histórico
            robot_height: Altura onde o robô pega o objeto (metros)
            gravity: Aceleração da gravidade (m/s²)
            drag_coeff: Coeficiente de resistência do ar (aprox 0.01 para objetos leves)
        """
        self.robot_height = robot_height
        self.gravity = gravity
        self.drag_coeff = drag_coeff
        
        # Histórico circular
        self.positions = deque(maxlen=history_size)
        self.timestamps = deque(maxlen=history_size)
    
    def add_point(self, position_3d):
        """Adiciona ponto 3D ao histórico"""
        self.positions.append(position_3d)
        self.timestamps.append(time())
    
    def clear_history(self):
        """Limpa histórico"""
        self.positions.clear()
        self.timestamps.clear()
    
    def calculate_velocity(self):
        """
        Calcula velocidade atual usando regressão linear dos pontos recentes.
        Isso serve como condição inicial (v0) para a simulação física.
        """
        if len(self.positions) < 3:
            return None
        
        # Converter para arrays numpy
        t = np.array(self.timestamps)
        pos = np.array(self.positions)
        
        # Normalizar tempo (último frame = 0)
        t_rel = t - t[-1]
        
        # Regressão linear para cada eixo
        # O slope (coeficiente angular) da reta posição x tempo é a velocidade
        vx = np.polyfit(t_rel, pos[:, 0], 1)[0]
        vy = np.polyfit(t_rel, pos[:, 1], 1)[0]
        vz = np.polyfit(t_rel, pos[:, 2], 1)[0]
        
        return np.array([vx, vy, vz])

    def _trajectory_ode(self, state, t):
        """
        Define o sistema de EDOs:
        ds/dt = v
        dv/dt = g - (drag * v * |v|)
        """
        x, y, z, vx, vy, vz = state
        
        # Aceleração devido à resistência do ar (proporcional ao quadrado da velocidade)
        # O sinal negativo e abs(v) garantem que a força é sempre oposta ao movimento
        ax = -self.drag_coeff * vx * abs(vx)
        ay = -self.drag_coeff * vy * abs(vy)
        az = -self.gravity - (self.drag_coeff * vz * abs(vz))
        
        return [vx, vy, vz, ax, ay, az]
    
    def predict_landing(self):
        """
        Prediz ponto de impacto usando integração numérica.
        Substitui a solução analítica (Bhaskara) pela simulação EDO.
        """
        if len(self.positions) < 3:
            return None
        
        # Obter estado inicial (posição e velocidade atuais)
        current_pos = self.positions[-1]
        velocity = self.calculate_velocity()
        
        if velocity is None:
            return None
            
        x0, y0, z0 = current_pos
        vx0, vy0, vz0 = velocity
        
        # Se o objeto já estiver abaixo da altura alvo, não há predição
        if z0 <= self.robot_height:
            return current_pos

        # Estado inicial: [x, y, z, vx, vy, vz]
        initial_state = [x0, y0, z0, vx0, vy0, vz0]
        
        # Configuração da integração
        dt = 0.02  # Passo de tempo (segundos)
        max_time = 5.0  # Tempo limite para evitar loops infinitos
        
        # Loop de simulação passo a passo
        # Usamos um loop externo para verificar a colisão a cada passo pequeno
        current_state = initial_state
        
        for t in np.arange(0, max_time, dt):
            # Integra apenas um passo de tempo [t, t + dt]
            time_span = [0, dt] 
            result = odeint(self._trajectory_ode, current_state, time_span)
            
            # O resultado [1] é o estado no tempo t + dt
            next_state = result[1]
            z_next = next_state[2]
            
            # Verificar se cruzou a altura do robô
            if z_next <= self.robot_height:
                # Interpolação linear simples para refinar o ponto exato de cruzamento
                # entre o passo anterior e o atual (opcional, mas melhora precisão)
                z_prev = current_state[2]
                fraction = (self.robot_height - z_prev) / (z_next - z_prev + 1e-6)
                
                final_x = current_state[0] + (next_state[0] - current_state[0]) * fraction
                final_y = current_state[1] + (next_state[1] - current_state[1]) * fraction
                
                return np.array([final_x, final_y, self.robot_height])
            
            # Atualiza estado para o próximo passo
            current_state = next_state
            
        return None # Não atingiu o chão no tempo limite
    
    def predict_trajectory(self, step=0.05):
        """
        Gera pontos da trajetória completa futura para visualização.
        """
        if len(self.positions) < 3:
            return []
            
        current_pos = self.positions[-1]
        velocity = self.calculate_velocity()
        
        if velocity is None:
            return []

        x0, y0, z0 = current_pos
        vx0, vy0, vz0 = velocity
        
        trajectory = []
        current_state = [x0, y0, z0, vx0, vy0, vz0]
        
        # Adiciona ponto inicial
        trajectory.append(np.array([x0, y0, z0]))
        
        max_steps = 100
        dt = step
        
        for _ in range(max_steps):
            time_span = [0, dt]
            result = odeint(self._trajectory_ode, current_state, time_span)
            next_state = result[1]
            
            x, y, z = next_state[0], next_state[1], next_state[2]
            
            trajectory.append(np.array([x, y, z]))
            
            # Parar se atingir o chão/robô
            if z <= self.robot_height:
                break
                
            current_state = next_state
            
        return trajectory