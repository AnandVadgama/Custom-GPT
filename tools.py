import math
from contextvars import ContextVar
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from database import save_memory, search_memory
from rag import retrieve_from_rag



load_dotenv()


CURRENT_THREAD_ID = ContextVar("current_thread_id", default="default")


def set_current_thread_id(thread_id: str):
    CURRENT_THREAD_ID.set(thread_id)


web_search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="advanced"
)


@tool
def calculator(expression: str) -> str:
    """
    Useful for simple math calculations.
    Input should be a valid math expression.
    Example: 2 + 2, math.sqrt(16), 10 * 5
    """

    try:
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum
        }

        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)

    except Exception as e:
        return f"Calculation error: {str(e)}"
    


@tool
def search_uploaded_documents(query: str) -> str:
    """
    Search uploaded documents for relevant information.
    Use this when the user asks about uploaded PDFs, DOCX, TXT, notes, files, or documents.
    Also use it for references such as "it", "this", "the file", or "the document" when a file was uploaded earlier in the current chat.
    If content is returned, use it to answer the user's question instead of asking for the file again.
    """

    return retrieve_from_rag(
        query=query,
        thread_id=CURRENT_THREAD_ID.get()
    )




@tool
def remember_this(memory: str) -> str:
    """
    Save an important user preference or fact into long-term memory.
    Use this when the user asks you to remember something.
    """

    return save_memory(
        thread_id=CURRENT_THREAD_ID.get(),
        memory=memory
    )



@tool
def recall_memory(query: str) -> str:
    """
    Recall saved long-term memories about the user or this conversation.
    """

    return search_memory(
        thread_id=CURRENT_THREAD_ID.get(),
        query=query
    )





tools = [
    calculator,
    search_uploaded_documents,
    remember_this,
    recall_memory,
    web_search
]