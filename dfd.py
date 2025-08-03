from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Safely load API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in a .env file or environment variables.")

openai = OpenAI(api_key=api_key)

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Is knee surgery covered in a 3-month-old health policy for a 46-year-old man in Pune?"}]
)

print(response.choices[0].message.content)
