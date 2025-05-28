import csv
import os

from github_scraper import GitHubScraper


def process_repository(owner, repo, token=None, output_file="features.csv"):
	print(f"\n Processing repository: {owner}/{repo}")

	scraper = GitHubScraper(token=token)

	# Step 1: Get repo metadata
	metadata = scraper.get_repo_metadata(owner, repo)
	if not metadata:
		print("Failed to fetch metadata. Exiting.")
		return

	# Step 2: Get Python files
	py_files = scraper.get_python_files(owner, repo)
	if not py_files:
		print("No Python files found. Exiting.")
		return

	print(f"Found {len(py_files)} Python files")

	# Step 3: Process each file
	all_features = []

	for path in py_files:
		print(f"Analyzing {path}")
		code = scraper.download_file_content(owner, repo, path)
		if not code:
			continue

		feature_objects = scraper.extract_features_from_code(path, code, metadata)
		all_features.extend(feature_objects)

	print(f"\nExtracted features from {len(all_features)} functions.")

	# Step 4: Save to CSV
	if all_features:
		save_features_to_csv(all_features, output_file)
		print(f"Saved results to {output_file}")
	else:
		print("No features to save.")


def save_features_to_csv(objects, filename):
	file_exists = os.path.exists(filename)
	write_header = not file_exists or os.stat(filename).st_size == 0

	with open(filename, "a", newline="", encoding="utf-8") as f:
		writer = csv.writer(f)
		header = list(vars(objects[0]).keys())

		if write_header:
			writer.writerow(header)

		for obj in objects:
			writer.writerow([getattr(obj, key) for key in header])


