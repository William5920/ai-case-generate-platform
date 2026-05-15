from typing import List, Optional, Dict
import uuid
import os
from app.models.knowledge_base import Document, KnowledgeRecallParams, DocumentSlice
from app.core.config import settings
from pymilvus import (Collection, CollectionSchema, FieldSchema, DataType, 
                     connections, utility, MilvusException)

class KnowledgeBaseService:
    def __init__(self):
        # 初始化Milvus连接
        self._init_milvus()
        # 文档存储（内存模拟，实际项目中应使用数据库）
        self.documents: Dict[uuid.UUID, Document] = {}
        # 文档切片存储
        self.document_slices: Dict[uuid.UUID, List[DocumentSlice]] = {}
        # 召回参数
        self.recall_params = KnowledgeRecallParams()
    
    def _init_milvus(self):
        """初始化Milvus连接和集合"""
        try:
            # 连接到Milvus
            connections.connect(
                host="127.0.0.1",
                port=19530
            )
            
            # 定义集合模式
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
                FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="chunk_id", dtype=DataType.INT64),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)  # 使用1536维向量
            ]
            
            schema = CollectionSchema(fields, "知识库文档向量集合")
            
            # 创建或获取集合
            if utility.has_collection("knowledge_base"):
                self.collection = Collection("knowledge_base")
            else:
                self.collection = Collection(
                    name="knowledge_base",
                    schema=schema
                )
                
                # 创建索引
                index_params = {
                    "index_type": "IVF_FLAT",
                    "metric_type": "L2",
                    "params": {"nlist": 1024}
                }
                self.collection.create_index(field_name="embedding", index_params=index_params)
            
            print("Milvus连接和集合初始化成功")
            
        except MilvusException as e:
            print(f"Milvus初始化失败: {str(e)}")
            raise Exception(f"Milvus初始化失败: {str(e)}")
    
    def _simple_text_splitter(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """简单的文本分割函数"""
        if not text:
            return []
            
        chunks = []
        start = 0
        length = len(text)
        
        while start < length:
            end = min(start + chunk_size, length)
            chunks.append(text[start:end])
            start += (chunk_size - chunk_overlap)
            
        return chunks
    
    def _extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """从不同类型的文件中提取文本"""
        try:
            # 仅支持文本文件，其他类型返回文件名
            if file_type.startswith("text/"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 对于非文本文件，返回文件名作为内容
                return f"文档类型: {file_type}\n文件名: {os.path.basename(file_path)}"
                
        except Exception as e:
            return f"文件内容提取失败: {str(e)}"
    
    def _generate_embedding(self, text: str) -> List[float]:
        """生成文本的向量表示（使用模拟向量，实际项目中应调用AI服务）"""
        # 这里使用模拟的向量，实际项目中应调用OpenAI等服务生成真实embedding
        import random
        return [random.uniform(-1, 1) for _ in range(1536)]
    
    def process_document(self, document: Document) -> None:
        """处理文档：提取文本、切片、向量化并存储到Milvus"""
        try:
            # 1. 提取文本内容
            text = self._extract_text_from_file(document.file_path, document.file_type)
            
            # 2. 文本切片
            chunks = self._simple_text_splitter(text)
            
            # 3. 向量化并存储到Milvus
            slices = []
            for i, chunk in enumerate(chunks):
                # 生成切片ID
                slice_id = uuid.uuid4()
                
                # 生成向量
                embedding = self._generate_embedding(chunk)
                
                # 创建文档切片记录
                doc_slice = DocumentSlice(
                    id=slice_id,
                    document_id=document.id,
                    content=chunk,
                    chunk_id=i
                )
                slices.append(doc_slice)
                
                # 插入到Milvus
                self.collection.insert([
                    [str(slice_id)],
                    [str(document.id)],
                    [i],
                    [chunk[:4096]],
                    [embedding]
                ])
            
            # 保存文档和切片记录到内存
            self.documents[document.id] = document
            self.document_slices[document.id] = slices
            
        except MilvusException as e:
            raise Exception(f"Milvus操作失败: {str(e)}")
        except Exception as e:
            raise Exception(f"文档处理失败: {str(e)}")
    
    def get_documents(self, skip: int = 0, limit: int = 10) -> List[Document]:
        """获取文档列表"""
        docs = list(self.documents.values())[skip:skip+limit]
        return docs
    
    def get_document_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """根据ID获取文档"""
        return self.documents.get(document_id)
    
    def delete_document(self, document_id: uuid.UUID) -> bool:
        """删除文档"""
        if document_id not in self.documents:
            return False
        
        try:
            # 删除物理文件
            document = self.documents[document_id]
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # 删除Milvus中的切片
            expr = f"document_id == '{str(document_id)}'"
            self.collection.delete(expr)
            
            # 删除内存中的记录
            del self.documents[document_id]
            if document_id in self.document_slices:
                del self.document_slices[document_id]
            
            return True
            
        except MilvusException as e:
            raise Exception(f"Milvus删除失败: {str(e)}")
        except Exception as e:
            raise Exception(f"文档删除失败: {str(e)}")
    
    def update_recall_params(self, params: KnowledgeRecallParams) -> None:
        """更新召回参数"""
        self.recall_params = params
    
    def test_recall(self, query: str, params: Optional[KnowledgeRecallParams] = None) -> List[Dict]:
        """使用Milvus进行向量召回测试"""
        if params is None:
            params = self.recall_params
        
        try:
            # 生成查询向量
            query_embedding = self._generate_embedding(query)
            
            # 设置搜索参数
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }
            
            # 执行搜索
            self.collection.load()
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=params.top_k,
                expr=None,
                output_fields=["document_id", "chunk_id", "content"]
            )
            
            # 处理搜索结果
            recall_results = []
            for hits in results:
                for hit in hits:
                    # 转换L2距离为相似度分数（1/(1+距离)）
                    similarity_score = 1 / (1 + hit.distance)
                    if similarity_score >= params.threshold:
                        result = {
                            "document_id": hit.entity.get("document_id"),
                            "chunk_id": hit.entity.get("chunk_id"),
                            "content": hit.entity.get("content"),
                            "score": similarity_score
                        }
                        recall_results.append(result)
            
            # 按相似度分数排序
            recall_results.sort(key=lambda x: x["score"], reverse=True)
            
            return recall_results
            
        except MilvusException as e:
            raise Exception(f"Milvus召回失败: {str(e)}")
        except Exception as e:
            raise Exception(f"召回测试失败: {str(e)}")
