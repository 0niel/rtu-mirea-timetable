from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine


def formation_query_for_kill_connections_to_db(db_name: str) -> str:
    query = text(
        "SELECT pg_terminate_backend(pg_stat_activity.pid)"
        "FROM pg_stat_activity "
        f"WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid();"
    )
    return query


async def create_test_db(db_url: str, db_name: str) -> None:
    default_engine = AsyncEngine(create_engine(db_url, isolation_level="AUTOCOMMIT"))
    async with default_engine.connect() as default_conn:
        await default_conn.execute(text(f"CREATE DATABASE {db_name}"))
    await default_engine.dispose()


async def drop_test_db(db_url: str, db_name_for_delete: str) -> None:
    default_engine = AsyncEngine(create_engine(db_url, isolation_level="AUTOCOMMIT"))
    async with default_engine.connect() as default_conn:
        await default_conn.execute(formation_query_for_kill_connections_to_db(db_name_for_delete))
        await default_conn.execute(text(f"DROP DATABASE IF EXISTS {db_name_for_delete}"))
    await default_engine.dispose()
