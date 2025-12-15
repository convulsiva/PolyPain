from bot.infra.models import User


class UserRepository:
    async def get_or_create(
        self,
        chat_id: int,
        username: str | None,
        first_name: str | None,
    ) -> User:
        user, created = await User.get_or_create(
            id=chat_id,
            defaults={
                "username": username,
                "first_name": first_name,
            },
        )

        if not created:
            changed = False

            if user.username != username:
                user.username = username
                changed = True

            if user.first_name != first_name:
                user.first_name = first_name
                changed = True

            if changed:
                await user.save()

        return user

    async def set_group(self, chat_id: int, group: str) -> None:
        await User.filter(id=chat_id).update(group=group)

    async def get_group(self, chat_id: int) -> str | None:
        user = await User.filter(id=chat_id).first()
        return user.group if user else None

    async def count_all(self) -> int:
        return await User.all().count()

    async def count_with_group(self) -> int:
        return await User.filter(group__not_isnull=True).count()

    async def get_all_chat_ids(self) -> list[int]:
        return await User.all().values_list("id", flat=True)

    async def is_notify_enabled(self, chat_id: int) -> bool:
        user = await User.filter(id=chat_id).first()
        return bool(user and user.notify_enabled)

    async def set_notify(self, chat_id: int, enabled: bool) -> None:
        await User.filter(id=chat_id).update(notify_enabled=enabled)

    async def get_all_with_notifications(self) -> list[User]:
        return await User.filter(
            notify_enabled=True,
            group__not_isnull=True,
        )
