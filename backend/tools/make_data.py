"""
make_data script - 自動產生測試資料

用法:
    python tools/make_data.py                # 新增資料（保留既有資料）
    python tools/make_data.py --reset        # 清空所有DB
    python tools/make_data.py --undo         # 只刪除本 make_data 批次新增的資料
    python tools/make_data.py --force-undo   # 強制清除（undo 遇到 FK 衝突時使用）
"""

import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import BUSINESS_TZ
from app.extensions import db
from app.models import (
    User, Company, CompanyUser,
    Shift, ShiftAssignment, ShiftTakeover,
    Unavailability, Leave,
)
from app.services.auth_service import AuthService

NOW = datetime.now(BUSINESS_TZ)


# ── 種子資料定義 ──────────────────────────────────────────────

USERS_DATA = [
    {"username": "Ansel",  "email": "ansel@example.com",   "password": "root1234"},
    {"username": "Joy",    "email": "joy@example.com",     "password": "root1234"},
    {"username": "user01", "email": "user01@example.com",  "password": "root1234"},
    {"username": "user02", "email": "user02@example.com",  "password": "root1234"},
    {"username": "user03", "email": "user03@example.com",  "password": "root1234"},
    {"username": "user04", "email": "user04@example.com",  "password": "root1234"},
    {"username": "user05", "email": "user05@example.com",  "password": "root1234"},
]

COMPANIES_DATA = [
    {"name": "Google",  "description": "軟體開發公司"},
    {"name": "Apple",   "description": "全球最大蘋果銷售公司"},
    {"name": "Amazon",  "description": "全球最大的網際網路線上零售商之一"},
    {"name": "Netflix", "description": "提供網路隨選串流影片的OTT服務公司"},
    {"name": "Nvidia",  "description": "以設計和銷售圖形處理器（GPU）為主的無廠半導體公司"},
    {"name": "Meta",    "description": "全球最大的社群媒體與科技公司之一"},
]


def _dt(days_offset: int, hour: int, minute: int = 0) -> datetime:
    """產生相對於今天的 timezone-aware datetime"""
    base = NOW.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return base + timedelta(days=days_offset)


# ── 主要建立函式 ──────────────────────────────────────────────

def create_users() -> list[User]:
    users = []
    for u in USERS_DATA:
        existing = User.query.filter_by(email=u["email"]).first()
        if existing:
            print(f"  [skip] User {u['email']} 已存在")
            users.append(existing)
            continue
        user = User(
            username=u["username"],
            email=u["email"],
            hash=AuthService.hash_password(u["password"]),
        )
        db.session.add(user)
        users.append(user)
        print(f"  [+] User {u['email']}")
    db.session.flush()
    return users


def create_companies(users: list[User]) -> list[tuple[Company, User]]:
    """建立公司並設定 owner，回傳 (company, owner) 的列表"""
    result = []
    owner_cycle = [users[0], users[1]]  # Ansel, Joy 各當一間公司 owner，其餘循環

    for idx, c in enumerate(COMPANIES_DATA):
        existing = Company.query.filter_by(name=c["name"]).filter(
            Company.deleted_at.is_(None)
        ).first()
        if existing:
            print(f"  [skip] Company '{c['name']}' 已存在")
            owner_cu = CompanyUser.query.filter_by(
                company_id=existing.id, role="owner"
            ).filter(CompanyUser.deleted_at.is_(None)).first()
            owner = User.query.get(owner_cu.user_id) if owner_cu else users[idx % len(owner_cycle)]
            result.append((existing, owner))
            continue

        owner = owner_cycle[idx % len(owner_cycle)]
        company = Company(name=c["name"], description=c["description"])
        db.session.add(company)
        db.session.flush()

        cu = CompanyUser(user_id=owner.id, company_id=company.id, role="owner")
        db.session.add(cu)
        db.session.flush()

        result.append((company, owner))
        print(f"  [+] Company '{c['name']}' (owner: {owner.username})")

    return result


