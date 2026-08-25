import os
import json
import uuid
import asyncio
from groq import AsyncGroq
from sqlalchemy import select
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import ChatMessage, AgentResponse, ThoughtStep, ToolCallDetail  
from app.database import SessionLocal
from app.models import Chunk, Document
from app.services.rag.retriever import retrieve_vec

load_dotenv()

client = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": (
                "Search for relevant text chunks in a specific document "
                "based on the user's query. "
                "Use this tool when the user asks about the content of an uploaded document."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The UUID of the document to search within.",
                    },
                    "query": {
                        "type": "string",
                        "description": "The query or search term to look for in the document.",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "The number of relevant text chunks to return. Defaults to 5.",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_documents",
            "description": (
                "List all documents that have been uploaded to the system. "
                "Use this tool when the user wants to know what documents are available "
                "or needs to find a document_id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of documents to return. Defaults to 20.",
                        "default": 20,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_full_document",
            "description": (
                "Retrieve the full content of a document. "
                "Use this tool when you need to read the entire document text instead of "
                "just searching for relevant chunks. Only use for short documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The UUID of the document to retrieve the full content for.",
                    },
                },
                "required": ["document_id"],
            },
        },
    },
]

async def execute_tool(
    tool_name: str,
    tool_input: dict,
    db: AsyncSession,
) -> str:
    """
    Execute a tool and return the result as a string.
    LLM only receives strings — format clearly.
    """
    if not db:
        return "Error: No database connection available to execute query."
 
    if tool_name == "search_document":
        document_id_str = tool_input["document_id"]
        query = tool_input["query"]
        top_k = tool_input.get("top_k", 5)

        doc_uuid = None
        doc = None

        if document_id_str:
            try:
                doc_uuid = uuid.UUID(document_id_str)
            except ValueError:
                return f"Error: '{document_id_str}' is not a valid UUID."
 
            # Check if the document exists
            doc = await db.scalar(select(Document).where(Document.id == doc_uuid))
            if not doc:
                return f"Error: Document with ID '{document_id_str}' not found."
 
        # Use retrieve_vec() available in the repository
        chunks: list[Chunk] = await retrieve_vec(query, doc_uuid, top_k, db)
 
        if not chunks:
            return "No relevant text chunks found for this query."

        result_lines = []

        if doc_uuid:
            result_lines.append(f"Found {len(chunks)} relevant chunks in '{doc.filename}':\n")
            for i, chunk in enumerate(chunks, 1):
                result_lines.append(f"[Chunk {i}]\n{chunk.content}\n")
        else:
            result_lines.append(f"Found {len(chunks)} relevant chunks across all documents:\n")
            for i, chunk in enumerate(chunks, 1):
                filename = await db.scalar(select(Document.filename).where(Document.id == chunk.document_id))
                result_lines.append(
                    f"[Chunk {i}] (From Document: '{filename}' | ID: {chunk.document_id})\n"
                    f"{chunk.content}\n"
                )
 
        return "\n".join(result_lines)
 
    elif tool_name == "list_documents":
        limit = tool_input.get("limit", 20)
        docs = (
            await db.scalars(
                select(Document)
                .order_by(Document.created_at.desc())
                .limit(limit)
            )
        ).all()
 
        if not docs:
            return "No documents have been uploaded to the system yet."
 
        lines = [f"The system has {len(docs)} documents:\n"]
        for doc in docs:
            lines.append(
                f"- ID: {doc.id}\n"
                f"  Filename: {doc.filename}\n"
                f"  Uploaded at: {doc.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            )
        return "\n".join(lines)
 
    elif tool_name == "get_full_document":
        document_id_str = tool_input["document_id"]
 
        try:
            doc_uuid = uuid.UUID(document_id_str)
        except ValueError:
            return f"Error: '{document_id_str}' is not a valid UUID."
 
        doc = await db.scalar(select(Document).where(Document.id == doc_uuid))
        if not doc:
            return f"Error: Document with ID '{document_id_str}' not found."
 
        content = doc.content
        # Limit to avoid context window overflow
        if len(content) > 5_000:
            content = content[:5_000] + "\n\n[... content truncated due to length ...]"
 
        return f"Full content of '{doc.filename}':\n\n{content}"
 
    else:
        return f"Error: Tool '{tool_name}' is not recognized."



async def run_agent(
    question: str,
    chat_history: list[ChatMessage] | None = None,
    db: AsyncSession | None = None,
    document_id: uuid.UUID | None = None,
    max_loops: int = 8
) -> AgentResponse:
    """_summary_

    Args:
        question (str): the query of user
        chat_history (list[ChatMessage] | None, optional): all messages before user's query. Defaults to None.
        db (AsyncSession | None, optional): database session. Defaults to None.
        document_id (uuid.UUID | None, optional): the if of document that user want to query. Defaults to None.
        max_loops (int, optional): number of interation that agent try to execute tools. Defaults to 8.

    Returns:
        str: response of agent in text
    """
    system_parts = [
        "You are an intelligent assistant that can search for and read document content.",
        "When the user asks about document content, use the tool to search before answering.",
        "Respond in English, concisely, and base your answer on the information found.",
        "If no relevant information is found, state that clearly.",
    ]

    if document_id:
        system_parts.append(
            f"\nThe user is asking about the document with ID: {document_id}. "
            f"Prioritize using the search_document tool with this document_id."
        )
    
    system_prompt = "\n".join(system_parts)

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    if chat_history:
        for chat in chat_history:
            messages.append(chat.model_dump())

    messages.append({"role": "user", "content": question})

    thought_steps: list[ThoughtStep] = []

    loops = 0
    while loops < max_loops:
        tool_calls: list[ToolCallDetail] = []
        try:
            response = await client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=messages,
                tools=TOOLS,
            )
        except Exception as e:
            raise RuntimeError(f"Generate failed: {e}")

        messages.append(response.choices[0].message)

        if not response.choices[0].message.tool_calls:
            thought_steps.append(ThoughtStep(
                loop_index=loops,
                token=response.usage.total_tokens,
                thought=response.choices[0].message.content,
                tool_calls=tool_calls
            ))
            return AgentResponse(
                answer=response.choices[0].message.content or "",
                thought_steps=thought_steps
            )

        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)

            result = await execute_tool(
                tool_name=tool_name,
                tool_input=tool_input,
                db=db
            )

            tool_calls.append(ToolCallDetail(
                id=tool_call.id,
                name=tool_name,
                arguments=tool_input,
                result=str(result)
            ))

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        thought_steps.append(ThoughtStep(
            loop_index=loops,
            token=response.usage.total_tokens,
            thought=response.choices[0].message.content,
            tool_calls=tool_calls
        ))

        loops += 1

    return AgentResponse(
        answer=f"No answer from Agent with tool with {loops} loops\n",
        thought_steps=thought_steps
    )

async def main():
    async with SessionLocal() as session:
        message = await run_agent(question="Which document in db?", db=session)

    return message
        
if __name__ == "__main__":
    message = asyncio.run(main())
    print(f"Message: {message}")