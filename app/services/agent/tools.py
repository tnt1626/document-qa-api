import uuid
import ollama
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ollama_client import client, GENERATE_MODEL_NAME
from app.services.rag.generator import OllamaConnectionError, OllamaModelNotFound

async def say_hi(name: str):
    return f"Hi {name}"

async def get_day():
    return "Tuesday"

async def get_secret():
    return "AGENT_TOOL_WORKED_928374"

TOOLS = {
    'say_hi': say_hi,
    'get_day': get_day,
    'get_secret': get_secret,
}

async def run_agent(
    quenstion: str,
    db: AsyncSession | None = None,
    document_id: uuid.UUID | None = None,
    max_loops: int = 8
):
    system_parts = [
        "You are an intelligent assistant that can search for and read document content.",
        "When the user asks about document content, use the tool to search before answering.",
        "Respond in Vietnamese, concisely, and base your answer on the information found.",
        "If no relevant information is found, state that clearly.",
    ]

    if document_id:
        system_parts.append(
            f"\nThe user is asking about the document with ID: {document_id}. "
            f"Prioritize using the search_document tool with this document_id."
        )
    
    system_prompt = "\n".join(system_parts)

    # Context Window
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": quenstion}
    ]

    loops = 0
    while loops < max_loops:
        try:
            response = await client.chat(
                # model=GENERATE_MODEL_NAME,
                model="llama3.1:latest",
                messages=messages,
                tools=[say_hi, get_day, get_secret],
            )
        except ollama.RequestError:
            raise OllamaConnectionError()
        except ollama.ResponseError as e:
            if e.status_code == 404:
                raise OllamaModelNotFound()
            raise
        except Exception as e:
            raise RuntimeError(f"Generate failed: {e}")

        messages.append(response.message)

        if not response.message.tool_calls:
            return response.message.content

        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            if not tool_name in TOOLS:
                messages.append({
                    "role": "tool", 
                    "tool_name": tool_name, 
                    "content": f"Tool {tool_name} not found"
                })
                continue

            try:
                result = await TOOLS[tool_name](**tool_call.function.arguments)
            except Exception as e:
                result = f"Error executing tool: {e}"
            messages.append({"role": "tool", "tool_name": tool_name, "content": str(result)})

        loops += 1

    return f"No answer from Agent with tool with {loops} loops\n"
        
if __name__ == "__main__":
    message = asyncio.run(run_agent(quenstion="What day is today?"))
    print(f"Message: {message}")