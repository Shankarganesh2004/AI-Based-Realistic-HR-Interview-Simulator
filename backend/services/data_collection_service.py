"""
Data Collection & Preprocessing Service
────────────────────────────────────────
Component 1: Multi-source candidate profiling pipeline
  • Resume parsing (PDF/DOCX)
  • GitHub repository analysis
  • Knowledge graph construction
  • Embedding generation using transformers
  • Vector database integration (ChromaDB)

Architecture:
  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
  │ Resume (PDF/ │──▶│ Feature      │──▶│ Knowledge Graph  │
  │ DOCX)        │   │ Engineering  │   │ (NetworkX)       │
  └─────────────┘   └──────────────┘   └─────────────────┘
  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
  │ GitHub Repos │──▶│ Code Analysis│──▶│ Embedding Store  │
  └─────────────┘   └──────────────┘   │ (ChromaDB)       │
  ┌─────────────┐   ┌──────────────┐   └─────────────────┘
  │ Portfolio    │──▶│ NLP Pipeline │──▶   Candidate Profile
  └─────────────┘   └──────────────┘
"""

import re
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import httpx
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

try:
    import networkx as nx
    NX_AVAILABLE = True
except ImportError:
    NX_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# ── Data Schema ─────────────────────────────────────────
CANDIDATE_PROFILE_SCHEMA = {
    "candidate_id": "string",
    "name": "string",
    "email": "string",
    "resume": {
        "raw_text": "string",
        "skills": ["string"],
        "experience": [
            {
                "company": "string",
                "role": "string",
                "duration_months": "int",
                "description": "string",
                "technologies": ["string"],
            }
        ],
        "education": [
            {
                "institution": "string",
                "degree": "string",
                "field": "string",
                "gpa": "float",
            }
        ],
        "certifications": ["string"],
        "projects": [
            {
                "name": "string",
                "description": "string",
                "technologies": ["string"],
                "url": "string",
            }
        ],
    },
    "github": {
        "username": "string",
        "repositories": [
            {
                "name": "string",
                "language": "string",
                "stars": "int",
                "description": "string",
                "topics": ["string"],
            }
        ],
        "contribution_score": "float",
        "primary_languages": ["string"],
        "total_commits": "int",
    },
    "knowledge_graph": {
        "nodes": [{"id": "string", "type": "string", "label": "string"}],
        "edges": [{"source": "string", "target": "string", "relation": "string"}],
    },
    "embeddings": {
        "skills_embedding": "vector",
        "experience_embedding": "vector",
        "overall_embedding": "vector",
    },
    "feature_vector": "vector",
    "profile_summary": "string",
    "created_at": "datetime",
}


