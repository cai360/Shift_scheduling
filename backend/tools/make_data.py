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
import json
import logging
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

logger = logging.getLogger(__name__)

NOW = datetime.now(BUSINESS_TZ)

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), ".make_data_manifest.json")


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

def create_users() -> tuple[list[User], list[int]]:
    """回傳 (all_users, created_user_ids)"""
    users = []
    new_users = []
    for u in USERS_DATA:
        existing = User.query.filter_by(email=u["email"]).first()
        if existing:
            logger.info("User already exists, skipping: %s", u["email"])
            users.append(existing)
            continue
        user = User(
            username=u["username"],
            email=u["email"],
            hash=AuthService.hash_password(u["password"]),
        )
        db.session.add(user)
        users.append(user)
        new_users.append(user)
        logger.info("Created user: %s", u["email"])
    db.session.flush()
    return users, [u.id for u in new_users]


def create_companies(users: list[User]) -> tuple[list[tuple[Company, User]], list[int], list[int]]:
    """建立公司並設定 owner，回傳 (companies_owners, created_company_ids, created_cu_ids)"""
    result = []
    new_company_ids = []
    new_cu_ids = []
    owner_cycle = [users[0], users[1]]  # Ansel, Joy 各當一間公司 owner，其餘循環

    for idx, c in enumerate(COMPANIES_DATA):
        existing = Company.query.filter_by(name=c["name"]).filter(
            Company.deleted_at.is_(None)
        ).first()
        if existing:
            logger.info("Company already exists, skipping: %s", c["name"])
            owner_cu = CompanyUser.query.filter_by(
                company_id=existing.id, role="owner"
            ).filter(CompanyUser.deleted_at.is_(None)).first()
            if not owner_cu:
                logger.error(
                    "Company '%s' has no active owner; cannot proceed with seed. "
                    "Please assign an owner manually before re-running.",
                    c["name"],
                )
                sys.exit(1)
            owner = User.query.filter_by(id=owner_cu.user_id).filter(
                User.deleted_at.is_(None)
            ).first()
            if not owner:
                logger.error(
                    "Company '%s' owner (user_id=%s) is missing or inactive; "
                    "cannot proceed with seed. Please assign an active owner manually.",
                    c["name"], owner_cu.user_id,
                )
                sys.exit(1)
            result.append((existing, owner))
            continue

        owner = owner_cycle[idx % len(owner_cycle)]
        company = Company(name=c["name"], description=c["description"])
        db.session.add(company)
        db.session.flush()
        new_company_ids.append(company.id)

        cu = CompanyUser(user_id=owner.id, company_id=company.id, role="owner")
        db.session.add(cu)
        db.session.flush()
        new_cu_ids.append(cu.id)

        result.append((company, owner))
        logger.info("Created company '%s' with owner: %s", c["name"], owner.username)

    return result, new_company_ids, new_cu_ids


