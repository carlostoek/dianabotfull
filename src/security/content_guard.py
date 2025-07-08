# src/security/content_guard.py

class ContentGuard:
    """
    Protege el contenido contra leaks y accesos no autorizados.
    """
    def __init__(self):
        pass

    def apply_watermark(self, content: str, user_id: int) -> str:
        """
        Aplica una marca de agua dinámica al contenido con el user_id.
        
        Args:
            content (str): El contenido original.
            user_id (int): El ID del usuario al que se le muestra el contenido.
            
        Returns:
            str: El contenido con la marca de agua.
        """
        watermarked_content = f"<!-- Watermark: UserID-{user_id} -->\n{content}"
        return watermarked_content

    def disable_forwarding(self, content: str) -> str:
        """
        Implementa medidas para deshabilitar el reenvío de contenido.
        (Esto es una simulación, la implementación real dependería del tipo de contenido y plataforma)
        
        Args:
            content (str): El contenido original.
            
        Returns:
            str: El contenido con medidas para deshabilitar el reenvío.
        """
        # En un entorno real, esto podría implicar:
        # - Añadir metadatos que impidan el reenvío en ciertas plataformas.
        # - Convertir el contenido a un formato no fácilmente compartible.
        # - Usar DRM (Digital Rights Management).
        
        # Para esta simulación, simplemente añadimos un aviso.
        return f"{content}\n<!-- Aviso: Reenvío deshabilitado para este contenido. -->"

content_guard = ContentGuard()