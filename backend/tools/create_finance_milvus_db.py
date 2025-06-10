from pymilvus import model
from pymilvus import MilvusClient
import pandas as pd
from tqdm import tqdm
import logging
from dotenv import load_dotenv
load_dotenv()
import torch    
from pymilvus import MilvusClient, DataType, FieldSchema, CollectionSchema

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化嵌入函数
embedding_function = model.dense.SentenceTransformerEmbeddingFunction(
            model_name='BAAI/bge-m3',
            device='cuda:0' if torch.cuda.is_available() else 'cpu',
            trust_remote_code=True
        )

# 文件路径
file_path = "data/万条金融标准术语.csv"
db_path = "db/finance_bge_m3.db"

# 连接到 Milvus
client = MilvusClient(db_path)

collection_name = "finance_terms"  # 金融术语集合

# 加载数据
logging.info("Loading finance terms data from CSV")
df = pd.read_csv(file_path, 
                 dtype=str, 
                 low_memory=False,
                 header=None,  # 根据示例数据，没有列标题
                 names=['term_name', 'term_type']  # 指定列名
                ).fillna("NA")

# 为每个术语生成唯一ID和其他字段
df['term_id'] = df.index + 1
df['term_category'] = 'FINTERM'  # 所有术语都属于金融术语类别
df['definition'] = 'NA'  # 暂时没有定义
df['synonyms'] = 'NA'    # 暂时没有同义词

logging.info(f"Loaded {len(df)} finance terms")

# 获取向量维度（使用一个样本文档）
sample_doc = "Sample Financial Term"
sample_embedding = embedding_function([sample_doc])[0]
vector_dim = len(sample_embedding)

# 构造Schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dim), 
    FieldSchema(name="term_id", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="term_name", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="term_category", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="term_type", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="definition", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="synonyms", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="input_file", dtype=DataType.VARCHAR, max_length=500),
]
schema = CollectionSchema(fields, 
                          "Finance Terms Collection", 
                          enable_dynamic_field=True)

# 如果集合存在，先删除
if client.has_collection(collection_name):
    client.drop_collection(collection_name)
    logging.info(f"Dropped existing collection: {collection_name}")

# 创建集合
client.create_collection(
    collection_name=collection_name,
    schema=schema,
)
logging.info(f"Created new collection: {collection_name}")

# 在创建集合后添加索引
index_params = client.prepare_index_params()
index_params.add_index(
    field_name="vector",  
    index_type="AUTOINDEX",  
    metric_type="COSINE",  
    params={"nlist": 1024}  
)

client.create_index(
    collection_name=collection_name,
    index_params=index_params
)

# 批量处理
batch_size = 1024

for start_idx in tqdm(range(0, len(df), batch_size), desc="Processing finance terms batches"):
    end_idx = min(start_idx + batch_size, len(df))
    batch_df = df.iloc[start_idx:end_idx]

    # 准备文档 - 只使用术语名称进行向量化
    docs = []
    for _, row in batch_df.iterrows():
        docs.append(row['term_name'])

    # 生成嵌入
    try:
        embeddings = embedding_function(docs)
        logging.info(f"Generated embeddings for finance terms batch {start_idx // batch_size + 1}")
    except Exception as e:
        logging.error(f"Error generating embeddings for batch {start_idx // batch_size + 1}: {e}")
        continue

    # 准备数据
    data = [
        {
            "vector": embeddings[idx],
            "term_id": str(row['term_id']),
            "term_name": str(row['term_name']),
            "term_category": str(row['term_category']),
            "term_type": str(row['term_type']),
            "definition": str(row['definition']),
            "synonyms": str(row['synonyms']),
            "input_file": file_path
        } for idx, (_, row) in enumerate(batch_df.iterrows())
    ]

    # 插入数据
    try:
        res = client.insert(
            collection_name=collection_name,
            data=data
        )
        logging.info(f"Inserted finance terms batch {start_idx // batch_size + 1}, result: {res}")
    except Exception as e:
        logging.error(f"Error inserting batch {start_idx // batch_size + 1}: {e}")

logging.info("Finance terms insert process completed.")

# 示例查询
query = "investment"
query_embeddings = embedding_function([query])

# 搜索余弦相似度最高的
search_result = client.search(
    collection_name=collection_name,
    data=[query_embeddings[0].tolist()],
    limit=5,
    output_fields=["term_name", "term_type", "term_category"]
)
logging.info(f"Search result for 'investment': {search_result}")

# 查询所有匹配的实体
query_result = client.query(
    collection_name=collection_name,
    filter="term_type == 'FINTERM'",
    output_fields=["term_name", "term_type", "term_category"],
    limit=5
)
logging.info(f"Query result for term_type == 'FINTERM': {query_result}")

logging.info("Finance terms database creation completed successfully!") 