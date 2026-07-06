from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.app.dependencies import get_session
from backend.app.schemas import CreateUserProfileRequest, UserProfileResponse
from backend.db.repositories import create_user_profile, get_user_profile, list_user_profiles
from backend.mcp_server.schemas import dump_user_profile

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("", response_model=UserProfileResponse)
async def post_profile(req: CreateUserProfileRequest, session: AsyncSession = Depends(get_session)):
    try:
        user = await create_user_profile(
            session,
            sex=req.sex,
            age=req.age,
            height_cm=req.height_cm,
            display_name=req.display_name,
            goal=req.goal,
            target_weight_kg=req.target_weight_kg
        )
        await session.commit()
        return dump_user_profile(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_profile(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await get_user_profile(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dump_user_profile(user)

@router.get("", response_model=List[UserProfileResponse])
async def list_profiles(session: AsyncSession = Depends(get_session)):
    users = await list_user_profiles(session)
    return [dump_user_profile(u) for u in users]
