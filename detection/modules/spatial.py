"""
Processamento espacial 3D - Conversão de pixels para coordenadas reais
"""

import numpy as np


class SpatialProcessor:
    """Converte coordenadas 2D (pixels) para 3D (metros)"""
    
    def __init__(self, camera_width, camera_height, focal_length):
        """
        Args:
            camera_width: Largura da câmera em pixels
            camera_height: Altura da câmera em pixels
            focal_length: Distância focal calibrada
        """
        self.focal_length = focal_length
        self.cx = camera_width // 2
        self.cy = camera_height // 2
    
    def calculate_3d_position(self, bbox, real_object_width):
        """
        Calcula posição 3D do objeto baseado no tamanho aparente
        
        Args:
            bbox: (x1, y1, x2, y2) - Bounding box em pixels
            real_object_width: Largura real do objeto em metros
        
        Returns:
            np.array([x, y, z]) - Posição 3D em metros
            None se cálculo inválido
        """
        x1, y1, x2, y2 = bbox
        
        # Tamanho aparente (pixels)
        w_pixel = x2 - x1
        h_pixel = y2 - y1
        
        if w_pixel < 1:
            return None
        
        # 1. Calcular profundidade (Z) baseado na largura
        z = (self.focal_length * real_object_width) / w_pixel
        
        # 2. Centro do objeto em pixels
        cx_obj = (x1 + x2) / 2
        cy_obj = (y1 + y2) / 2
        
        # 3. Converter para coordenadas 3D
        x = (cx_obj - self.cx) * z / self.focal_length
        y = (cy_obj - self.cy) * z / self.focal_length
        
        return np.array([x, y, z])
    
    def is_valid_position(self, position, max_distance=5.0, max_height=3.0):
        """
        Valida se posição 3D é fisicamente plausível
        
        Args:
            position: np.array([x, y, z])
            max_distance: Distância máxima horizontal (metros)
            max_height: Altura máxima (metros)
        
        Returns:
            bool: True se posição é válida
        """
        if position is None:
            return False
        
        x, y, z = position
        
        # Verificar limites
        if abs(x) > max_distance or abs(y) > max_distance:
            return False
        
        if z < 0 or z > max_height:
            return False
        
        return True
