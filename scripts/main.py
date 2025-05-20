from github_scraper import GitHubScraper
import csv
import os

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
    token = "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"
    repos = [
        ("keon", "algorithms"),
        ("psf", "requests"),
        ("pallets", "flask")
    ]

    for owner, repo in repos:
        process_repository(owner, repo, token, output_file="function_features.csv")