# install: pip install llama-index llama-index-vector-stores-chroma chromadb llama-parse
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
import chromadb
Settings.embed_model = OpenAIEmbedding(api_key=open("cred").read())
# 1. Setup Persistent Storage (Saves to folder "./chroma_db")
db = chromadb.PersistentClient(path="/Users/zero_skill/Documents/negotiation_DB")
chroma_collection = db.get_or_create_collection("my_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 2. High-Quality Loading
# SimpleDirectoryReader automatically handles PDF, JSON, DOCX, TXT.
# It uses file extensions to decide how to parse.
print("Loading files... this may take a moment but happens only once.")
documents = SimpleDirectoryReader("/Users/zero_skill/Documents/negotiation_info").load_data()

# 3. Build & Save Index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)

print("✅ Index saved to disk! You can now run queries instantly.")