from typing import List, Optional, Dict
import uuid
import os
import time
import hashlib
from datetime import datetime
from app.models.knowledge_base import (
    DocumentItem, DocumentListData, DocumentDetailData, DocumentMetadata,
    StorageInfo, StorageDetailData, DocumentRetryData,
    ChunkItem, ChunkListData, ChunkMetadata,
    DocumentContentData, DocumentStatusData, BatchStatusItem, BatchStatusData,
    RecallSettingsData, RecallSettingsUpdate, RecallSettingsUpdateData,
    ReprocessData,
    RecallTestResultItem, RecallTestData, UsedSettings,
    RecallTestHistoryItem, RecallTestHistoryData,
    DocumentStatisticsData, ProcessingStatisticsData,
)
from app.core.config import settings


class KnowledgeBaseService:
    def __init__(self):
        self.collection = None
        self.documents: Dict[str, dict] = {}
        self.document_chunks: Dict[str, list] = {}
        self.recall_settings = RecallSettingsData()
        self.recall_test_history: list = []
        self._milvus_initialized = False

    def _ensure_milvus(self):
        if self._milvus_initialized:
            return
        try:
            from pymilvus import (Collection, CollectionSchema, FieldSchema, DataType,
                                 connections, utility, MilvusException)
            connections.connect(
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT
            )
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
                FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="chunk_id", dtype=DataType.INT64),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)
            ]
            schema = CollectionSchema(fields, "知识库文档向量集合")
            if utility.has_collection(settings.MILVUS_COLLECTION_NAME):
                self.collection = Collection(settings.MILVUS_COLLECTION_NAME)
            else:
                self.collection = Collection(
                    name=settings.MILVUS_COLLECTION_NAME,
                    schema=schema
                )
                index_params = {
                    "index_type": "IVF_FLAT",
                    "metric_type": "L2",
                    "params": {"nlist": 1024}
                }
                self.collection.create_index(field_name="embedding", index_params=index_params)
            print("Milvus连接和集合初始化成功")
        except Exception as e:
            print(f"Milvus初始化失败: {str(e)}")
        finally:
            self._milvus_initialized = True

    def _simple_text_splitter(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
        if not text:
            return []
        cs = chunk_size or self.recall_settings.chunkSize
        co = chunk_overlap or self.recall_settings.chunkOverlap
        chunks = []
        start = 0
        length = len(text)
        while start < length:
            end = min(start + cs, length)
            chunks.append(text[start:end])
            start += (cs - co)
        return chunks

    def _extract_text_from_file(self, file_path: str, file_type: str) -> str:
        try:
            if file_type.startswith("text/"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"文档类型: {file_type}\n文件名: {os.path.basename(file_path)}"
        except Exception as e:
            return f"文件内容提取失败: {str(e)}"

    def _generate_embedding(self, text: str) -> List[float]:
        import math
        hash_bytes = hashlib.sha256(text.encode('utf-8')).digest()
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            int_val = int.from_bytes(hash_bytes[i:i+4], byteorder='big', signed=True)
            float_val = int_val / (2**31 - 1)
            embedding.append(float_val)
        while len(embedding) < 1536:
            idx = len(embedding) % len(embedding)
            new_val = math.sin(embedding[idx] * math.pi * len(embedding))
            embedding.append(new_val)
        return embedding[:1536]

    def _get_format_from_filename(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        format_map = {
            "docx": "docx", "doc": "docx",
            "xlsx": "xlsx", "xls": "xlsx",
            "pdf": "pdf",
            "txt": "txt",
            "md": "md", "markdown": "md",
        }
        return format_map.get(ext, ext)

    def _is_supported_format(self, filename: str) -> bool:
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        return ext in {"docx", "doc", "xlsx", "xls", "pdf", "txt", "md", "markdown"}

    def _calc_storage(self) -> StorageDetailData:
        used = sum(doc["size"] for doc in self.documents.values())
        max_bytes = 2147483648
        pct = used / max_bytes if max_bytes > 0 else 0
        available = max_bytes - used
        level = "normal"
        if pct >= 0.9:
            level = "critical"
        elif pct >= 0.75:
            level = "warning"
        def fmt(b):
            if b >= 1073741824:
                return f"{b/1073741824:.2f} GB"
            elif b >= 1048576:
                return f"{b/1048576:.2f} MB"
            else:
                return f"{b/1024:.2f} KB"
        return StorageDetailData(
            usedBytes=used,
            maxBytes=max_bytes,
            usedPercentage=round(pct, 3),
            usedText=f"{fmt(used)} / {fmt(max_bytes)}",
            documentCount=len(self.documents),
            availableSpace=available,
            warningLevel=level,
        )

    def _doc_to_item(self, doc: dict) -> DocumentItem:
        chunks = self.document_chunks.get(doc["id"], [])
        avg_len = 0
        chunk_count = 0
        if doc["status"] == "ready" and chunks:
            chunk_count = len(chunks)
            avg_len = int(sum(len(c["content"]) for c in chunks) / chunk_count) if chunk_count > 0 else 0
        return DocumentItem(
            id=doc["id"],
            name=doc["name"],
            format=doc["format"],
            size=doc["size"],
            uploadTime=doc["upload_time"],
            status=doc["status"],
            chunkCount=chunk_count,
            avgChunkLength=avg_len,
            errorMessage=doc.get("error_message"),
            retryCount=doc.get("retry_count", 0),
        )

    # ========== 文档管理 ==========
    def get_documents(
        self,
        page: int = 1,
        pageSize: int = 20,
        keyword: Optional[str] = None,
        format: Optional[str] = None,
        status: Optional[str] = None,
        sortBy: str = "uploadTime",
        sortOrder: str = "desc",
    ) -> DocumentListData:
        docs = list(self.documents.values())

        if keyword:
            docs = [d for d in docs if keyword.lower() in d["name"].lower()]
        if format and format != "all":
            docs = [d for d in docs if d["format"] == format]
        if status and status != "all":
            docs = [d for d in docs if d["status"] == status]

        sort_key_map = {"uploadTime": "upload_time", "name": "name", "size": "size"}
        sort_key = sort_key_map.get(sortBy, "upload_time")
        docs.sort(key=lambda d: d.get(sort_key, ""), reverse=(sortOrder == "desc"))

        total = len(docs)
        start = (page - 1) * pageSize
        end = start + pageSize
        page_docs = docs[start:end]

        return DocumentListData(
            total=total,
            page=page,
            pageSize=pageSize,
            documents=[self._doc_to_item(d) for d in page_docs],
        )

    def get_document_detail(self, document_id: str) -> Optional[DocumentDetailData]:
        doc = self.documents.get(document_id)
        if not doc:
            return None
        item = self._doc_to_item(doc)
        content_preview = ""
        chunks = self.document_chunks.get(document_id, [])
        if chunks:
            content_preview = chunks[0]["content"][:500]
        return DocumentDetailData(
            **item.model_dump(),
            contentPreview=content_preview,
            metadata=DocumentMetadata(),
        )

    def upload_document(self, file_path: str, original_filename: str, overwrite: bool = False) -> UploadResponseData:
        if not self._is_supported_format(original_filename):
            raise ValueError("不支持的文件格式")

        existing = None
        for doc in self.documents.values():
            if doc["name"] == original_filename:
                existing = doc
                break

        if existing and not overwrite:
            raise FileExistsError("已存在同名文件")

        if existing and overwrite:
            self._delete_document_internal(existing["id"])

        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:
            raise ValueError("文件大小超过限制（50MB）")

        if len(self.documents) >= 100:
            raise ValueError("文档数量已达上限（100个）")

        storage = self._calc_storage()
        if storage.usedBytes + file_size > storage.maxBytes:
            raise ValueError("存储空间不足")

        doc_id = f"doc-{uuid.uuid4().hex[:13]}"
        doc_format = self._get_format_from_filename(original_filename)
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        doc = {
            "id": doc_id,
            "name": original_filename,
            "format": doc_format,
            "size": file_size,
            "upload_time": now,
            "status": "uploading",
            "file_path": file_path,
            "error_message": None,
            "retry_count": 0,
        }
        self.documents[doc_id] = doc

        try:
            self._process_document(doc_id)
        except Exception as e:
            doc["status"] = "failed"
            doc["error_message"] = str(e)

        storage = self._calc_storage()
        return UploadResponseData(
            document=self._doc_to_item(doc),
            storageInfo=StorageInfo(**storage.model_dump(exclude={"documentCount", "availableSpace", "warningLevel"})),
        )

    def _process_document(self, document_id: str) -> None:
        doc = self.documents.get(document_id)
        if not doc:
            return

        try:
            doc["status"] = "slicing"
            text = self._extract_text_from_file(doc["file_path"], f"application/{doc['format']}")
            chunks_text = self._simple_text_splitter(text)

            doc["status"] = "vectorizing"
            chunks = []
            for i, chunk in enumerate(chunks_text):
                embedding = self._generate_embedding(chunk)
                chunk_id = f"chunk-{uuid.uuid4().hex[:8]}"
                chunks.append({
                    "id": chunk_id,
                    "document_id": document_id,
                    "content": chunk,
                    "chunk_index": i,
                    "metadata": {},
                })
                if self.collection:
                    self.collection.insert([
                        [chunk_id],
                        [document_id],
                        [i],
                        [chunk[:4096]],
                        [embedding]
                    ])

            self.document_chunks[document_id] = chunks
            doc["status"] = "ready"
        except Exception as e:
            doc["status"] = "failed"
            doc["error_message"] = str(e)
            raise

    def delete_document(self, document_id: str, force: bool = False) -> Optional[StorageInfo]:
        doc = self.documents.get(document_id)
        if not doc:
            return None
        if doc["status"] in ("uploading", "slicing", "vectorizing") and not force:
            raise ValueError("文档正在处理中，无法删除")
        self._delete_document_internal(document_id)
        storage = self._calc_storage()
        return StorageInfo(**storage.model_dump(exclude={"documentCount", "availableSpace", "warningLevel"}))

    def _delete_document_internal(self, document_id: str) -> bool:
        doc = self.documents.get(document_id)
        if not doc:
            return False
        try:
            if os.path.exists(doc.get("file_path", "")):
                os.remove(doc["file_path"])
            if self.collection:
                expr = f"document_id == '{document_id}'"
                self.collection.delete(expr)
            self.documents.pop(document_id, None)
            self.document_chunks.pop(document_id, None)
            return True
        except Exception as e:
            raise Exception(f"文档删除失败: {str(e)}")

    def retry_document(self, document_id: str, from_step: str = "slice") -> Optional[DocumentRetryData]:
        doc = self.documents.get(document_id)
        if not doc:
            return None
        if doc["status"] != "failed":
            raise ValueError("只能重试处理失败的文档")
        if doc.get("retry_count", 0) >= 3:
            raise ValueError("重试次数已达上限（3次）")

        doc["retry_count"] = doc.get("retry_count", 0) + 1
        doc["error_message"] = None

        try:
            self._process_document(document_id)
        except Exception as e:
            doc["status"] = "failed"
            doc["error_message"] = str(e)

        return DocumentRetryData(
            id=document_id,
            status=doc["status"],
            retryCount=doc["retry_count"],
        )

    def get_document_chunks(self, document_id: str, page: int = 1, pageSize: int = 20) -> Optional[ChunkListData]:
        doc = self.documents.get(document_id)
        if not doc:
            return None
        chunks = self.document_chunks.get(document_id, [])
        total = len(chunks)
        avg_len = int(sum(len(c["content"]) for c in chunks) / total) if total > 0 else 0
        start = (page - 1) * pageSize
        end = start + pageSize
        page_chunks = chunks[start:end]
        items = []
        for c in page_chunks:
            items.append(ChunkItem(
                index=c["chunk_index"] + 1,
                content=c["content"],
                length=len(c["content"]),
                vectorId=c["id"],
                metadata=ChunkMetadata(**c.get("metadata", {})),
            ))
        return ChunkListData(totalChunks=total, avgChunkLength=avg_len, chunks=items)

    def get_document_content(self, document_id: str) -> Optional[DocumentContentData]:
        doc = self.documents.get(document_id)
        if not doc:
            return None
        chunks = self.document_chunks.get(document_id, [])
        full_content = "\n".join(c["content"] for c in chunks) if chunks else ""
        return DocumentContentData(content=full_content, length=len(full_content))

    def get_storage_info(self) -> StorageDetailData:
        return self._calc_storage()

    # ========== 文档处理状态 ==========
    def get_document_status(self, document_id: str) -> Optional[DocumentStatusData]:
        doc = self.documents.get(document_id)
        if not doc:
            return None
        progress_map = {
            "uploading": 10,
            "slicing": 40,
            "vectorizing": 70,
            "ready": 100,
            "failed": 0,
        }
        step_map = {
            "uploading": "上传文件",
            "slicing": "文档切片",
            "vectorizing": "向量化处理",
            "ready": "处理完成",
            "failed": "处理失败",
        }
        return DocumentStatusData(
            status=doc["status"],
            progress=progress_map.get(doc["status"], 0),
            currentStep=step_map.get(doc["status"]),
            errorMessage=doc.get("error_message"),
            retryCount=doc.get("retry_count", 0),
        )

    def batch_get_status(self, document_ids: List[str]) -> BatchStatusData:
        statuses = []
        for did in document_ids:
            doc = self.documents.get(did)
            if doc:
                statuses.append(BatchStatusItem(
                    documentId=did,
                    status=doc["status"],
                    errorMessage=doc.get("error_message"),
                ))
            else:
                statuses.append(BatchStatusItem(documentId=did, status="not_found"))
        return BatchStatusData(statuses=statuses)

    # ========== 知识召回设置 ==========
    def get_recall_settings(self) -> RecallSettingsData:
        return self.recall_settings

    def update_recall_settings(self, update: RecallSettingsUpdate) -> RecallSettingsUpdateData:
        requires_reprocess = False
        if update.chunkSize is not None and update.chunkSize != self.recall_settings.chunkSize:
            self.recall_settings.chunkSize = update.chunkSize
            requires_reprocess = True
        if update.chunkOverlap is not None and update.chunkOverlap != self.recall_settings.chunkOverlap:
            self.recall_settings.chunkOverlap = update.chunkOverlap
            requires_reprocess = True
        if update.enabled is not None:
            self.recall_settings.enabled = update.enabled
        if update.topK is not None:
            self.recall_settings.topK = update.topK
        if update.scoreThreshold is not None:
            self.recall_settings.scoreThreshold = update.scoreThreshold
        if update.recallStrategy is not None:
            self.recall_settings.recallStrategy = update.recallStrategy

        self.recall_settings.updatedAt = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        reprocess_count = 0
        if requires_reprocess:
            reprocess_count = sum(1 for d in self.documents.values() if d["status"] == "ready")

        return RecallSettingsUpdateData(
            settings=self.recall_settings.model_copy(),
            requiresReprocess=requires_reprocess,
            reprocessDocuments=reprocess_count,
        )

    def reprocess_documents(self, chunk_size: int, chunk_overlap: int) -> ReprocessData:
        self.recall_settings.chunkSize = chunk_size
        self.recall_settings.chunkOverlap = chunk_overlap
        processing_ids = []
        for doc_id, doc in list(self.documents.items()):
            if doc["status"] == "ready":
                doc["status"] = "slicing"
                processing_ids.append(doc_id)
                try:
                    self._process_document(doc_id)
                except Exception:
                    doc["status"] = "failed"
        return ReprocessData(
            totalDocuments=len(processing_ids),
            processingDocuments=processing_ids,
            estimatedTime=len(processing_ids) * 5,
        )

    # ========== 召回测试 ==========
    def test_recall(self, request) -> RecallTestData:
        start_time = time.time()
        top_k = request.topK or self.recall_settings.topK
        threshold = request.scoreThreshold or self.recall_settings.scoreThreshold
        strategy = request.recallStrategy or self.recall_settings.recallStrategy

        results = []
        try:
            query_embedding = self._generate_embedding(request.query)
            if self.collection:
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
                self.collection.load()
                hits = self.collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    output_fields=["document_id", "chunk_id", "content"]
                )
                for hit_list in hits:
                    for hit in hit_list:
                        score = 1 / (1 + hit.distance)
                        if score >= threshold:
                            doc_id = hit.entity.get("document_id")
                            doc = self.documents.get(doc_id, {})
                            results.append(RecallTestResultItem(
                                index=len(results) + 1,
                                score=round(score, 4),
                                documentId=doc_id,
                                documentName=doc.get("name", "未知文档"),
                                chunkIndex=hit.entity.get("chunk_id", 0),
                                content=hit.entity.get("content", ""),
                                length=len(hit.entity.get("content", "")),
                            ))
        except Exception:
            pass

        elapsed = round((time.time() - start_time) * 1000, 1)
        used = UsedSettings(topK=top_k, scoreThreshold=threshold, recallStrategy=strategy)

        history_item = RecallTestHistoryItem(
            id=f"hist-{uuid.uuid4().hex[:8]}",
            query=request.query,
            resultCount=len(results),
            elapsedTime=elapsed,
            createdAt=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            settings=used,
        )
        self.recall_test_history.append(history_item.model_dump())

        return RecallTestData(
            query=request.query,
            results=results,
            totalResults=len(results),
            elapsedTime=elapsed,
            usedSettings=used,
        )

    def get_recall_test_history(self, page: int = 1, pageSize: int = 10) -> RecallTestHistoryData:
        total = len(self.recall_test_history)
        start = (page - 1) * pageSize
        end = start + pageSize
        page_items = self.recall_test_history[start:end]
        return RecallTestHistoryData(
            total=total,
            page=page,
            pageSize=pageSize,
            history=[RecallTestHistoryItem(**h) for h in page_items],
        )

    # ========== 统计信息 ==========
    def get_document_statistics(self) -> DocumentStatisticsData:
        total = len(self.documents)
        ready = sum(1 for d in self.documents.values() if d["status"] == "ready")
        processing = sum(1 for d in self.documents.values() if d["status"] in ("uploading", "slicing", "vectorizing"))
        failed = sum(1 for d in self.documents.values() if d["status"] == "failed")
        total_chunks = sum(len(chunks) for chunks in self.document_chunks.values())
        avg_chunks = total_chunks / total if total > 0 else 0
        total_len = sum(len(c["content"]) for chunks in self.document_chunks.values() for c in chunks)
        avg_len = total_len / total_chunks if total_chunks > 0 else 0
        by_format: Dict[str, int] = {}
        for d in self.documents.values():
            fmt = d["format"]
            by_format[fmt] = by_format.get(fmt, 0) + 1
        return DocumentStatisticsData(
            totalDocuments=total,
            readyDocuments=ready,
            processingDocuments=processing,
            failedDocuments=failed,
            totalChunks=total_chunks,
            avgChunksPerDocument=round(avg_chunks, 1),
            avgChunkLength=round(avg_len, 1),
            byFormat=by_format,
        )

    def get_processing_statistics(self) -> ProcessingStatisticsData:
        counts: Dict[str, int] = {}
        for d in self.documents.values():
            counts[d["status"]] = counts.get(d["status"], 0) + 1
        return ProcessingStatisticsData(
            uploading=counts.get("uploading", 0),
            slicing=counts.get("slicing", 0),
            vectorizing=counts.get("vectorizing", 0),
            ready=counts.get("ready", 0),
            failed=counts.get("failed", 0),
        )
