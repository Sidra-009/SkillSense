from typing import List, Dict, Any
import re
from config import EMBEDDING_MODEL, SPACY_MODEL
import spacy
from sentence_transformers import SentenceTransformer, util

# A simple static skill ontology to bootstrap matching. Expand this for production.
BASE_SKILLS = [
    "python", "java", "c++", "sql", "data analysis", "machine learning",
    "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "git", "docker", "kubernetes", "aws", "azure", "react", "javascript",
    "flask", "django", "excel", "power bi", "tableau", "unity", "3d modeling",
    "sql server", "xammp"
]

class SkillExtractor:
    def __init__(self):
        # load spaCy for NER / POS
        try:
            self.nlp = spacy.load(SPACY_MODEL)
        except:
            # helpful fallback: download model when necessary
            import subprocess, sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", SPACY_MODEL])
            self.nlp = spacy.load(SPACY_MODEL)

        # sentence-transformer for semantic matching
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        # precompute embeddings of skill ontology
        self.skill_corpus = BASE_SKILLS
        self.skill_embeddings = self.embedder.encode(self.skill_corpus, convert_to_tensor=True)

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def extract_candidates(self, text: str) -> List[str]:
        doc = self.nlp(text)
        candidates = set()

        # Named Entities and noun chunks as candidates
        for ent in doc.ents:
            candidates.add(ent.text.lower())
        for chunk in doc.noun_chunks:
            # filter small chunks
            txt = chunk.text.lower().strip()
            if len(txt.split()) <= 4:
                candidates.add(txt)

        # also pull hyphenated/tech tokens via regex
        tech_tokens = re.findall(r"[A-Za-z\+\#]{2,}", text)
        for t in tech_tokens:
            candidates.add(t.lower())

        return list(candidates)

    def semantic_match(self, text: str, top_k:int=5) -> List[Dict[str,Any]]:
        # chunk text into sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if not sentences:
            sentences = [text]

        sent_emb = self.embedder.encode(sentences, convert_to_tensor=True)

        # compute similarities between sentences and skills
        results = {}
        for i, sent in enumerate(sentences):
            sims = util.cos_sim(sent_emb[i], self.skill_embeddings)[0]  # similarity vector
            top_results = list(enumerate(sims.cpu().numpy()))
            # sort descending
            top_sorted = sorted(top_results, key=lambda x: x[1], reverse=True)[:top_k]
            for idx, score in top_sorted:
                skill = self.skill_corpus[idx]
                if skill not in results or results[skill]["confidence"] < float(score):
                    results[skill] = {
                        "confidence": float(score),
                        "evidence": [sent]
                    }
                else:
                    results[skill]["evidence"].append(sent)

        # format
        profile_skills = []
        for skill, meta in results.items():
            profile_skills.append({
                "skill": skill,
                "confidence": round(meta["confidence"], 3),
                "evidence": meta["evidence"]
            })

        # sort by confidence
        profile_skills.sort(key=lambda x: x["confidence"], reverse=True)
        return profile_skills

    def extract_profile(self, text: str) -> Dict[str,Any]:
        text = self._clean_text(text)
        candidates = self.extract_candidates(text)

        # semantic match across entire text
        sem_matches = self.semantic_match(text, top_k=6)

        # build profile with evidence count and normalized confidence
        profile = {
            "summary": (text[:800] + "...") if len(text) > 800 else text,
            "skills": sem_matches
        }
        return profile
