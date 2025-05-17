class ResponsiveScaler:
    """
    Sistema de escalado responsivo que mantiene proporciones consistentes
    en diferentes resoluciones de pantalla.
    """
    def __init__(self, base_width=1280, base_height=720):
        """
        Inicializa el escalador con dimensiones base de referencia.
        
        Args:
            base_width: Ancho base de diseño (por defecto 1280)
            base_height: Alto base de diseño (por defecto 720)
        """
        self.base_width = base_width
        self.base_height = base_height
        self.current_width = base_width
        self.current_height = base_height
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.aspect_ratio = base_width / base_height
        self.cached_values = {}
        
    def update(self, width, height):
        """
        Actualiza los factores de escala basados en las nuevas dimensiones.
        
        Args:
            width: Ancho actual de la pantalla
            height: Alto actual de la pantalla
        """
        self.current_width = width
        self.current_height = height
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height
        self.aspect_ratio = width / height
        # Limpiar caché cuando cambian las dimensiones
        self.cached_values = {}
        
    def scale_x_value(self, value):
        """Escala un valor horizontal."""
        cache_key = f"x_{value}"
        if cache_key not in self.cached_values:
            self.cached_values[cache_key] = int(value * self.scale_x)
        return self.cached_values[cache_key]
        
    def scale_y_value(self, value):
        """Escala un valor vertical."""
        cache_key = f"y_{value}"
        if cache_key not in self.cached_values:
            self.cached_values[cache_key] = int(value * self.scale_y)
        return self.cached_values[cache_key]
    
    def scale_font_size(self, size):
        """Escala un tamaño de fuente de manera balanceada."""
        cache_key = f"font_{size}"
        if cache_key not in self.cached_values:
            # Usar un promedio ponderado para que la fuente no sea demasiado grande o pequeña
            scale_factor = (self.scale_x * 0.6 + self.scale_y * 0.4)
            self.cached_values[cache_key] = max(12, int(size * scale_factor))
        return self.cached_values[cache_key]
    
    def scale_rect(self, x, y, width, height):
        """Escala un rectángulo completo."""
        return (
            self.scale_x_value(x),
            self.scale_y_value(y),
            self.scale_x_value(width),
            self.scale_y_value(height)
        )
    
    def get_centered_rect(self, width, height, vertical_offset=0):
        """
        Obtiene un rectángulo centrado en la pantalla con dimensiones escaladas.
        
        Args:
            width: Ancho base del rectángulo
            height: Alto base del rectángulo
            vertical_offset: Desplazamiento vertical desde el centro (positivo = hacia abajo)
        
        Returns:
            Tupla (x, y, width, height) con valores escalados
        """
        scaled_width = self.scale_x_value(width)
        scaled_height = self.scale_y_value(height)
        x = (self.current_width - scaled_width) // 2
        y = (self.current_height - scaled_height) // 2 + self.scale_y_value(vertical_offset)
        return (x, y, scaled_width, scaled_height)
    
    def maintain_aspect_ratio(self, width, height):
        """
        Ajusta dimensiones para mantener la relación de aspecto.
        Útil para imágenes y elementos visuales que no deben distorsionarse.
        """
        target_ratio = width / height
        if target_ratio > self.aspect_ratio:
            # Limitar por ancho
            new_width = self.scale_x_value(width)
            new_height = int(new_width / target_ratio)
        else:
            # Limitar por alto
            new_height = self.scale_y_value(height)
            new_width = int(new_height * target_ratio)
        return new_width, new_height
