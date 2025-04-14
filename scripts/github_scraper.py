import requests
from datetime import datetime
import ast
from code_processing import CodeFeatureExtractor

class GitHubScraper:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})
        self.session.headers.update({"Accept": "application/vnd.github.v3+json"})

    def get_repo_metadata(self, owner, repo):
        """Fetch repository-level metadata."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data["name"],
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "watchers": data["subscribers_count"],
                "language": data["language"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "topics": data.get("topics", [])
            }
        else:
            print(f"[ERROR] Failed to fetch repo metadata: {response.status_code}")
            return None
        
    def get_python_files(self, owner, repo):

        """Return a list of all .py file paths in a GitHub repo."""

        # Step 1: Get the default branch (usually 'main' or 'master')
        repo_url = f"{self.base_url}/repos/{owner}/{repo}"
        repo_resp = self.session.get(repo_url)
        if repo_resp.status_code != 200:
            print(f"[ERROR] Could not fetch repo info: {repo_resp.status_code}")
            return []

        default_branch = repo_resp.json().get("default_branch", "main")

        # Step 2: Get the tree SHA for the default branch
        tree_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        tree_resp = self.session.get(tree_url)
        if tree_resp.status_code != 200:
            print(f"[ERROR] Could not fetch file tree: {tree_resp.status_code}")
            return []

        tree_data = tree_resp.json()
        all_files = tree_data.get("tree", [])

        # Step 3: Filter for Python files
        py_files = [f["path"] for f in all_files if f["path"].endswith(".py") and f["type"] == "blob"]

        return py_files
    
    def download_file_content(self, owner, repo, file_path):
        """Download raw content of a file from the repo."""
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{file_path}"
        response = self.session.get(url)

        if response.status_code == 200:
            return response.text
        else:
            print(f"[ERROR] Failed to download {file_path}: {response.status_code}")
            return None
    
    def extract_features_from_code(self, file_path, code_str, repo_metadata):
        """Extract features from top-level functions in a code string."""
        features = []

        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            print(f"[ERROR] Failed to parse {file_path}: {e}")
            return features

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name
                node_type = "function"

                snippet = ast.get_source_segment(code_str, node) or ""

                extractor = CodeFeatureExtractor(
                    name=name,
                    node_type=node_type,
                    file_path=file_path,
                    code_snippet=snippet
                )

                # Attach repo metadata
                extractor.repo_name = repo_metadata.get("name")
                extractor.repo_stars = repo_metadata.get("stars")
                extractor.repo_forks = repo_metadata.get("forks")
                extractor.repo_watchers = repo_metadata.get("watchers")
                extractor.repo_language = repo_metadata.get("language")
                extractor.repo_created_at = repo_metadata.get("created_at")
                extractor.repo_last_updated = repo_metadata.get("updated_at")
                extractor.repo_topics = repo_metadata.get("topics")

                # Extract internal features
                extractor.set_features(node)

                features.append(extractor)

        return features


