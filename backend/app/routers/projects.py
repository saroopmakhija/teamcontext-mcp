from fastapi import APIRouter, HTTPException, status, Depends
from app.models.project import ProjectCreate, ProjectUpdate, ProjectResponse, ContributorAdd
from app.db.mongodb import get_database
from app.dependencies import verify_api_key
from datetime import datetime
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

async def get_current_user(user_id: str = Depends(verify_api_key)):
    """Helper to get current user from user_id"""
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    user: dict = Depends(get_current_user)
):
    """Create a new project (GitHub-style)"""
    db = get_database()

    project_doc = {
        "name": project.name,
        "description": project.description,
        "owner_id": user["_id"],
        "contributors": [],  # Start with no contributors
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = await db.projects.insert_one(project_doc)

    return ProjectResponse(
        id=str(result.inserted_id),
        name=project_doc["name"],
        description=project_doc["description"],
        owner_id=str(user["_id"]),
        owner_name=user["name"],
        contributors=[],
        created_at=project_doc["created_at"],
        updated_at=project_doc["updated_at"]
    )

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(user: dict = Depends(get_current_user)):
    """List all projects user owns or contributes to"""
    db = get_database()

    # Find projects where user is owner OR contributor
    projects = await db.projects.find({
        "$or": [
            {"owner_id": user["_id"]},
            {"contributors": user["_id"]}
        ]
    }).to_list(length=100)

    result = []
    for proj in projects:
        # Get owner info
        owner = await db.users.find_one({"_id": proj["owner_id"]})

        # Get contributor details
        contributors = []
        for contrib_id in proj.get("contributors", []):
            contrib = await db.users.find_one({"_id": contrib_id})
            if contrib:
                contributors.append({
                    "id": str(contrib["_id"]),
                    "name": contrib["name"],
                    "email": contrib["email"]
                })

        result.append(ProjectResponse(
            id=str(proj["_id"]),
            name=proj["name"],
            description=proj["description"],
            owner_id=str(proj["owner_id"]),
            owner_name=owner["name"] if owner else "Unknown",
            contributors=contributors,
            created_at=proj["created_at"],
            updated_at=proj["updated_at"]
        ))

    return result

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: dict = Depends(get_current_user)
):
    """Get project details"""
    db = get_database()

    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check access
    if project["owner_id"] != user["_id"] and user["_id"] not in project.get("contributors", []):
        raise HTTPException(status_code=403, detail="Access denied")

    owner = await db.users.find_one({"_id": project["owner_id"]})
    contributors = []
    for contrib_id in project.get("contributors", []):
        contrib = await db.users.find_one({"_id": contrib_id})
        if contrib:
            contributors.append({
                "id": str(contrib["_id"]),
                "name": contrib["name"],
                "email": contrib["email"]
            })

    return ProjectResponse(
        id=str(project["_id"]),
        name=project["name"],
        description=project["description"],
        owner_id=str(project["owner_id"]),
        owner_name=owner["name"] if owner else "Unknown",
        contributors=contributors,
        created_at=project["created_at"],
        updated_at=project["updated_at"]
    )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    user: dict = Depends(get_current_user)
):
    """Update project (owner only)"""
    db = get_database()

    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["owner_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Only owner can update project")

    update_data = updates.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": update_data}
    )

    return await get_project(project_id, user)

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete project (owner only)"""
    db = get_database()

    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["owner_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Only owner can delete project")

    await db.projects.delete_one({"_id": ObjectId(project_id)})

    # Also delete all context associated with this project
    await db.contexts.delete_many({"metadata.project_id": project_id})

    return {"status": "deleted", "project_id": project_id}

@router.post("/{project_id}/contributors")
async def add_contributor(
    project_id: str,
    contributor: ContributorAdd,
    user: dict = Depends(get_current_user)
):
    """Add contributor to project (owner only)"""
    db = get_database()

    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["owner_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Only owner can add contributors")

    # Find user by email
    new_contributor = await db.users.find_one({"email": contributor.email})
    if not new_contributor:
        raise HTTPException(status_code=404, detail=f"User with email {contributor.email} not found")

    # Check if already contributor or owner
    if new_contributor["_id"] == project["owner_id"]:
        raise HTTPException(status_code=400, detail="User is already the owner")

    if new_contributor["_id"] in project.get("contributors", []):
        raise HTTPException(status_code=400, detail="User is already a contributor")

    # Add contributor
    await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {
            "$push": {"contributors": new_contributor["_id"]},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    return {
        "status": "added",
        "contributor": {
            "id": str(new_contributor["_id"]),
            "name": new_contributor["name"],
            "email": new_contributor["email"]
        }
    }

@router.delete("/{project_id}/contributors/{user_id}")
async def remove_contributor(
    project_id: str,
    user_id: str,
    user: dict = Depends(get_current_user)
):
    """Remove contributor from project (owner only)"""
    db = get_database()

    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["owner_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Only owner can remove contributors")

    # Remove contributor
    await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {
            "$pull": {"contributors": ObjectId(user_id)},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    return {"status": "removed", "user_id": user_id}
