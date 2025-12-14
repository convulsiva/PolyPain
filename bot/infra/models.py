from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=64, null=True)
    first_name = fields.CharField(max_length=64, null=True)
    group = fields.CharField(max_length=32, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"


class Admin(Model):
    id = fields.IntField(pk=True)  # user_id
    username = fields.CharField(max_length=64, null=True)
    added_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "admins"
