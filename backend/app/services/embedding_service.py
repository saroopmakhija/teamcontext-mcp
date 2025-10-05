import os
import numpy as np
from google import genai
from typing import Union, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)
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
            # Prepare config if dimensionality specified
            config = None
            if output_dimensionality:
                from google.genai import types
                config = types.EmbedContentConfig(output_dimensionality=output_dimensionality)

            # Handle single string vs list
            is_single = isinstance(text, str)
            contents = text if not is_single else [text]

            # Generate embeddings
            response = self.client.models.embed_content(
                model=self.model,
                contents=contents,
                config=config
            )

            # Extract embeddings from response
            if hasattr(response, 'embeddings'):
                embeddings = [emb.values for emb in response.embeddings]
            else:
                # Fallback for different response structure
                embeddings = response.get('embeddings', [])
                embeddings = [emb.get('values', []) for emb in embeddings]

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
