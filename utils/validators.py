"""
Validation utilities for GitHub Issue Summarizer.
"""

import re
from typing import Tuple, Optional
from urllib.parse import urlparse

def validate_github_url(url: str) -> bool:
    """
    Validate if the provided URL is a valid GitHub repository URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        Boolean indicating if the URL is valid
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    # GitHub repository URL pattern
    github_pattern = r'^https://github\.com/[^/\s]+/[^/\s]+/?$'
    
    if not re.match(github_pattern, url):
        return False
    
    # Additional validation using urlparse
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme == 'https' and
            parsed.netloc == 'github.com' and
            len(parsed.path.strip('/').split('/')) == 2
        )
    except Exception:
        return False

def extract_repo_info(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract repository owner and name from GitHub URL.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Tuple of (owner, repository_name) or (None, None) if invalid
    """
    if not validate_github_url(url):
        return None, None
    
    try:
        # Remove trailing slash and split path
        path = url.rstrip('/').split('github.com/')[-1]
        parts = path.split('/')
        
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1]
            
            # Basic validation of owner and repo names
            if owner and repo and owner != '.' and repo != '.':
                return owner, repo
    except Exception:
        pass
    
    return None, None

def validate_pagination_params(page: int, per_page: int) -> Tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number
        per_page: Items per page
        
    Returns:
        Tuple of validated (page, per_page)
    """
    # Normalize page number
    page = max(1, int(page) if isinstance(page, (int, str)) and str(page).isdigit() else 1)
    
    # Normalize per_page (limit to reasonable range)
    if isinstance(per_page, (int, str)) and str(per_page).isdigit():
        per_page = max(1, min(100, int(per_page)))
    else:
        per_page = 10
    
    return page, per_page

def sanitize_text(text: str) -> str:
    """
    Sanitize text input to prevent XSS and other issues.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove null bytes and other control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Basic HTML entity escaping for safety
    html_escape_chars = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    
    for char, entity in html_escape_chars.items():
        text = text.replace(char, entity)
    
    return text.strip()

def validate_issue_data(issue_data: dict) -> bool:
    """
    Validate GitHub issue data structure.
    
    Args:
        issue_data: Issue data dictionary from GitHub API
        
    Returns:
        Boolean indicating if the data is valid
    """
    required_fields = ['number', 'title', 'state', 'html_url', 'created_at', 'updated_at']
    
    if not isinstance(issue_data, dict):
        return False
    
    for field in required_fields:
        if field not in issue_data:
            return False
    
    # Validate specific field types
    try:
        if not isinstance(issue_data['number'], int) or issue_data['number'] <= 0:
            return False
        
        if not isinstance(issue_data['title'], str) or not issue_data['title'].strip():
            return False
        
        if issue_data['state'] not in ['open', 'closed']:
            return False
        
        if not isinstance(issue_data['html_url'], str) or not issue_data['html_url'].startswith('https://'):
            return False
    except (KeyError, TypeError):
        return False
    
    return True

def normalize_github_url(url: str) -> str:
    """
    Normalize GitHub URL to a consistent format.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Normalized URL or original if invalid
    """
    if not validate_github_url(url):
        return url
    
    # Remove trailing slash and ensure consistent format
    url = url.rstrip('/')
    
    # Ensure https protocol
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    
    return url

def validate_api_request(data: dict) -> Tuple[bool, str]:
    """
    Validate API request data.
    
    Args:
        data: Request data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Request data must be a JSON object"
    
    if 'repo_url' not in data:
        return False, "Missing required field: repo_url"
    
    repo_url = data['repo_url']
    if not validate_github_url(repo_url):
        return False, "Invalid GitHub repository URL"
    
    # Validate optional parameters
    if 'page' in data:
        try:
            page = int(data['page'])
            if page < 1 or page > 1000:
                return False, "Page number must be between 1 and 1000"
        except (ValueError, TypeError):
            return False, "Page number must be a valid integer"
    
    if 'per_page' in data:
        try:
            per_page = int(data['per_page'])
            if per_page < 1 or per_page > 100:
                return False, "Per page count must be between 1 and 100"
        except (ValueError, TypeError):
            return False, "Per page count must be a valid integer"
    
    return True, ""
