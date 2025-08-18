/**
 * GitHub Issue Summarizer - Frontend JavaScript
 * Handles form interactions, validation, and dynamic content
 */

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    setupFormValidation();
    setupFormSubmission();
    setupCollapsibleContent();
    setupTooltips();
    
    console.log('GitHub Issue Summarizer initialized');
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const repoUrlInput = document.getElementById('repo_url');
    
    if (repoUrlInput) {
        repoUrlInput.addEventListener('input', function(e) {
            validateGitHubUrl(e.target);
        });
        
        repoUrlInput.addEventListener('blur', function(e) {
            validateGitHubUrl(e.target);
        });
    }
    
    // Page number validation
    const pageInput = document.getElementById('page');
    if (pageInput) {
        pageInput.addEventListener('input', function(e) {
            const value = parseInt(e.target.value);
            if (value < 1) {
                e.target.value = 1;
            } else if (value > 100) {
                e.target.value = 100;
            }
        });
    }
}

/**
 * Validate GitHub URL format
 * @param {HTMLInputElement} input - The input element to validate
 */
function validateGitHubUrl(input) {
    const url = input.value.trim();
    const githubUrlPattern = /^https:\/\/github\.com\/[^\/\s]+\/[^\/\s]+\/?$/;
    
    // Remove existing validation classes
    input.classList.remove('is-valid', 'is-invalid');
    
    if (url === '') {
        input.setCustomValidity('');
        return;
    }
    
    if (githubUrlPattern.test(url)) {
        input.classList.add('is-valid');
        input.setCustomValidity('');
        
        // Show repository info preview
        showRepositoryPreview(url);
    } else {
        input.classList.add('is-invalid');
        input.setCustomValidity('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repository)');
        
        // Hide repository preview
        hideRepositoryPreview();
    }
}

/**
 * Show repository preview information
 * @param {string} url - GitHub repository URL
 */
function showRepositoryPreview(url) {
    const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)/);
    if (match) {
        const owner = match[1];
        const repo = match[2].replace(/\/$/, ''); // Remove trailing slash
        
        let previewElement = document.getElementById('repo-preview');
        if (!previewElement) {
            previewElement = document.createElement('div');
            previewElement.id = 'repo-preview';
            previewElement.className = 'mt-2 p-2 bg-success bg-opacity-10 border border-success rounded';
            
            const repoInput = document.getElementById('repo_url');
            repoInput.parentNode.appendChild(previewElement);
        }
        
        previewElement.innerHTML = `
            <small class="text-success">
                <i data-feather="check-circle" class="me-1"></i>
                Repository: <strong>${owner}/${repo}</strong>
            </small>
        `;
        
        // Re-initialize feather icons
        feather.replace();
    }
}

/**
 * Hide repository preview
 */
function hideRepositoryPreview() {
    const previewElement = document.getElementById('repo-preview');
    if (previewElement) {
        previewElement.remove();
    }
}

/**
 * Setup form submission handling
 */
function setupFormSubmission() {
    const analyzeForm = document.getElementById('analyzeForm');
    
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            } else {
                showLoadingState();
            }
            
            this.classList.add('was-validated');
        });
    }
    
    // Handle pagination forms
    const paginationForms = document.querySelectorAll('form[action*="analyze_repository"]');
    paginationForms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoadingState();
        });
    });
}

/**
 * Show loading state during form submission
 */
function showLoadingState() {
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (submitBtn && submitText && loadingSpinner) {
        submitBtn.disabled = true;
        submitText.classList.add('d-none');
        loadingSpinner.classList.remove('d-none');
    }
    
    // Show page loading overlay
    showPageLoadingOverlay();
}

/**
 * Show page loading overlay
 */
function showPageLoadingOverlay() {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        overlay.style.cssText = 'background: rgba(0,0,0,0.5); z-index: 9999;';
        
        overlay.innerHTML = `
            <div class="text-center text-white">
                <div class="spinner-border mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5>Analyzing Repository Issues...</h5>
                <p class="mb-0">This may take a moment while we fetch and summarize the issues.</p>
            </div>
        `;
        
        document.body.appendChild(overlay);
    }
    
    overlay.style.display = 'flex';
}

/**
 * Setup collapsible content handlers
 */
function setupCollapsibleContent() {
    // Handle show/hide original content buttons
    const toggleButtons = document.querySelectorAll('[data-bs-toggle="collapse"]');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const icon = this.querySelector('i[data-feather="eye"]');
            const targetId = this.getAttribute('data-bs-target');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.addEventListener('shown.bs.collapse', function() {
                    button.innerHTML = button.innerHTML.replace('Toggle', 'Hide');
                });
                
                targetElement.addEventListener('hidden.bs.collapse', function() {
                    button.innerHTML = button.innerHTML.replace('Hide', 'Toggle');
                });
            }
        });
    });
}

/**
 * Setup tooltips for better UX
 */
function setupTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Export functionality for results page
 */
function exportToJSON() {
    try {
        // This function is called from the results template
        // The actual implementation is in the template for access to template variables
        console.log('Exporting results to JSON...');
    } catch (error) {
        console.error('Export failed:', error);
        showNotification('Export failed. Please try again.', 'error');
    }
}

/**
 * Show notification message
 * @param {string} message - Message to display
 * @param {string} type - Notification type (success, error, info, warning)
 */
function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'danger' : type;
    const iconName = {
        'success': 'check-circle',
        'error': 'alert-circle',
        'danger': 'alert-circle',
        'warning': 'alert-triangle',
        'info': 'info'
    }[type] || 'info';
    
    const alertHtml = `
        <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
            <i data-feather="${iconName}" class="me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at top of main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        const alertContainer = document.createElement('div');
        alertContainer.innerHTML = alertHtml;
        mainContent.insertBefore(alertContainer.firstElementChild, mainContent.firstElementChild);
        
        // Re-initialize feather icons
        feather.replace();
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = mainContent.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

/**
 * Utility function to format dates
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Utility function to truncate text
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Handle API errors gracefully
 * @param {Error} error - Error object
 */
function handleAPIError(error) {
    console.error('API Error:', error);
    
    let message = 'An unexpected error occurred. Please try again.';
    
    if (error.message.includes('404')) {
        message = 'Repository not found or is private.';
    } else if (error.message.includes('403')) {
        message = 'Access denied. The repository may be private or rate limits exceeded.';
    } else if (error.message.includes('timeout')) {
        message = 'Request timed out. Please check your connection and try again.';
    }
    
    showNotification(message, 'error');
}

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Don't show notification for every error, just log it
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    handleAPIError(e.reason);
});
