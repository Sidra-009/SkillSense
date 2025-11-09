import re
import json
import os
import math

class SkillExtractor:
    def __init__(self):
        self.SKILL_SYNONYMS = self._load_skill_synonyms()

    def _load_skill_synonyms(self):
        """Load skill synonyms from file or use defaults."""
        synonyms_path = "data_sources/skill_synonyms.json"
        if os.path.exists(synonyms_path):
            with open(synonyms_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "python": ["python programming", "python dev", "python coder"],
                "java": ["java programming", "java developer"],
                "excel": ["microsoft excel", "excel sheet"],
                "sql": ["structured query language", "database query", "mysql"],
                "power bi": ["bi dashboard", "business intelligence"],
                "html": ["html5", "web markup"],
                "css": ["cascading style sheets"],
                "javascript": ["js", "node.js", "frontend js", "react"],
                "flask": ["flask web", "python flask"],
                "django": ["django framework"],
            }

    def extract_skills(self, text):
        """Return detailed list of detected skills with confidence and evidence."""
        text_lower = text.lower()
        lines = text.splitlines()
        results = []

        for skill, synonyms in self.SKILL_SYNONYMS.items():
            pattern = r"\b(" + "|".join(map(re.escape, synonyms + [skill])) + r")\b"
            matches = list(re.finditer(pattern, text_lower))
            if matches:
                # Confidence based on how many times it appears
                confidence = min(1.0, 0.5 + math.log(len(matches) + 1, 10))

                # Find the line(s) containing the skill
                evidence_lines = []
                for line in lines:
                    if any(word in line.lower() for word in synonyms + [skill]):
                        evidence_lines.append(line.strip())

                result = {
                    "skill": skill,
                    "confidence": round(confidence, 2),
                    "evidence": evidence_lines[:3]  # limit to 3 evidence lines
                }
                results.append(result)

        return results

    def extract_profile(self, text):
        """Extract a full profile including name, email, phone, and detailed skill info."""
        profile = {}

        # Extract basic info
        profile["email"] = self._extract_email(text)
        profile["phone"] = self._extract_phone(text)
        profile["name"] = self._extract_name(text)
        profile["skills"] = self.extract_skills(text)

        return profile

    def _extract_email(self, text):
        match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        return match.group(0) if match else None

    def _extract_phone(self, text):
        match = re.search(r'\+?\d[\d\s\-\(\)]{8,}\d', text)
        return match.group(0) if match else None

    def _extract_name(self, text):
        lines = text.strip().splitlines()
        for line in lines:
            if not re.search(r'\d|@', line):
                return line.strip()
        return None
