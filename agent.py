import os
import google.generativeai as genai
from google.generativeai.types import RequestOptions
from google.api_core import retry
import tools  # <--- This imports the file you just pasted

# --- CONFIGURATION ---
# PASTE YOUR API KEY HERE
GOOGLE_API_KEY = "AIzaSyDMseP_f_ioCMv9qxGAQc_ulBlGZl3A87c"

genai.configure(api_key=GOOGLE_API_KEY)

# --- SYSTEM PROMPT ---
# We teach the AI how to use your specific tools here.
SYSTEM_INSTRUCTION = """
You are "Nova", an intelligent Customer Support Voice Agent for an e-commerce platform.

YOUR TOOLKIT:
1. `search_products`: Use this to find items. You can filter by category or max_price.
2. `get_order_status`: Use this to track orders. You NEED an Order ID (like 'O0001').
3. `get_policy_info`: Use this for questions about returns, refunds, or warranty.
4. `get_product_faq`: Use this when a user asks specific questions about a product's features (e.g., "Does the Luma camera have night vision?").

RULES:
1. **Voice Optimized:** Your answers will be spoken out loud. Keep them SHORT (max 2-3 sentences).
2. **No Hallucinations:** If `search_products` returns "No products found", tell the user exactly that. Do not invent products.
3. **Smart Filtering:** If the user says "Find me cheap shoes", call `search_products(query='shoes', max_price=50)`.
4. **Politeness:** If the user just says "Hello", greet them warmly without calling tools.
"""

class VoiceAgent:
    def __init__(self):
        print("--- Initializing AI Brain (Gemini 2.0 Flash) ---")
        
        # 1. Register the tools EXACTLY as defined in tools.py
        self.tools_list = [
            tools.search_products,
            tools.get_order_status,
            tools.get_policy_info,
            tools.get_product_faq
        ]

        # 2. Setup the Model
        # using 'gemini-1.5-flash' for maximum speed
        self.model = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            tools=self.tools_list,
            system_instruction=SYSTEM_INSTRUCTION
        )

        # 3. Start the Chat Session
        # Automatic function calling handles the DB queries for you
        self.chat_session = self.model.start_chat(
            enable_automatic_function_calling=True
        )

    def get_response(self, user_text):
        """
        Main entry point for the App.
        Input: "Where is order O0001?"
        Output: "Order O0001 was delivered on Friday."
        """
        try:
            # Retry policy helps if the API has a tiny hiccup
            response = self.chat_session.send_message(
                user_text,
                request_options=RequestOptions(retry=retry.Retry(initial=1.0, multiplier=2.0, maximum=10.0))
            )
            return response.text
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return "I am sorry, I am having trouble accessing the database right now."

# --- TESTING BLOCK (Run this file directly to test the Brain) ---
if __name__ == "__main__":
    agent = VoiceAgent()
    print("\n💬 Chat with Nova (Type 'quit' to exit)\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        
        response = agent.get_response(user_input)
        print(f"Nova: {response}")