def add_members(companies_owners: list[tuple[Company, User]], users: list[User]):
    """
    分配成員（僅 Google / Apple 有額外成員，其餘公司只有 owner）：
      Google (0, owner: Ansel) → user01(manager), user02(employee), user03(employee)
      Apple  (1, owner: Joy)   → user01(employee), user04(manager), user05(employee)
    """
    memberships = [
        # (company_index, user, role)
        (0, users[2], "manager"),   # user01 → Google manager
        (0, users[3], "employee"),  # user02 → Google employee
        (0, users[4], "employee"),  # user03 → Google employee
        (1, users[2], "employee"),  # user01 → Apple employee
        (1, users[5], "manager"),   # user04 → Apple manager
        (1, users[6], "employee"),  # user05 → Apple employee
    ]

    for company_idx, user, role in memberships:
        company, owner = companies_owners[company_idx]
        # 跳過已是 owner 的人
        if user.id == owner.id:
            continue
        existing = CompanyUser.query.filter_by(
            company_id=company.id, user_id=user.id
        ).filter(CompanyUser.deleted_at.is_(None)).first()
        if existing:
            print(f"  [skip] {user.username} 已在 '{company.name}' ({existing.role})")
            continue
        cu = CompanyUser(user_id=user.id, company_id=company.id, role=role)
        db.session.add(cu)
        print(f"  [+] {user.username} → '{company.name}' as {role}")

    db.session.flush()


def create_shifts(companies_owners: list[tuple[Company, User]]) -> list[Shift]:
    """為 Google 和 Apple 各產生過去 / 當週 / 未來的班次"""
    all_shifts = []

    for company, _ in companies_owners[:2]:  # Google (0), Apple (1)
        shifts = []

        # 已發佈的過去班次（-4 ~ -1 天，2 時段）
        for day in range(-4, 0):
            for start_h, end_h in [(9, 13), (17, 21)]:
                s = Shift(
                    company_id=company.id,
                    capacity=random.randint(2, 3),
                    start_at=_dt(day, start_h),
                    end_at=_dt(day, end_h),
                    published_at=_dt(day - 1, 8),
                )
                db.session.add(s)
                shifts.append(s)

        # 本週班次（0 ~ 3 天，2 時段）- 部分已發佈
        for day in range(0, 4):
            for start_h, end_h in [(8, 12), (16, 20)]:
                published = _dt(day - 2, 9) if day <= 2 else None
                s = Shift(
                    company_id=company.id,
                    capacity=random.randint(2, 4),
                    start_at=_dt(day, start_h),
                    end_at=_dt(day, end_h),
                    published_at=published,
                )
                db.session.add(s)
                shifts.append(s)

        # 未來班次（7 ~ 10 天，1 時段，草稿）
        for day in range(7, 11):
            s = Shift(
                company_id=company.id,
                capacity=random.randint(2, 3),
                start_at=_dt(day, 9),
                end_at=_dt(day, 13),
                published_at=None,
            )
            db.session.add(s)
            shifts.append(s)

        all_shifts.extend(shifts)
        print(f"  [+] {len(shifts)} 個班次 for '{company.name}'")

    db.session.flush()
    return all_shifts


def create_assignments(
    shifts: list[Shift],
    companies_owners: list[tuple[Company, User]],
) -> list[ShiftAssignment]:
    """將員工分配到 Google 和 Apple 已發佈的班次（人數不填滿，指派人混合 owner/manager）"""
    all_assignments = []

    for company, owner in companies_owners[:2]:  # Google (0), Apple (1)
        members = CompanyUser.query.filter_by(
            company_id=company.id
        ).filter(CompanyUser.deleted_at.is_(None)).all()
        member_ids = [m.user_id for m in members]

        manager_cu = CompanyUser.query.filter_by(
            company_id=company.id, role="manager"
        ).filter(CompanyUser.deleted_at.is_(None)).first()
        assigner_ids = [owner.id] + ([manager_cu.user_id] if manager_cu else [])

        published_shifts = [
            s for s in shifts
            if s.company_id == company.id and s.published_at is not None
        ]

        for shift in published_shifts:
            # 隨機指派人數，不強制填滿 capacity
            k = random.randint(1, min(len(member_ids), shift.capacity))
            assignees = random.sample(member_ids, k=k)
            assigned_by = random.choice(assigner_ids)

            for uid in assignees:
                exists = ShiftAssignment.query.filter_by(
                    shift_id=shift.id, user_id=uid
                ).filter(ShiftAssignment.deleted_at.is_(None)).first()
                if exists:
                    continue
                a = ShiftAssignment(
                    shift_id=shift.id,
                    user_id=uid,
                    assigned_by=assigned_by,
                )
                db.session.add(a)
                all_assignments.append(a)

    db.session.flush()
    print(f"  [+] {len(all_assignments)} 個班次分配")
    return all_assignments


