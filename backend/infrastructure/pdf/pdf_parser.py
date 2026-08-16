from pypdf import PdfReader


class PyPDFParser:
    def extract_text(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