if __name__ == "__main__":
	token = os.getenv("GITHUB_PAT", "")
	repos = [
		("psf", "requests"),        # Popular HTTP library
	("pallets", "flask"),       # Lightweight web framework
	("django", "django"),       # High-level web framework
	("numpy", "numpy"),         # Numerical computing
	("pandas-dev", "pandas"),   # Data analysis
	("scikit-learn", "scikit-learn"),  # ML library
	("matplotlib", "matplotlib"),  # Plotting library
	("tensorflow", "tensorflow"),  # Deep learning framework
	("keras-team", "keras"),       # High-level neural networks API
	("pytorch", "pytorch"),         # Deep learning framework
	("fastai", "fastai"),           # High-level deep learning library
	("scrapy", "scrapy"),           # Web scraping framework
	("beautifulsoup", "beautifulsoup4"),  # HTML parsing library
	("pytest-dev", "pytest"),       # Testing framework
	("jupyter", "notebook"),        # Jupyter Notebook server
	("ipython", "ipython"),          # Interactive Python shell

	
	# === Low-Quality/Educational Repos ===
	("satwikkansal", "wtfpython"),     # Confusing examples
	("geekcomputers", "Python"),       # Random scripts
	("aviaryan", "python-gems"),       # Inconsistent quality
	("realpython", "disaster-aversion-training"),  # Intentional anti-patterns
	#  bad codes examples
	("TheAlgorithms", "Python"),      # Collection of algorithms in Python
	("TheAlgorithms", "Python-Data-Structures"),  # Data structures in Python
	("TheAlgorithms", "Python-Design-Patterns"),  # Design patterns in Python
	("TheAlgorithms", "Python-ML-Algorithms"),  # Machine learning algorithms in Python
	("TheAlgorithms", "Python-Deep-Learning"),  # Deep learning algorithms in Python
	("TheAlgorithms", "Python-Computer-Vision"),  # Computer vision algorithms in Python
	("TheAlgorithms", "Python-Web-Scraping"),  # Web scraping examples in Python
	("TheAlgorithms", "Python-Game-Development"),  # Game development examples in Python
	("TheAlgorithms", "Python-Networking"),  # Networking examples in Python
	("TheAlgorithms", "Python-Data-Science"),  # Data science examples in Python
	("TheAlgorithms", "Python-Data-Visualization"),  # Data visualization examples in Python
	("TheAlgorithms", "Python-Testing"),  # Testing examples in Python
	("TheAlgorithms", "Python-Utilities"),  # Utility scripts in Python
	("TheAlgorithms", "Python-APIs"),  # API examples in Python
	("TheAlgorithms", "Python-Blockchain"),  # Blockchain examples in Python
	("TheAlgorithms", "Python-Internet-of-Things"),  # IoT examples in Python
	("TheAlgorithms", "Python-Security"),  # Security examples in Python
	("TheAlgorithms", "Python-DevOps"),  # DevOps examples in Python
	("TheAlgorithms", "Python-Cloud-Computing"),  # Cloud computing examples in Python
	("TheAlgorithms", "Python-Embedded-Systems"),  # Embedded systems examples in Python
	("TheAlgorithms", "Python-AI"),  # AI examples in Python
	("TheAlgorithms", "Python-NLP"),  # Natural language processing examples in Python
	("TheAlgorithms", "Python-Robotics"),  # Robotics examples in Python
	("TheAlgorithms", "Python-Quantum-Computing"),  # Quantum computing examples in Python
	("TheAlgorithms", "Python-Parallel-Computing"),  # Parallel computing examples in Python
	("TheAlgorithms", "Python-Game-Development"),  # Game development examples in Python
	("TheAlgorithms", "Python-Data-Engineering"),  # Data engineering examples in Python
	("TheAlgorithms", "Python-Data-Analytics"),  # Data analytics examples in Python
	("TheAlgorithms", "Python-Data-Processing"),  # Data processing examples in Python
	("TheAlgorithms", "Python-Data-Integration"),  # Data integration examples in Python
	("TheAlgorithms", "Python-Data-Wrangling"),  # Data wrangling examples in Python
	("TheAlgorithms", "Python-Data-Quality"),  # Data quality examples in Python
	("TheAlgorithms", "Python-Data-Governance"),  # Data governance examples in Python
	("TheAlgorithms", "Python-Data-Privacy"),  # Data privacy examples in Python
	("TheAlgorithms", "Python-Data-Security"),  # Data security examples in Python
	("TheAlgorithms", "Python-Data-Compliance"),  # Data compliance examples in Python
	("TheAlgorithms", "Python-Data-Visualization"),  # Data visualization examples in Python
	("TheAlgorithms", "Python-Data-Science-Projects"),  # Data science projects in Python
	("TheAlgorithms", "Python-Data-Science-Examples"),  # Data science examples in Python
	("TheAlgorithms", "Python-Data-Science-Tutorials"),  # Data science tutorials in Python
	("TheAlgorithms", "Python-Data-Science-Resources"),  # Data science resources in Python
	("TheAlgorithms", "Python-Data-Science-Tools"),  # Data science tools in Python
	("TheAlgorithms", "Python-Data-Science-Libraries"),  # Data science libraries in Python
	("TheAlgorithms", "Python-Data-Science-Frameworks"),  # Data science frameworks in Python


	# === Additional Repos for Diversity ===
	("python", "cpython"),          # Python's official implementation
	("python", "python-docs-samples"),  # Python documentation samples
	("python", "python-patterns"),  # Python design patterns
	("python", "python-ideas"),     # Python enhancement proposals
	("python", "python-asyncio"),   # Asynchronous programming examples
	("python", "python-typing"),    # Type hints and annotations
	("python", "python-requests"),  # Requests library examples
	("python", "python-logging"),   # Logging best practices
	("python", "python-concurrency"),  # Concurrency examples
	("python", "python-testing"),   # Testing best practices
	("python", "python-web-frameworks"),  # Web frameworks comparison
	("python", "python-data-science"),  # Data science examples
	("python", "python-machine-learning"),  # Machine learning examples
	("python", "python-deep-learning"),  # Deep learning examples
	("python", "python-web-scraping"),  # Web scraping examples
	("python", "python-gui-development"),  # GUI development examples
	("python", "python-game-development"),  # Game development examples
	("python", "python-automation"),  # Automation scripts
	("python", "python-scripting"),  # General scripting examples
	("python", "python-utilities"),  # Utility scripts
	("python", "python-education"),  # Educational resources
	("python", "python-community"),  # Community-driven projects
	


		]

	from concurrent.futures import ThreadPoolExecutor, as_completed

	if __name__ == "__main__":
		token = os.getenv("GITHUB_PAT", "")
		output_file = "function_features.csv"

		def run_job(repo_tuple):
			owner, repo = repo_tuple
			process_repository(owner, repo, token=token, output_file=output_file)

		with ThreadPoolExecutor(max_workers=8) as executor:
			futures = [executor.submit(run_job, repo_pair) for repo_pair in repos]
			for future in as_completed(futures):
				try:
					future.result()
				except Exception as e:
					print(f"Error processing a repository: {e}")
