from bot.infra.models import Admin


class AdminRepository:
    async def is_admin(self, user_id: int) -> bool:
        return await Admin.filter(id=user_id).exists()

    async def add_admin(self, user_id: int, username: str | None = None) -> None:
        await Admin.get_or_create(
            id=user_id,
            defaults={"username": username},
        )

    async def remove_admin(self, user_id: int) -> None:
        await Admin.filter(id=user_id).delete()

    async def get_all_admins(self) -> list[Admin]:
        return await Admin.all()
