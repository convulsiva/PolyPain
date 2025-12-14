from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=64, null=True)
    first_name = fields.CharField(max_length=64, null=True)
    group = fields.CharField(max_length=32, null=True)
    notify_enabled = fields.BooleanField(default=True)

    class Meta:
        table = "users"


class Admin(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=64, null=True)

    class Meta:
        table = "admins"
