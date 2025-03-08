from typing import Dict, List, Any
from app.models.schemas import CriterionEnum, Evidence


class CriteriaMatcher:
    """Service for matching CV content to O-1A criteria"""
    
    def __init__(self):
        """Initialize matcher with criteria descriptions and patterns"""
        self.criteria_descriptions = {
            CriterionEnum.AWARDS: (
                "Receipt of nationally or internationally recognized prizes or awards for excellence "
                "in the field of endeavor."
            ),
            CriterionEnum.MEMBERSHIP: (
                "Membership in associations in the field which require outstanding achievements "
                "of their members, as judged by recognized national or international experts."
            ),
            CriterionEnum.PRESS: (
                "Published material about the person in professional or major trade publications or "
                "other major media, relating to the person's work in the field."
            ),
            CriterionEnum.JUDGING: (
                "Participation, either individually or on a panel, as a judge of the work of others "
                "in the same or an allied field of specialization."
            ),
            CriterionEnum.ORIGINAL_CONTRIBUTION: (
                "Original scientific, scholarly, artistic, or business-related contributions of "
                "major significance in the field."
            ),
            CriterionEnum.SCHOLARLY_ARTICLES: (
                "Authorship of scholarly articles in the field, in professional or major trade "
                "publications or other major media."
            ),
            CriterionEnum.CRITICAL_EMPLOYMENT: (
                "Employment in a critical or essential capacity at an organization with a "
                "distinguished reputation."
            ),
            CriterionEnum.HIGH_REMUNERATION: (
                "Command of a high salary or other significantly high remuneration for services, "
                "in relation to others in the field."
            )
        }
        
        # Map section names to criteria for better matching
        self.section_to_criteria_map = {
            "awards": [CriterionEnum.AWARDS],
            "honors": [CriterionEnum.AWARDS],
            "achievements": [CriterionEnum.AWARDS, CriterionEnum.ORIGINAL_CONTRIBUTION],
            "publications": [CriterionEnum.SCHOLARLY_ARTICLES, CriterionEnum.PRESS],
            "memberships": [CriterionEnum.MEMBERSHIP],
            "affiliations": [CriterionEnum.MEMBERSHIP],
            "professional activities": [CriterionEnum.JUDGING, CriterionEnum.MEMBERSHIP],
            "research": [CriterionEnum.ORIGINAL_CONTRIBUTION, CriterionEnum.SCHOLARLY_ARTICLES],
            "projects": [CriterionEnum.ORIGINAL_CONTRIBUTION],
            "experience": [CriterionEnum.CRITICAL_EMPLOYMENT, CriterionEnum.HIGH_REMUNERATION],
            "employment": [CriterionEnum.CRITICAL_EMPLOYMENT, CriterionEnum.HIGH_REMUNERATION],
            "work experience": [CriterionEnum.CRITICAL_EMPLOYMENT, CriterionEnum.HIGH_REMUNERATION],
        }
    
    async def match_criteria(self, nlp_results: Dict[str, Any]) -> Dict[CriterionEnum, List[Evidence]]:
        """
        Match CV content to O-1A criteria
        
        Args:
            nlp_results: Results from NLP analysis of CV sections
            
        Returns:
            Dictionary mapping criteria to lists of evidence
        """
        evidence_by_criterion = {criterion: [] for criterion in CriterionEnum}
        
        # Process each section's analysis
        for section_name, section_data in nlp_results.items():
            # Get potential criteria for this section
            potential_criteria = self.section_to_criteria_map.get(section_name.lower(), [])
            
            # Process all criterion matches identified by NLP
            for criterion, sentences in section_data["criterions"].items():
                # Convert string criterion to enum
                try:
                    criterion_enum = CriterionEnum(criterion)
                except ValueError:
                    # Skip if not a valid criterion
                    continue
                
                # Boost confidence for sentences from relevant sections
                for sentence in sentences:
                    evidence = Evidence(
                        text=sentence["text"],
                        confidence=sentence["confidence"] * (1.2 if criterion_enum in potential_criteria else 1.0),
                        source_section=sentence["source_section"]
                    )
                    
                    # Add to evidence if confidence is reasonable
                    if evidence.confidence > 0.6:
                        evidence_by_criterion[criterion_enum].append(evidence)
        
        # Filter and sort the evidence for each criterion
        for criterion in evidence_by_criterion:
            # Sort by confidence
            evidence_by_criterion[criterion] = sorted(
                evidence_by_criterion[criterion], 
                key=lambda e: e.confidence, 
                reverse=True
            )
            
            # Take top 5 pieces of evidence
            evidence_by_criterion[criterion] = evidence_by_criterion[criterion][:5]
        
        return evidence_by_criterion