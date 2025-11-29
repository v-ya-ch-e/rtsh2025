import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

# 1. SETUP SETTINGS (Must match ingestion)
# Make sure this API key is the same one used during ingestion!
Settings.embed_model = OpenAIEmbedding(api_key=open("cred").read())

# 2. CONNECT TO DATABASE (No ingestion logic here)
db_path = "/Users/zero_skill/Documents/negotiation_DB"
db = chromadb.PersistentClient(path=db_path)

# Get the existing collection.
# Note: get_collection() is safer than get_or_create() for querying
# because it will throw an error if the DB is empty (alerting you something is wrong).
chroma_collection = db.get_collection("my_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 3. LOAD INDEX (Instant)
# We load directly from the vector store. No storage_context needed for pure retrieval.
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=Settings.embed_model
)

# 4. RUN RETRIEVER
print("🚀 Index loaded! Running query...")
retriever = index.as_retriever(similarity_top_k=15)
nodes = retriever.retrieve("Find all prices mentioned in the files")

# 5. DISPLAY RESULTS
print(f"Found {len(nodes)} relevant snippets.")
context_str = "\n\n".join([n.node.get_content() for n in nodes])
print(context_str)