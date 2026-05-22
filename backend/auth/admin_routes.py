from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth.dependencies import require_admin
from auth.schemas import ALLOWED_ROLES, ApproveUserRequest, UpdateRoleRequest, UserResponse
from auth.services import approve_user, get_user_by_id, list_users, reject_user, update_user_role
from security.audit import log_event

router = APIRouter(prefix="/admin", tags=["Admin"])


def _client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _user_payload(user) -> UserResponse:
    return UserResponse(**user.public_dict())


@router.get("/users", response_model=list[UserResponse])
async def list_all_users(
    request: Request,
    status_filter: str | None = None,
    admin=Depends(require_admin),
):
    users = list_users(approval_status=status_filter)
    log_event(admin.id, "ADMIN_LIST_USERS", ip=_client_ip(request), metadata={"filter": status_filter})
    return [_user_payload(u) for u in users]


@router.post("/users/{user_id}/approve", response_model=UserResponse)
async def approve_employee(
    user_id: str,
    body: ApproveUserRequest,
    request: Request,
    admin=Depends(require_admin),
):
    role = body.role.strip().lower()
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported role.")
    if role == "admin" and admin.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot assign admin role.")
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    try:
        user = approve_user(user_id, admin.id, role, body.department)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    log_event(
        admin.id,
        "ADMIN_APPROVE_USER",
        ip=_client_ip(request),
        metadata={"target_user": user_id, "role": role, "department": body.department},
    )
    return _user_payload(user)


@router.post("/users/{user_id}/reject", response_model=UserResponse)
async def reject_employee(
    user_id: str,
    request: Request,
    admin=Depends(require_admin),
):
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    try:
        user = reject_user(user_id, admin.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    log_event(admin.id, "ADMIN_REJECT_USER", ip=_client_ip(request), metadata={"target_user": user_id})
    return _user_payload(user)


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def change_employee_role(
    user_id: str,
    body: UpdateRoleRequest,
    request: Request,
    admin=Depends(require_admin),
):
    role = body.role.strip().lower()
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported role.")
    target = get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if target.approval_status != "approved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must be approved first.")
    try:
        user = update_user_role(user_id, role, body.department)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    log_event(
        admin.id,
        "ADMIN_UPDATE_ROLE",
        ip=_client_ip(request),
        metadata={"target_user": user_id, "role": role},
    )
    return _user_payload(user)
