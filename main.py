"""
JSON CRUD 콘솔 애플리케이션 진입점.
"""

from json_store import init_store
from crud import (
    DB_PATH,
    create_user,
    read_all,
    read_by_id,
    search_by_name,
    update_user,
    delete_user,
    UPDATABLE_FIELDS,
)


# ──────────────────────────────────────────────
# 출력 헬퍼
# ──────────────────────────────────────────────

DIVIDER = "─" * 40


def print_user(user: dict) -> None:
    print(f"  ID {user['id']:>3} │ {user['name']} │ {user['age']}세 │ {user['city']}")


def print_list(users: list[dict]) -> None:
    if not users:
        print("  (결과 없음)")
        return
    print(f"  {'ID':>3}   이름       나이   도시")
    print("  " + "─" * 34)
    for u in users:
        print_user(u)


# ──────────────────────────────────────────────
# 입력 헬퍼
# ──────────────────────────────────────────────

def input_int(prompt: str) -> int | None:
    raw = input(prompt).strip()
    if raw.isdigit():
        return int(raw)
    print("  [오류] 숫자를 입력하세요.")
    return None


# ──────────────────────────────────────────────
# 메뉴 핸들러
# ──────────────────────────────────────────────

def handle_create() -> None:
    print(f"\n{DIVIDER}")
    print("[ 사용자 추가 ]")
    name = input("  이름: ").strip()
    if not name:
        print("  [오류] 이름을 입력하세요.")
        return
    age = input_int("  나이: ")
    if age is None:
        return
    city = input("  도시: ").strip()
    if not city:
        print("  [오류] 도시를 입력하세요.")
        return

    user = create_user(name, age, city)
    print(f"  ✔ 저장 완료 →", end=" ")
    print_user(user)


def handle_read() -> None:
    print(f"\n{DIVIDER}")
    print("[ 조회 ]  1) 전체목록  2) ID검색  3) 이름검색")
    choice = input("  선택: ").strip()

    if choice == "1":
        users = read_all()
        print(f"\n  총 {len(users)}건")
        print_list(users)

    elif choice == "2":
        uid = input_int("  조회할 ID: ")
        if uid is None:
            return
        user = read_by_id(uid)
        if user:
            print_user(user)
        else:
            print(f"  ID {uid} 를 찾을 수 없습니다.")

    elif choice == "3":
        keyword = input("  검색어: ").strip()
        results = search_by_name(keyword)
        print(f"\n  '{keyword}' 검색 결과 {len(results)}건")
        print_list(results)

    else:
        print("  [오류] 올바른 메뉴를 선택하세요.")


def handle_update() -> None:
    print(f"\n{DIVIDER}")
    print("[ 수정 ]")
    uid = input_int("  수정할 ID: ")
    if uid is None:
        return

    user = read_by_id(uid)
    if not user:
        print(f"  ID {uid} 를 찾을 수 없습니다.")
        return

    print("  현재 데이터:", end=" ")
    print_user(user)
    print(f"  수정 가능 필드: {', '.join(sorted(UPDATABLE_FIELDS))}")

    field = input("  수정할 필드: ").strip()
    if field not in UPDATABLE_FIELDS:
        print(f"  [오류] '{field}' 은(는) 수정할 수 없습니다.")
        return

    new_val: str | int = input(f"  새 값 ({field}): ").strip()
    if field == "age":
        if not new_val.isdigit():
            print("  [오류] 나이는 숫자여야 합니다.")
            return
        new_val = int(new_val)

    updated = update_user(uid, **{field: new_val})
    print("  ✔ 수정 완료 →", end=" ")
    print_user(updated)


def handle_delete() -> None:
    print(f"\n{DIVIDER}")
    print("[ 삭제 ]")
    uid = input_int("  삭제할 ID: ")
    if uid is None:
        return

    user = read_by_id(uid)
    if not user:
        print(f"  ID {uid} 를 찾을 수 없습니다.")
        return

    print("  삭제 대상:", end=" ")
    print_user(user)
    confirm = input("  정말 삭제하시겠습니까? (y/N): ").strip().lower()
    if confirm != "y":
        print("  삭제를 취소했습니다.")
        return

    delete_user(uid)
    print(f"  ✔ ID {uid} 삭제 완료.")


# ──────────────────────────────────────────────
# 메인 루프
# ──────────────────────────────────────────────

MENU = {
    "1": ("추가 (Create)", handle_create),
    "2": ("조회 (Read)",   handle_read),
    "3": ("수정 (Update)", handle_update),
    "4": ("삭제 (Delete)", handle_delete),
}


def main() -> None:
    init_store(DB_PATH)
    print("=" * 40)
    print("   JSON CRUD 콘솔 애플리케이션")
    print(f"   DB: {DB_PATH}")
    print("=" * 40)

    while True:
        print(f"\n{DIVIDER}")
        for key, (label, _) in MENU.items():
            print(f"  {key}) {label}")
        print("  0) 종료")
        choice = input("\n  메뉴 선택: ").strip()

        if choice == "0":
            print("  프로그램을 종료합니다.")
            break
        elif choice in MENU:
            MENU[choice][1]()
        else:
            print("  [오류] 0~4 중에서 선택하세요.")


if __name__ == "__main__":
    main()
