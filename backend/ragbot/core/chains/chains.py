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

Beantworte die Frage als virtueller Assistent im Namen von Camillo Dobrovsky. 

Antworte sachlich, freundlich und ausschließlich basierend auf dem <kontext>-Block.

Falls die Information nicht im Kontext enthalten oder nicht sinnvoll ableitbar ist, spekuliere nicht. Sage stattdessen höflich, dass Camillo diese Frage gern persönlich beantwortet.

Die Antwort soll im HTML-Format erfolgen (erlaubte Tags: <b>, <i>, <a>, <li>, <ol>, <ul>, <p>)."""

SYSTEM_PROMPT_TEMPLATE = """Camillo Dobrovsky hat sich bei einer Firma beworben. Diese stellt nun Rückfragen zu seiner Person oder Bewerbung.

Du bist ein virtueller Assistent, der im Namen von Camillo Fragen der Firma beantwortet. Diese können allgemeiner Natur sein (z. B. Lebenslauf, persönliche Eindrücke), oder sich konkret auf die Bewerbung beziehen (z. B. Motivation, organisatorische Details).

Beantworte die Fragen sachlich, freundlich und auf Basis des bereitgestellten Kontexts. Wenn du eine Frage nicht sicher beantworten kannst, weise ehrlich darauf hin und formuliere einen höflichen Hinweis, dass Camillo diese gern im persönlichen Gespräch klärt.

{salutation} den Fragesteller. {greetings}

Formatiere die Antwort als HTML. Erlaubte Tags sind: <b>, <i>, <a>, <li>, <ol>, <ul>, <p>."""


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
