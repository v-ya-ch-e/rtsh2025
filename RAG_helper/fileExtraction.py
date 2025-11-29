# install: pip install llama-index llama-index-vector-stores-chroma chromadb llama-parse
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from llama_index.core import SimpleDirectoryReader
import chromadb
import constants
# 1. Setup Persistent Storage
db_path = "/Users/zero_skill/Documents/negotiation_DB"
db = chromadb.PersistentClient(path=db_path)
chroma_collection = db.create_collection(
    name="test_collection_1",
    embedding_function=OpenAIEmbeddingFunction(
        api_key=open("cred").read(),
        model_name="text-embedding-3-large"
    )
)
#vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
#storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 2. High-Quality Loading
# SimpleDirectoryReader automatically handles PDF, JSON, DOCX, TXT.
# It uses file extensions to decide how to parse.
print("Loading files... this may take a moment but happens only once.")
reader = SimpleDirectoryReader("/Users/zero_skill/Documents/negotiation_info")
llama_documents = reader.load_data()
docs_text = []
docs_ids = []
for i, doc in enumerate(llama_documents):
    # Extract the raw text
    docs_text.append(doc.text)

    # Create a unique ID (id+Index)
    # LlamaIndex docs have an internal ID, but making a readable one is often better
    # filename = doc.metadata.get('file_name', 'unknown_file')
    unique_id = f"id_{i}"
    docs_ids.append(unique_id)

chroma_collection.add(
    ids=docs_ids,
    documents=docs_text
)

print("✅ Index saved to disk! You can now run queries instantly.")