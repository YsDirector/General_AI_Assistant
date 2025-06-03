# General AI Assistant

## Language

- [English](#english)
- [中文](#中文)

---

### English

#### Introduction
Configure your models and prompts to interact with AI easily.

#### Installation Guide
##### For Regular Users
1. Download the Release version.
2. Install Java 8 SE (or higher) to use it.

##### For Professional Users
1. Download the code.
2. Adjust as needed and build using Electron methods.

#### Usage Instructions
1. Go to the settings page, configure API_URL, API_KEY, and MODEL in the "Model Settings".
2. Configure Toolname and Prompt corresponding to the MODEL in the "Toolbar Settings".
3. Save the settings, then you can invoke the toolbar by pressing Alt+F6 in any text box on your computer.

#### Contribution Guidelines
Feel free to create branches or submit Pull Requests to add new features or optimize the code.

#### License Information
This project is licensed under the Apache 2.0 license.

#### Author List & Acknowledgments
- YsDirector (Main)

#### Contact Information
yushendirector@126.com

#### Version Plan
Originally, I planned to add streaming functionality in version 1.1.0, but I discovered that Electron's efficiency in system-level interactions was too low, causing issues with token output speeds on devices where the output is extremely fast. Therefore, I will devote all my energy to developing version 2.x.x. Version 1.x.x is now discontinued for maintenance.

##### 2.x.x Version
Considering most excellent AI projects are developed based on Python, and after successfully experimenting with streaming functionality, it was decided to port the project to Pywebview.
The 2.0.0 version will retain all features of the 1.0.2 version while making the following changes:
1) Add plugin functionality: This allows importation of other Python format API request scripts compatible with OpenAI APIs for secondary development, enhancing compatibility.
2) Add streaming support: Streaming capabilities can be directly used in any text box.
3) Add help documentation: This addresses the issue newbies have with understanding AI API concepts.
4) Project name change: Due to the introduction of plugin functionality, I found that this plugin would not only be applicable to AI functionalities. Therefore, I will rename the project as General Assistant.
5) Multilingual support: A feature promised in the 1.x.x version.

---

### 中文

#### 简介
通过配置您的模型与提示词，轻松实现与AI的交互。

#### 安装指南
##### 普通用户
1. 直接下载Release版本。
2. 安装Java 8 SE（或更高版本）即可使用。

##### 专业用户
1. 下载代码。
2. 自行调整后，按照Electron的方法进行构建。

#### 使用方法
1. 前往设置页面，在“模型设置”中配置API_URL、API_KEY和MODEL。
2. 在“工具栏设置”中配置MODEL对应的Toolname和Prompt。
3. 保存设置后，您可以在电脑的任何文本框中按下Alt+F6快捷键呼出工具栏使用。

#### 贡献指南
欢迎创建分支或提交Pull请求，为我们的项目添加新功能或优化代码。

#### 许可证信息
本项目采用Apache 2.0许可证。

#### 作者列表及致谢
- YsDirector (主创)

#### 联系方式
yushendirector@126.com

#### 版本计划
原本我打算在1.1.0版本中加入流式传输功能，但发现Electron在系统级的交互上的效率偏低，导致在Tokens输出速度极高的设备上，会出现吞字的现象。因此，我会将精力全部投入在2.x.x版本的开发当中。1.x.x版本即日起停止维护。
##### 2.x.x版本
考虑到大部分优秀的ai项目都基于Python开发，而且在对流式传输功能小试牛刀获得成功后，最终决定将项目迁移到Pywebview.
2.0.0版本会保留1.0.2版本的所有功能，并进行如下改动：
1）添加插件功能：可以导入非OpenAI API兼容的其它Python格式API请求脚本，进行二次开发，提高兼容性。
2）添加流式传输支持：可以直接在任意文本框中使用的流式传输功能。
3）添加帮助文档：解决新手不理解AI API相关概念的问题。
4）项目名称变更：由于插件功能的引入，我发现该插件将不仅仅可以用于AI功能。因此，我会将项目名称修改为 General Assistant.
5）多语言支持：原本承诺在1.x.x版本加入的功能。Version Plan
