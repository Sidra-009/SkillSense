# database/operations.py
from datetime import datetime
import json
from .models import Database

class SkillProfileOperations:
    def __init__(self):
        self.db = Database()

    def create_user(self, email, name=None):
        query = "INSERT INTO users (email, name) VALUES (?, ?)"
        user_id = self.db.execute_query(query, (email, name))
        return user_id

    def get_user(self, email):
        query = "SELECT * FROM users WHERE email = ?"
        result = self.db.execute_query(query, (email,))
        return result[0] if result else None

    def save_skill_profile(self, user_id, profile_data):
        query = """
        INSERT INTO skill_profiles 
        (user_id, profile_name, source_type, raw_text, processed_data, total_skills, overall_confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        profile_id = self.db.execute_query(query, (
            user_id,
            profile_data['profile_name'],
            profile_data['source_type'],
            profile_data.get('raw_text', ''),
            json.dumps(profile_data.get('processed_data', {})),
            profile_data['total_skills'],
            profile_data['overall_confidence']
        ))
        
        # Save individual skills
        if profile_id and 'skills' in profile_data:
            self._save_skills(profile_id, profile_data['skills'])
        
        return profile_id

    def _save_skills(self, profile_id, skills):
        for skill in skills:
            query = """
            INSERT INTO skills 
            (profile_id, skill_name, category, confidence_score, source, evidence, mentions, is_explicit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute_query(query, (
                profile_id,
                skill['skill_name'],
                skill['category'],
                skill['confidence_score'],
                skill['source'],
                json.dumps(skill.get('evidence', [])),
                skill.get('mentions', 1),
                1 if skill.get('is_explicit', True) else 0
            ))

    def get_user_profiles(self, user_id):
        query = """
        SELECT * FROM skill_profiles 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        """
        return self.db.execute_query(query, (user_id,))

    def get_profile_skills(self, profile_id):
        query = """
        SELECT * FROM skills 
        WHERE profile_id = ? 
        ORDER BY confidence_score DESC
        """
        return self.db.execute_query(query, (profile_id,))

    def save_job_match(self, user_id, job_data):
        query = """
        INSERT INTO job_matches 
        (user_id, job_title, job_description, match_percentage, matching_skills, missing_skills)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (
            user_id,
            job_data['job_title'],
            job_data['job_description'],
            job_data['match_percentage'],
            json.dumps(job_data['matching_skills']),
            json.dumps(job_data['missing_skills'])
        ))

    def save_skill_gap(self, user_id, gap_data):
        query = """
        INSERT INTO skill_gaps 
        (user_id, target_role, current_coverage, missing_skills, recommendations)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (
            user_id,
            gap_data['target_role'],
            gap_data['current_coverage'],
            json.dumps(gap_data['missing_skills']),
            json.dumps(gap_data['recommendations'])
        ))