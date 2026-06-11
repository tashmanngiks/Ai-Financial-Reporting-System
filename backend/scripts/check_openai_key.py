import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

backend_dir = Path(__file__).resolve().parents[1]
load_dotenv(backend_dir / '.env')

key = (os.environ.get('OPENAI_API_KEY') or '').strip()
model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini').strip()

if not key:
    print('ERROR: OPENAI_API_KEY not found in backend/.env or environment')
    sys.exit(2)

try:
    client = OpenAI(api_key=key)
    models = client.models.list()
    model_count = len(models.data) if hasattr(models, 'data') else 'unknown'
    print(f'OK: authenticated — models returned: {model_count}')

    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': 'Reply with the single word: ok'}],
        max_tokens=10,
    )
    text = response.choices[0].message.content.strip()
    print(f'OK: chat completion with {model}: {text}')
    sys.exit(0)
except Exception as exc:
    print('ERROR: OpenAI test failed:', str(exc))
    sys.exit(3)
