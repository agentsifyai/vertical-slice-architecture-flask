from dataclasses import dataclass
from typing import List

from app.features.defect_report_analysis.strategy.bullet_report.prompts import Prompts
from app.infra.llm.service import LLMService

import logging, re


@dataclass
class Chunk:
    chunk_content: str
    page_number: int


class Chunker:
    """
    A class that chunks the text into sections based on the location section.
    """

    prompts = Prompts()
    llm = LLMService()

    async def get_chunks(self, text: str) -> List[Chunk]:
        """Split the text into chunks respecting page markers and overlaps."""
        # Split text into pages using regex (case-insensitive)
        pages = re.split(r'<!--\s*page\s*\d+\s*-->', text, flags=re.IGNORECASE)
        
        chunks = []
        page_number = 1

        # Skip first element if empty (in case text starts with page marker)
        if pages[0].strip() == '':
            pages = pages[1:]

        for page_content in pages:
            # Split page content into lines
            lines = page_content.splitlines()
            
            # Chunk measurement parameters
            chunk_size = 36
            overlap = 6
            
            # Create chunks for current page
            for j in range(0, len(lines), chunk_size - overlap):
                chunk = lines[j:j + chunk_size]
                if chunk:  # Only add non-empty chunks
                    chunk_content = "\n".join(chunk)
                    logging.debug("[Page %d] Chunk content:\n %s", page_number, chunk_content)
                    chunks.append(Chunk(
                        chunk_content=chunk_content,
                        page_number=page_number
                    ))
            page_number += 1

        return chunks