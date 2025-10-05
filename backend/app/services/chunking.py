import google.generativeai as genai
from typing import List
import json
import logging

logger = logging.getLogger(__name__)


def chunk_text(text: str, max_tokens: int = 2000) -> List[str]:
    """
    Chunk text into semantic pieces under the token limit.
    Uses Gemini for intelligent semantic chunking when needed.
    
    Args:
        text: The text to chunk
        max_tokens: Maximum tokens per chunk (default 2000)
    
    Returns:
        List of text chunks
    """
    # Initialize model for token counting
    embedding_model = genai.GenerativeModel('gemini-embedding-001')
    
    # Count tokens
    token_count = embedding_model.count_tokens(text).total_tokens
    
    # If within limit, return as-is
    if token_count <= max_tokens:
        return [text]
    
    # Use Gemini to semantically chunk the text
    return _chunk_with_gemini(text, max_tokens)


def _chunk_with_gemini(text: str, max_tokens: int) -> List[str]:
    """Use Gemini to semantically chunk text into smaller pieces."""
    
    # Use a more capable model for chunking logic
    chunking_model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={
            "response_mime_type": "application/json"
        }
    )
    
    prompt = f"""You are a text chunking assistant. Split the following text into semantic chunks.

REQUIREMENTS:
- Each chunk MUST be under {max_tokens} tokens
- Split at natural boundaries (paragraphs, sections, topics)
- Preserve meaning and context within each chunk
- Do NOT summarize or modify the text
- Return ONLY a JSON object with this exact structure:

{{
  "chunks": [
    "first chunk text here",
    "second chunk text here"
  ]
}}

TEXT TO CHUNK:
{text}"""
    
    try:
        response = chunking_model.generate_content(prompt)
        
        # Parse the JSON response
        result = json.loads(response.text)
        
        # Validate response structure
        if not isinstance(result, dict) or 'chunks' not in result:
            raise ValueError("Invalid response structure from Gemini")
        
        chunks = result['chunks']
        
        if not isinstance(chunks, list):
            raise ValueError("Chunks must be a list")
        
        # Verify each chunk is under the token limit
        embedding_model = genai.GenerativeModel('gemini-embedding-001')
        validated_chunks = []
        
        for i, chunk in enumerate(chunks):
            if not isinstance(chunk, str):
                raise ValueError(f"Chunk {i} is not a string")
            
            chunk_tokens = embedding_model.count_tokens(chunk).total_tokens
            
            if chunk_tokens > max_tokens:
                logger.warning(f"Chunk {i} exceeds token limit ({chunk_tokens} > {max_tokens}), re-chunking...")
                # Recursively chunk this piece
                validated_chunks.extend(_chunk_with_gemini(chunk, max_tokens))
            else:
                validated_chunks.append(chunk)
        
        return validated_chunks
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from Gemini: {e}")
        raise ValueError("Gemini returned invalid JSON")
    except Exception as e:
        logger.error(f"Error during chunking: {e}")
        raise