def create_takeovers(assignments: list[ShiftAssignment], users: list[User]):
    """在已分配的班次中建立幾筆交班申請（各種狀態，最多 8 筆）"""
    if not assignments:
        return

    ansel, joy, user01, user02 = users[0], users[1], users[2], users[3]
    statuses = ["pending", "approved", "rejected", "cancelled"]
    samples = assignments[:min(8, len(assignments))]

    for i, assignment in enumerate(samples):
        status = statuses[i % len(statuses)]
        responder = user01 if i % 2 == 0 else user02
        respond_at = NOW - timedelta(hours=3) if status != "pending" else None
        # 前 4 筆由 Ansel 審核，後 4 筆由 Joy 審核
        approved_by = (ansel if i < 4 else joy) if status == "approved" else None
        approved_at = NOW - timedelta(hours=2) if status == "approved" else None

        t = ShiftTakeover(
            assignment_id=assignment.id,
            requester_id=assignment.user_id,
            responder_id=responder.id if status != "pending" else None,
            respond_at=respond_at,
            approved_by=approved_by.id if approved_by else None,
            approved_at=approved_at,
            status=status,
        )
        db.session.add(t)
        print(f"  [+] Takeover ({status}) for assignment {str(assignment.id)[:8]}…")

    db.session.flush()


def create_unavailabilities(
    companies_owners: list[tuple[Company, User]],
    users: list[User],
):
    """為 Google 和 Apple 的員工各產生不可用時段"""
    entries = [
        # (company_index, user, days_offset_start, days_offset_end)
        (0, users[2], 1,  3),   # user01 → Google 明後天不可用
        (0, users[3], -3, -1),  # user02 → Google 前幾天不可用（歷史記錄）
        (1, users[5], 2,  5),   # user04 → Apple 2~5天後不可用
        (1, users[6], -4, -2),  # user05 → Apple 前幾天不可用（歷史記錄）
    ]

    for company_idx, user, start_offset, end_offset in entries:
        company, _ = companies_owners[company_idx]
        start = _dt(start_offset, 0)
        end   = _dt(end_offset, 23, 59)
        existing = Unavailability.query.filter_by(
            company_id=company.id,
            user_id=user.id,
            start_at=start,
            end_at=end,
        ).filter(Unavailability.deleted_at.is_(None)).first()
        if existing:
            print(f"  [skip] Unavailability for {user.username} @ '{company.name}' 已存在")
            continue
        u = Unavailability(
            company_id=company.id,
            user_id=user.id,
            start_at=start,
            end_at=end,
        )
        db.session.add(u)
        print(f"  [+] Unavailability: {user.username} @ '{company.name}' ({start_offset}~{end_offset} days)")

    db.session.flush()


def create_leaves(
    companies_owners: list[tuple[Company, User]],
    users: list[User],
):
    """為 Google 和 Apple 建立各種狀態的請假記錄"""
    leaves_spec = [
        # (company_idx, requester, leave_type, start_off, end_off, status, reason)
        (0, users[2], "annual",    3,  5, "pending",   "年假旅遊"),   # user01 → Google
        (0, users[3], "sick",     -5, -4, "approved",  "感冒發燒"),   # user02 → Google
        (0, users[4], "personal", -2, -1, "rejected",  "個人事務"),   # user03 → Google
        (1, users[5], "annual",    4,  6, "pending",   "家族旅行"),   # user04 → Apple
        (1, users[6], "sick",     -6, -5, "approved",  "發燒頭痛"),   # user05 → Apple
        (1, users[2], "personal",  2,  3, "pending",   "搬家"),       # user01 → Apple
    ]

    for company_idx, requester, leave_type, s_off, e_off, status, reason in leaves_spec:
        company, owner = companies_owners[company_idx]
        manager_cu = CompanyUser.query.filter_by(
            company_id=company.id, role="manager"
        ).filter(CompanyUser.deleted_at.is_(None)).first()
        reviewer = User.query.get(manager_cu.user_id) if manager_cu else owner

        start = _dt(s_off, 9)
        end   = _dt(e_off, 18)

        reviewed_at   = (NOW - timedelta(days=1)) if status in ("approved", "rejected") else None
        reviewed_by   = reviewer.id               if status in ("approved", "rejected") else None
        reject_reason = "不符請假規定"             if status == "rejected"              else None

        leave = Leave(
            company_id=company.id,
            user_id=requester.id,
            status=status,
            start_at=start,
            end_at=end,
            leave_type=leave_type,
            reason=reason,
            reject_reason=reject_reason,
            assigned_reviewer_id=reviewer.id,
            reviewed_by=reviewed_by,
            reviewed_at=reviewed_at,
        )
        db.session.add(leave)
        print(f"  [+] Leave ({status}) {requester.username} @ '{company.name}': {leave_type} {s_off}~{e_off}d")

    db.session.flush()


