# ADR-002: 采用 Vue 3 + TypeScript 前端架构

## 状态
已接受

## 背景
原系统使用 Jinja2 模板 + jQuery ，存在以下问题：
- 前后端耦合，页面刷新需全量加载
- jQuery 命令式编程，状态管理混乱
- 缺乏类型安全，重构困难
- 组件复用性差

## 决策
采用 Vue 3 + TypeScript + Vite 技术栈构建 SPA 前端。

### 技术选型

| 技术 | 用途 |
|------|------|
| Vue 3 (Composition API) | 渐进式响应式框架 |
| TypeScript | 类型安全，IDE 智能提示 |
| Vite | 快速开发服务器 + 构建工具 |
| Vue Router | 客户端路由，SPA 体验 |
| Pinia | 轻量级状态管理 |
| Element Plus | UI 组件库 |

### 项目结构

```
frontend/
├── src/
│   ├── api/                 # API 调用层（Axios 封装）
│   ├── components/         # 公共组件
│   ├── views/               # 页面视图
│   ├── stores/              # Pinia 状态管理
│   ├── router/              # Vue Router 配置
│   ├── types/               # TypeScript 类型定义
│   └── styles/              # 全局样式
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 替代方案考虑

| 替代方案 | 优点 | 缺点 |
|---------|------|------|
| React | 生态大，社区活跃 | 学习曲线陡，JSX 语法 |
| Angular | 企业级，功能完整 | 过于重量，学习成本高 |
| 保持 jQuery | 简单 | 技术落后，难以维护 |
| Next.js/Nuxt | SSR 支持 | 复杂度增加 |

## 后果

### 正面
- SPA 体验：页面无刷新，响应迅速
- 类型安全：编译时发现问题
- 组件化：高度复用，易于维护
- 现代工具链：Vite 热更新快速

### 负面
- SEO 不友好（需 SSR 解决）
- 首屏加载需加载 JS 框架
- 需处理登录态存储（Token vs Session）
- 迁移成本：需重写前端代码