# Ops Platform (运维平台)

Ops Platform 是一个轻量级的服务器运维管理平台，提供主机管理、Web 终端连接、批量任务执行等功能。采用前后端分离架构，部署简单，开箱即用。

## 🏗️ 项目架构

本项目采用现代化的前后端分离技术栈：

### 前端 (Frontend)
- **核心框架**: Vue 3 + TypeScript + Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **终端组件**: xterm.js (支持 Web SSH 连接)
- **网络请求**: Axios

### 后端 (Backend)
- **核心框架**: FastAPI (Python)
- **数据库**: SQLite (通过 SQLAlchemy ORM 管理)
- **SSH 支持**: AsyncSSH / Paramiko
- **实时通信**: WebSocket (用于 Web Terminal 和实时日志)

---

## ✨ 主要功能

1. **主机管理 (Host Management)**
   - 支持添加、编辑、删除主机信息。
   - 支持密码和 SSH 密钥两种认证方式。
   - 主机标签管理。

2. **Web 终端 (Web Terminal)**
   - 基于 WebSocket 和 xterm.js 实现。
   - 直接在浏览器中通过 SSH 连接服务器，无需安装额外客户端。

3. **任务执行 (Task Execution)**
   - **命令广播**: 同时向多台主机发送命令。
   - **批量执行**: 支持分批次执行任务，具备失败暂停策略。
   - **执行记录**: 实时查看每台主机的执行状态、输出日志和退出码。

4. **用户管理 (User Management)**
   - 用户登录/认证。
   - 基础的权限控制。

---

## 🚀 快速启动 (Quick Start)

### 环境要求
- **Python**: 3.9 或更高版本
- **Node.js**: 16 或更高版本
- **OS**: Windows (推荐), Linux/macOS (需手动运行命令)

### 方法一：一键启动 (Windows 推荐)

在项目根目录下，右键使用 PowerShell 运行启动脚本：

```powershell
.\start_project.ps1
```

脚本会自动：
1. 检查环境依赖。
2. 在新窗口中启动 Backend 服务 (端口 8000)。
3. 在新窗口中启动 Frontend 服务 (端口 5173)。

启动成功后，访问浏览器：[http://localhost:5173](http://localhost:5173)

### 方法二：手动启动

**1. 启动后端**

```bash
cd backend
# 创建虚拟环境 (可选)
python -m venv venv
# Windows 激活虚拟环境: .\venv\Scripts\activate
# Linux/Mac 激活虚拟环境: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload
```
后端地址：http://localhost:8000 (API 文档: /docs)

**2. 启动前端**

```bash
cd frontend
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```
前端地址：http://localhost:5173

---

## 🛑 关闭服务

### 如果使用脚本启动
直接关闭弹出的两个 PowerShell 窗口（分别运行着 Backend 和 Frontend）即可。

### 如果手动启动
在运行服务的终端窗口中，按下 `Ctrl + C` 组合键即可停止服务。
