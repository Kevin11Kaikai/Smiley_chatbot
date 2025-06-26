import os
from openai import OpenAI

# Create an OpenAI client instance (API key should be set via environment variable for security)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def refine_text(original_text, user_profile, tone="casual_friendly"): # original_text is the text to be refined, user_profile is the profile of the user, tone is the tone of the message

    # Construct the prompt for the GPT model, instructing it to rewrite the message for the user's profile and tone
    prompt = f"""
You are an expert in youth communication, acting as a friendly and empathetic chatbot assistant. Your task is to rewrite the following formal text to make it engaging and relatable for a specific teenager.

**Teenager's Profile:**
- Age: {user_profile.get("age", "a teenager")}
- Gender: {user_profile.get("gender", "a user")}
- Interests: {user_profile.get("interests", "various topics")}
- Identity Context: The user identifies as {user_profile.get("race_ethnicity", "")} and {user_profile.get("sexual_identity", "")}. Be mindful, inclusive, and positive in your language.

**Instructions:**
- Adapt the tone to be {tone.replace("_", " ")}.
- If the user is into gaming, feel free to use light gaming metaphors. If they are into art, use creative analogies.
- Keep the core message of the original text intact.
- IMPORTANT: Return ONLY the rewritten message.

**Original Text:**
\"\"\"{original_text}\"\"\"

**Rewritten Message:**
""" # prompt is the prompt for the GPT model
    try:
        # Call the OpenAI API to get the refined message
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        # Extract the content of the response
        refined_text = response.choices[0].message.content.strip()
        
        # Clean up any potential debug prefixes from the response
        if "Original message:" in refined_text:
            # Extract only the rewritten part if the model returns extra text
            parts = refined_text.split("Rewritten message:")
            if len(parts) > 1:
                refined_text = parts[1].strip()
            else:
                refined_text = original_text
        
        return refined_text
    except Exception as e:
        # Print the error for debugging and return the original text to prevent crashes
        print(f"Error during OpenAI API call: {e}")
        return original_text