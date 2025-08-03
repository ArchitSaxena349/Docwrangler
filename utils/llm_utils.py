import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Safely load API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in a .env file or environment variables.")

# Initialize OpenAI client
openai = OpenAI(api_key=api_key)

def extract_entities(query_text):
    prompt = f"""
    Extract structured data from this query:

    "{query_text}"

    Return JSON with: age, gender, procedure, location, policy_duration.
    """
    res = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def decision_prompt(user_query, relevant_chunks):
    excerpts_text = "\n\n".join(c.page_content for c in relevant_chunks)

    prompt = f"""
    A user asked: "{user_query}"

    Based on the policy excerpts below, determine:
    - If the procedure is covered
    - Payout (if any)
    - Justification with clause references

    Excerpts:
    {excerpts_text}

    Return JSON with: decision, amount, justification (summary, referenced_clauses).
    """
    res = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()
