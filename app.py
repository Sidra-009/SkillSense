from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)

# Ensure directories exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

class SkillAnalyzer:
    def __init__(self):
        self.skill_framework = {
            "Programming Languages": ["python", "javascript", "java", "c++", "c#", "go", "rust", "swift", "kotlin", "typescript"],
            "Web Development": ["html", "css", "react", "vue", "angular", "node.js", "django", "flask", "express", "spring"],
            "Data Science": ["machine learning", "deep learning", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "data analysis"],
            "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ci/cd"],
            "Databases": ["sql", "mysql", "postgresql", "mongodb", "redis", "oracle"],
            "Tools": ["git", "github", "gitlab", "jira", "confluence", "vs code", "pycharm"],
            "Soft Skills": ["problem solving", "communication", "leadership", "teamwork", "project management"]
        }
    
    def analyze_resume_text(self, text):
        """Analyze skills from resume text"""
        skills_found = []
        text_lower = text.lower()
        
        for category, skills in self.skill_framework.items():
            for skill in skills:
                if skill in text_lower:
                    # Calculate confidence based on frequency and context
                    frequency = text_lower.count(skill)
                    confidence = min(0.3 + (frequency * 0.1), 0.9)
                    
                    # Find evidence sentences
                    evidence = self._find_evidence(text, skill)
                    
                    skills_found.append({
                        "skill": skill,
                        "confidence": round(confidence, 2),
                        "category": category,
                        "evidence": evidence,
                        "source": "resume"
                    })
        
        return skills_found
    
    def analyze_linkedin_data(self, linkedin_url):
        """Mock LinkedIn analysis"""
        try:
            # Extract username from LinkedIn URL
            username = self._extract_linkedin_username(linkedin_url)
            
            # Mock LinkedIn data based on common patterns
            linkedin_skills = [
                {
                    "skill": "python",
                    "confidence": 0.85,
                    "category": "Programming Languages",
                    "evidence": [f"LinkedIn: 15+ endorsements for Python from connections"],
                    "source": "linkedin"
                },
                {
                    "skill": "machine learning",
                    "confidence": 0.78,
                    "category": "Data Science", 
                    "evidence": ["LinkedIn: Machine Learning skill badge and recommendations"],
                    "source": "linkedin"
                },
                {
                    "skill": "communication",
                    "confidence": 0.72,
                    "category": "Soft Skills",
                    "evidence": ["LinkedIn: Strong communication skills highlighted in recommendations"],
                    "source": "linkedin"
                },
                {
                    "skill": "project management",
                    "confidence": 0.65,
                    "category": "Soft Skills",
                    "evidence": ["LinkedIn: Project management experience verified by connections"],
                    "source": "linkedin"
                }
            ]
            return linkedin_skills
        except:
            return []
    
    def analyze_github_data(self, github_url):
        """Analyze GitHub profile"""
        try:
            # Extract username from GitHub URL
            username = self._extract_github_username(github_url)
            
            # Mock GitHub analysis based on common developer profiles
            github_skills = [
                {
                    "skill": "python",
                    "confidence": 0.88,
                    "category": "Programming Languages",
                    "evidence": [f"GitHub: Multiple repositories with Python code ({username})"],
                    "source": "github"
                },
                {
                    "skill": "javascript",
                    "confidence": 0.75,
                    "category": "Programming Languages",
                    "evidence": [f"GitHub: Web development projects using JavaScript ({username})"],
                    "source": "github"
                },
                {
                    "skill": "react",
                    "confidence": 0.70,
                    "category": "Web Development",
                    "evidence": [f"GitHub: Frontend projects with React ({username})"],
                    "source": "github"
                },
                {
                    "skill": "git",
                    "confidence": 0.95,
                    "category": "Tools",
                    "evidence": [f"GitHub: Active repository management ({username})"],
                    "source": "github"
                },
                {
                    "skill": "data analysis",
                    "confidence": 0.68,
                    "category": "Data Science",
                    "evidence": [f"GitHub: Data analysis projects and notebooks ({username})"],
                    "source": "github"
                }
            ]
            return github_skills
        except:
            return []
    
    def _extract_linkedin_username(self, url):
        """Extract username from LinkedIn URL"""
        patterns = [
            r'linkedin\.com/in/([^/?]+)',
            r'linkedin\.com/in/([^/?]+)/?'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return "profile"
    
    def _extract_github_username(self, url):
        """Extract username from GitHub URL"""
        patterns = [
            r'github\.com/([^/]+)',
            r'https://github\.com/([^/?]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return "user"
    
    def _find_evidence(self, text, skill):
        """Find sentences containing the skill as evidence"""
        sentences = re.split(r'[.!?]+', text)
        evidence = []
        for sentence in sentences:
            if skill.lower() in sentence.lower():
                clean_sentence = sentence.strip()
                if clean_sentence:
                    evidence.append(clean_sentence)
                    if len(evidence) >= 2:  # Limit to 2 evidence sentences
                        break
        return evidence if evidence else [f"Found reference to {skill} in the text"]
    
    def merge_skills(self, skills_lists):
        """Merge skills from multiple sources"""
        merged_skills = {}
        
        for skills in skills_lists:
            for skill_data in skills:
                skill_name = skill_data['skill']
                if skill_name in merged_skills:
                    # Update confidence and combine evidence
                    existing = merged_skills[skill_name]
                    existing['confidence'] = max(existing['confidence'], skill_data['confidence'])
                    existing['evidence'].extend(skill_data['evidence'])
                    existing['sources'].append(skill_data['source'])
                    # Remove duplicate evidence
                    existing['evidence'] = list(set(existing['evidence']))
                else:
                    merged_skills[skill_name] = {
                        **skill_data,
                        'sources': [skill_data['source']]
                    }
        
        # Convert to list and sort by confidence
        result = sorted(merged_skills.values(), key=lambda x: x['confidence'], reverse=True)
        
        # Round confidence scores
        for skill in result:
            skill['confidence'] = round(skill['confidence'], 2)
            
        return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get the submitted data
        text_input = request.form.get('text_input', '')
        file = request.files.get('resume_file')
        linkedin_url = request.form.get('linkedin_url', '')
        github_url = request.form.get('github_url', '')
        
        print(f"Received data - Text: {len(text_input)} chars, LinkedIn: {linkedin_url}, GitHub: {github_url}")
        
        analyzer = SkillAnalyzer()
        all_skills = []
        sources_used = {
            "resume": False,
            "linkedin": False,
            "github": False
        }
        
        # Analyze resume text
        if text_input.strip():
            resume_skills = analyzer.analyze_resume_text(text_input)
            all_skills.append(resume_skills)
            sources_used["resume"] = True
            print(f"Resume analysis found {len(resume_skills)} skills")
        
        # Analyze LinkedIn
        if linkedin_url.strip():
            linkedin_skills = analyzer.analyze_linkedin_data(linkedin_url)
            all_skills.append(linkedin_skills)
            sources_used["linkedin"] = True
            print(f"LinkedIn analysis found {len(linkedin_skills)} skills")
        
        # Analyze GitHub
        if github_url.strip():
            github_skills = analyzer.analyze_github_data(github_url)
            all_skills.append(github_skills)
            sources_used["github"] = True
            print(f"GitHub analysis found {len(github_skills)} skills")
        
        # Merge all skills
        if all_skills:
            merged_skills = analyzer.merge_skills(all_skills)
        else:
            merged_skills = []
        
        profile_data = {
            "name": "Sidra",  # You can extract this from LinkedIn or other sources
            "title": "Software Developer",
            "skills": merged_skills,
            "sources_used": sources_used,
            "linkedin_url": linkedin_url,
            "github_url": github_url
        }
        
        print(f"Total merged skills: {len(merged_skills)}")
        
        return render_template('results.html', profile=profile_data)
    
    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results_demo():
    """Direct route to see results page for testing"""
    profile = {
        "name": "Sidra",
        "title": "Software Developer", 
        "skills": [
            {
                "skill": "python",
                "confidence": 0.95,
                "category": "Programming Languages",
                "evidence": [
                    "Resume: Developed multiple Python applications for data analysis",
                    "GitHub: Multiple repositories with Python code"
                ],
                "sources": ["resume", "github"]
            },
            {
                "skill": "machine learning", 
                "confidence": 0.88,
                "category": "Data Science",
                "evidence": [
                    "Resume: Developed machine learning models for predictive analytics",
                    "LinkedIn: Machine Learning skill badge and recommendations"
                ],
                "sources": ["resume", "linkedin"]
            },
            {
                "skill": "react",
                "confidence": 0.75,
                "category": "Web Development",
                "evidence": ["GitHub: Frontend projects with React"],
                "sources": ["github"]
            }
        ],
        "sources_used": {
            "resume": True,
            "linkedin": True,
            "github": True
        },
        "linkedin_url": "https://linkedin.com/in/sidrasac",
        "github_url": "https://github.com/Sidra-009"
    }
    return render_template('results.html', profile=profile)

if __name__ == '__main__':
    print("🚀 Starting SkillSense Flask application...")
    print("📧 Open your browser and go to: http://127.0.0.1:5000")
    print("🔧 Debug mode: ON")
    app.run(debug=True, host='127.0.0.1', port=5000)