def add_members(companies_owners: list[tuple[Company, User]], users: list[User]) -> list[int]:
    """
    分配成員（僅 Google / Apple 有額外成員，其餘公司只有 owner）：
      Google (0, owner: Ansel) → user01(manager), user02(employee), user03(employee)
      Apple  (1, owner: Joy)   → user01(employee), user04(manager), user05(employee)
    回傳 created_cu_ids
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

    new_cus = []
    for company_idx, user, role in memberships:
        company, owner = companies_owners[company_idx]
        # 跳過已是 owner 的人
        if user.id == owner.id:
            continue
        existing = CompanyUser.query.filter_by(
            company_id=company.id, user_id=user.id
        ).filter(CompanyUser.deleted_at.is_(None)).first()
        if existing:
            logger.info(
                "Member already exists, skipping: %s in '%s' (%s)",
                user.username, company.name, existing.role,
            )
            continue
        cu = CompanyUser(user_id=user.id, company_id=company.id, role=role)
        db.session.add(cu)
        new_cus.append(cu)
        logger.info("Added %s to '%s' as %s", user.username, company.name, role)

    db.session.flush()
    return [cu.id for cu in new_cus]


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
        logger.info("Created %d shifts for '%s'", len(shifts), company.name)

    db.session.flush()
    return all_shifts


def create_assignments(
    shifts: list[Shift],
    companies_owners: list[tuple[Company, User]],
) -> tuple[list[ShiftAssignment], list[int]]:
    """將員工分配到 Google 和 Apple 已發佈的班次（人數不填滿，指派人混合 owner/manager）
    回傳 (all_assignments, created_assignment_ids)"""
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
    logger.info("Created %d shift assignments", len(all_assignments))
    return all_assignments, [a.id for a in all_assignments]


def create_takeovers(assignments: list[ShiftAssignment]) -> list[int]:
    """在已分配的班次中建立幾筆交班申請（各種狀態，最多 8 筆）
    approver / responder 從 assignment 所屬公司的成員動態選取。
    回傳 created_takeover_ids"""
    if not assignments:
        return []

    statuses = ["pending", "approved", "rejected", "cancelled"]
    samples = assignments[:min(8, len(assignments))]
    new_takeovers = []

    for i, assignment in enumerate(samples):
        shift = db.session.get(Shift, assignment.shift_id)
        company_id = shift.company_id

        approver_cu = CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.role.in_(["owner", "manager"]),
            CompanyUser.deleted_at.is_(None),
        ).first()
        if not approver_cu:
            logger.warning(
                "Skipping takeover for assignment %s: no owner or manager found in company",
                str(assignment.id)[:8],
            )
            continue

        candidate_ids = [
            cu.user_id for cu in CompanyUser.query.filter(
                CompanyUser.company_id == company_id,
                CompanyUser.deleted_at.is_(None),
                CompanyUser.user_id != assignment.user_id,
            ).all()
        ]
        if not candidate_ids:
            logger.warning(
                "Skipping takeover for assignment %s: no other members available as responder",
                str(assignment.id)[:8],
            )
            continue

        status = statuses[i % len(statuses)]
        responder_id = random.choice(candidate_ids)
        respond_at = NOW - timedelta(hours=3) if status != "pending" else None
        approved_by = approver_cu.user_id if status == "approved" else None
        approved_at = NOW - timedelta(hours=2) if status == "approved" else None

        t = ShiftTakeover(
            assignment_id=assignment.id,
            requester_id=assignment.user_id,
            responder_id=responder_id if status != "pending" else None,
            respond_at=respond_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status=status,
        )
        db.session.add(t)
        new_takeovers.append(t)
        logger.info("Created takeover (%s) for assignment %s", status, str(assignment.id)[:8])

    db.session.flush()
    return [t.id for t in new_takeovers]


def create_unavailabilities(
    companies_owners: list[tuple[Company, User]],
    users: list[User],
) -> list[int]:
    """為 Google 和 Apple 的員工各產生不可用時段，回傳 created_unavailability_ids"""
    entries = [
        # (company_index, user, days_offset_start, days_offset_end)
        (0, users[2], 1,  3),   # user01 → Google 明後天不可用
        (0, users[3], -3, -1),  # user02 → Google 前幾天不可用（歷史記錄）
        (1, users[5], 2,  5),   # user04 → Apple 2~5天後不可用
        (1, users[6], -4, -2),  # user05 → Apple 前幾天不可用（歷史記錄）
    ]

    new_unavails = []
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
            logger.info(
                "Unavailability already exists, skipping: %s @ '%s'",
                user.username, company.name,
            )
            continue
        u = Unavailability(
            company_id=company.id,
            user_id=user.id,
            start_at=start,
            end_at=end,
        )
        db.session.add(u)
        new_unavails.append(u)
        logger.info(
            "Created unavailability: %s @ '%s' (%+d~%+d days)",
            user.username, company.name, start_offset, end_offset,
        )

    db.session.flush()
    return [u.id for u in new_unavails]


def create_leaves(
    companies_owners: list[tuple[Company, User]],
    users: list[User],
) -> list[int]:
    """為 Google 和 Apple 建立各種狀態的請假記錄，回傳 created_leave_ids"""
    leaves_spec = [
        # (company_idx, requester, leave_type, start_off, end_off, status, reason)
        (0, users[2], "annual",    3,  5, "pending",   "年假旅遊"),   # user01 → Google
        (0, users[3], "sick",     -5, -4, "approved",  "感冒發燒"),   # user02 → Google
        (0, users[4], "personal", -2, -1, "rejected",  "個人事務"),   # user03 → Google
        (1, users[5], "annual",    4,  6, "pending",   "家族旅行"),   # user04 → Apple
        (1, users[6], "sick",     -6, -5, "approved",  "發燒頭痛"),   # user05 → Apple
        (1, users[2], "personal",  2,  3, "pending",   "搬家"),       # user01 → Apple
    ]

    new_leaves = []
    for company_idx, requester, leave_type, s_off, e_off, status, reason in leaves_spec:
        company, owner = companies_owners[company_idx]
        manager_cu = CompanyUser.query.filter_by(
            company_id=company.id, role="manager"
        ).filter(CompanyUser.deleted_at.is_(None)).first()
        reviewer = (
            User.query.filter_by(id=manager_cu.user_id)
            .filter(User.deleted_at.is_(None))
            .first()
            if manager_cu else None
        ) or owner

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
        new_leaves.append(leave)
        logger.info(
            "Created leave (%s) for %s @ '%s': %s %+d~%+dd",
            status, requester.username, company.name, leave_type, s_off, e_off,
        )

    db.session.flush()
    return [l.id for l in new_leaves]


# ── 清空資料庫 ────────────────────────────────────────────────

_MANIFEST_REQUIRED_KEYS = [
    "user_ids", "company_ids", "company_user_ids",
    "shift_ids", "assignment_ids", "takeover_ids",
    "unavailability_ids", "leave_ids",
]


def _validate_manifest(manifest: object) -> None:
    if not isinstance(manifest, dict):
        raise ValueError(f"expected a JSON object, got {type(manifest).__name__}")
    for key in _MANIFEST_REQUIRED_KEYS:
        if key not in manifest:
            raise ValueError(f"missing required key: '{key}'")
        if not isinstance(manifest[key], list):
            raise ValueError(f"'{key}' must be a list, got {type(manifest[key]).__name__}")


def reset_db():
    logger.warning("Clearing all tables...")
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    logger.info("reset_db done")


def undo_seed():
    """只刪除 manifest 記錄的 ID，不動其他既有資料"""
    logger.info("Rolling back make_data seed (deleting manifest-tracked records only)...")

    if not os.path.exists(MANIFEST_PATH):
        logger.error(
            "Manifest file not found at %s. Cannot safely undo. "
            "Use --force-undo for a broad cleanup.",
            MANIFEST_PATH,
        )
        sys.exit(1)

    try:
        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(
            "Manifest file is invalid JSON (%s). Use --force-undo for a broad cleanup.", e
        )
        sys.exit(1)

    try:
        _validate_manifest(manifest)
    except ValueError as e:
        logger.error(
            "Manifest validation failed (%s). Use --force-undo for a broad cleanup.", e
        )
        sys.exit(1)

    takeover_ids       = manifest.get("takeover_ids", [])
    leave_ids          = manifest.get("leave_ids", [])
    unavailability_ids = manifest.get("unavailability_ids", [])
    assignment_ids     = manifest.get("assignment_ids", [])
    shift_ids          = manifest.get("shift_ids", [])
    cu_ids             = manifest.get("company_user_ids", [])
    company_ids        = manifest.get("company_ids", [])
    user_ids           = manifest.get("user_ids", [])

    try:
        deleted = ShiftTakeover.query.filter(
            ShiftTakeover.id.in_(takeover_ids)
        ).delete(synchronize_session=False)
        logger.info("Deleted ShiftTakeovers  : %d", deleted)

        deleted = Leave.query.filter(
            Leave.id.in_(leave_ids)
        ).delete(synchronize_session=False)
        logger.info("Deleted Leaves          : %d", deleted)

        deleted = Unavailability.query.filter(
            Unavailability.id.in_(unavailability_ids)
        ).delete(synchronize_session=False)
        logger.info("Deleted Unavailabilities: %d", deleted)

        deleted = ShiftAssignment.query.filter(
            ShiftAssignment.id.in_(assignment_ids)
        ).delete(synchronize_session=False)
        logger.info("Deleted ShiftAssignments: %d", deleted)

        deleted = Shift.query.filter(
            Shift.id.in_(shift_ids)
        ).delete(synchronize_session=False)
        logger.info("Deleted Shifts          : %d", deleted)

        deleted = CompanyUser.query.filter(
            CompanyUser.id.in_(cu_ids)
        ).delete(synchronize_session=False)
        logger.info("Deleted CompanyUsers    : %d", deleted)

        deleted = Company.query.filter(
            Company.id.in_(company_ids)
        ).delete(synchronize_session=False)
        logger.info("Deleted Companies       : %d", deleted)

        deleted = User.query.filter(
            User.id.in_(user_ids)
        ).delete(synchronize_session=False)
        logger.info("Deleted Users           : %d", deleted)

        db.session.commit()
        os.remove(MANIFEST_PATH)
        logger.info("Manifest deleted")
        logger.info("undo_seed done")
    except Exception as e:
        db.session.rollback()
        logger.error(
            "undo_seed failed (%s). Use --force-undo to clean up.", e
        )
        raise


def force_undo():
    """
    強制清除所有 make_data 定義的實體，以 user_ids 為核心涵蓋所有 FK 參照。
    用於舊資料殘留、undo_seed 因 FK 衝突失敗時的補救。
    """
    logger.warning("force_undo: forcibly clearing all make_data-defined records...")

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
    logger.info("Deleted ShiftTakeovers  : %d", deleted)

    # Leaves：user_id / reviewed_by / assigned_reviewer_id 任一為 seed user 的全清
    deleted = Leave.query.filter(
        Leave.user_id.in_(seed_user_ids) |
        Leave.reviewed_by.in_(seed_user_ids) |
        Leave.assigned_reviewer_id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    logger.info("Deleted Leaves          : %d", deleted)

    deleted = Unavailability.query.filter(
        Unavailability.user_id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    logger.info("Deleted Unavailabilities: %d", deleted)

    deleted = ShiftAssignment.query.filter(
        ShiftAssignment.id.in_(all_assignment_ids)
    ).delete(synchronize_session=False)
    logger.info("Deleted ShiftAssignments: %d", deleted)

    deleted = Shift.query.filter(
        Shift.company_id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    logger.info("Deleted Shifts          : %d", deleted)

    deleted = CompanyUser.query.filter(
        CompanyUser.company_id.in_(seed_company_ids) |
        CompanyUser.user_id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    logger.info("Deleted CompanyUsers    : %d", deleted)

    deleted = Company.query.filter(
        Company.id.in_(seed_company_ids)
    ).delete(synchronize_session=False)
    logger.info("Deleted Companies       : %d", deleted)

    deleted = User.query.filter(
        User.id.in_(seed_user_ids)
    ).delete(synchronize_session=False)
    logger.info("Deleted Users           : %d", deleted)

    db.session.commit()
    logger.info("force_undo done")


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

        if os.path.exists(MANIFEST_PATH):
            logger.info("Existing manifest found, running undo first...")
            try:
                undo_seed()
            except Exception as e:
                logger.error(
                    "Auto-undo failed (%s). Please run --force-undo first.", e
                )
                sys.exit(1)

        logger.info("=== [1/7] Creating Users ===")
        users, new_user_ids = create_users()

        logger.info("=== [2/7] Creating Companies ===")
        companies_owners, new_company_ids, new_owner_cu_ids = create_companies(users)

        logger.info("=== [3/7] Adding Members ===")
        new_member_cu_ids = add_members(companies_owners, users)

        logger.info("=== [4/7] Creating Shifts ===")
        shifts = create_shifts(companies_owners)

        logger.info("=== [5/7] Creating ShiftAssignments ===")
        assignments, new_assignment_ids = create_assignments(shifts, companies_owners)

        logger.info("=== [6/7] Creating ShiftTakeovers ===")
        new_takeover_ids = create_takeovers(assignments)

        logger.info("=== [7/7] Creating Unavailabilities & Leaves ===")
        new_unavailability_ids = create_unavailabilities(companies_owners, users)
        new_leave_ids = create_leaves(companies_owners, users)

        db.session.commit()

        manifest = {
            "created_at": NOW.isoformat(),
            "user_ids": [str(i) for i in new_user_ids],
            "company_ids": [str(i) for i in new_company_ids],
            "company_user_ids": [str(i) for i in new_owner_cu_ids + new_member_cu_ids],
            "shift_ids": [str(s.id) for s in shifts],
            "assignment_ids": [str(i) for i in new_assignment_ids],
            "takeover_ids": [str(i) for i in new_takeover_ids],
            "unavailability_ids": [str(i) for i in new_unavailability_ids],
            "leave_ids": [str(i) for i in new_leave_ids],
        }
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
        logger.info("Manifest written to %s", MANIFEST_PATH)

        logger.info("Make data complete!")
        _print_summary()


def _print_summary():
    logger.info("── Summary ───────────────────────────────────")
    logger.info("  Users        : %d", User.query.count())
    logger.info("  Companies    : %d", Company.query.filter(Company.deleted_at.is_(None)).count())
    logger.info("  CompanyUsers : %d", CompanyUser.query.filter(CompanyUser.deleted_at.is_(None)).count())
    logger.info("  Shifts       : %d", Shift.query.filter(Shift.deleted_at.is_(None)).count())
    logger.info("  Assignments  : %d", ShiftAssignment.query.filter(ShiftAssignment.deleted_at.is_(None)).count())
    logger.info("  Takeovers    : %d", ShiftTakeover.query.filter(ShiftTakeover.deleted_at.is_(None)).count())
    logger.info("  Unavail.     : %d", Unavailability.query.filter(Unavailability.deleted_at.is_(None)).count())
    logger.info("  Leaves       : %d", Leave.query.filter(Leave.deleted_at.is_(None)).count())
    logger.info("  Default accounts (password: root1234):")
    for u in User.query.all():
        logger.info("    %s", u.email)


if __name__ == "__main__":
    run_seed()
