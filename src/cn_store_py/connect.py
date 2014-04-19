from mongokit import Connection
from .models import Item, Source
from config import settings


def get_connection():
    Item.__database__ = settings.MONGO_DB
    Source.__database__ = settings.MONGO_DB

    connection = Connection(host=settings.MONGO_HOST)
    connection.register([Item, Source])

    return connection