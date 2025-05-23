from app.infra.pdf.service import PdfReaderService

class Prompts:

    def __init__(self):
        self.scanned_report_system_prompt = """
        You will receive a PDF document as an attachment. 
        The PDF document will contain a scan of a defect report.

        Your task is to output the contents of a scanned report in a markdown format, making markdown as similar as possible to the original report structure.

        You should use markdown headings for labels that could be considered as headings, and adjust heading levels for each embedded heading. Use lists and other markdown features as well when necessary.

        The contents of the report must remain unchanged and in the same language as the original. You must extract all possible data from the scanned report.

        You must not omit the contained images within the scanned report. 

        If an image is contained within the report document, you have to replace it with a detailed description of what is in the image, considering that the image represents things related to the construction defects described in the report. 

        You must delimit each page of the report with a line containing the text '<!-- Page X -->', where X is the page number. 
        Page numbering starts from 1. Therefore, first page must start with <!-- Page 1 --> and so on. 

        Answer with the markdown content only - do not include greetings etc.
        """
        self.scanned_report_user_prompt = """
        Please provide a markdown content of this document:
        """

    def get_scanned_report_messages(self, file_path: str) -> list[dict[str, str]]:
        """
        Get the messages for scanned report processing.
        :return: List of messages for the scanned report processing.
        """
        return [
        { 
            "role": "system", 
            "content": [
            {
              "type": "text",
              "text": self.scanned_report_system_prompt
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": self.scanned_report_user_prompt
            },
            {
              "type": "file",
              "file": {
                "filename": "scannedReport.pdf",
                "file_data": "data:application/pdf;base64," + PdfReaderService.pdf_to_base64(file_path) 
              }
            }
          ]
        }
        ]