# ── 清空資料庫 ────────────────────────────────────────────────

def reset_db():
    print("⚠️  清空所有資料表...")
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    print("   Done.\n")


def undo_seed():
    """只刪除本 make_data 批次新增的資料，不動其他既有資料"""
    print("↩️  回滾 make_data 資料（僅刪除 make_data 定義的實體）...")

    seed_emails = [u["email"] for u in USERS_DATA]
    seed_company_names = [c["name"] for c in COMPANIES_DATA]

    seed_users = User.query.filter(User.email.in_(seed_emails)).all()
    seed_user_ids = [u.id for u in seed_users]

    seed_companies = Company.query.filter(
        Company.name.in_(seed_company_names)
    ).all()
    seed_company_ids = [c.id for c in seed_companies]

    # 找出 make_data 公司的所有班次 id（用於串接刪除）
    seed_shift_ids = [
        s.id for s in Shift.query.filter(
            Shift.company_id.in_(seed_company_ids)
        ).all()
    ]
    seed_assignment_ids = [
        a.id for a in ShiftAssignment.query.filter(
            ShiftAssignment.shift_id.in_(seed_shift_ids)
        ).all()
    ]

    # 依外鍵反向順序刪除
    deleted = ShiftTakeover.query.filter(
        ShiftTakeover.assignment_id.in_(seed_assignment_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] ShiftTakeovers  : {deleted}")

    deleted = Leave.query.filter(
        Leave.company_id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Leaves          : {deleted}")

    deleted = Unavailability.query.filter(
        Unavailability.company_id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Unavailabilities: {deleted}")

    deleted = ShiftAssignment.query.filter(
        ShiftAssignment.shift_id.in_(seed_shift_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] ShiftAssignments: {deleted}")

    deleted = Shift.query.filter(
        Shift.company_id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Shifts          : {deleted}")

    deleted = CompanyUser.query.filter(
        CompanyUser.company_id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] CompanyUsers    : {deleted}")

    deleted = Company.query.filter(
        Company.id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Companies       : {deleted}")

    # 清除 seed users 在其他公司的殘留 CompanyUser（不在 seed_company_ids 內的）
    deleted = CompanyUser.query.filter(
        CompanyUser.user_id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    if deleted:
        print(f"  [-] CompanyUsers (殘留): {deleted}")

    # 清除其他公司中 reviewer/assigned_reviewer 為 seed user 的 Leave
    # （避免刪 user 時 FK SET NULL 觸發 ck_approval_consistency 約束）
    for field in (Leave.reviewed_by, Leave.assigned_reviewer_id):
        deleted = Leave.query.filter(
            field.in_(seed_user_ids)
        ).delete(synchronize_session=False)
        if deleted:
            print(f"  [-] Leaves (reviewer 殘留): {deleted}")

    deleted = User.query.filter(
        User.id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Users           : {deleted}")

    db.session.commit()
    print("   Done.\n")


def force_undo():
    """
    強制清除所有 make_data 定義的實體，以 user_ids 為核心涵蓋所有 FK 參照。
    用於舊資料殘留、undo_seed 因 FK 衝突失敗時的補救。
    """
    print("🔧 force_undo：強制清除 make_data 殘留資料...")

    seed_emails        = [u["email"] for u in USERS_DATA]
    seed_company_names = [c["name"]  for c in COMPANIES_DATA]

    seed_users       = User.query.filter(User.email.in_(seed_emails)).all()
    seed_user_ids    = [u.id for u in seed_users]
    seed_companies   = Company.query.filter(Company.name.in_(seed_company_names)).all()
    seed_company_ids = [c.id for c in seed_companies]

    # assignment ids：seed user 被指派的 + seed 公司班次上的所有 assignment
    seed_shift_ids = [
        s.id for s in Shift.query.filter(
            Shift.company_id.in_(seed_company_ids)
        ).all()
    ]
    all_assignment_ids = list({
        a.id
        for a in ShiftAssignment.query.filter(
            ShiftAssignment.user_id.in_(seed_user_ids) |
            ShiftAssignment.shift_id.in_(seed_shift_ids)
        ).all()
    })

    deleted = ShiftTakeover.query.filter(
        ShiftTakeover.assignment_id.in_(all_assignment_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] ShiftTakeovers  : {deleted}")

    # Leaves：user_id / reviewed_by / assigned_reviewer_id 任一為 seed user 的全清
    deleted = Leave.query.filter(
        Leave.user_id.in_(seed_user_ids) |
        Leave.reviewed_by.in_(seed_user_ids) |
        Leave.assigned_reviewer_id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Leaves          : {deleted}")

    deleted = Unavailability.query.filter(
        Unavailability.user_id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Unavailabilities: {deleted}")

    deleted = ShiftAssignment.query.filter(
        ShiftAssignment.id.in_(all_assignment_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] ShiftAssignments: {deleted}")

    deleted = Shift.query.filter(
        Shift.company_id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Shifts          : {deleted}")

    deleted = CompanyUser.query.filter(
        CompanyUser.company_id.in_(seed_company_ids) |
        CompanyUser.user_id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] CompanyUsers    : {deleted}")

    deleted = Company.query.filter(
        Company.id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Companies       : {deleted}")

    deleted = User.query.filter(
        User.id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    print(f"  [-] Users           : {deleted}")

    db.session.commit()
    print("   Done.\n")


# ── 入口 ──────────────────────────────────────────────────────

def run_seed():
    app = create_app()
    with app.app_context():
        if "--force-undo" in sys.argv:
            force_undo()
            return

        if "--undo" in sys.argv:
            undo_seed()
            return

        if "--reset" in sys.argv:
            confirm = input("確定要清空DB?[Y/N]：")
            if confirm in ["y", "Y"]:
                reset_db()
            return

        print("=== [1/7] 建立 Users ===")
        users = create_users()

        print("\n=== [2/7] 建立 Companies ===")
        companies_owners = create_companies(users)

        print("\n=== [3/7] 新增成員 ===")
        add_members(companies_owners, users)

        print("\n=== [4/7] 建立 Shifts ===")
        shifts = create_shifts(companies_owners)

        print("\n=== [5/7] 建立 ShiftAssignments ===")
        assignments = create_assignments(shifts, companies_owners)

        print("\n=== [6/7] 建立 ShiftTakeovers ===")
        create_takeovers(assignments, users)

        print("\n=== [7/7] 建立 Unavailabilities & Leaves ===")
        create_unavailabilities(companies_owners, users)
        create_leaves(companies_owners, users)

        db.session.commit()
        print("\n✅ Make data 完成！")
        _print_summary(users, companies_owners, shifts, assignments)


def _print_summary(users, companies_owners, shifts, assignments):
    print("\n── 資料摘要 ──────────────────────────────────")
    print(f"  Users        : {User.query.count()}")
    print(f"  Companies    : {Company.query.filter(Company.deleted_at.is_(None)).count()}")
    print(f"  CompanyUsers : {CompanyUser.query.filter(CompanyUser.deleted_at.is_(None)).count()}")
    print(f"  Shifts       : {Shift.query.filter(Shift.deleted_at.is_(None)).count()}")
    print(f"  Assignments  : {ShiftAssignment.query.filter(ShiftAssignment.deleted_at.is_(None)).count()}")
    print(f"  Takeovers    : {ShiftTakeover.query.filter(ShiftTakeover.deleted_at.is_(None)).count()}")
    print(f"  Unavail.     : {Unavailability.query.filter(Unavailability.deleted_at.is_(None)).count()}")
    print(f"  Leaves       : {Leave.query.filter(Leave.deleted_at.is_(None)).count()}")
    print("──────────────────────────────────────────────")
    print("\n預設帳號（密碼皆為 root1234）：")
    for u in User.query.all():
        print(f"  {u.email}")


if __name__ == "__main__":
    run_seed()
