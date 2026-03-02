import json
from .base import BaseParser

class JSONParser(BaseParser):

    def parse(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        text_blocks = []

        def flatten(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    flatten(v, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    flatten(v, f"{path}[{i}]")
            else:
                text_blocks.append(f"{path}: {obj}")

        flatten(data)

        return [{
            "text": "\n".join(text_blocks),
            "metadata": {
                "source": file_path,
                "type": "json"
            }
        }]

