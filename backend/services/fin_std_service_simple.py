from pymilvus import MilvusClient, model
from dotenv import load_dotenv
import os
from typing import List, Dict
import logging
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class FinStdServiceSimple:
    """
    简化版金融术语标准化服务
    直接使用pymilvus模型，避免langchain依赖冲突
    """
    def __init__(self, 
                 db_path="db/finance_bge_m3.db",
                 collection_name="finance_terms"):
        """
        初始化金融术语标准化服务
        
        Args:
            db_path: Milvus 数据库路径
            collection_name: 集合名称
        """
        # 创建embedding函数
        self.embedding_func = model.dense.SentenceTransformerEmbeddingFunction(
            model_name='BAAI/bge-m3',
            device='cuda:0' if torch.cuda.is_available() else 'cpu',
            trust_remote_code=True
        )
        
        # 连接 Milvus
        self.client = MilvusClient(db_path)
        self.collection_name = collection_name
        
        # 检查集合是否存在
        if self.client.has_collection(self.collection_name):
            self.client.load_collection(self.collection_name)
        else:
            logger.warning(f"Collection {self.collection_name} does not exist. Please create it first.")

    def search_similar_terms(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索与查询文本相似的金融术语
        
        Args:
            query: 查询文本
            limit: 返回结果的最大数量
            
        Returns:
            包含相似术语信息的列表
        """
        # 检查集合是否存在
        if not self.client.has_collection(self.collection_name):
            return []
            
        try:
            # 获取查询的向量表示
            query_embeddings = self.embedding_func([query])
            
            # 设置搜索参数
            search_params = {
                "collection_name": self.collection_name,
                "data": [query_embeddings[0].tolist()],
                "limit": limit,
                "output_fields": [
                    "term_id", "term_name", "term_category", 
                    "term_type", "definition", "synonyms"
                ]
            }
            
            # 搜索相似项
            search_result = self.client.search(**search_params)

            results = []
            for hit in search_result[0]:
                results.append({
                    "term_id": hit['entity'].get('term_id'),
                    "term_name": hit['entity'].get('term_name'),
                    "term_category": hit['entity'].get('term_category'),
                    "term_type": hit['entity'].get('term_type'),
                    "definition": hit['entity'].get('definition'),
                    "synonyms": hit['entity'].get('synonyms'),
                    "distance": float(hit['distance'])
                })

            return results
        except Exception as e:
            logger.error(f"Error searching similar terms: {str(e)}")
            return []

    def __del__(self):
        """清理资源，释放集合"""
        if hasattr(self, 'client') and hasattr(self, 'collection_name'):
            try:
                if self.client.has_collection(self.collection_name):
                    self.client.release_collection(self.collection_name)
            except:
                pass 