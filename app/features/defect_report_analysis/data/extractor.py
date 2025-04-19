from app.domain.models import MarkdownReport
from app.infra.vlm.service import VlmService
from app.infra.pdf.service import PdfReaderService
from app.infra.xls.service import ExcelReaderService
from docling.document_converter import DocumentConverter
import re
import logging


class ReportDataExtractor:
    file_path: str

    def __init__(self) -> None:
        self.vlm = VlmService()
        self.pdf_reader = PdfReaderService()
        self.excel_reader = ExcelReaderService()

    def is_scanned_pdf(self, file_path: str) -> bool:
        """Checks if the PDF file is scanned."""
        if "protocole" in file_path.lower():
            return False
        # TODO: Find out a faster way to get a count of images and actual text.
        return True  # Placeholder for actual implementation

    def handle_pdfs(self, file_path) -> str:
        """Handles PDF files."""
        # Attempt to read the text from the PDF. If the first pass has no text, use the VLM to read it.
        # pdf_res = self.pdf_reader.read_pdf_text_as_markdown(file_path)
        # Use the VLM service to extract text from scanned PDFs

        try:
            converter = DocumentConverter()
            result = converter.convert(file_path)

            pages = result.document.pages
            content_chunks = []
            text_found = False
            for i, page in enumerate(pages):
                text = getattr(page, "text", "").strip()
                if text:
                    text_found = True
                content_chunks.append(f"<!-- Page {i + 1} -->\n{text}")

            if not text_found:
                logging.warning("Docling returned no page text — falling back to PdfReaderService")
                raise ValueError("Docling returned empty")

            return "\n\n".join(content_chunks)
        except Exception:
        # fallback if anything fails
            pdf_res = self.pdf_reader.read_pdf_text_as_markdown(file_path)
            if pdf_res == 'No readable text found in the PDF. The document might be scanned or contain only images.':
                return self.vlm.extract_scanned_report_as_markdown(file_path)
            else:
                return pdf_res
        
    def _add_page_breaks(self, file_path: str) -> str:
        try:
            converter = DocumentConverter()
            result = converter.convert(file_path)

            chunks = []
            for i, page in enumerate(result.document.pages):
                text = getattr(page, "text", "")
                logging.info(f"Page {i+1} content:\n{text}")
                chunks.append(f"<!-- Page {i + 1} -->\n{text.strip()}")

            return "\n\n".join(chunks)

        except Exception as e:
            import traceback
            logging.error("Error adding page breaks:\n%s", traceback.format_exc())
            return f"Error adding page breaks: {str(e)}"

    def _flatten_tables(self, markdown: str) -> str:
        def table_to_list(match):
            table = match.group(0)
            lines = table.strip().split('\n')
            headers = [h.strip() for h in lines[0].strip('|').split('|')]
            rows = [line.strip('|').split('|') for line in lines[2:]]

            flattened = ""
            for row in rows:
                items = [f"{k}: {v.strip()}" for k, v in zip(headers, row)]
                flattened += "- " + ", ".join(items) + "\n"
            return flattened.strip()

        pattern = r'\|.*\|\n\|[-\s|]+\|\n(?:\|.*\|\n?)+'
        return re.sub(pattern, table_to_list, markdown)    

    async def extract_markdown(self, file_path: str) -> MarkdownReport:
        """Extracts content from a file as markdown."""
        # If the file is a scanned report, use VLM service to extract text
        match file_path:
            case file_path if file_path.endswith('.pdf'):
                content = self.handle_pdfs(file_path)
            case file_path if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                content = self.excel_reader.read_excel_text_as_markdown(file_path)
            case _:
                raise ValueError("Unsupported file type. Only PDF and Excel files are supported.")

        # Page breaks and flatten tables
        final_markdown = self._flatten_tables(content)

        logging.info("Extracted Markdown Report:\n%s", final_markdown)

        return MarkdownReport(content)
