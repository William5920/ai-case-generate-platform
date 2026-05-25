from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.requirement import Requirement, UploadedFile, SplitRequirement
from app.schemas.requirement import (
    CreateRequirementRequest, UpdateRequirementRequest, RequirementListQuery,
    RequirementDetail, RequirementListItem, RequirementListData,
    FileInfoSchema, SplitRequirementItem
)


class RequirementService:

    async def create_requirement(
        self,
        db: AsyncSession,
        user_id: str,
        data: CreateRequirementRequest
    ) -> dict:
        from datetime import datetime
        import uuid

        req_id = f"req-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        if data.inputMode == "text" and not data.rawContent:
            raise ValueError("文本输入模式下 rawContent 不能为空")
        if data.inputMode == "file" and not data.fileId:
            raise ValueError("文档上传模式下 fileId 不能为空")

        requirement = Requirement(
            id=req_id,
            user_id=user_id,
            title=data.title,
            input_mode=data.inputMode,
            raw_content=data.rawContent,
            file_id=data.fileId,
            template_id=data.templateId or "user-story",
            status="draft",
            explore_data=[],
            created_at=now,
            updated_at=now
        )
        db.add(requirement)
        await db.commit()
        await db.refresh(requirement)

        return self._format_requirement(requirement, db)

    async def get_requirement_list(
        self,
        db: AsyncSession,
        user_id: str,
        query: RequirementListQuery
    ) -> dict:
        base_query = select(Requirement).where(Requirement.user_id == user_id)
        count_query = select(func.count(Requirement.id)).where(Requirement.user_id == user_id)

        filters = []
        if query.keyword:
            filters.append(Requirement.title.contains(query.keyword))
        if query.status:
            filters.append(Requirement.status == query.status)

        if filters:
            base_query = base_query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        base_query = base_query.order_by(Requirement.updated_at.desc())
        base_query = base_query.offset((query.pageNo - 1) * query.pageSize).limit(query.pageSize)

        result = await db.execute(base_query)
        requirements = result.scalars().all()

        items = []
        for req in requirements:
            items.append({
                "id": req.id,
                "title": req.title,
                "status": req.status,
                "createdAt": req.created_at.isoformat() + "Z" if req.created_at else None,
                "updatedAt": req.updated_at.isoformat() + "Z" if req.updated_at else None
            })

        return {
            "items": items,
            "pageNo": query.pageNo,
            "pageSize": query.pageSize,
            "total": total
        }

    async def get_requirement_detail(
        self,
        db: AsyncSession,
        user_id: str,
        req_id: str
    ) -> Optional[dict]:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == req_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        return await self._format_requirement_detail(requirement, db)

    async def update_requirement(
        self,
        db: AsyncSession,
        user_id: str,
        req_id: str,
        data: UpdateRequirementRequest
    ) -> Optional[dict]:
        from datetime import datetime

        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == req_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        if data.title is not None:
            requirement.title = data.title
        if data.rawContent is not None:
            requirement.raw_content = data.rawContent
        if data.templateId is not None:
            requirement.template_id = data.templateId
        if data.standardizedContent is not None:
            requirement.standardized_content = data.standardizedContent
        if data.exploreData is not None:
            requirement.explore_data = data.exploreData
        if data.status is not None:
            requirement.status = data.status

        requirement.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(requirement)

        return {
            "id": requirement.id,
            "title": requirement.title,
            "updatedAt": requirement.updated_at.isoformat() + "Z"
        }

    async def delete_requirement(
        self,
        db: AsyncSession,
        user_id: str,
        req_id: str
    ) -> bool:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == req_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return False

        await db.delete(requirement)
        await db.commit()
        return True

    def _format_requirement(self, req: Requirement, db: AsyncSession) -> dict:
        return {
            "id": req.id,
            "title": req.title,
            "inputMode": req.input_mode,
            "rawContent": req.raw_content,
            "templateId": req.template_id,
            "status": req.status,
            "createdAt": req.created_at.isoformat() + "Z" if req.created_at else None,
            "updatedAt": req.updated_at.isoformat() + "Z" if req.updated_at else None
        }

    async def _format_requirement_detail(self, req: Requirement, db: AsyncSession) -> dict:
        file_info = None
        if req.file_id:
            file_result = await db.execute(select(UploadedFile).where(UploadedFile.id == req.file_id))
            uploaded_file = file_result.scalar_one_or_none()
            if uploaded_file:
                file_info = {
                    "fileName": uploaded_file.original_filename,
                    "fileSize": uploaded_file.file_size,
                    "fileType": uploaded_file.file_type
                }

        split_result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == req.id)
            .order_by(SplitRequirement.order_index)
        )
        splits = split_result.scalars().all()
        split_items = [
            {"id": s.id, "content": s.content, "order": s.order_index}
            for s in splits
        ]

        return {
            "id": req.id,
            "title": req.title,
            "inputMode": req.input_mode,
            "rawContent": req.raw_content,
            "templateId": req.template_id,
            "fileInfo": file_info,
            "exploreData": req.explore_data or [],
            "standardizedContent": req.standardized_content,
            "splitRequirements": split_items,
            "status": req.status,
            "createdAt": req.created_at.isoformat() + "Z" if req.created_at else None,
            "updatedAt": req.updated_at.isoformat() + "Z" if req.updated_at else None
        }


requirement_service = RequirementService()
