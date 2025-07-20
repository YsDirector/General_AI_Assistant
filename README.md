# General Assistant 2

## Table of Contents
- [English Version](#english-version)
- [中文版本](#中文版本)

<a name="english-version"></a>

## English Version

General assistant desktop application, providing chatbot, plugin management, toolbar functions, etc.

### ✨ Features
- **Multi-language support**: Supports switching between Chinese and English interfaces.
- **Plugin system**: Supports Python + HTML plugin development.
- **AI model management**: Configurable parameters for multiple AI models.
- **System toolbar**: Provides quick tool menus.
- **Chatbot**: Supports streaming conversation and Markdown rendering.
- **System tray**: Runs in the background and supports shortcut key invocation.
- **Configuration management**: Saves user settings and plugin configurations.

### 🛠️ Technology Stack
#### Backend Core
- **Framework**: Bottle.py
- **System Integration**: `pywin32` (Windows API), `plyer` (hardware access)
- **Asynchronous Communication**: SSE (Server-Sent Events)
- **Dependency Libraries**: `pywin32`, `plyer`, `pystray`, `bottle`, `requests`

#### Frontend Interface
- Native HTML/CSS/JS
- Support for multi-language files (locales directory)

#### Project Structure
general-assistant-2/
├── backend/ # Backend core
├── frontend/ # Frontend interface
├── plugin/ # Plugin system
└── python_embed/ # Embedded Python environment


#### Main Function Entry Points
- **System Tray Menu**: Access features by right-clicking the tray icon.
- **Toolbar**: Invoke by pressing `Ctrl+C` twice consecutively.
- **Settings Interface**: Open via the tray menu.

#### 🔌 Plugin Development (Advanced)
Plugins are located in the `plugin/` directory and support two types:

1. **Python Plugins**: Extend backend functionality.
2. **HTML Plugins**: Provide frontend interaction interfaces or configuration pages for backend plugins.

#### ⚙️ Configuration Management
User configurations are saved in the `%APPDATA%/general-assistant-2/` directory:

- `settings.json`: Global settings such as language.
- `toolbar.json`: Toolbar configuration.
- `models.json`: AI model configuration.

#### 📜 License
Apache License 2.0 - See the `LICENSE` file in the root directory of the project.

#### 📬 Contact Information
Author: YsDirector  
Email: yushendirector@126.com

---

## 中文版本

通用智能助手桌面应用，提供聊天机器人、插件管理、工具栏等功能。

### ✨ 功能特性
- **多语言支持**：支持中英文界面切换。
- **插件系统**：支持 Python + HTML 插件开发。
- **AI 模型管理**：可配置多个 AI 模型参数。
- **系统工具栏**：提供快捷工具菜单。
- **聊天机器人**：支持流式对话和 Markdown 渲染。
- **系统托盘**：后台运行，支持快捷键呼出。
- **配置管理**：保存用户设置和插件配置。

### 🛠️ 技术栈
#### 后端核心
- **框架**：Bottle.py
- **系统集成**：`pywin32` (Windows API), `plyer` (硬件访问)
- **异步通信**：SSE (Server-Sent Events)
- **依赖库**：`pywin32`, `plyer`, `pystray`, `bottle`, `requests`

#### 前端界面
- 原生 HTML/CSS/JS
- 多语言文件支持 (locales 目录)

#### 项目结构
general-assistant-2/
├── backend/ # 后端核心
├── frontend/ # 前端界面
├── plugin/ # 插件系统
└── python_embed/ # 嵌入式 Python 环境


#### 主要功能入口
- **系统托盘菜单**：右键托盘图标访问功能。
- **工具栏**：连续按两下 `Ctrl+C` 呼出。
- **设置界面**：通过托盘菜单打开。

#### 🔌 插件开发（高级）
插件位于 `plugin/` 目录，支持两种类型：

1. **Python 插件** ：实现后端功能扩展。
2. **HTML 插件** ：提供前端交互界面或后端插件的配置页面。

#### ⚙️ 配置管理
用户配置保存在 `%APPDATA%/general-assistant-2/` 目录：

- `settings.json`：语言等全局设置。
- `toolbar.json`：工具栏配置。
- `models.json`：AI 模型配置。

#### 📜 开源协议
Apache License 2.0 - 详见项目根目录 `LICENSE` 文件。

#### 📬 联系信息
作者：YsDirector  
邮箱：yushendirector@126.com