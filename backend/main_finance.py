from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from services.fin_std_service_simple import FinStdServiceSimple
from typing import List, Dict, Optional, Literal
import logging
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title="金融术语标准化API", description="金融领域专有名词标准化系统")

# 配置跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础模型类
class BaseInputModel(BaseModel):
    """基础输入模型"""
    llmOptions: Dict[str, str] = Field(
        default_factory=lambda: {
            "provider": "ollama",
            "model": "qwen2.5:7b"
        },
        description="大语言模型配置选项"
    )

class FinanceEmbeddingOptions(BaseModel):
    """金融向量数据库配置选项"""
    provider: Literal["huggingface", "openai", "bedrock"] = Field(
        default="huggingface",
        description="向量数据库提供商"
    )
    model: str = Field(
        default="BAAI/bge-m3",
        description="嵌入模型名称"
    )
    dbName: str = Field(
        default="finance_bge_m3",
        description="金融向量数据库名称"
    )
    collectionName: str = Field(
        default="finance_terms",
        description="金融术语集合名称"
    )

class FinanceTextInput(BaseInputModel):
    """金融文本输入模型，用于金融术语标准化"""
    text: str = Field(..., description="输入金融文本")
    termCategories: Dict[str, bool] = Field(
        default_factory=lambda: {
            "investment": True,
            "banking": True,
            "insurance": True,
            "securities": True,
            "accounting": True,
            "economics": True,
            "derivatives": True,
            "real_estate": True,
            "fintech": True,
            "regulation": True,
            "all_finance_terms": True
        },
        description="金融术语类别"
    )
    embeddingOptions: FinanceEmbeddingOptions = Field(
        default_factory=FinanceEmbeddingOptions,
        description="金融向量数据库配置选项"
    )

# API 端点：金融术语标准化
@app.post("/api/fin-std")
async def finance_standardization(input: FinanceTextInput):
    try:
        # 记录请求信息
        logger.info(f"Received finance standardization request: text={input.text}")

        # 初始化金融标准化服务
        finance_service = FinStdServiceSimple(
            db_path=f"db/{input.embeddingOptions.dbName}.db",
            collection_name=input.embeddingOptions.collectionName
        )

        # 将输入文本按空格或标点符号分割，提取可能的金融术语
        # 简单的术语提取：按空格和标点分割，过滤掉太短的词
        potential_terms = re.findall(r'\b[A-Za-z][A-Za-z\s\-\.]*\b', input.text)
        potential_terms = [term.strip() for term in potential_terms if len(term.strip()) > 2]
        
        if not potential_terms:
            # 如果没有提取到术语，就用整个文本进行搜索
            potential_terms = [input.text]

        # 标准化每个潜在的金融术语
        standardized_results = []
        for term in potential_terms:
            std_result = finance_service.search_similar_terms(term)
            if std_result:  # 只添加有结果的术语
                standardized_results.append({
                    "original_term": term,
                    "standardized_results": std_result
                })

        return {
            "message": f"处理了 {len(potential_terms)} 个潜在金融术语，找到 {len(standardized_results)} 个匹配结果",
            "standardized_terms": standardized_results
        }

    except Exception as e:
        logger.error(f"Error in finance standardization processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "金融术语标准化API正在运行", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "finance_term_standardization"}

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 