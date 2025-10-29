from fastapi.exceptions import HTTPException

from app.shared.utils.db import SqlRunner


def get_server_private_key_encrypted(*, db: SqlRunner) -> bytes:
    """Get the encrypted server private key from the database."""
    row = db.query("""
        SELECT content
        FROM secrets
        WHERE name = 'server_private_key'
    """).first_row()

    if not row:
        raise HTTPException(
            status_code=500, detail="Server private key not found in database"
        )

    return bytes(row["content"])
