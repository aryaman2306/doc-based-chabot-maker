from pypdf import PdfReader
from .base import BaseParser

class PDFParser(BaseParser):

    def parse(self, file_path: str):
        reader = PdfReader(file_path)
        results = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                results.append({
                    "text": text,
                    "metadata": {
                        "source": file_path,
                        "type": "pdf",
                        "page": i + 1
                    }
                })

        return results

