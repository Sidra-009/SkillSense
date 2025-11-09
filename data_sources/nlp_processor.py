# services/nlp_processor.py
import spacy
from typing import List, Dict, Any
import re

class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.nlp_loaded = True
        except OSError:
            self.nlp = None
            self.nlp_loaded = False

    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text"""
        if not self.nlp_loaded or not text:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities

    def extract_noun_phrases(self, text: str) -> List[str]:
        """Extract noun phrases from text"""
        if not self.nlp_loaded or not text:
            return []
        
        doc = self.nlp(text)
        noun_phrases = []
        
        for chunk in doc.noun_chunks:
            noun_phrases.append(chunk.text)
        
        return noun_phrases

    def analyze_sentences(self, text: str) -> List[Dict]:
        """Analyze sentences for skill-related content"""
        if not self.nlp_loaded or not text:
            return []
        
        doc = self.nlp(text)
        sentences = []
        
        for sent in doc.sents:
            sentence_analysis = {
                'text': sent.text,
                'tokens': len(sent),
                'contains_tech_terms': self._contains_tech_terms(sent.text),
                'contains_experience_indicators': self._contains_experience_indicators(sent.text)
            }
            sentences.append(sentence_analysis)
        
        return sentences

    def _contains_tech_terms(self, text: str) -> bool:
        """Check if text contains technical terms"""
        tech_indicators = [
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\breact\b', r'\bangular\b',
            r'\baws\b', r'\bazure\b', r'\bdocker\b', r'\bkubernetes\b', r'\bmachine learning\b',
            r'\bsql\b', r'\bmongodb\b', r'\bgit\b', r'\bapi\b', r'\bmicroservices\b'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in tech_indicators)

    def _contains_experience_indicators(self, text: str) -> bool:
        """Check if text contains experience indicators"""
        experience_indicators = [
            r'\bexperienced\b', r'\bproficient\b', r'\bskilled\b', r'\bexpert\b',
            r'\byears?\b', r'\bdeveloped\b', r'\bbuilt\b', r'\bcreated\b',
            r'\bimplemented\b', r'\bmanaged\b', r'\bled\b'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in experience_indicators)

# Singleton instance
nlp_processor = NLPProcessor()