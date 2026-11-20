from langchain_core.messages import HumanMessage, SystemMessage, convert_to_messages

from store import LARGE, azure_chat, azure_embeddings, open_store

RETRIEVAL_K = 10

SYSTEM_PROMPT = """
You are a knowledgeable, friendly assistant representing the company Insurellm.
You are chatting with a user about Insurellm.
If relevant, use the given context to answer any question.
If you don't know the answer, say so.
Context:
{context}
"""

embeddings = azure_embeddings()
vectorstore = open_store(LARGE, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVAL_K})
llm = azure_chat(temperature=0)


def fetch_context(question):
    return retriever.invoke(question)


def combined_question(question, history):
    prior = []
    for message in history or []:
        if message.get("role") == "user" and isinstance(message.get("content"), str):
            prior.append(message["content"])
    return "\n".join(prior + [question])


def answer_question(question, history=None):
    history = history or []
    docs = fetch_context(combined_question(question, history))
    context = "\n\n".join(doc.page_content for doc in docs)
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(context=context))]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    return response.content, docs
