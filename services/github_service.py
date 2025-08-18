"""
GitHub API service for fetching repository issues.
"""

import os
import requests
import logging
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for interacting with GitHub API."""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        
        # Set up authentication headers
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "GitHub-Issue-Summarizer/1.0"
            })
        else:
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "GitHub-Issue-Summarizer/1.0"
            })
    
    def get_repository_issues(self, owner: str, repo: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Fetch issues from a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            page: Page number for pagination
            per_page: Number of issues per page (max 100)
            
        Returns:
            Dictionary containing issues data or error information
        """
        try:
            # Limit per_page to prevent abuse
            per_page = min(per_page, 100)
            
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            params = {
                "state": "all",  # Get both open and closed issues
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc"
            }
            
            logger.info(f"Fetching issues from {owner}/{repo} - Page {page}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 404:
                return {"error": "Repository not found or is private"}
            elif response.status_code == 403:
                # Check if it's a rate limit issue
                if 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
                    reset_time = response.headers.get('X-RateLimit-Reset', 'unknown')
                    return {"error": f"GitHub API rate limit exceeded. Reset time: {reset_time}"}
                else:
                    return {"error": "Access forbidden. Repository may be private or token invalid."}
            elif response.status_code != 200:
                return {"error": f"GitHub API error: {response.status_code} - {response.text}"}
            
            issues = response.json()
            
            # Filter out pull requests (GitHub API includes PRs in issues endpoint)
            issues = [issue for issue in issues if 'pull_request' not in issue]
            
            # Check for pagination
            has_next = self._check_has_next_page(response.headers.get('Link'))
            
            # Get total count from repository info if available
            total_count = self._get_total_issue_count(owner, repo)
            
            logger.info(f"Successfully fetched {len(issues)} issues from {owner}/{repo}")
            
            return {
                "issues": issues,
                "has_next": has_next,
                "total_count": total_count,
                "rate_limit_remaining": response.headers.get('X-RateLimit-Remaining'),
                "rate_limit_reset": response.headers.get('X-RateLimit-Reset')
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching issues from {owner}/{repo}")
            return {"error": "Request timeout. GitHub API is not responding."}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error fetching issues from {owner}/{repo}")
            return {"error": "Connection error. Please check your internet connection."}
        except Exception as e:
            logger.error(f"Unexpected error fetching issues from {owner}/{repo}: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _check_has_next_page(self, link_header: Optional[str]) -> bool:
        """
        Check if there's a next page based on GitHub's Link header.
        
        Args:
            link_header: The Link header from GitHub API response
            
        Returns:
            Boolean indicating if there's a next page
        """
        if not link_header:
            return False
        
        links = {}
        for link in link_header.split(','):
            parts = link.strip().split(';')
            if len(parts) == 2:
                url = parts[0].strip('<>')
                rel = parts[1].strip().split('=')[1].strip('"')
                links[rel] = url
        
        return 'next' in links
    
    def _get_total_issue_count(self, owner: str, repo: str) -> Optional[int]:
        """
        Get total issue count for the repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Total issue count or None if unavailable
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                return repo_data.get('open_issues_count', 0)  # This includes both issues and PRs
            
        except Exception as e:
            logger.warning(f"Could not fetch total issue count: {str(e)}")
        
        return None
    
    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information or error
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 404:
                return {"error": "Repository not found"}
            elif response.status_code != 200:
                return {"error": f"GitHub API error: {response.status_code}"}
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching repository info: {str(e)}")
            return {"error": f"Error fetching repository info: {str(e)}"}
    
    def health_check(self) -> bool:
        """
        Check if GitHub API is accessible.
        
        Returns:
            Boolean indicating service health
        """
        try:
            response = self.session.get(f"{self.base_url}/rate_limit", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        Get current rate limit information.
        
        Returns:
            Rate limit information
        """
        try:
            response = self.session.get(f"{self.base_url}/rate_limit", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Could not fetch rate limit info"}
        except Exception as e:
            return {"error": f"Error fetching rate limit: {str(e)}"}
