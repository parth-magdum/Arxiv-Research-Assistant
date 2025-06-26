from langchain_community.chat_models import ChatOpenAI

def get_llm(api_key, api_base, model):
    return ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base=api_base,
        model=model,
        temperature=0.2
    )
#     model=os.getenv("GROQ_MODEL"),
#     temperature=0.2
# )
