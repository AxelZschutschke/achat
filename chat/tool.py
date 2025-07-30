from __future__ import annotations
import inspect

class Tool:
    class Serializer:
        @staticmethod
        def __call__(tool:Tool):
            lut = {
                "int": "integer",
                "float": "number",
                "str": "string",
                "bool": "bool",
            }
            translate = lambda x: lut[x] if x in lut else x

            return {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            k: {"type":translate(v)} for k,v in tool.parameters.values()
                        },
                        "required": tool.required,
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }

    def __init__(self, tool:callable):
        self.cb = tool
        self.name = tool.__name__
        self.description = tool.__doc__
        spec = inspect.signature(tool).parameters.values()
        self.parameters = {
            param.name: (param.annotation.__class__) for param in spec
        }
        self.required = [
            param.name for param in spec if isinstance(param.default, inspect._empty)
        ]

    def serialize(self, serializer:Serializer=Serializer()):
        return serializer(self)
