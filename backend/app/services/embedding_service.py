import os
import numpy as np
import google.generativeai as genai
from typing import Union, List

class EmbeddingService:
    """
    Embedding service using Google's Gemini gemini-embedding-001 model.

    Features:
    - Supports embedding text, code, and any string content
    - Uses gemini-embedding-001 (768 dimensions)
    - Configurable output dimensionality
    - Handles both single strings and lists of strings
    - Compatible with external chunking services
    """

    def __init__(self):
        print("🔄 Initializing Gemini embedding service (gemini-embedding-001)...")

        # Get API key from config
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError("gemini_api_key not found in configuration")

        # Initialize Gemini client
        genai.configure(api_key=api_key)
        self.model = 'gemini-embedding-001'

        print("✅ Gemini embedding service initialized!")

    def generate_embedding(
        self,
        text: Union[str, List[str]],
        output_dimensionality: int = None
    ) -> Union[list[float], List[list[float]]]:
        """
        Generate embedding vector(s) for text/code content.

        Args:
            text: Single string or list of strings to embed
            output_dimensionality: Optional dimension reduction (e.g., 256, 512)

        Returns:
            Single embedding list or list of embedding lists
        """
        try:
            # Handle single string vs list
            is_single = isinstance(text, str)
            contents = text if not is_single else [text]

            # Generate embeddings using Gemini API
            embeddings = []
            for content in contents:
                result = genai.embed_content(
                    model=self.model,
                    content=content,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])

            # Return single embedding if single string input
            return embeddings[0] if is_single else embeddings

        except Exception as e:
            print(f"❌ Error generating embedding: {str(e)}")
            raise

    def calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between -1 and 1 (higher = more similar)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        # Handle zero vectors
        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

    def embed_batch(
        self,
        texts: List[str],
        output_dimensionality: int = None
    ) -> List[list[float]]:
        """
        Batch embed multiple texts efficiently.

        Args:
            texts: List of strings to embed
            output_dimensionality: Optional dimension reduction

        Returns:
            List of embedding vectors
        """
        return self.generate_embedding(texts, output_dimensionality)

# Global instance
embedding_service = EmbeddingService()
