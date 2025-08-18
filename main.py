"""
Data models for the GitHub Issue Summarizer application.
This file contains Pydantic models for data validation and serialization.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class GitHubUser:
    """GitHub user information."""
    login: str
    id: int
    avatar_url: str
    html_url: str

@dataclass
class GitHubLabel:
    """GitHub issue label."""
    name: str
    color: str
    description: Optional[str] = None

@dataclass
class GitHubIssue:
    """GitHub issue data model."""
    number: int
    title: str
    body: Optional[str]
    state: str
    labels: List[GitHubLabel]
    user: Optional[GitHubUser]
    created_at: str
    updated_at: str
    html_url: str
    comments: int = 0

@dataclass
class SummarizedIssue:
    """Summarized GitHub issue with AI-generated summary."""
    number: int
    title: str
    original_body: str
    summary: str
    state: str
    labels: List[str]
    created_at: str
    updated_at: str
    html_url: str
    user: str
    confidence_score: Optional[float] = None

@dataclass
class RepositoryInfo:
    """Repository information."""
    owner: str
    name: str
    url: str
    full_name: str

@dataclass
class PaginationInfo:
    """Pagination information for API responses."""
    current_page: int
    per_page: int
    has_next: bool
    has_previous: bool
    total_count: int

@dataclass
class AnalysisResult:
    """Complete analysis result with repository info, issues, and pagination."""
    repository: RepositoryInfo
    issues: List[SummarizedIssue]
    pagination: PaginationInfo
    processing_time: Optional[float] = None
    cache_hit: bool = False
