from skills_extractor import SkillExtractor

def test_extract_profile_basic():
    se = SkillExtractor()
    text = "Experienced in Python, Flask, and building REST APIs. Worked with Docker and AWS for deployments."
    profile = se.extract_profile(text)
    assert "skills" in profile
    # expect at least python and docker to appear with reasonable confidence
    skills = [s["skill"] for s in profile["skills"]]
    assert any("python" in k for k in skills)
