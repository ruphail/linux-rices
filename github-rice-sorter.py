import requests
import base64
import re
import time
from typing import List, Tuple
import json
import os

def get_github_token() -> str:
    """Get GitHub token from environment variable or prompt user."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        token = input("Please enter your GitHub token: ")
    return token

def get_readme_content(token: str) -> str:
    """Fetch the README content from awesome-rices repository."""
    api_url = "https://api.github.com/repos/zemmsoares/awesome-rices/readme"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch README: {response.status_code}")
    
    content = base64.b64decode(response.json()["content"]).decode("utf-8")
    return content

def extract_github_urls(content: str) -> List[str]:
    """Extract GitHub repository URLs from markdown content."""
    pattern = r'\[([^\]]+)\]\((https://github\.com/[^/]+/[^/\s)+]+)(?:/(?:blob|tree|raw)/[^)\s]+)?\)'
    matches = re.finditer(pattern, content)
    
    urls = []
    for match in matches:
        url = match.group(2)
        url = url.rstrip('/')
        if url not in urls:
            urls.append(url)
    
    return urls

def get_repo_info(url: str, token: str) -> Tuple[str, int, str, str]:
    """Get repository information using GitHub API."""
    repo_path = url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return (
                url,
                data.get("stargazers_count", 0),
                data.get("description", ""),
                data.get("language", "")
            )
        else:
            print(f"Error fetching {repo_path}: {response.status_code}")
            return (url, 0, "", "")
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return (url, 0, "", "")

def main():
    try:
        # Get GitHub token
        token = get_github_token()
        
        # Get README content
        print("Fetching README content...")
        content = get_readme_content(token)
        
        # Extract GitHub URLs
        print("Extracting GitHub URLs...")
        urls = extract_github_urls(content)
        print(f"Found {len(urls)} repositories")
        
        # Fetch star counts and info for each repository
        print("\nFetching repository information...")
        repos_info = []
        for i, url in enumerate(urls, 1):
            print(f"Processing {i}/{len(urls)}: {url}")
            repo_info = get_repo_info(url, token)
            repos_info.append(repo_info)
            time.sleep(0.5)  # Reduced sleep time since we're authenticated
        
        # Sort by stars
        sorted_repos = sorted(repos_info, key=lambda x: x[1], reverse=True)
        
        # Save results
        print("\nSaving results...")
        
        # Save as formatted text
        with open("sorted_rices.txt", 'w') as f:
            f.write("Awesome Rices Sorted by Stars\n")
            f.write("===========================\n\n")
            for url, stars, desc, lang in sorted_repos:
                f.write(f"Stars: {stars}\n")
                f.write(f"URL: {url}\n")
                if desc:
                    f.write(f"Description: {desc}\n")
                if lang:
                    f.write(f"Language: {lang}\n")
                f.write("-" * 50 + "\n")
        
        # Save as JSON for programmatic use
        with open("sorted_rices.json", 'w') as f:
            json_data = [
                {
                    "url": url,
                    "stars": stars,
                    "description": desc,
                    "language": lang
                }
                for url, stars, desc, lang in sorted_repos
            ]
            json.dump(json_data, f, indent=2)
        
        # Print top 10
        print("\nTop 10 Rices by Stars:")
        print("=====================")
        for url, stars, desc, lang in sorted_repos[:10]:
            print(f"\nStars: {stars}")
            print(f"URL: {url}")
            if desc:
                print(f"Description: {desc}")
            if lang:
                print(f"Language: {lang}")

    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")

if __name__ == "__main__":
    main()
