from fastapi import APIRouter, Request

from app.shared.dependencies.db import PostgresRunnerDep
from app.auth.dependencies import CurrentSubjectDep
from app.auth.enums import AccessLevel
from app.auth.decorators import authorize
from app.audit.decorators import audit

from .dto import LoadTestDataResponse
from . import service as admin_service


router = APIRouter()


@router.post("/load-test/up")
@audit()
@authorize(AccessLevel.CONFIDENTIAL)
async def execute_load_test_up(
    db: PostgresRunnerDep,
    subject: CurrentSubjectDep,
    request: Request,
) -> LoadTestDataResponse:
    """Create 100 test users and 30 test projects for load testing"""
    return admin_service.create_load_test_data(db=db)


@router.post("/load-test/down")
@audit()
@authorize(AccessLevel.CONFIDENTIAL)
async def execute_load_test_down(
    db: PostgresRunnerDep,
    subject: CurrentSubjectDep,
    request: Request,
) -> dict[str, str]:
    """Delete all test users and projects created by load-test/up"""
    admin_service.cleanup_load_test_data(db=db)
    return {"status": "success", "message": "Load test data cleaned up"}
