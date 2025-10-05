#!/usr/bin/env python3
"""
Test suite for chunking functionality
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.chunking import chunk_text, _chunk_with_gemini


class TestChunking:
    """Test cases for text chunking functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.short_text = "This is a short text that should not be chunked."
        self.long_text = """
        This is a much longer text that definitely needs to be chunked because it contains
        multiple paragraphs and sections. We need to test how the chunking algorithm handles
        longer content that exceeds the token limit.
        
        Here's another paragraph with more content to ensure we have enough text to trigger
        the chunking mechanism. This should help us verify that the semantic chunking works
        correctly and preserves the meaning of the text.
        
        And here's a third paragraph to make sure we have sufficient content for testing
        the chunking functionality with multiple sections and topics.
        """

    @patch('app.services.chunking.genai.GenerativeModel')
    def test_short_text_no_chunking(self, mock_genai_model):
        """Test that short text is returned as-is without chunking"""
        # Mock the token counting
        mock_model = Mock()
        mock_token_count = Mock()
        mock_token_count.total_tokens = 10  # Under limit
        mock_model.count_tokens.return_value = mock_token_count
        mock_genai_model.return_value = mock_model
        
        result = chunk_text(self.short_text, max_tokens=100)
        
        assert result == [self.short_text]
        mock_model.count_tokens.assert_called_once_with(self.short_text)

    @patch('app.services.chunking.genai.GenerativeModel')
    def test_long_text_triggers_chunking(self, mock_genai_model):
        """Test that long text triggers chunking"""
        # Mock the token counting to exceed limit
        mock_model = Mock()
        mock_token_count = Mock()
        mock_token_count.total_tokens = 3000  # Over limit
        mock_model.count_tokens.return_value = mock_token_count
        mock_genai_model.return_value = mock_model
        
        # Mock the chunking response
        mock_chunks = ["First chunk", "Second chunk", "Third chunk"]
        with patch('app.services.chunking._chunk_with_gemini', return_value=mock_chunks):
            result = chunk_text(self.long_text, max_tokens=1000)
        
        assert result == mock_chunks
        mock_model.count_tokens.assert_called_once_with(self.long_text)

    @patch('app.services.chunking.genai.GenerativeModel')
    def test_chunk_with_gemini_success(self, mock_genai_model):
        """Test successful chunking with Gemini"""
        # Mock the chunking model response
        mock_chunking_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"chunks": ["First semantic chunk", "Second semantic chunk"]}'
        mock_chunking_model.generate_content.return_value = mock_response
        
        # Mock the embedding model for token counting
        mock_embedding_model = Mock()
        mock_token_count = Mock()
        mock_token_count.total_tokens = 500  # Under limit
        mock_embedding_model.count_tokens.return_value = mock_token_count
        
        # Configure the mock to return different models
        def model_side_effect(model_name, **kwargs):
            if 'embedding' in model_name:
                return mock_embedding_model
            else:
                return mock_chunking_model
        
        mock_genai_model.side_effect = model_side_effect
        
        result = _chunk_with_gemini(self.long_text, max_tokens=1000)
        
        assert result == ["First semantic chunk", "Second semantic chunk"]
        mock_chunking_model.generate_content.assert_called_once()

    @patch('app.services.chunking.genai.GenerativeModel')
    def test_chunk_with_gemini_invalid_json(self, mock_genai_model):
        """Test handling of invalid JSON response from Gemini"""
        # Mock the chunking model to return invalid JSON
        mock_chunking_model = Mock()
        mock_response = Mock()
        mock_response.text = 'Invalid JSON response'
        mock_chunking_model.generate_content.return_value = mock_response
        
        # Mock the embedding model
        mock_embedding_model = Mock()
        mock_genai_model.return_value = mock_chunking_model
        
        with pytest.raises(ValueError, match="Gemini returned invalid JSON"):
            _chunk_with_gemini(self.long_text, max_tokens=1000)

    @patch('app.services.chunking.genai.GenerativeModel')
    def test_chunk_with_gemini_malformed_response(self, mock_genai_model):
        """Test handling of malformed response structure"""
        # Mock the chunking model to return malformed JSON
        mock_chunking_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"invalid_key": ["chunk1", "chunk2"]}'
        mock_chunking_model.generate_content.return_value = mock_response
        
        mock_genai_model.return_value = mock_chunking_model
        
        with pytest.raises(ValueError, match="Invalid response structure from Gemini"):
            _chunk_with_gemini(self.long_text, max_tokens=1000)

    @patch('app.services.chunking.genai.GenerativeModel')
    def test_chunk_with_gemini_recursive_chunking(self, mock_genai_model):
        """Test recursive chunking when a chunk exceeds token limit"""
        # Mock the chunking model
        mock_chunking_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"chunks": ["Very long chunk that exceeds limit", "Short chunk"]}'
        mock_chunking_model.generate_content.return_value = mock_response
        
        # Mock the embedding model for token counting
        mock_embedding_model = Mock()
        
        def token_count_side_effect(text):
            mock_count = Mock()
            if "Very long chunk" in text:
                mock_count.total_tokens = 1500  # Exceeds limit
            else:
                mock_count.total_tokens = 100   # Under limit
            return mock_count
        
        mock_embedding_model.count_tokens.side_effect = token_count_side_effect
        
        # Configure the mock to return different models
        def model_side_effect(model_name, **kwargs):
            if 'embedding' in model_name:
                return mock_embedding_model
            else:
                return mock_chunking_model
        
        mock_genai_model.side_effect = model_side_effect
        
        # Mock the recursive chunking call
        with patch('app.services.chunking._chunk_with_gemini') as mock_recursive:
            mock_recursive.return_value = ["Recursively chunked piece 1", "Recursively chunked piece 2"]
            
            result = _chunk_with_gemini(self.long_text, max_tokens=1000)
        
        assert result == ["Recursively chunked piece 1", "Recursively chunked piece 2", "Short chunk"]

    @patch('app.services.chunking.genai.GenerativeModel')
    def test_chunk_with_gemini_non_string_chunk(self, mock_genai_model):
        """Test handling of non-string chunks in response"""
        # Mock the chunking model to return non-string chunks
        mock_chunking_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"chunks": [123, "Valid chunk"]}'
        mock_chunking_model.generate_content.return_value = mock_response
        
        mock_genai_model.return_value = mock_chunking_model
        
        with pytest.raises(ValueError, match="Chunk 0 is not a string"):
            _chunk_with_gemini(self.long_text, max_tokens=1000)

    def test_empty_text(self):
        """Test handling of empty text"""
        with patch('app.services.chunking.genai.GenerativeModel') as mock_genai_model:
            mock_model = Mock()
            mock_token_count = Mock()
            mock_token_count.total_tokens = 0
            mock_model.count_tokens.return_value = mock_token_count
            mock_genai_model.return_value = mock_model
            
            result = chunk_text("", max_tokens=100)
            
            assert result == [""]

    def test_none_text(self):
        """Test handling of None text"""
        with patch('app.services.chunking.genai.GenerativeModel') as mock_genai_model:
            mock_model = Mock()
            mock_token_count = Mock()
            mock_token_count.total_tokens = 1
            mock_model.count_tokens.return_value = mock_token_count
            mock_genai_model.return_value = mock_model
            
            result = chunk_text(None, max_tokens=100)
            
            assert result == [None]


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
