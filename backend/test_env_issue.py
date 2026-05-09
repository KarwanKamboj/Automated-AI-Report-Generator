import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
print("ENV PATH:", env_path)
print("EXISTS:", os.path.exists(env_path))

result = load_dotenv(env_path)
print("LOAD RESULT:", result)

print("KEY:", os.getenv("GEMINI_API_KEY"))
