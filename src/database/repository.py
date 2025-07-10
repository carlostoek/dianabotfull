class UserProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Optional[UserProgress]:
        result = await self.session.execute(select(UserProgress).filter_by(user_id=user_id))
        return result.scalar_one_or_none()

    async def update_progress(self, user_id: int, **kwargs) -> UserProgress:
        user_progress = await self.get_by_user_id(user_id)
        if not user_progress:
            raise ValueError(f"UserProgress for user_id {user_id} not found.")

        for key, value in kwargs.items():
            setattr(user_progress, key, value)
        
        await self.session.commit()
        await self.session.refresh(user_progress)
        return user_progress