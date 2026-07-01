from fastapi import APIRouter

from app.api.v1 import auth, orgs, grants, applications, knowledge, compliance, billing

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(orgs.router, prefix="/orgs", tags=["orgs"])
api_router.include_router(grants.router, prefix="/grants", tags=["grants"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
