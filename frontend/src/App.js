import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import NERPage from './pages/NERPage';
import StdPage from './pages/StdPage';
import FinStdPage from './pages/FinStdPage';
import CorrPage from './pages/CorrPage';
import AbbrPage from './pages/AbbrPage';
import GenPage from './pages/GenPage';

const WelcomePage = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <img src="/images/medical-img.png" alt="医疗记录处理" className="w-96 h-auto mb-8" />
      <h1 className="text-3xl font-bold text-gray-800 mb-4">欢迎使用医疗记录处理工具箱</h1>
      <p className="text-xl text-gray-600 mb-4">请从左侧菜单选择要使用的功能</p>
      <div className="bg-blue-50 p-4 rounded-lg">
        <h2 className="text-lg font-semibold text-blue-800 mb-2">🆕 新增功能</h2>
        <p className="text-blue-700">现已支持金融领域专有名词标准化功能！</p>
      </div>
    </div>
  );
};

const App = () => {
  const [sidebarWidth, setSidebarWidth] = useState(250);

  const handleResize = (e) => {
    setSidebarWidth(e.clientX);
  };

  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        <Sidebar width={sidebarWidth} />
        <div
          className="w-1 cursor-col-resize bg-gray-300 hover:bg-blue-500"
          onMouseDown={() => {
            document.addEventListener('mousemove', handleResize);
            document.addEventListener('mouseup', () => {
              document.removeEventListener('mousemove', handleResize);
            });
          }}
        />
        <main className="flex-1 overflow-y-auto p-5">
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/ner" element={<NERPage />} />
            <Route path="/stand" element={<StdPage />} />
            <Route path="/fin-std" element={<FinStdPage />} />
            <Route path="/corr" element={<CorrPage />} />
            <Route path="/abbr" element={<AbbrPage />} />
            <Route path="/gen" element={<GenPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;