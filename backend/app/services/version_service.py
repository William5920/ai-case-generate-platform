import uuid
import difflib
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.requirement import Requirement, DocVersion


class VersionService:

    async def get_version_list(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str
    ) -> Optional[dict]:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        version_result = await db.execute(
            select(DocVersion)
            .where(DocVersion.requirement_id == requirement_id)
            .order_by(DocVersion.version_number.desc())
        )
        versions = version_result.scalars().all()

        version_items = []
        for v in versions:
            version_items.append({
                "versionId": v.id,
                "versionNumber": v.version_number,
                "description": v.description,
                "createdAt": v.created_at.isoformat() + "Z" if v.created_at else None
            })

        latest_result = await db.execute(
            select(DocVersion)
            .where(DocVersion.requirement_id == requirement_id)
            .order_by(DocVersion.version_number.desc())
            .limit(1)
        )
        latest_version = latest_result.scalar_one_or_none()

        return {
            "versions": version_items,
            "currentVersionId": latest_version.id if latest_version else None
        }

    async def get_version_detail(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        version_id: str
    ) -> Optional[dict]:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        version_result = await db.execute(
            select(DocVersion).where(
                and_(
                    DocVersion.id == version_id,
                    DocVersion.requirement_id == requirement_id
                )
            )
        )
        version = version_result.scalar_one_or_none()
        if not version:
            return None

        return {
            "versionId": version.id,
            "versionNumber": version.version_number,
            "content": version.content,
            "description": version.description,
            "createdAt": version.created_at.isoformat() + "Z" if version.created_at else None
        }

    async def restore_version(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        version_id: str
    ) -> Optional[dict]:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        version_result = await db.execute(
            select(DocVersion).where(
                and_(
                    DocVersion.id == version_id,
                    DocVersion.requirement_id == requirement_id
                )
            )
        )
        version = version_result.scalar_one_or_none()
        if not version:
            return None

        requirement.standardized_content = version.content
        requirement.updated_at = datetime.utcnow()

        max_version_result = await db.execute(
            select(func.max(DocVersion.version_number))
            .where(DocVersion.requirement_id == requirement_id)
        )
        max_version = max_version_result.scalar() or 0
        new_version_number = max_version + 1

        new_version_id = f"ver-{uuid.uuid4().hex[:8]}"
        new_version = DocVersion(
            id=new_version_id,
            requirement_id=requirement_id,
            version_number=new_version_number,
            content=version.content,
            description=f"恢复自版本 {version.version_number}",
            created_at=datetime.utcnow()
        )
        db.add(new_version)
        await db.commit()

        return {
            "newVersionId": new_version_id,
            "newVersionNumber": new_version_number,
            "content": version.content,
            "description": f"恢复自版本 {version.version_number}"
        }

    async def get_version_diff(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        from_version_id: str,
        to_version_id: str
    ) -> Optional[dict]:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        from_result = await db.execute(
            select(DocVersion).where(DocVersion.id == from_version_id)
        )
        from_version = from_result.scalar_one_or_none()

        to_result = await db.execute(
            select(DocVersion).where(DocVersion.id == to_version_id)
        )
        to_version = to_result.scalar_one_or_none()

        if not from_version or not to_version:
            return None

        from_lines = from_version.content.splitlines(keepends=True)
        to_lines = to_version.content.splitlines(keepends=True)

        diff = list(difflib.unified_diff(from_lines, to_lines, lineterm=""))

        diff_lines = []
        added_count = 0
        modified_count = 0
        removed_count = 0
        line_number = 0

        for line in diff:
            if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
                continue
            line_number += 1
            if line.startswith("+"):
                diff_lines.append({
                    "lineNumber": line_number,
                    "text": line[1:].strip(),
                    "type": "added"
                })
                added_count += 1
            elif line.startswith("-"):
                diff_lines.append({
                    "lineNumber": line_number,
                    "text": line[1:].strip(),
                    "type": "removed"
                })
                removed_count += 1

        return {
            "fromVersionId": from_version_id,
            "toVersionId": to_version_id,
            "diffLines": diff_lines,
            "summary": {
                "addedCount": added_count,
                "modifiedCount": modified_count,
                "removedCount": removed_count
            }
        }


version_service = VersionService()
