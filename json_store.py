"""
PoC json_poc.py 의 파일 I/O 함수를 그대로 유지하는 저장소 레이어.
"""

import json
from pathlib import Path


# ──────────────────────────────────────────────
# PoC 원본 함수 (변경 없음)
# ──────────────────────────────────────────────

def parse_json_string(raw: str) -> dict | list:
    """JSON 문자열을 Python 객체로 변환."""
    return json.loads(raw)


def load_json_file(path: str | Path) -> dict | list:
    """JSON 파일을 읽어 Python 객체로 반환."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json_file(data: dict | list, path: str | Path, indent: int = 2) -> None:
    """Python 객체를 JSON 파일로 저장."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def to_json_string(data: dict | list, indent: int | None = None) -> str:
    """Python 객체를 JSON 문자열로 직렬화."""
    return json.dumps(data, ensure_ascii=False, indent=indent)


# ──────────────────────────────────────────────
# 저장소 초기화 / 스토어 I/O
# ──────────────────────────────────────────────

def init_store(path: str | Path) -> None:
    """DB 파일이 없으면 초기 스토어로 생성."""
    p = Path(path)
    if not p.exists():
        save_json_file({"next_id": 1, "records": []}, p)


def load_store(path: str | Path) -> dict:
    """스토어 전체(next_id + records)를 반환."""
    return load_json_file(path)


def save_store(store: dict, path: str | Path) -> None:
    """스토어 전체를 파일에 저장."""
    save_json_file(store, path)


def load_records(path: str | Path) -> list[dict]:
    """저장된 레코드 목록만 반환."""
    return load_store(path)["records"]


def persist_records(records: list[dict], path: str | Path) -> None:
    """레코드 목록을 파일에 반영 (next_id는 유지)."""
    store = load_store(path)
    store["records"] = records
    save_store(store, path)
