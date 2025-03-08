import os
import tempfile
from typing import Dict, List, Tuple
import PyPDF2
import docx
import re


class DocumentProcessor:
    """Service for processing CV documents and extracting structured information"""
    
    def __init__(self):
        self.section_headers = [
            "education", "experience", "employment", "work experience", 
            "skills", "publications", "awards", "honors", "achievements",
            "projects", "research", "leadership", "professional activities",
            "languages", "certifications", "memberships", "affiliations",
            "volunteering", "references", "personal"
        ]
    
    async def process_document(self, file_content: bytes, filename: str) -> Dict[str, List[str]]:
        """
        Process the uploaded CV document and extract text by sections
        
        Args:
            file_content (bytes): The binary content of the uploaded file
            filename (str): Original filename with extension
            
        Returns:
            Dict[str, List[str]]: Dictionary with section names as keys and lists of text paragraphs as values
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        try:
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                text = self._extract_from_pdf(temp_path)
            elif filename.lower().endswith(('.docx', '.doc')):
                text = self._extract_from_docx(temp_path)
            else:
                # For other formats, try using textract
                text = self._extract_using_textract(temp_path)
            
            # Divide text into sections
            sections = self._divide_into_sections(text)
            return sections
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file"""
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    
    def _extract_using_textract(self, file_path: str) -> str:
        """
        Fallback for unsupported file formats
        Note: This is a simplified version since textract is not installed
        """
        raise ValueError(f"Unsupported file format for {file_path}. Only PDF and DOCX files are supported.")
    
    def _divide_into_sections(self, text: str) -> Dict[str, List[str]]:
        """
        Divide the CV text into sections based on common section headers
        
        Args:
            text (str): Full CV text
            
        Returns:
            Dict[str, List[str]]: Dictionary with section names as keys and content as values
        """
        # Initialize with an "unknown" section for content before the first recognized header
        sections = {"unknown": []}
        current_section = "unknown"
        
        # Split text into lines
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            new_section = None
            for section_header in self.section_headers:
                # Compile regex patterns for section headers
                # Look for common formatting like all caps, bold (indicated by multiple spaces), etc.
                patterns = [
                    rf"^[A-Z\s]{{3,}}({section_header})[A-Z\s]*$",  # ALL CAPS
                    rf"^[^a-z]*({section_header})[^a-z]*$",  # No lowercase letters
                    rf"^\s*({section_header})\s*:.*$",  # Header with colon
                    rf"^[^\w]*({section_header})[^\w]*$"  # Surrounded by non-word chars
                ]
                
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        new_section = section_header
                        break
                if new_section:
                    break
            
            if new_section:
                current_section = new_section
                sections[current_section] = []
            else:
                sections[current_section].append(line)
        
        return sections


    def get_all_text(self, sections: Dict[str, List[str]]) -> str:
        """Combine all sections into a single text string"""
        all_text = ""
        for section, lines in sections.items():
            all_text += f"\n{section.upper()}:\n"
            all_text += "\n".join(lines) + "\n"
        return all_text