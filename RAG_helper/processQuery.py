import os
try:
    import chromadb
    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
    CHROMA_AVAILABLE = True
except ImportError:
    print("ChromaDB not available. RAG context will be disabled.")
    CHROMA_AVAILABLE = False

from RAG_helper.constants import QUERY_RES_LIMIT

# 2. CONNECT TO DATABASE (No ingestion logic here)
def processQuery(query, company_id):
    if not CHROMA_AVAILABLE:
        return ""

    # Use absolute paths relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "data", "context_company_" + str(company_id))
    cred_path = os.path.join(base_dir, "cred")

    if not os.path.exists(db_path):
        print(f"RAG DB path not found: {db_path}")
        return ""

    try:
        if os.path.exists(cred_path):
            api_key = open(cred_path).read().strip()
        else:
            api_key = os.environ.get("OPENAI_API_KEY")
            
        if not api_key:
            print("OpenAI API Key not found.")
            return ""

        db = chromadb.PersistentClient(path=db_path)
        chroma_collection = db.get_collection(
            name="collection_dev_0" + str(company_id),
            embedding_function=OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name="text-embedding-3-small"
            )
        )

        # print("Collection loaded. Running query...")

        results = chroma_collection.query(
            query_texts=[query],
            n_results=QUERY_RES_LIMIT
        )

        # 5. DISPLAY RESULTS
        # print(f"Found {len(results)} relevant snippets.")
        if results and results["documents"]:
            context_str = "\n".join([n for n in results["documents"][0]])
            return context_str
        return ""
    except Exception as e:
        print(f"Error in processQuery: {e}")
        return ""

if __name__ == "__main__":
    print(processQuery("product prices", 1))
