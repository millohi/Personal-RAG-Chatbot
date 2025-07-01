from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
    PromptTemplate, format_document
from langchain_core.runnables import RunnablePassthrough

INSTRUCTION_PROMPT_TEMPLATE = """<kontext>
{context}
</kontext>

<frage>
{question}
</frage>

Beantworte die Frage nur basierend auf dem Kontext.
Falls die Antwort nicht im Kontext vorhanden ist, sage nichts Falsches."""

SYSTEM_PROMPT_TEMPLATE = """
Camillo Dobrovsky hat sich bei einer Firma beworben, welche nun Rückfragen zu Camillo und der Bewerbung hat. 
Du bist ein virtueller Assistent, der die Fragen über Camillo beantwortet. 
Beziehe dich **ausschließlich** auf die bereitgestellten Kontext aus der Wissensdatenbank.
Wenn du eine Frage nicht beantworten kannst, sag ehrlich: 
„Dazu liegen mir keine Informationen vor, Camillo beantwortet die Frage aber gerne im persönlichen Gespräch.“
Antworte sachlich, freundlich und in der „Du“-Form. Beantworte nur die Frage und gib keine zusätzlichen Infos.
"""

def combine_documents(docs, document_prompt, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def build_chain(llm, retriever):
    llm_prompt = ChatPromptTemplate([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE),
        HumanMessagePromptTemplate.from_template(INSTRUCTION_PROMPT_TEMPLATE),
    ])
    document_prompt = PromptTemplate.from_template("{page_content}")
    document_seperator = "\n\n"

    retrieve_documents = {"docs": itemgetter("question") | retriever,
                          "question": itemgetter("question"),
                          "user_group": itemgetter("user_group")} | RunnablePassthrough()

    prepare_context = {
        "context": lambda x: combine_documents(x['docs'], document_prompt, document_seperator),
        "question": itemgetter("question"),
        "user_group": itemgetter("user_group"),
    }

    return retrieve_documents | prepare_context | llm_prompt | llm