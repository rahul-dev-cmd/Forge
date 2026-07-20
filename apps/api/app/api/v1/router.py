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
    activities
)

api_router = APIRouter()

# Include healthcheck and resource routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repositories"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(invitations.router, prefix="/invitations", tags=["Invitations"])
api_router.include_router(activities.router, prefix="/activities", tags=["Activities"])
