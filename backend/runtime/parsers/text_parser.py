from .base import BaseParser

class TextParser(BaseParser):

    def parse(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return [{
            "text": content,
            "metadata": {
                "source": file_path,
                "type": "text"
            }
        }]

