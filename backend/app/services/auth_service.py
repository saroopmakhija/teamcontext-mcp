from fastapi import HTTPException, status
from typing import Optional
from app.services.snowflake_user_service import bump_usage_stats
from app.db.mongodb import get_database
from app.utils.security import verify_api_key as verify_api_key_hash
from app.services.jwt_service import verify_token
from bson import ObjectId


class AuthService:
    """
    Centralized authentication service that handles both JWT and API key authentication.
    Provides methods to get user info, check permissions, and verify project access.
    """

    def __init__(self):
        self.user_id: Optional[str] = None
        self.user: Optional[dict] = None

    async def _set_authenticated_user(self, user: dict) -> str:
        user_id = str(user["_id"])
        self.user_id = user_id
        self.user = user
        email = user.get("email")
        if email:
            await bump_usage_stats(email)
        return user_id

    async def authenticate(
        self,
        token: Optional[str] = None,
        cookie_token: Optional[str] = None
    ) -> str:
        """
        Authenticate user using JWT (cookie or header) or API key.
        Priority: Cookie > JWT header > API key header

        Args:
            token: Token from Authorization header
            cookie_token: Token from cookie

        Returns:
            user_id: The authenticated user's ID

        Raises:
            HTTPException: If authentication fails
        """
        # Priority 1: Check JWT cookie
        if cookie_token:
            user_id = verify_token(cookie_token, token_type="access")
            if user_id:
                db = get_database()
                user = await db.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    return await self._set_authenticated_user(user)

        # Priority 2: Check Authorization header
        if token:
            # Try JWT verification first
            user_id = verify_token(token, token_type="access")
            if user_id:
                db = get_database()
                user = await db.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    return await self._set_authenticated_user(user)

            # Try API key verification
            db = get_database()
            users = await db.users.find({}).to_list(length=None)
            for user in users:
                if "hashed_api_key" in user and verify_api_key_hash(token, user["hashed_api_key"]):
                    return await self._set_authenticated_user(user)

        # No valid authentication found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - provide valid JWT token or API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def get_user_id(self) -> str:
        """Get the authenticated user's ID."""
        if not self.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        return self.user_id

    def get_user(self) -> dict:
        """Get the authenticated user's full document."""
        if not self.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        return self.user

    async def check_project_access(self, project_id: str) -> dict:
        """
        Check if authenticated user has access to a project.

        Args:
            project_id: The project ID to check access for

        Returns:
            project: The project document if user has access

        Raises:
            HTTPException: If project not found or user doesn't have access
        """
        if not self.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        db = get_database()
        project = await db.projects.find_one({"_id": ObjectId(project_id)})

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Check if user is owner or contributor
        user_obj_id = ObjectId(self.user_id)
        if project["owner_id"] != user_obj_id and user_obj_id not in project.get("contributors", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )

        return project

    async def check_is_project_owner(self, project_id: str) -> dict:
        """
        Check if authenticated user is the owner of a project.

        Args:
            project_id: The project ID to check ownership for

        Returns:
            project: The project document if user is owner

        Raises:
            HTTPException: If project not found or user is not owner
        """
        if not self.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        db = get_database()
        project = await db.projects.find_one({"_id": ObjectId(project_id)})

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Check if user is owner
        if project["owner_id"] != ObjectId(self.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can perform this action"
            )

        return project

    async def get_accessible_projects(self) -> list:
        """
        Get all projects the authenticated user has access to.

        Returns:
            projects: List of project documents user can access
        """
        if not self.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        db = get_database()
        user_obj_id = ObjectId(self.user_id)

        projects = await db.projects.find({
            "$or": [
                {"owner_id": user_obj_id},
                {"contributors": user_obj_id}
            ]
        }).to_list(length=100)

        return projects


# Create singleton instance
auth_service = AuthService()
