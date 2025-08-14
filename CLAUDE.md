- Claude开发工作流程
文件夹结构要求
创建 claude_message/ 文件夹，包含：
claude_code.md - 代码变更记录
## [日期] 功能名称 - **提交ID**: commit_hash - **修改文件**: `src/components/Header.vue`, `src/api/user.js` - **主要变更**: 实现功能描述 claude_work.md - 工作内容记录
## [日期] 新实现功能 - 功能1：描述 - 功能2：描述  ### 核心代码示例 ```vue // 组件代码示例 <template><div>示例</div></template> 
// API代码示例
export const api = () => {}

claude_project.md - 项目结构
## 目录结构 project/ ├── claude_message/ ├── src/components/ └── src/api/


## 模块代码示例
### src/components/
```vue
<template><nav>导航</nav></template>

src/api/

export const userAPI = {
  login: (data) => fetch('/api/login', {method: 'POST'})
}

工作流程
1.开发功能
2.提交git: git commit -m "feat: 功能描述"
3.更新三个md文件(必须包含代码示例)
4.继续下个功能
要求
●每个功能完成后立即提交git
●claude_work.md和claude_project.md必须包含代码示例
●文档简洁易懂，便于下次阅读