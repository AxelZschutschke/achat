from __future__ import annotations

class Message:
    class Serializer:
        @staticmethod
        def __call__(message:Message):
            return {"content":message.content, "role":message.role} | message.kwargs

    def __init__(self, content, role="user", **kwargs):
        self.content = content
        self.role = role
        self.kwargs = kwargs

    def serialize(self, serializer:Serializer=Serializer()):
        return serializer(self)
    
    def __repr__(self):
        return f"({self.role}) {self.content}"
    