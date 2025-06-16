import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client
client = OpenAI(api_key=api_key)


def ask_forensicgpt(prompt: str) -> str:
    """
    Sends a prompt to OpenAI's GPT model and returns a response.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[
                {
                    "role": "system",
                    "content": "You are a forensic expert specializing in blood spatter analysis.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
