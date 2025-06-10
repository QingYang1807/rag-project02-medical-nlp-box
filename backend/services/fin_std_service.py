from pymilvus import MilvusClient
from dotenv import load_dotenv
from utils.embedding_factory import EmbeddingFactory
from utils.embedding_config import EmbeddingProvider, EmbeddingConfig
import os
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class FinStdService:
    """
    金融术语标准化服务
    使用向量数据库进行金融术语的标准化和相似度搜索
    """
    def __init__(self, 
                 provider="huggingface",
                 model="BAAI/bge-m3",
                 db_path="db/finance_bge_m3.db",
                 collection_name="finance_terms"):
        """
        初始化金融术语标准化服务
        
        Args:
            provider: 嵌入模型提供商 (openai/bedrock/huggingface)
            model: 使用的模型名称
            db_path: Milvus 数据库路径
            collection_name: 集合名称
        """
        # 根据 provider 字符串匹配正确的枚举值
        provider_mapping = {
            'openai': EmbeddingProvider.OPENAI,
            'bedrock': EmbeddingProvider.BEDROCK,
            'huggingface': EmbeddingProvider.HUGGINGFACE
        }
        
        # 创建 embedding 函数
        embedding_provider = provider_mapping.get(provider.lower())
        if embedding_provider is None:
            raise ValueError(f"Unsupported provider: {provider}")
            
        config = EmbeddingConfig(
            provider=embedding_provider,
            model_name=model
        )
        self.embedding_func = EmbeddingFactory.create_embedding_function(config)
        
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
            包含相似术语信息的列表，每个术语包含：
            - term_id: 术语ID
            - term_name: 术语名称
            - term_category: 术语类别
            - term_type: 术语类型
            - definition: 术语定义
            - synonyms: 同义词
            - distance: 相似度距离
        """
        # 检查集合是否存在
        if not self.client.has_collection(self.collection_name):
            return []
            
        try:
            # 获取查询的向量表示
            query_embedding = self.embedding_func.embed_query(query)
            
            # 设置搜索参数
            search_params = {
                "collection_name": self.collection_name,
                "data": [query_embedding],
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