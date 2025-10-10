from typing import List, Dict

class ConversationMemory:
    """
    Clase para gestionar y mantener el historial de conversaciones.
    Almacena mensajes con roles y contenido, con límite de longitud.

    Params:
        max_history (int, optional): Número máximo de mensajes a mantener en el historial. Por defecto 10.

    """

    def __init__(self, max_history: int = 10):

        self.max_history = max_history
        self.conversation_history = []


    def add_message(self, role: str, content: str):
        """
        Añade un mensaje al historial de conversación.

        Params:
            role (str): Rol del emisor (ej: 'user', 'system')
            content (str): Contenido del mensaje
        """
        message = {
            "role": role,
            "content": content
        }
        self.conversation_history.append(message)
        
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[1:]

    def get_conversation_as_text(self, include_roles: bool = True) -> str:
        """
        Convierte el historial de conversación a texto formateado.

        Params:
            include_roles (bool, optional): Si incluir los roles en el texto. Por defecto True.
        """
        if not self.conversation_history:
            return ""
        
        lines = []
        for message in self.conversation_history:
            if include_roles:
                lines.append(f"{message['role'].upper()}: {message['content']}")
            else:
                lines.append(message['content'])
        
        return "\n".join(lines)

    def get_full_history(self) -> List[Dict]:
        """
        Devuelve una copia completa del historial de conversación.

        """
        return self.conversation_history.copy()
    

    def is_empty(self) -> bool:
        """
        Verifica si el historial de conversación está vacío.
        """
        return len(self.conversation_history) == 0
