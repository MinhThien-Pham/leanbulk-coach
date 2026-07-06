from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.dependencies import get_session
from backend.workflows.seed_demo_data import seed_demo_profile

router = APIRouter(prefix="/seed", tags=["seed"])

@router.post("/demo-profile")
async def post_seed_demo_profile(session: AsyncSession = Depends(get_session)):
    res = await seed_demo_profile(session)
    return res
