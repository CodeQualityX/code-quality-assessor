import pandas as pd
import subprocess
import tempfile
import re
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# File paths
INPUT_FILE = "data/raw/function_features.csv"
OUTPUT_FILE = "data/interim/function_features_with_scores.csv"
LOG_ERRORS = "flake8_failures.log"
LOG_DEBUG = "flake8_debug.log"

def get_flake8_score(code_string):
    try:
        # Save the function code to a temp file
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write(code_string)
            tmp_path = tmp.name

        # Run flake8 on the temp file
        result = subprocess.run(
            [r'C:\Users\Nour\AppData\Roaming\Python\Python312\Scripts\flake8.exe', tmp_path],
            capture_output=True,
            text=True
        )

        # Count violations
        violations = result.stdout.strip().splitlines()
        num_violations = len(violations)

        # Log for debugging
        with open(LOG_DEBUG, 'a', encoding='utf-8') as log:
            log.write("\n==== SNIPPET ====\n" + code_string[:300])
            log.write(f"\nViolations: {num_violations}\n")
            log.write("STDOUT:\n" + result.stdout + "\nSTDERR:\n" + result.stderr + "\n")

        # Convert number of violations into a score from 10 to 0
        score = max(10.0 - num_violations, 0.0)
        return score

    except Exception as e:
        with open(LOG_ERRORS, 'a', encoding='utf-8') as f:
            f.write(f"Error for code:\n{code_string[:80]}\n{str(e)}\n\n")
    return None

def run_parallel(data, func, workers=None):
    workers = workers or cpu_count()
    print(f"Running on {workers} workers...")
    with Pool(processes=workers) as pool:
        return list(tqdm(pool.imap(func, data), total=len(data)))

def main():
    print("Loading dataset...")
    df = pd.read_csv(INPUT_FILE)

    if 'code_snippet' not in df.columns:
        raise ValueError("Missing 'code_snippet' column in input file.")

    print("Scoring functions in parallel with flake8...")
    df['quality_score'] = run_parallel(df['code_snippet'].tolist(), get_flake8_score)

    print("Saving output...")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Done. Saved to {OUTPUT_FILE}")

    print("\n🔍 Quality score summary:")
    print(df['quality_score'].value_counts(dropna=False))

if __name__ == "__main__":
    main()
