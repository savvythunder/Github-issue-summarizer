
# GitHub Issue Summarizer

A Flask web application that analyzes GitHub repositories and provides AI-generated summaries of issues to help developers quickly understand project status and common problems.

## Features

- Fetch issues from any public GitHub repository
- AI-powered summarization of issue content
- Clean, responsive web interface
- Caching for improved performance
- Support for pagination through large issue lists
- REST API endpoints

## Getting Started

1. **Set up GitHub Token (Optional but recommended):**
   - Create a personal access token on GitHub
   - Add it as `GITHUB_TOKEN` in the Secrets tab

2. **Run the application:**
   - Click the "Run" button in Replit
   - The app will be available at the provided URL

3. **Use the application:**
   - Enter a GitHub repository URL (e.g., `https://github.com/owner/repo`)
   - Click "Analyze Repository" to get issue summaries

## Configuration

The application can be configured using environment variables:

- `GITHUB_TOKEN`: GitHub personal access token (recommended)
- `HUGGINGFACE_MODEL`: AI model for summarization (default: facebook/bart-large-cnn)
- `MAX_SUMMARY_LENGTH`: Maximum summary length (default: 150)
- `CACHE_TYPE`: Cache type (simple, redis, filesystem)

## API Endpoints

- `POST /api/analyze`: Analyze repository issues (JSON API)
- `GET /api/health`: Health check endpoint

## Tech Stack

- **Backend:** Flask, Python
- **AI:** Hugging Face Transformers
- **Caching:** Flask-Caching
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Replit

## License

This project is open source and available under the MIT License.

---
## Images 
![Screenshot_18-8-2025_194958_db922807-bf41-47b7-88fe-5d55aa308e90-00-2t9r0s34hr2wo janeway replit dev](https://github.com/user-attachments/assets/aeea4f83-b3a1-4865-a97b-607aa6f14dbd)


![Screenshot_18-8-2025_195036_db922807-bf41-47b7-88fe-5d55aa308e90-00-2t9r0s34hr2wo janeway replit dev](https://github.com/user-attachments/assets/0ed2deda-f46a-45d6-b729-3e2d7aea7bca)

