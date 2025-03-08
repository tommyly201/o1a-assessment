from typing import Dict, List, Any
from app.models.schemas import (
    CriterionEnum, 
    QualificationLevel,
    Evidence, 
    CriterionAssessment,
    O1AAssessment
)


class AssessmentEngine:
    """Service for generating O-1A visa qualification assessment"""
    
    def __init__(self):
        """Initialize the assessment engine"""
        # O-1A requires meeting at least 3 of the 8 criteria
        self.minimum_criteria_met = 3
        
        # Define thresholds for evidence quality
        self.threshold_high = 0.85
        self.threshold_medium = 0.7
        self.threshold_low = 0.6
    
    async def generate_assessment(
        self, 
        evidence_by_criterion: Dict[CriterionEnum, List[Evidence]]
    ) -> O1AAssessment:
        """
        Generate a complete O-1A assessment based on evidence matched to criteria
        
        Args:
            evidence_by_criterion: Dictionary mapping criteria to lists of evidence
            
        Returns:
            Complete O-1A assessment with overall rating and recommendations
        """
        # Assess each criterion
        criteria_assessments = {}
        for criterion, evidence_list in evidence_by_criterion.items():
            if evidence_list:
                # Generate assessment for this criterion
                assessment = self._assess_criterion(criterion, evidence_list)
                criteria_assessments[criterion] = assessment
        
        # Count how many criteria are met (medium or high strength)
        criteria_met = sum(
            1 for assessment in criteria_assessments.values() 
            if assessment.strength in [QualificationLevel.MEDIUM, QualificationLevel.HIGH]
        )
        
        # Count how many criteria are strongly met (high strength)
        criteria_strongly_met = sum(
            1 for assessment in criteria_assessments.values() 
            if assessment.strength == QualificationLevel.HIGH
        )
        
        # Generate overall rating
        if criteria_strongly_met >= 3 or (criteria_strongly_met >= 1 and criteria_met >= 4):
            overall_rating = QualificationLevel.HIGH
        elif criteria_met >= self.minimum_criteria_met:
            overall_rating = QualificationLevel.MEDIUM
        else:
            overall_rating = QualificationLevel.LOW
        
        # Generate summary and recommendations
        summary = self._generate_summary(criteria_assessments, criteria_met, criteria_strongly_met)
        recommendation = self._generate_recommendation(overall_rating, criteria_met)
        
        return O1AAssessment(
            criteria_assessments=criteria_assessments,
            overall_rating=overall_rating,
            summary=summary,
            recommendation=recommendation
        )
    
    def _assess_criterion(
        self, 
        criterion: CriterionEnum, 
        evidence_list: List[Evidence]
    ) -> CriterionAssessment:
        """
        Assess a single criterion based on the provided evidence
        
        Args:
            criterion: The criterion being assessed
            evidence_list: List of evidence for this criterion
            
        Returns:
            Assessment for this criterion
        """
        # Calculate average confidence across all evidence
        if evidence_list:
            avg_confidence = sum(evidence.confidence for evidence in evidence_list) / len(evidence_list)
            
            # Determine strength based on evidence quality and quantity
            if avg_confidence >= self.threshold_high and len(evidence_list) >= 3:
                strength = QualificationLevel.HIGH
            elif avg_confidence >= self.threshold_medium or (avg_confidence >= self.threshold_low and len(evidence_list) >= 2):
                strength = QualificationLevel.MEDIUM
            else:
                strength = QualificationLevel.LOW
        else:
            strength = QualificationLevel.LOW
        
        # Generate description based on strength
        description = self._generate_criterion_description(criterion, strength, len(evidence_list))
        
        return CriterionAssessment(
            criterion=criterion,
            evidence=evidence_list,
            description=description,
            strength=strength
        )
    
    def _generate_criterion_description(
        self, 
        criterion: CriterionEnum, 
        strength: QualificationLevel,
        evidence_count: int
    ) -> str:
        """Generate a description for a criterion assessment"""
        criterion_name = criterion.value.replace("_", " ").title()
        
        if strength == QualificationLevel.HIGH:
            return f"Strong evidence of {criterion_name}. Found {evidence_count} compelling examples."
        elif strength == QualificationLevel.MEDIUM:
            return f"Moderate evidence of {criterion_name}. Found {evidence_count} relevant examples."
        else:
            if evidence_count > 0:
                return f"Limited evidence of {criterion_name}. Found {evidence_count} potential examples."
            else:
                return f"No significant evidence of {criterion_name} found in the provided CV."
    
    def _generate_summary(
        self, 
        criteria_assessments: Dict[CriterionEnum, CriterionAssessment],
        criteria_met: int,
        criteria_strongly_met: int
    ) -> str:
        """Generate a summary of the assessment"""
        if criteria_met >= self.minimum_criteria_met:
            summary = (
                f"Based on the analysis of the provided CV, the applicant meets {criteria_met} of the 8 "
                f"O-1A criteria, with {criteria_strongly_met} met at a high level of evidence. "
            )
            
            # Add details about strongest criteria
            strong_criteria = [
                assessment.criterion.value.replace("_", " ").title()
                for assessment in criteria_assessments.values()
                if assessment.strength == QualificationLevel.HIGH
            ]
            
            if strong_criteria:
                summary += f"The strongest evidence is in the areas of {', '.join(strong_criteria)}. "
            
            # Add details about areas needing improvement
            weak_criteria = [
                assessment.criterion.value.replace("_", " ").title()
                for assessment in criteria_assessments.values()
                if assessment.strength == QualificationLevel.LOW
            ]
            
            if weak_criteria:
                summary += f"Areas with limited or no evidence include {', '.join(weak_criteria)}."
        else:
            summary = (
                f"Based on the analysis of the provided CV, the applicant meets only {criteria_met} of the "
                f"required minimum of 3 O-1A criteria. Additional evidence would be needed to strengthen "
                f"the application."
            )
        
        return summary
    
    def _generate_recommendation(self, overall_rating: QualificationLevel, criteria_met: int) -> str:
        """Generate recommendations based on the assessment"""
        if overall_rating == QualificationLevel.HIGH:
            return (
                "The applicant shows strong qualifications for an O-1A visa. With compelling evidence "
                "across multiple criteria, this application has a high chance of success. It is recommended "
                "to proceed with the application, focusing on highlighting the strongest evidence areas."
            )
        elif overall_rating == QualificationLevel.MEDIUM:
            return (
                "The applicant meets the minimum requirements for an O-1A visa. While the evidence is "
                "sufficient, strengthening the application with additional documentation in key areas "
                "would improve the chances of approval. Consider gathering more evidence particularly "
                "for criteria currently assessed at medium strength."
            )
        else:
            if criteria_met > 0:
                return (
                    f"The applicant currently meets only {criteria_met} of the required minimum of 3 O-1A "
                    f"criteria. It is recommended to gather substantial additional evidence before proceeding "
                    f"with an application. Consider focusing on achievements, recognition, and contributions "
                    f"that align with the O-1A criteria."
                )
            else:
                return (
                    "Based on the provided CV, there is insufficient evidence to support an O-1A visa "
                    "application at this time. The applicant should focus on building a stronger profile "
                    "with nationally or internationally recognized achievements before considering an "
                    "O-1A application."
                )