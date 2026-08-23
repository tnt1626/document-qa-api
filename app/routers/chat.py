import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.services.agent.tools import run_agent
from app.schemas import AgentQuery, AgentResponse

logger = logging.getLogger(__name__)

MAX_LOOPS = 8

agent_router = APIRouter(prefix='/agent')

@agent_router.post('/query', response_model=AgentResponse)
async def chat(
    payload: AgentQuery,
    db: AsyncSession = Depends(get_db),
):
    try:
        message = await run_agent(
            question=payload.question,
            chat_history=payload.chat_history,
            db=db,
            document_id=payload.document_id,
            max_loops=MAX_LOOPS
        )

        return {"answer": message}

    except RuntimeError as e:
        logger.error(f"Agent failed to run: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI service is temporarily unavailable, Please try again later."
        )