import chromadb
import constants
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from RAG_helper.constants import QUERY_RES_LIMIT

# 2. CONNECT TO DATABASE (No ingestion logic here)
def processQuery(query, company_id):
    db_path = "data/context_company_" + str(company_id)
    db = chromadb.PersistentClient(path=db_path)
    chroma_collection = db.get_collection(
        name="collection_dev_0" + str(company_id),
        embedding_function=OpenAIEmbeddingFunction(
            api_key=open("cred").read(),
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
    context_str = "\n".join([n for n in results["documents"][0]])
    return context_str

print(processQuery("product prices", 1))
