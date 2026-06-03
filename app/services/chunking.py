import re 
from typing import List
class ChunkingEngine:
    @staticmethod
    def chunk_fixed_size(text: str, chunk_size: int = 600, chunk_overlap: int = 60) -> List[str]:
        """Strategy 1: Pure Fixed-Character Sliding Window Overlap"""
        chunks: List[str] = []
        if not text:
            return chunks
        
        start = 0 
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start += (chunk_size - chunk_overlap)
        return chunks

    @staticmethod
    def chunk_recursive_paragraph(text: str, max_chunk_size: int = 800) -> List[str]:
        """Strategy B: Recursive Structural Splitter (Paragraphs down to Sentences)"""
        paragraphs = re.split(r'\n{2,}', text.strip())
        final_chunks: List[str] = []
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            if len(current_chunk) + len(paragraph) + 1 <= max_chunk_size:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
            else:
                if current_chunk:
                    final_chunks.append(current_chunk)
                    current_chunk = ""

                if len(paragraph) <= max_chunk_size:
                    current_chunk = paragraph
                else:
                    
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
                            current_chunk += " " + sentence if current_chunk else sentence
                        else:
                            if current_chunk:
                                final_chunks.append(current_chunk)
                            current_chunk = sentence

        if current_chunk:
            final_chunks.append(current_chunk)
        
        return final_chunks