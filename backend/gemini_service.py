import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        # Use the current available model from your test results
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def get_voice_response(self, text: str) -> str:
        """Get response for voice assistant queries - SDLC topics only, no code"""
        try:
            prompt = f"""You are a specialized SDLC (Software Development Life Cycle) assistant. You ONLY answer questions related to software development, SDLC processes, methodologies, best practices, tools, and concepts.

IMPORTANT RULES:
1. If the question is NOT related to software development, politely decline and say: "I can only help with software development and SDLC related questions. Please ask me about development processes, methodologies, or best practices."

2. NEVER provide code snippets or programming code in your response. Instead, explain the PROCESS, STEPS, METHODOLOGY, or CONCEPT behind it.

3. Focus on explaining:
   - Processes and workflows
   - Methodologies (Agile, Scrum, Waterfall, etc.)
   - Best practices and principles
   - Tools and their purposes
   - Concepts and definitions
   - Steps to follow

4. Keep responses concise (2-4 sentences) and suitable for voice output.

User Question: '{text}'

Your Response:"""
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

gemini_service = GeminiService()