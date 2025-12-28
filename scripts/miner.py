from pydriller import Repository
import pandas as pd

def collect_git_history(repo_path):
    history = []
    print(f"Extraction des données depuis {repo_path}...")
    
    # On parcourt les commits pour voir quels fichiers changent ensemble
    for commit in Repository(repo_path).traverse_commits():
        for file in commit.modified_files:
            history.append({
                'commit': commit.hash,
                'date': commit.author_date,
                'filename': file.filename,
                'complexity': file.complexity,
                'added': file.added_lines,
                'removed': file.deleted_lines
            })
    
    df = pd.DataFrame(history)
    df.to_csv('data/git_history.csv', index=False)
    print("Fichier data/git_history.csv généré.")

if __name__ == "__main__":
    # Testez sur votre propre repo pour commencer
    collect_git_history('.')

