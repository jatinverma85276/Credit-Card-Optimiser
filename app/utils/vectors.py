from langchain_openai import OpenAIEmbeddings
import os

# Initialize the embedding model once
# 'text-embedding-3-small' is cheaper and faster than ada-002
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

def get_text_embedding(text: str) -> list:
    """
    Converts text concept into a vector.
    Example: "Coffee at Starbucks" -> [0.002, -0.015, ...]
    """
    # Clean newlines to ensure consistent vectors
    clean_text = text.replace("\n", " ").strip()
    return embedding_model.embed_query(clean_text)