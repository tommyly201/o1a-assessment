from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel


class CriterionEnum(str, Enum):
    AWARDS = "awards"
    MEMBERSHIP = "membership"
    PRESS = "press"
    JUDGING = "judging"
    ORIGINAL_CONTRIBUTION = "original_contribution"
    SCHOLARLY_ARTICLES = "scholarly_articles"
    CRITICAL_EMPLOYMENT = "critical_employment"
    HIGH_REMUNERATION = "high_remuneration"


class QualificationLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Evidence(BaseModel):
    """Model for a piece of evidence from the CV"""
    text: str
    confidence: float
    source_section: Optional[str] = None


class CriterionAssessment(BaseModel):
    """Assessment for a single criterion"""
    criterion: CriterionEnum
    evidence: List[Evidence]
    description: str
    strength: QualificationLevel


class O1AAssessment(BaseModel):
    """Complete O-1A assessment result"""
    criteria_assessments: Dict[CriterionEnum, CriterionAssessment]
    overall_rating: QualificationLevel
    summary: str
    recommendation: str