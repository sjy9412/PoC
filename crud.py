"""
CRUD 비즈니스 로직 레이어.
json_store 의 I/O 함수를 통해서만 파일에 접근한다.
"""

from pathlib import Path
from json_store import load_records, persist_records

DB_PATH = Path("data/users.json")


# ──────────────────────────────────────────────
# Create
# ──────────────────────────────────────────────

def create_user(name: str, age: int, city: str) -> dict:
    """새 사용자를 생성하고 저장 후 반환."""
    records = load_records(DB_PATH)

    next_id = max((r["id"] for r in records), default=0) + 1
    user = {"id": next_id, "name": name, "age": age, "city": city}

    records.append(user)
    persist_records(records, DB_PATH)
    return user


# ──────────────────────────────────────────────
# Read
# ──────────────────────────────────────────────

def read_all() -> list[dict]:
    """전체 사용자 목록 반환."""
    return load_records(DB_PATH)


def read_by_id(user_id: int) -> dict | None:
    """ID로 단일 사용자 검색. 없으면 None."""
    return next((r for r in load_records(DB_PATH) if r["id"] == user_id), None)


def search_by_name(keyword: str) -> list[dict]:
    """이름에 키워드가 포함된 사용자 목록 반환."""
    return [r for r in load_records(DB_PATH) if keyword in r["name"]]


# ──────────────────────────────────────────────
# Update
# ──────────────────────────────────────────────

UPDATABLE_FIELDS = {"name", "age", "city"}


def update_user(user_id: int, **fields) -> dict | None:
    """지정한 ID의 사용자 필드를 수정. 성공 시 갱신된 레코드 반환."""
    invalid = set(fields) - UPDATABLE_FIELDS
    if invalid:
        raise ValueError(f"수정 불가 필드: {invalid}")

    records = load_records(DB_PATH)
    for record in records:
        if record["id"] == user_id:
            record.update(fields)
            persist_records(records, DB_PATH)
            return record

    return None


# ──────────────────────────────────────────────
# Delete
# ──────────────────────────────────────────────

def delete_user(user_id: int) -> bool:
    """지정한 ID의 사용자를 삭제. 성공 여부 반환."""
    records = load_records(DB_PATH)
    filtered = [r for r in records if r["id"] != user_id]

    if len(filtered) == len(records):
        return False

    persist_records(filtered, DB_PATH)
    return True
