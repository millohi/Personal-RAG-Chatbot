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

{user_name} 
Beantworte die Frage nur basierend auf dem Kontext.
Falls die Antwort nicht im Kontext vorhanden ist, sage nichts Falsches."""

SYSTEM_PROMPT_TEMPLATE = """
Camillo Dobrovsky hat sich bei einer Firma beworben, welche nun Rückfragen zu Camillo und der Bewerbung hat. 
Du bist ein virtueller Assistent, der die Fragen über Camillo beantwortet. 
Beziehe dich **ausschließlich** auf den bereitgestellten Kontext über Camillo.
Wenn du eine Frage nicht beantworten kannst, sage dies ehrlich und weise darauf hin, dass Camillo Fragen gerne im persönlichen Gespräch beantwortet. 
Antworte sachlich, freundlich und {salutation} den Fragesteller. {greetings}
Formatiere die Antwort als HTML.
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
                          "salutation": itemgetter("salutation"),
                          "user_name": itemgetter("user_name"),
                          "greetings": itemgetter("greetings")} | RunnablePassthrough()

    prepare_context = {
        "context": lambda x: combine_documents(x['docs'], document_prompt, document_seperator),
        "question": itemgetter("question"),
        "salutation": itemgetter("salutation"),
        "user_name": itemgetter("user_name"),
        "greetings": itemgetter("greetings")
    }

    return retrieve_documents | prepare_context | llm_prompt | llm
