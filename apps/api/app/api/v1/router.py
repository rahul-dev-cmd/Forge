from fastapi import APIRouter
from app.api.v1 import (
    health,
    users,
    workspaces,
    projects,
    repositories,
    notifications,
    organizations,
    invitations,
    activities,
    github,
    webhooks,
    code_intelligence,
    ai_knowledge,
    copilot,
    admin,
    collaboration,
)

api_router = APIRouter()

# Include healthcheck and resource routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repositories"])
api_router.include_router(code_intelligence.router, prefix="/repositories", tags=["Code Intelligence"])
api_router.include_router(ai_knowledge.router, prefix="/repositories", tags=["AI Knowledge"])
api_router.include_router(copilot.router, tags=["AI Copilot"])
api_router.include_router(admin.router, tags=["Admin Dashboard"])
api_router.include_router(collaboration.router, tags=["Collaboration & Team Features"])
api_router.include_router(github.router, prefix="/github", tags=["GitHub"])

api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(invitations.router, prefix="/invitations", tags=["Invitations"])
api_router.include_router(activities.router, prefix="/activities", tags=["Activities"])


