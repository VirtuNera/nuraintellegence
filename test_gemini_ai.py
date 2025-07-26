"""
Test Gemini AI service integration
"""

import os
import json
import logging
from google import genai
from google.genai import types

def test_gemini_integration():
    """Test Gemini API integration"""
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        return
        
    print("✅ Gemini API key found")
    
    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        model = "gemini-2.5-flash"
        
        print("✅ Gemini client initialized")
        
        # Test simple prompt
        test_prompt = """
        You are Nura, an AI learning assistant. Provide a sample feedback for a student who scored 85% on a math quiz.
        
        Respond with JSON in this format:
        {
            "overall_assessment": "Brief assessment",
            "strengths": ["List of strengths"],
            "areas_for_improvement": ["Areas to work on"],
            "motivation_message": "Encouraging message"
        }
        """
        
        response = client.models.generate_content(
            model=model,
            contents=test_prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            print("✅ Gemini API call successful")
            result = json.loads(response.text)
            print("✅ JSON parsing successful")
            print("\n📋 Sample AI Response:")
            print(f"Assessment: {result.get('overall_assessment', 'N/A')}")
            print(f"Strengths: {result.get('strengths', [])}")
            print(f"Motivation: {result.get('motivation_message', 'N/A')}")
            
            return True
        else:
            print("❌ No response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini: {e}")
        return False

if __name__ == "__main__":
    test_gemini_integration()