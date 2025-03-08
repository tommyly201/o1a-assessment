# O-1A Visa Qualification Assessment API

This application provides an AI-powered assessment of a person's qualifications for an O-1A immigration visa based on their CV.

## Overview

The O-1A visa is for individuals with extraordinary ability in sciences, education, business, or athletics. This API analyzes a CV against the 8 criteria defined in O-1A requirements:

1. Awards
2. Membership
3. Press
4. Judging
5. Original contribution
6. Scholarly articles
7. Critical employment
8. High remuneration

## Features

- CV analysis using NLP to extract relevant information
- Matching CV content to each of the 8 O-1A criteria
- Assessment of qualification chance (low, medium, high)
- Detailed evidence and recommendations

## API Endpoints

### POST /assessment/o1a

Upload a CV file to assess O-1A visa qualification.

**Request:**
- Content-Type: multipart/form-data
- Body: CV file (PDF, DOCX, or DOC)

**Response:**
```json
{
  "criteria_assessments": {
    "awards": {
      "criterion": "awards",
      "evidence": [
        {
          "text": "Received Excellence Award for outstanding achievement in...",
          "confidence": 0.85,
          "source_section": "Achievements"
        }
      ],
      "description": "Strong evidence of Awards. Found 1 compelling example.",
      "strength": "high"
    },
    // Other criteria...
  },
  "overall_rating": "medium",
  "summary": "Based on the analysis of the provided CV, the applicant meets 4 of the 8 O-1A criteria...",
  "recommendation": "The applicant meets the minimum requirements for an O-1A visa..."
}
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- Conda (recommended) or Python virtual environment

### Option 1: Using Conda (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/o1a-assessment.git
cd o1a-assessment
```

2. Create and activate a conda environment:
```bash
conda create -n o1a python=3.10
conda activate o1a
```

3. Install required packages:
```bash
pip install fastapi uvicorn python-multipart python-dotenv PyPDF2 python-docx nltk spacy scikit-learn transformers sentence-transformers
```

4. Install the spaCy English model and download NLTK resources:
```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

5. Run the application:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option 2: Using Python Virtual Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/o1a-assessment.git
cd o1a-assessment
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install fastapi uvicorn python-multipart python-dotenv PyPDF2 python-docx nltk spacy scikit-learn transformers sentence-transformers
```

4. Install the spaCy English model and download NLTK resources:
```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

5. Run the application:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Setup (Optional)

1. Build and run using Docker:
```bash
docker-compose up --build
```

## Accessing the API

The API will be available at http://localhost:8000.
- API documentation: http://localhost:8000/docs
- Upload your CV file through the Swagger UI at the `/assessment/o1a` endpoint

## Troubleshooting

If you encounter issues:

1. **NLTK Resources**: If you see NLTK errors, try downloading all resources:
```bash
python -c "import nltk; nltk.download('all')"
```

2. **Path Issues**: Make sure to run the application from the project root directory
 
3. **Python Environment**: If using `uvicorn` directly gives errors, use the module approach:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

Run the tests with pytest:
```bash
pytest
```

## Project Structure

```
o1a-assessment/
│
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── routers/
│   │   └── assessment.py       # API endpoints
│   │
│   ├── services/
│   │   ├── document_processor.py  # PDF/DOCX parsing and text extraction
│   │   ├── nlp_engine.py          # NLP processing
│   │   ├── criteria_matcher.py    # Matching CV content to criteria
│   │   └── assessment_engine.py   # Final assessment generation
│   │
│   └── models/
│       └── schemas.py          # Pydantic models for requests/responses
│
└── tests/                      # Test files
```

## Design Decisions

Please refer to [DESIGN.md](DESIGN.md) for detailed information on the design choices and evaluation methodology.

## License

[MIT License](LICENSE)