from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import json

load_dotenv()

llm = init_chat_model(model="gpt-4o-mini")

def load_design_tokens():
    with open("app/engine/design_tokens.json", "r") as f:
        return json.load(f)

design_tokens = load_design_tokens()