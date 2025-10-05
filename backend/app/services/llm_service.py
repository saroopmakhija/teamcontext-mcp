import os
from google import genai
from google.genai import types
from typing import List, Dict, Generator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMService:
    """
    LLM service using Google's Gemini Flash 2.0 for chat completions.

    Features:
    - Chat completion with context injection (RAG)
    - Streaming support for real-time responses
    - Conversation history management
    - System prompts for context-aware responses
    """

    def __init__(self):
        print("🔄 Initializing Gemini Flash 2.0 LLM service...")

        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash-exp'

        print("✅ Gemini Flash 2.0 LLM service initialized!")

    def generate_rag_prompt(
        self,
        user_message: str,
        context_chunks: List[Dict],
        project_name: str = "this project"
    ) -> str:
        """
        Create a RAG prompt by injecting retrieved context into the user message.

        Args:
            user_message: The user's question/message
            context_chunks: List of relevant context chunks from vector DB
            project_name: Name of the project for context

        Returns:
            Formatted prompt with context injection
        """
        if not context_chunks:
            return f"""You are a helpful AI assistant for {project_name}.

User question: {user_message}

Note: No relevant context was found in the project knowledge base. Please provide a helpful response based on your general knowledge, but mention that you don't have specific project context for this question."""

        # Build context section
        context_section = "# Relevant Project Context\n\n"
        for i, chunk in enumerate(context_chunks, 1):
            similarity = chunk.get('similarity_score', 0)
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            source = metadata.get('source', 'unknown')

            context_section += f"## Context {i} (Relevance: {similarity:.2%})\n"
            context_section += f"Source: {source}\n"
            context_section += f"Content:\n{content}\n\n"

        # Build final prompt
        prompt = f"""You are a helpful AI assistant for {project_name}. You have access to the project's knowledge base and conversation history.

{context_section}

# Instructions
- Answer the user's question using the provided context above
- If the context contains relevant information, cite it in your response
- If the context doesn't fully answer the question, use your general knowledge but mention this
- Be concise and helpful
- If asked about implementation details, provide code examples when relevant

# User Question
{user_message}

# Response
"""
        return prompt

    def chat_completion(
        self,
        message: str,
        history: List[Dict] = None,
        system_prompt: str = None
    ) -> str:
        """
        Generate a chat completion response.

        Args:
            message: User's message (can be RAG-enhanced prompt)
            history: Previous conversation history
            system_prompt: Optional system prompt

        Returns:
            AI response text
        """
        try:
            # Build conversation history
            chat_history = []

            if history:
                for msg in history:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    chat_history.append(
                        types.Content(
                            role=role,
                            parts=[types.Part(text=content)]
                        )
                    )

            # Create chat session
            config = None
            if system_prompt:
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt
                )

            chat = self.client.chats.create(
                model=self.model,
                config=config,
                history=chat_history
            )

            # Send message and get response
            response = chat.send_message(message=message)

            return response.text

        except Exception as e:
            print(f"❌ Error generating chat completion: {str(e)}")
            raise

    def chat_completion_stream(
        self,
        message: str,
        history: List[Dict] = None,
        system_prompt: str = None
    ) -> Generator[str, None, None]:
        """
        Generate a streaming chat completion response.

        Args:
            message: User's message (can be RAG-enhanced prompt)
            history: Previous conversation history
            system_prompt: Optional system prompt

        Yields:
            Text chunks as they're generated
        """
        try:
            # Build conversation history
            chat_history = []

            if history:
                for msg in history:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    chat_history.append(
                        types.Content(
                            role=role,
                            parts=[types.Part(text=content)]
                        )
                    )

            # Create chat session
            config = None
            if system_prompt:
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt
                )

            chat = self.client.chats.create(
                model=self.model,
                config=config,
                history=chat_history
            )

            # Stream response
            response_stream = chat.send_message_stream(message=message)

            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"❌ Error generating streaming chat completion: {str(e)}")
            raise

# Global instance
llm_service = LLMService()
