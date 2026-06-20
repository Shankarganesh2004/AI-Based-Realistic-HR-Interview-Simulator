"""
Data Collection Router
──────────────────────
Endpoints for candidate profile extraction from GitHub, LinkedIn, and Resumes.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.core.security import get_current_user
from app.core.database import get_database
from app.services.data_collection_service import data_collection_service

router = APIRouter(prefix="/api/data-collection", tags=["Data Collection"])


@router.post("/analyze-github")
async def analyze_github(
    github_url: str,
    user: dict = Depends(get_current_user),
):
    """
    Extract coding profile data from a GitHub profile or repo URL.
    Accepts formats:
      - https://github.com/username
      - https://github.com/username/repo
      - github.com/username
      - username
    """
    username = _extract_github_username(github_url)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL or username")

    result = await data_collection_service.analyze_github_profile(username)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # Persist into user profile for future interviews
    db = get_database()
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "github_profile": result,
            "github_username": username,
        }},
    )

    return {
        "username": result.get("username"),
        "name": result.get("name"),
        "bio": result.get("bio"),
        "public_repos": result.get("public_repos", 0),
        "total_stars": result.get("total_stars", 0),
        "primary_languages": result.get("primary_languages", []),
        "contribution_score": result.get("contribution_score", 0),
        "repositories": result.get("repositories", [])[:10],
        "profile_url": result.get("profile_url"),
    }


@router.post("/analyze-linkedin")
async def analyze_linkedin(
    linkedin_url: str,
    user: dict = Depends(get_current_user),
):
    """
    Store LinkedIn profile URL and extract username.
    Note: LinkedIn API requires OAuth, so we store the URL
    and extract basic info from the URL pattern.
    """
    linkedin_username = _extract_linkedin_username(linkedin_url)
    if not linkedin_username:
        raise HTTPException(
            status_code=400,
            detail="Invalid LinkedIn URL. Use format: linkedin.com/in/username",
        )

    # Store in user profile
    db = get_database()
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "linkedin_url": linkedin_url.strip(),
            "linkedin_username": linkedin_username,
        }},
    )

    return {
        "linkedin_username": linkedin_username,
        "linkedin_url": linkedin_url.strip(),
        "message": "LinkedIn profile linked successfully",
    }


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Parse a PDF or DOCX resume and extract structured profile data."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    if ext == "pdf":
        result = data_collection_service.parse_resume_pdf(file_bytes)
    else:
        result = data_collection_service.parse_resume_docx(file_bytes)

    if "error" in result and not result.get("raw_text"):
        raise HTTPException(status_code=422, detail=result["error"])

    # Persist parsed resume into user profile
    db = get_database()
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"parsed_resume": result}},
    )

    return {
        "skills": result.get("skills", []),
        "years_of_experience": result.get("years_of_experience", 0),
        "degrees": result.get("degrees", []),
        "certifications": result.get("certifications", []),
        "sections_detected": result.get("sections_detected", []),
        "word_count": result.get("word_count", 0),
    }


@router.get("/profile")
async def get_candidate_profile(user: dict = Depends(get_current_user)):
    """Return the stored profile data (GitHub + LinkedIn + Resume)."""
    db = get_database()
    user_doc = await db.users.find_one({"_id": user["_id"]})

    return {
        "github": user_doc.get("github_profile"),
        "github_username": user_doc.get("github_username"),
        "linkedin_url": user_doc.get("linkedin_url"),
        "linkedin_username": user_doc.get("linkedin_username"),
        "resume": user_doc.get("parsed_resume"),
    }


@router.post("/build-full-profile")
async def build_full_profile(
    github_url: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    """
    Build a comprehensive candidate profile combining all sources.
    Uses previously uploaded resume + GitHub + LinkedIn.
    Returns knowledge graph, embeddings, and feature vector.
    """
    db = get_database()
    user_doc = await db.users.find_one({"_id": user["_id"]})

    github_username = None
    if github_url:
        github_username = _extract_github_username(github_url)
    elif user_doc.get("github_username"):
        github_username = user_doc["github_username"]

    # Build profile using data collection service
    profile = await data_collection_service.build_candidate_profile(
        name=user_doc.get("name", "Candidate"),
        email=user_doc.get("email", ""),
        github_username=github_username,
    )

    # Merge with stored resume data if available
    if user_doc.get("parsed_resume"):
        profile["resume"] = user_doc["parsed_resume"]
        # Rebuild knowledge graph and features with resume data
        profile["knowledge_graph"] = data_collection_service.build_knowledge_graph(profile)
        profile["features"] = data_collection_service.engineer_features(profile)

    # Store the full profile
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"candidate_profile": profile}},
    )

    kg = profile.get("knowledge_graph", {})
    return {
        "profile_summary": profile.get("profile_summary", ""),
        "skills": profile.get("resume", {}).get("skills", []),
        "github": {
            "username": profile.get("github", {}).get("username"),
            "public_repos": profile.get("github", {}).get("public_repos", 0),
            "primary_languages": profile.get("github", {}).get("primary_languages", []),
            "contribution_score": profile.get("github", {}).get("contribution_score", 0),
            "repos_analyzed": len(profile.get("github", {}).get("repositories", [])),
        },
        "knowledge_graph": {
            "node_count": kg.get("node_count", 0),
            "edge_count": kg.get("edge_count", 0),
            "central_skills": kg.get("central_skills", []),
            "skill_clusters": kg.get("skill_clusters", {}),
        },
        "features": profile.get("features", {}),
    }


# ── Helpers ───────────────────────────────────────────

def _extract_github_username(url_or_username: str) -> Optional[str]:
    """Extract GitHub username from a URL or raw username."""
    url_or_username = url_or_username.strip().rstrip("/")

    # Direct username (no slashes, no dots)
    if "/" not in url_or_username and "." not in url_or_username:
        return url_or_username if url_or_username else None

    # URL patterns: github.com/username or github.com/username/repo
    import re
    match = re.search(r"github\.com/([A-Za-z0-9\-_]+)", url_or_username)
    if match:
        return match.group(1)

    return None


def _extract_linkedin_username(url: str) -> Optional[str]:
    """Extract LinkedIn username from a profile URL."""
    url = url.strip().rstrip("/")

    import re
    match = re.search(r"linkedin\.com/in/([A-Za-z0-9\-_]+)", url)
    if match:
        return match.group(1)

    return None
