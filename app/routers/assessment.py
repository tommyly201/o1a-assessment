from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Any

from app.services.document_processor import DocumentProcessor
from app.services.nlp_engine import NLPEngine
from app.services.criteria_matcher import CriteriaMatcher
from app.services.assessment_engine import AssessmentEngine
from app.models.schemas import O1AAssessment

router = APIRouter(
    prefix="/assessment",
    tags=["assessment"],
    responses={404: {"description": "Not found"}},
)


def get_document_processor():
    return DocumentProcessor()


def get_nlp_engine():
    return NLPEngine()


def get_criteria_matcher():
    return CriteriaMatcher()


def get_assessment_engine():
    return AssessmentEngine()


@router.post("/o1a", response_model=O1AAssessment)
async def assess_o1a_qualification(
    cv_file: UploadFile = File(...),
    document_processor: DocumentProcessor = Depends(get_document_processor),
    nlp_engine: NLPEngine = Depends(get_nlp_engine),
    criteria_matcher: CriteriaMatcher = Depends(get_criteria_matcher),
    assessment_engine: AssessmentEngine = Depends(get_assessment_engine),
) -> Any:
    """
    Assess O-1A visa qualification based on a CV
    
    - **cv_file**: CV file (PDF, DOCX, or DOC)
    
    Returns an assessment of O-1A qualification including:
    - Evidence matching each criterion
    - Overall rating (low, medium, high)
    - Summary and recommendations
    """
    # Validate file format
    allowed_formats = [".pdf", ".docx", ".doc"]
    file_ext = "." + cv_file.filename.split(".")[-1].lower()
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Please upload a file in one of these formats: {', '.join(allowed_formats)}"
        )
    
    try:
        # Read file content
        file_content = await cv_file.read()
        
        # Process document
        sections = await document_processor.process_document(file_content, cv_file.filename)
        
        # Analyze CV with NLP
        nlp_results = await nlp_engine.analyze_cv_sections(sections)
        
        # Match content to O-1A criteria
        evidence_by_criterion = await criteria_matcher.match_criteria(nlp_results)
        
        # Generate assessment
        assessment = await assessment_engine.generate_assessment(evidence_by_criterion)
        
        return assessment
    
    except Exception as e:
        # Log error in a real application
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CV: {str(e)}"
        )