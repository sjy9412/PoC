"""CRUD 기능 자동 검증 스크립트."""

import shutil
from pathlib import Path

# 테스트용 DB 경로로 교체
import crud
crud.DB_PATH = Path("data/test_users.json")

from json_store import init_store
from crud import create_user, read_all, read_by_id, search_by_name, update_user, delete_user

DB = crud.DB_PATH


def setup():
    if DB.exists():
        DB.unlink()
    init_store(DB)


def teardown():
    if DB.parent.exists():
        shutil.rmtree(DB.parent)


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        raise AssertionError(label)


def run():
    setup()
    print("\n=== Create ===")
    u1 = create_user("홍길동", 30, "서울")
    u2 = create_user("김철수", 25, "부산")
    u3 = create_user("이영희", 28, "서울")
    check("ID 자동 증가 (1, 2, 3)", [u1["id"], u2["id"], u3["id"]] == [1, 2, 3])
    check("이름 저장 확인", u1["name"] == "홍길동")

    print("\n=== Read ===")
    all_users = read_all()
    check("전체 조회 3건", len(all_users) == 3)

    found = read_by_id(2)
    check("ID=2 조회 성공", found is not None and found["name"] == "김철수")

    not_found = read_by_id(99)
    check("존재하지 않는 ID → None", not_found is None)

    results = search_by_name("길동")
    check("이름 검색 '길동' → 1건", len(results) == 1 and results[0]["id"] == 1)

    results2 = search_by_name("서울")  # city 가 아닌 name 검색이므로 0건이어야 함
    check("이름 검색 '서울' → 0건 (city 는 검색 안 함)", len(results2) == 0)

    print("\n=== Update ===")
    updated = update_user(1, age=31, city="인천")
    check("age 수정 확인", updated["age"] == 31)
    check("city 수정 확인", updated["city"] == "인천")

    reload = read_by_id(1)
    check("파일에 반영됐는지 확인", reload["city"] == "인천")

    not_updated = update_user(99, name="없음")
    check("존재하지 않는 ID 수정 → None", not_updated is None)

    try:
        update_user(1, invalid_field="x")
        check("허용되지 않은 필드 수정 → 예외", False)
    except ValueError:
        check("허용되지 않은 필드 수정 → ValueError 발생", True)

    print("\n=== Delete ===")
    result = delete_user(2)
    check("ID=2 삭제 성공 → True", result is True)
    check("삭제 후 전체 2건", len(read_all()) == 2)
    check("삭제된 ID 조회 → None", read_by_id(2) is None)

    result2 = delete_user(99)
    check("존재하지 않는 ID 삭제 → False", result2 is False)

    teardown()
    print("\n모든 테스트 통과.")


if __name__ == "__main__":
    run()
