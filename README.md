# Cubism Chat

基于Cubism Editor 5.4 alpha的尝鲜版LLM 对话式 Live2D Cubism Editor 编辑工具。通过自然语言控制 Cubism Editor 5.4 的 WebSocket API，支持参数编辑、键位管理、变形器操作、规则系统等。未来随着live2d官方推出的更新可能会有各种改动，图一乐

## 架构

- 后端：Python FastAPI + WebSocket
- 前端：单页 HTML（暗色主题聊天界面）
- LLM：DeepSeek API（OpenAI 兼容 function calling）
- 编辑目标：Live2D Cubism Editor 5.4 alpha1 外部集成 API

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 4. 启动
python main.py
# 浏览器打开 http://127.0.0.1:8765
```

## 使用

1. 启动 Cubism Editor 5.4，在设置中启用外部应用集成
2. 点击右上角齿轮配置 API Key
3. 点击输入框左侧 `/` 按钮查看可用命令和规则

### 规则系统

用 `/` 命令或自然语言触发规则。创建规则：

```
添加规则：当我打三个参数点的时候，在最小值中间值最大值各加一个键位
```

规则保存到 `rules/` 目录，可手动编辑。

## 配置

所有配置通过 Web 界面右上角设置面板完成：
- **API Key**：DeepSeek API 密钥
- **模型**：建议使用DeepSeek V4系列
- **API Base URL**：DeepSeek API 地址
- **Cubism 端口**：Editor WebSocket 端口（默认 22033）
