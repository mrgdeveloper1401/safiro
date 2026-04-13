from clickhouse_connect import get_client
from django.conf import settings

def get_clickhouse_client():
    return get_client(
        host=settings.CLICKHOUSE_DB_HOST,
        port=settings.CLICKHOUSE_DB_PORT,
        username=settings.CLICKHOUSE_DB_USER,
        password=settings.CLICKHOUSE_DB_PASSWORD,
        database=settings.CLICKHOUSE_DB_DATABASE,
    )
