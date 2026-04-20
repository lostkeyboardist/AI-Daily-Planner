import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    st.error('API Key not found. Please check your .env file.')
    st.stop()

client = genai.Client(api_key=api_key)

def main():
    st.set_page_config(page_title="Your New Personal AI Assistant")
    st.title("Your New Personal AI Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I am your Context-Aware AI Planner. To save time and get a perfectly tuned schedule, please tell me your tasks, your current location, and any specific preferences (e.g., cravings for lunch, meeting types) all in one message!"}
        ]
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if prompt := st.chat_input("Type your tasks here..."):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        system_prompt = """Persona: You are a sharp, helpful friend who happens to be an incredible executive assistant. You're slightly witty but grounded. You speak naturally (using contractions like 'I'll' instead of 'I will').

Conversational Style: 
- Start with a brief, friendly 'Hey' or 'Alright,' and a one-sentence comment on the day (e.g., 'Bhopal is going to be a scorcher today, so stay hydrated!').
- Add very subtle, dry humor if a task or weather condition warrants it (e.g., 'Doing deep-focus coding in 40°C heat is a bold move—let's get that done before your brain melts.').

Core Directives:
- Context & Grounding: Identify the user's location, tasks, and preferences. Prioritize Google Search to check live weather and verify real venues.
- The Formatting: Keep the clean bolded time blocks: **10:00 AM - 12:00 PM**: Task.
- Advice: Keep the italicized reasoning, but make it sound like advice: *Advice: This gets your hardest work out of the way before the afternoon heat kicks in.*
- Hyperlinks: Always find real venues and hyperlinked them: [Venue Name](https://www.google.com/url?sa=E&source=gmail&q=https://www.google.com/maps/search/?api=1%26query=Venue+Name+City).
- Closing: End with a short, encouraging sign-off like 'Good luck with the move!' or 'Catch you later.'

Important: Never sound robotic. Avoid phrases like 'Allocating time for...' or 'Conducting the meeting...'. Use phrases like 'I've set aside time for...' or 'Let's knock out the...'."""
        
        full_prompt = f"{system_prompt}\n\nUser Input: {prompt}"
        
        with st.spinner('Optimizing your schedule...'):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        tools=[{"google_search": {}}]
                    )
                )
                assistant_reply = response.text
            except APIError as e:
                # Fallback handler for rate limits or other API errors
                if "429" in str(e):
                    st.error('System busy (Rate limit reached). Please wait 60 seconds and try again.')
                else:
                    st.error(f'API Error: {e}')
                st.stop()
        
        with st.chat_message("assistant"):
            st.write(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

if __name__ == "__main__":
    main()
