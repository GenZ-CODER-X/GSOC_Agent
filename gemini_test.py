from langchain_google_genai import ChatGoogleGenerativeAI
from core import config


llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    google_api_key=config.settings.gemini_api_key,
    temperature=0,
)

response = llm.invoke(
    "Tell me in one sentence why Python is useful for backend development."
)

print("MODEL OUTPUT:")
print(response.text)
