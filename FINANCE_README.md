# 金融领域专有名词标准化系统

基于医疗领域专有名词标准化系统框架，新增了金融领域的专有名词标准化功能。

## 🆕 新增功能

### 金融术语标准化
- **数据源**: 万条金融标准术语.csv
- **术语类别**: 投资、银行、保险、证券、会计、经济学、衍生品、房地产、金融科技、监管等
- **技术架构**: 使用 BAAI/bge-m3 嵌入模型 + Milvus 向量数据库

## 🚀 快速启动

### 1. 后端服务

由于依赖包版本冲突问题，我们创建了简化版的金融术语标准化API：

```bash
cd backend
python main_finance.py
```

服务将运行在 `http://localhost:8001`

### 2. 前端界面

前端已更新，新增了"金融术语标准化"菜单项：

```bash
cd frontend
npm start
```

前端将运行在 `http://localhost:3000`

## 📊 功能特性

### 金融术语标准化
- **输入**: 包含金融术语的文本
- **输出**: 标准化后的金融术语，包含相似度评分
- **支持术语类型**:
  - 投资相关: Investment, Portfolio, Asset Management
  - 银行业务: Banking, Credit, Loan, Deposit
  - 保险产品: Insurance, Premium, Coverage
  - 证券交易: Securities, Stock, Bond, Trading
  - 会计财务: Accounting, Financial Statement, Balance Sheet
  - 经济指标: Economics, GDP, Inflation, Interest Rate
  - 金融衍生品: Derivatives, Options, Futures, Swaps
  - 房地产金融: Real Estate, Mortgage, Property Investment
  - 金融科技: Fintech, Digital Banking, Blockchain
  - 监管合规: Regulation, Compliance, Risk Management

## 🔧 API 使用示例

### 金融术语标准化 API

**端点**: `POST http://localhost:8001/api/fin-std`

**请求示例**:
```json
{
  "text": "investment portfolio financial statement",
  "termCategories": {
    "all_finance_terms": true
  },
  "embeddingOptions": {
    "provider": "huggingface",
    "model": "BAAI/bge-m3",
    "dbName": "finance_bge_m3",
    "collectionName": "finance_terms"
  }
}
```

**响应示例**:
```json
{
  "message": "处理了 1 个潜在金融术语，找到 1 个匹配结果",
  "standardized_terms": [
    {
      "original_term": "investment portfolio financial statement",
      "standardized_results": [
        {
          "term_id": "10426",
          "term_name": "Portfolio Investment",
          "term_category": "FINTERM",
          "term_type": "FINTERM",
          "definition": "NA",
          "synonyms": "NA",
          "distance": 0.748
        }
      ]
    }
  ]
}
```

## 🎯 使用场景

1. **金融文档标准化**: 统一金融报告、分析文档中的术语表达
2. **投资研究**: 标准化投资研究报告中的专业术语
3. **合规检查**: 确保金融文档使用标准化的监管术语
4. **翻译辅助**: 为金融文档翻译提供标准术语参考
5. **数据清洗**: 清理和标准化金融数据中的术语字段

## 📁 文件结构

```
backend/
├── services/
│   ├── fin_std_service.py           # 完整版金融标准化服务 (有依赖冲突)
│   └── fin_std_service_simple.py    # 简化版金融标准化服务 (推荐使用)
├── tools/
│   └── create_finance_milvus_db.py  # 金融术语数据库创建工具
├── data/
│   └── 万条金融标准术语.csv        # 金融术语数据源
├── db/
│   └── finance_bge_m3.db           # 金融术语向量数据库
├── main.py                         # 完整版API (有依赖冲突)
└── main_finance.py                 # 简化版金融API (推荐使用)

frontend/src/pages/
└── FinStdPage.js                   # 金融术语标准化页面
```

## 🔄 技术路线图

1. **已完成**:
   - ✅ 金融术语数据库构建 (16,549条术语)
   - ✅ 简化版API服务
   - ✅ 前端页面集成
   - ✅ 基础功能测试

2. **待优化**:
   - 🔄 解决 langchain 依赖冲突问题
   - 🔄 增强术语分类精度
   - 🔄 添加批量处理功能
   - 🔄 优化向量搜索性能

## 🐛 已知问题

1. **依赖冲突**: 原版API中 langchain-huggingface 与 pydantic v2 存在版本冲突
2. **解决方案**: 使用简化版API (`main_finance.py`) 避免冲突
3. **影响范围**: 仅影响与 langchain 相关的功能，核心标准化功能正常

## 📞 支持

如遇问题，请检查：
1. 后端服务是否在 8001 端口正常运行
2. 金融术语数据库是否已创建
3. 前端是否正确连接到 8001 端口的API

---

*基于医疗NLP工具箱框架开发 - 新增金融领域支持* 