import re
import nltk
from typing import Dict, List, Set, Tuple, Any
import spacy
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


class NLPEngine:
    """NLP service for analyzing CV content"""
    
    def __init__(self):
        """Initialize NLP models and resources"""
        # Load spaCy model for entity recognition
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        # Named entity recognition pipeline
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        
        # Define keywords for each criterion
        self.criterion_keywords = {
            "awards": {
                "award", "prize", "recognition", "honor", "medal", "trophy", "distinction", 
                "finalist", "winner", "granted", "received", "presented with", "honored", 
                "recognized", "acclaimed", "commended", "acclaimed", "achievement"
            },
            "membership": {
                "member", "association", "society", "organization", "committee", "group",
                "council", "board", "fellow", "consortium", "association", "chapter",
                "admitted to", "invited to", "selected for", "elected to", "exclusive",
                "prestigious", "selective", "by invitation"
            },
            "press": {
                "featured in", "published in", "mentioned in", "highlighted in", "profiled in",
                "covered by", "cited in", "interviewed by", "press", "media", "news", 
                "article", "magazine", "newspaper", "blog", "website", "podcast", "radio", "tv"
            },
            "judging": {
                "judge", "jury", "reviewer", "evaluator", "panelist", "selection committee",
                "assessment", "evaluation", "review", "judging", "examined", "critiqued",
                "assessed", "selected", "reviewed", "evaluated"
            },
            "original_contribution": {
                "pioneered", "invented", "developed", "discovered", "established", "founded",
                "created", "designed", "implemented", "built", "launched", "innovation",
                "breakthrough", "novel", "original", "first", "innovative", "groundbreaking",
                "revolutionary", "transformative", "leading-edge", "cutting-edge", "patent"
            },
            "scholarly_articles": {
                "author", "published", "journal", "paper", "article", "publication", "conference",
                "proceedings", "research", "scholar", "academic", "peer-reviewed", "cited", 
                "bibliography", "preprint", "manuscript", "co-author", "first author"
            },
            "critical_employment": {
                "key role", "critical role", "essential role", "leading role", "crucial position",
                "vital member", "pivotal", "led", "directed", "managed", "oversaw", "headed",
                "spearheaded", "senior", "executive", "director", "chief", "VP", "C-level",
                "distinguished", "renowned", "eminent", "prominent", "prestigious company"
            },
            "high_remuneration": {
                "salary", "compensation", "remuneration", "income", "earnings", "wage", "pay",
                "stipend", "bonus", "stock options", "equity", "benefits", "package", "high",
                "substantial", "significant", "above average", "competitive", "premium", "top"
            }
        }
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
    
    async def analyze_cv_sections(self, sections: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze CV sections to extract relevant information for O-1A criteria"""
        results = {}
        
        # Process each section
        for section_name, paragraphs in sections.items():
            section_text = "\n".join(paragraphs)
            
            # Extract entities in this section
            entities = await self.extract_entities(section_text)
            
            # Extract sentences in this section
            sentences = nltk.sent_tokenize(section_text)
            
            # Map sentences to potential criteria
            criterions_data = {}
            for criterion, keywords in self.criterion_keywords.items():
                criterion_sentences = []
                for sentence in sentences:
                    # Check if any keyword is in the sentence
                    if any(re.search(r'\b' + re.escape(keyword) + r'\b', sentence, re.IGNORECASE) for keyword in keywords):
                        criterion_sentences.append({
                            "text": sentence,
                            "confidence": self._calculate_confidence(sentence, criterion),
                            "source_section": section_name
                        })
                
                criterions_data[criterion] = criterion_sentences
            
            results[section_name] = {
                "entities": entities,
                "criterions": criterions_data
            }
        
        return results
    
    def _calculate_confidence(self, sentence: str, criterion: str) -> float:
        """Calculate confidence score for a sentence matching a criterion"""
        # Count keyword matches
        keyword_count = sum(1 for keyword in self.criterion_keywords[criterion] 
                          if re.search(r'\b' + re.escape(keyword) + r'\b', sentence, re.IGNORECASE))
        
        # Normalize to 0-1 range with a base confidence of 0.5
        base_confidence = 0.5
        keyword_factor = min(keyword_count * 0.1, 0.4)  # Max 0.4 from keywords
        
        # Add some randomness for demonstration purposes (in real life, use a better model)
        # In a production system, this would be replaced with a proper classifier
        confidence = base_confidence + keyword_factor + (np.random.random() * 0.1)
        return min(confidence, 1.0)  # Cap at 1.0

    async def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        # Simple regex pattern for dates (could be improved)
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # DD/MM/YYYY or MM/DD/YYYY
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
            r'\b\d{4}[-–]\d{4}\b',  # YYYY-YYYY (periods)
            r'\b\d{4}[-–](present|current|now)\b',  # YYYY-present
            r'\b(since|from) \d{4}\b'  # since/from YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return dates

    async def analyze_companies(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze company entities to identify prestigious organizations"""
        # This would be connected to a database of prestigious companies
        # For now, we'll use a simplified approach
        
        prestigious_keywords = [
            "renowned", "prestigious", "leading", "top", "major", "prominent",
            "distinguished", "well-known", "respected", "established", "global"
        ]
        
        companies = []
        for entity in entities:
            if entity["label"] == "ORG":
                # This would check a database in a real implementation
                # For now, just use a simple heuristic
                is_prestigious = any(keyword in entity["text"].lower() for keyword in prestigious_keywords)
                
                companies.append({
                    "name": entity["text"],
                    "is_prestigious": is_prestigious,
                    "confidence": 0.8 if is_prestigious else 0.5
                })
        
        return companies