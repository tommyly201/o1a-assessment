import pytest
import os
import tempfile
from app.services.document_processor import DocumentProcessor


@pytest.fixture
def document_processor():
    return DocumentProcessor()


def test_extract_from_pdf(document_processor):
    # Create a test PDF file (this is a mock test)
    pdf_content = b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>/Contents 4 0 R>>\nendobj\n4 0 obj\n<</Length 21>>stream\nBT\n/F1 12 Tf\n(Test) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000056 00000 n \n0000000111 00000 n \n0000000212 00000 n \ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n296\n%%EOF"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_content)
        temp_path = temp_file.name
    
    # Test extraction
    try:
        text = document_processor._extract_from_pdf(temp_path)
        # Simple assertion - in a real test, we'd check more thoroughly
        assert isinstance(text, str)
    finally:
        os.unlink(temp_path)


def test_divide_into_sections(document_processor):
    # Test text with common section headers
    test_text = """
    EDUCATION
    University of Example, PhD in Computer Science, 2015-2020
    
    EXPERIENCE
    Senior Software Engineer, Tech Company, 2020-Present
    - Led development of critical features
    
    AWARDS
    Best Paper Award, International Conference, 2019
    """
    
    sections = document_processor._divide_into_sections(test_text)
    
    assert "education" in sections
    assert "experience" in sections
    assert "awards" in sections
    
    # Check content
    assert any("University of Example" in line for line in sections["education"])
    assert any("Senior Software Engineer" in line for line in sections["experience"])
    assert any("Best Paper Award" in line for line in sections["awards"])


# More tests would be added for other methods and edge cases