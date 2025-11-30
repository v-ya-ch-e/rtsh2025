import os
import json
import re

STORAGE_DIR = "storage"
KEYWORDS_FILE = os.path.join(STORAGE_DIR, "all_keywords.json")

def clean_text(text):
    # Remove markdown symbols
    text = re.sub(r'[*_#`]', '', text)
    # Replace newlines with spaces
    text = text.replace('\n', ' ')
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def migrate():
    companies_dir = os.path.join(STORAGE_DIR, "companies")
    if not os.path.exists(companies_dir):
        print("No companies directory found.")
        return

    all_keywords = {}

    for company_id in os.listdir(companies_dir):
        company_path = os.path.join(companies_dir, company_id)
        if not os.path.isdir(company_path):
            continue

        context_path = os.path.join(company_path, "context.txt")
        knowledge_path = os.path.join(company_path, "knowledge.txt")

        combined_text = ""
        
        if os.path.exists(context_path):
            with open(context_path, "r") as f:
                combined_text += f.read() + " "
        
        if os.path.exists(knowledge_path):
            with open(knowledge_path, "r") as f:
                combined_text += f.read() + " "

        cleaned_keywords = clean_text(combined_text)
        all_keywords[company_id] = cleaned_keywords
        print(f"Processed Company {company_id}: {len(cleaned_keywords)} chars")

    with open(KEYWORDS_FILE, "w") as f:
        json.dump(all_keywords, f, indent=2)
    
    print(f"Migration complete. Saved to {KEYWORDS_FILE}")

if __name__ == "__main__":
    migrate()
