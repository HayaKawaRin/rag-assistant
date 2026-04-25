# def build_answer_prompt(question: str, context: str) -> str:
#     return f"""Use the context below to answer the question.

# Question:
# {question}

# Context:
# {context}

# Instructions:
# - Answer only from the context.
# - If the context is insufficient, say that clearly.
# - Keep the answer concise and informative.
# """