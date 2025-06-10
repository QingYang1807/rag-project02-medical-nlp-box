import React, { useState } from 'react';
import { AlertCircle } from 'lucide-react';

const FinanceEmbeddingOptions = ({ options, onChange }) => (
  <div className="mb-6">
    <h3 className="text-lg font-semibold mb-3">向量数据库配置</h3>
    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">提供商</label>
        <select
          name="provider"
          value={options.provider}
          onChange={onChange}
          className="w-full border border-gray-300 rounded-md px-3 py-2"
        >
          <option value="huggingface">Hugging Face</option>
          <option value="openai">OpenAI</option>
          <option value="bedrock">AWS Bedrock</option>
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">模型</label>
        <input
          type="text"
          name="model"
          value={options.model}
          onChange={onChange}
          className="w-full border border-gray-300 rounded-md px-3 py-2"
          placeholder="BAAI/bge-m3"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">数据库名称</label>
        <input
          type="text"
          name="dbName"
          value={options.dbName}
          onChange={onChange}
          className="w-full border border-gray-300 rounded-md px-3 py-2"
          placeholder="finance_bge_m3"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">集合名称</label>
        <input
          type="text"
          name="collectionName"
          value={options.collectionName}
          onChange={onChange}
          className="w-full border border-gray-300 rounded-md px-3 py-2"
          placeholder="finance_terms"
        />
      </div>
    </div>
  </div>
);

const FinanceTextInput = ({ value, onChange, rows = 4, placeholder }) => (
  <div className="mb-6">
    <label className="block text-sm font-medium text-gray-700 mb-2">
      输入文本
    </label>
    <textarea
      value={value}
      onChange={onChange}
      rows={rows}
      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      placeholder={placeholder}
    />
  </div>
);

const FinStdPage = () => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // 金融术语类别选项
  const [termCategories, setTermCategories] = useState({
    investment: true,
    banking: true,
    insurance: true,
    securities: true,
    accounting: true,
    economics: true,
    derivatives: true,
    real_estate: true,
    fintech: true,
    regulation: true,
    all_finance_terms: true,
  });

  const [embeddingOptions, setEmbeddingOptions] = useState({
    provider: 'huggingface',
    model: 'BAAI/bge-m3',
    dbName: 'finance_bge_m3',
    collectionName: 'finance_terms'
  });

  const handleCategoryChange = (e) => {
    const { name, checked } = e.target;
    
    if (name === 'all_finance_terms') {
      // 如果选择 all_finance_terms，则设置所有选项为相同状态
      setTermCategories(prevCategories => {
        const newCategories = {};
        Object.keys(prevCategories).forEach(key => {
          newCategories[key] = checked;
        });
        return newCategories;
      });
    } else {
      // 更新单个选项
      setTermCategories(prevCategories => ({
        ...prevCategories,
        [name]: checked,
        // 如果取消选择任何一个选项，all_finance_terms 也取消选择
        all_finance_terms: checked && 
          Object.entries(prevCategories)
            .filter(([key]) => key !== 'all_finance_terms' && key !== name)
            .every(([, value]) => value)
      }));
    }
  };

  const handleEmbeddingOptionChange = (e) => {
    const { name, value } = e.target;
    setEmbeddingOptions(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) {
      setError('请输入要处理的金融文本');
      return;
    }

    setIsLoading(true);
    setError('');
    setResult('');

    try {
      const response = await fetch('http://localhost:8000/api/fin-std', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: input,
          termCategories,
          embeddingOptions
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error:', error);
      setError(error.message || '处理请求时发生错误');
    } finally {
      setIsLoading(false);
    }
  };

  const formatResult = (resultString) => {
    try {
      const data = JSON.parse(resultString);
      return (
        <div className="space-y-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="font-semibold text-blue-800">{data.message}</p>
          </div>
          {data.standardized_terms && data.standardized_terms.length > 0 && (
            <div className="space-y-3">
              {data.standardized_terms.map((term, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">
                    原始术语: "{term.original_term}"
                  </h4>
                  <div className="space-y-2">
                    {term.standardized_results.map((result, idx) => (
                      <div key={idx} className="bg-white p-3 rounded border">
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div><strong>标准术语:</strong> {result.term_name}</div>
                          <div><strong>相似度:</strong> {(1 - result.distance).toFixed(3)}</div>
                          <div><strong>类别:</strong> {result.term_category}</div>
                          <div><strong>类型:</strong> {result.term_type}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    } catch (e) {
      return <pre className="whitespace-pre-wrap">{resultString}</pre>;
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">金融术语标准化 💰</h1>
      <div className="grid grid-cols-3 gap-6">
        {/* 左侧面板：文本输入和嵌入选项 */}
        <div className="col-span-2 bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">输入金融文本</h2>
          <FinanceTextInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={4}
            placeholder="请输入包含金融术语的文本，例如：investment portfolio, derivatives trading, financial statements..."
          />
          
          <FinanceEmbeddingOptions 
            options={embeddingOptions} 
            onChange={handleEmbeddingOptionChange} 
          />

          <button
            onClick={handleSubmit}
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 w-full"
            disabled={isLoading}
          >
            {isLoading ? '处理中...' : '标准化金融术语'}
          </button>
        </div>

        {/* 右侧面板：术语类别选项 */}
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">金融术语类别</h2>
          <div className="space-y-3">
            {[
              ['investment', '投资'],
              ['banking', '银行业务'],
              ['insurance', '保险'],
              ['securities', '证券'],
              ['accounting', '会计'],
              ['economics', '经济学'],
              ['derivatives', '衍生品'],
              ['real_estate', '房地产'],
              ['fintech', '金融科技'],
              ['regulation', '金融监管'],
            ].map(([key, label]) => (
              <div key={key} className="flex items-center">
                <input
                  type="checkbox"
                  id={key}
                  name={key}
                  checked={termCategories[key]}
                  onChange={handleCategoryChange}
                  className="mr-2"
                />
                <label htmlFor={key}>{label}</label>
              </div>
            ))}
            
            <div className="flex items-center pt-4 border-t">
              <input
                type="checkbox"
                id="all_finance_terms"
                name="all_finance_terms"
                checked={termCategories.all_finance_terms}
                onChange={handleCategoryChange}
                className="mr-2"
              />
              <label htmlFor="all_finance_terms" className="font-semibold">所有金融术语</label>
            </div>
          </div>
        </div>
      </div>
      
      {/* 结果显示区域 */}
      {(error || result) && (
        <div className="mt-6">
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
              <div className="flex">
                <AlertCircle className="h-6 w-6 mr-2" />
                <div>
                  <p className="font-bold">错误</p>
                  <p>{error}</p>
                </div>
              </div>
            </div>
          )}
          {result && (
            <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6">
              <p className="font-bold mb-2">标准化结果</p>
              {formatResult(result)}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FinStdPage; 