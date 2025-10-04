from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    def __init__(self):
        print("🔄 Loading embedding model (all-mpnet-base-v2)...")
        # Best quality open-source model (768 dims)
        self.model = SentenceTransformer('all-mpnet-base-v2')
        print("✅ Embedding model loaded!")

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for text"""
        embedding = self.model.encode(text)
        return embedding.tolist()

    def calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

# Global instance
embedding_service = EmbeddingService()
