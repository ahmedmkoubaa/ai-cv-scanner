import unittest
from unittest.mock import MagicMock, patch

from infrastructure.pdf.pdf_parser import PyPDFParser


class TestPyPDFParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = PyPDFParser()

    @patch("infrastructure.pdf.pdf_parser.PdfReader")
    def test_extract_text_multipage(self, mock_pdf_reader_cls: MagicMock) -> None:
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Jane Doe\nSenior Developer"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "5 years experience in Python and FastAPI."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader_cls.return_value = mock_reader

        result = self.parser.extract_text("dummy_cv.pdf")
        mock_pdf_reader_cls.assert_called_once_with("dummy_cv.pdf")
        self.assertEqual(
            result,
            "Jane Doe\nSenior Developer\n5 years experience in Python and FastAPI.",
        )

    @patch("infrastructure.pdf.pdf_parser.PdfReader")
    def test_extract_text_handles_none_page_content(
        self, mock_pdf_reader_cls: MagicMock
    ) -> None:
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 Content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = None

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader_cls.return_value = mock_reader

        result = self.parser.extract_text("dummy_cv.pdf")
        self.assertEqual(result, "Page 1 Content")

    @patch("infrastructure.pdf.pdf_parser.PdfReader")
    def test_extract_text_file_not_found(self, mock_pdf_reader_cls: MagicMock) -> None:
        mock_pdf_reader_cls.side_effect = FileNotFoundError("File non_existent.pdf not found")

        with self.assertRaises(FileNotFoundError):
            self.parser.extract_text("non_existent.pdf")


if __name__ == "__main__":
    unittest.main()