class DataCollectionService:
    """Multi-source candidate profiling and feature engineering pipeline."""

    def __init__(self):
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def embedding_model(self) -> Optional[SentenceTransformer]:
        from app.services.model_registry import model_registry
        return model_registry.embedding_model

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    # ── Resume Parsing ────────────────────────────────

    def parse_resume_pdf(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extract text and structured data from a PDF resume."""
        if not PDF_AVAILABLE:
            return {"raw_text": "", "error": "PyPDF2 not installed"}

        try:
            from io import BytesIO
            reader = PdfReader(BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return self._extract_resume_features(text)
        except Exception as e:
            return {"raw_text": "", "error": str(e)}

    def parse_resume_docx(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extract text and structured data from a DOCX resume."""
        if not DOCX_AVAILABLE:
            return {"raw_text": "", "error": "python-docx not installed"}

        try:
            from io import BytesIO
            doc = docx.Document(BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            return self._extract_resume_features(text)
        except Exception as e:
            return {"raw_text": "", "error": str(e)}

    def _extract_resume_features(self, text: str) -> Dict[str, Any]:
        """NLP-based feature extraction from resume text."""
        # Skill extraction using pattern matching + NER
        skill_patterns = [
            r"(?i)\b(python|java|javascript|typescript|react|angular|vue|node\.?js|"
            r"django|flask|fastapi|spring|docker|kubernetes|aws|azure|gcp|"
            r"sql|mongodb|postgresql|redis|git|ci/cd|machine learning|deep learning|"
            r"tensorflow|pytorch|nlp|computer vision|rest api|graphql|"
            r"agile|scrum|html|css|c\+\+|c#|go|rust|swift|kotlin|"
            r"data structures|algorithms|system design|microservices|"
            r"linux|devops|terraform|jenkins|spark|hadoop|kafka)\b"
        ]
        skills = list(set(re.findall(skill_patterns[0], text, re.IGNORECASE)))

        # Experience extraction
        experience_pattern = r"(?i)(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)"
        exp_match = re.search(experience_pattern, text)
        years_of_experience = int(exp_match.group(1)) if exp_match else 0

        # Education extraction
        education_patterns = r"(?i)(B\.?(?:Tech|S|E|A)|M\.?(?:Tech|S|E|A)|Ph\.?D|MBA|Bachelor|Master|Doctorate)"
        degrees = re.findall(education_patterns, text)

        # Email extraction
        email_pattern = r"[\w.+-]+@[\w-]+\.[\w.-]+"
        emails = re.findall(email_pattern, text)

        # Phone extraction
        phone_pattern = r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}"
        phones = re.findall(phone_pattern, text)

        # Certification keywords
        cert_patterns = r"(?i)(AWS Certified|Google Cloud|Azure|PMP|Scrum Master|CISSP|CKA|"
        cert_patterns += r"Certified|Certificate|Certification)"
        certifications = re.findall(cert_patterns, text)

        # Project extraction (heuristic)
        project_sections = re.findall(
            r"(?i)(?:project[s]?\s*[:\-]?\s*)(.*?)(?=\n\n|\Z)",
            text, re.DOTALL
        )

        return {
            "raw_text": text,
            "skills": [s.lower() for s in skills],
            "years_of_experience": years_of_experience,
            "degrees": list(set(degrees)),
            "emails": emails[:1],
            "phones": phones[:1],
            "certifications": list(set(certifications)),
            "word_count": len(text.split()),
            "sections_detected": self._detect_sections(text),
        }

    def _detect_sections(self, text: str) -> List[str]:
        """Detect resume sections."""
        section_keywords = [
            "education", "experience", "skills", "projects",
            "certifications", "achievements", "summary", "objective",
            "publications", "awards", "languages", "interests",
        ]
        found = []
        text_lower = text.lower()
        for kw in section_keywords:
            if kw in text_lower:
                found.append(kw)
        return found

    # ── GitHub Analysis ───────────────────────────────

    async def analyze_github_profile(self, username: str) -> Dict[str, Any]:
        """Analyze a GitHub profile for coding skills and contributions."""
        try:
            # Fetch user info
            user_resp = await self.http_client.get(
                f"https://api.github.com/users/{username}",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            if user_resp.status_code != 200:
                return {"error": f"GitHub user not found: {username}"}

            user_data = user_resp.json()

            # Fetch repositories
            repos_resp = await self.http_client.get(
                f"https://api.github.com/users/{username}/repos",
                params={"sort": "updated", "per_page": 30},
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            repos = repos_resp.json() if repos_resp.status_code == 200 else []

            # Analyze repositories
            languages = {}
            total_stars = 0
            repo_details = []

            for repo in repos:
                if isinstance(repo, dict):
                    lang = repo.get("language")
                    if lang:
                        languages[lang] = languages.get(lang, 0) + 1
                    total_stars += repo.get("stargazers_count", 0)
                    repo_details.append({
                        "name": repo.get("name", ""),
                        "language": lang or "Unknown",
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "description": repo.get("description", ""),
                        "topics": repo.get("topics", []),
                        "is_fork": repo.get("fork", False),
                        "size_kb": repo.get("size", 0),
                        "updated_at": repo.get("updated_at", ""),
                    })

            # Sort languages by frequency
            primary_languages = sorted(
                languages.items(), key=lambda x: -x[1]
            )

            # Calculate contribution score
            contribution_score = min(100, (
                len(repos) * 2 +
                total_stars * 5 +
                user_data.get("public_gists", 0) * 1 +
                user_data.get("followers", 0) * 0.5
            ))

            return {
                "username": username,
                "name": user_data.get("name", ""),
                "bio": user_data.get("bio", ""),
                "public_repos": user_data.get("public_repos", 0),
                "followers": user_data.get("followers", 0),
                "following": user_data.get("following", 0),
                "repositories": repo_details[:20],
                "primary_languages": [l[0] for l in primary_languages[:5]],
                "language_distribution": dict(primary_languages[:10]),
                "total_stars": total_stars,
                "contribution_score": round(contribution_score, 1),
                "account_created": user_data.get("created_at", ""),
                "profile_url": user_data.get("html_url", ""),
            }
        except Exception as e:
            return {"error": str(e)}

    # ── Knowledge Graph Construction ──────────────────

    def build_knowledge_graph(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Construct a knowledge graph from candidate profile data."""
        nodes = []
        edges = []
        node_id = 0

        def add_node(label: str, node_type: str) -> str:
            nonlocal node_id
            nid = f"n_{node_id}"
            nodes.append({"id": nid, "type": node_type, "label": label})
            node_id += 1
            return nid

        # Central candidate node
        candidate_id = add_node(profile.get("name", "Candidate"), "candidate")

        # Skills
        skills = profile.get("resume", {}).get("skills", [])
        for skill in skills:
            skill_id = add_node(skill, "skill")
            edges.append({
                "source": candidate_id,
                "target": skill_id,
                "relation": "has_skill",
            })

        # Experience
        experiences = profile.get("resume", {}).get("experience", [])
        for exp in experiences:
            company = exp.get("company", "Unknown")
            role = exp.get("role", "Unknown")
            exp_id = add_node(f"{role} @ {company}", "experience")
            edges.append({
                "source": candidate_id,
                "target": exp_id,
                "relation": "worked_as",
            })
            # Link technologies to experience
            for tech in exp.get("technologies", []):
                tech_id = add_node(tech, "technology")
                edges.append({
                    "source": exp_id,
                    "target": tech_id,
                    "relation": "used_technology",
                })

        # Education
        education = profile.get("resume", {}).get("education", [])
        for edu in education:
            edu_label = f"{edu.get('degree', '')} - {edu.get('institution', '')}"
            edu_id = add_node(edu_label, "education")
            edges.append({
                "source": candidate_id,
                "target": edu_id,
                "relation": "studied_at",
            })

        # GitHub repos
        github = profile.get("github", {})
        for repo in github.get("repositories", [])[:10]:
            repo_id = add_node(repo.get("name", ""), "repository")
            edges.append({
                "source": candidate_id,
                "target": repo_id,
                "relation": "authored",
            })
            if repo.get("language"):
                lang_id = add_node(repo["language"], "language")
                edges.append({
                    "source": repo_id,
                    "target": lang_id,
                    "relation": "written_in",
                })

        # Derive central skills (skills with most connections)
        skill_nodes = [n for n in nodes if n["type"] == "skill"]
        central_skills = [n["label"] for n in skill_nodes[:10]]

        # Derive skill clusters from technology nodes grouped by experience
        tech_nodes = [n for n in nodes if n["type"] == "technology"]
        skill_clusters = {}
        for edge in edges:
            if edge["relation"] == "used_technology":
                # Find the experience node for this edge
                exp_node = next((n for n in nodes if n["id"] == edge["source"]), None)
                if exp_node:
                    cluster_name = exp_node["label"].split(" @ ")[0] if " @ " in exp_node["label"] else "General"
                    tech_node = next((n for n in nodes if n["id"] == edge["target"]), None)
                    if tech_node:
                        skill_clusters.setdefault(cluster_name, []).append(tech_node["label"])

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "central_skills": central_skills,
            "skill_clusters": skill_clusters,
        }

    # ── Embedding Generation ──────────────────────────

    def generate_embeddings(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate transformer-based embeddings for candidate profile."""
        if not self.embedding_model:
            return {"error": "SentenceTransformer not available"}

        texts_to_embed = {}

        # Skills embedding
        skills = profile.get("resume", {}).get("skills", [])
        if skills:
            texts_to_embed["skills"] = " ".join(skills)

        # Experience embedding
        raw_text = profile.get("resume", {}).get("raw_text", "")
        if raw_text:
            texts_to_embed["experience"] = raw_text[:2000]

        # GitHub embedding
        github = profile.get("github", {})
        github_texts = []
        for repo in github.get("repositories", [])[:10]:
            desc = repo.get("description", "")
            if desc:
                github_texts.append(desc)
        if github_texts:
            texts_to_embed["github"] = " ".join(github_texts)

        # Overall profile embedding
        all_text = " ".join(texts_to_embed.values())
        if all_text:
            texts_to_embed["overall"] = all_text

        embeddings = {}
        for key, text in texts_to_embed.items():
            emb = self.embedding_model.encode(text)
            embeddings[f"{key}_embedding"] = emb.tolist()

        return embeddings

    # ── Feature Engineering ───────────────────────────

    def engineer_features(self, profile: Dict[str, Any]) -> Dict[str, float]:
        """Create a numerical feature vector from candidate profile."""
        resume = profile.get("resume", {})
        github = profile.get("github", {})

        features = {
            # Resume features
            "num_skills": len(resume.get("skills", [])),
            "years_experience": resume.get("years_of_experience", 0),
            "num_degrees": len(resume.get("degrees", [])),
            "num_certifications": len(resume.get("certifications", [])),
            "resume_word_count": resume.get("word_count", 0),
            "num_sections": len(resume.get("sections_detected", [])),
            # GitHub features
            "num_repos": github.get("public_repos", 0),
            "total_stars": github.get("total_stars", 0),
            "num_languages": len(github.get("primary_languages", [])),
            "contribution_score": github.get("contribution_score", 0),
            "github_followers": github.get("followers", 0),
            # Derived features
            "has_github": 1.0 if github.get("username") else 0.0,
            "has_certifications": 1.0 if resume.get("certifications") else 0.0,
            "skill_diversity": min(1.0, len(resume.get("skills", [])) / 20),
            "experience_depth": min(1.0, resume.get("years_of_experience", 0) / 10),
        }

        return features

    # ── Full Pipeline ─────────────────────────────────

    async def build_candidate_profile(
        self,
        name: str,
        email: str,
        resume_bytes: Optional[bytes] = None,
        resume_type: str = "pdf",
        github_username: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run the full candidate profiling pipeline."""
        profile = {
            "name": name,
            "email": email,
            "resume": {},
            "github": {},
            "knowledge_graph": {},
            "embeddings": {},
            "features": {},
            "created_at": datetime.utcnow().isoformat(),
        }

        # Parse resume
        if resume_bytes:
            if resume_type == "pdf":
                profile["resume"] = self.parse_resume_pdf(resume_bytes)
            elif resume_type == "docx":
                profile["resume"] = self.parse_resume_docx(resume_bytes)

        # Analyze GitHub
        if github_username:
            profile["github"] = await self.analyze_github_profile(github_username)

        # Build knowledge graph
        profile["knowledge_graph"] = self.build_knowledge_graph(profile)

        # Generate embeddings
        profile["embeddings"] = self.generate_embeddings(profile)

        # Engineer features
        profile["features"] = self.engineer_features(profile)

        # Generate profile summary
        profile["profile_summary"] = self._generate_summary(profile)

        return profile

    def _generate_summary(self, profile: Dict[str, Any]) -> str:
        """Generate a human-readable profile summary."""
        resume = profile.get("resume", {})
        github = profile.get("github", {})

        parts = [f"Candidate: {profile.get('name', 'Unknown')}"]

        skills = resume.get("skills", [])
        if skills:
            parts.append(f"Skills: {', '.join(skills[:10])}")

        yoe = resume.get("years_of_experience", 0)
        if yoe:
            parts.append(f"Experience: {yoe} years")

        degrees = resume.get("degrees", [])
        if degrees:
            parts.append(f"Education: {', '.join(degrees)}")

        if github.get("username"):
            parts.append(
                f"GitHub: {github['username']} "
                f"({github.get('public_repos', 0)} repos, "
                f"{github.get('total_stars', 0)} stars)"
            )

        return " | ".join(parts)


# Singleton
data_collection_service = DataCollectionService()
