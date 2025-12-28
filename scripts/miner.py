import pandas as pd
from pydriller import Repository
import os

def mine_repository(repo_path='.'):
    """Extrait les features des commits pour l'entraînement du ML."""
    data = []
    print(f"🚀 Analyse du dépôt : {repo_path}...")

    for commit in Repository(repo_path).traverse_commits():
        for file in commit.modified_files:
            # On se concentre sur les fichiers de code
            if file.filename.endswith(('.py', '.js', '.go', '.cpp')):
                data.append({
                    'hash': commit.hash,
                    'author': commit.author.name,
                    'date': commit.author_date,
                    'file': file.filename,
                    'added': file.added_lines,
                    'removed': file.deleted_lines,
                    'complexity': file.complexity # Feature clé pour le ML
                })

    df = pd.DataFrame(data)
    # Sauvegarde dans le dossier data que vous avez créé
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/features_dataset.csv', index=False)
    print(f"✅ Dataset créé : {len(df)} lignes enregistrées dans data/features_dataset.csv")

if __name__ == "__main__":
    mine_repository()
