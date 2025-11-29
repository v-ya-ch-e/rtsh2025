import chromadb
import constants
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from RAG_helper.constants import QUERY_RES_LIMIT

# 2. CONNECT TO DATABASE (No ingestion logic here)
db_path = "/Users/zero_skill/Documents/negotiation_DB"
db = chromadb.PersistentClient(path=db_path)
chroma_collection = db.get_collection(
    name="test_collection_1",
    embedding_function=OpenAIEmbeddingFunction(
        api_key=open("cred").read(),
        model_name="text-embedding-3-large"
    )
)

print("Collection loaded. Running query...")

query_text = "Find all prices mentioned in the files"
results = chroma_collection.query(
    query_texts=[query_text],
    n_results=QUERY_RES_LIMIT
)

# 5. DISPLAY RESULTS
print(f"Found {len(results)} relevant snippets.")
context_str = "\n".join([n for n in results["documents"][0]])
print(context_str)