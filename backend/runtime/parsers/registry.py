import os
from .text_parser import TextParser
from .pdf_parser import PDFParser
from .json_parser import JSONParser

class ParserRegistry:

    def __init__(self):
        self.parsers = {
            ".txt": TextParser(),
            ".pdf": PDFParser(),
            ".json": JSONParser(),
        }

    def get_parser(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.parsers:
            raise ValueError(f"Unsupported file type: {ext}")
        return self.parsers[ext]

