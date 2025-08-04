# 产品评价管理系统 - 前端

基于Vue 3 + Element Plus + Tailwind CSS构建的现代化产品评价管理系统前端应用。

## 技术栈

### 核心框架
- **Vue 3.5.17** - 渐进式JavaScript框架，使用Composition API
- **Vite 7.0.4** - 下一代前端构建工具
- **Element Plus 2.10.4** - Vue 3组件库
- **Tailwind CSS 4.1.11** - 实用优先的CSS框架

### 路由和状态管理
- **Vue Router 4.5.1** - Vue.js官方路由管理器
- **Pinia 3.0.3** - Vue状态管理库

### 工具库
- **Vue I18n 11.1.9** - 国际化插件
- **Axios 1.10.0** - HTTP客户端
- **ECharts 5.6.0** - 数据可视化图表库
- **Day.js 1.11.13** - 轻量级日期处理库
- **@element-plus/icons-vue 2.3.1** - Element Plus图标库

### 开发工具
- **ESLint 9.30.1** - 代码质量检查
- **Prettier 3.6.2** - 代码格式化
- **PostCSS 8.5.6** - CSS后处理器
- **Autoprefixer 10.4.21** - CSS自动前缀

## 功能特性

### 🔐 认证与权限
- JWT Token认证系统
- 角色基础访问控制（RBAC）
- 四级权限体系：管理员 > 组长 > 组长助理 > 普通用户
- 自动token刷新和过期处理

### 📊 数据可视化
- 响应式图表组件（基于ECharts 5.6）
- 评价状态分布饼图
- 月度趋势线图
- 自定义图表工具库
- 图表导出功能

### 📝 评价流程管理
- 新产品评价流程（需二级审批）
- 量产评价流程（直接完成）
- 评价状态跟踪与管理
  - 直观的状态控制按钮（暂停/恢复/完成/取消）
  - 状态变更操作日志记录
  - 状态流程可视化展示
- 操作日志记录
- 文件上传和附件管理

### 🔍 高级搜索和筛选
- 多字段组合搜索
- 日期范围筛选
- 状态和类型筛选
- 表格排序功能
- 分页加载

### 🌍 国际化支持
- 完整的多语言支持：中文/英文/韩文
- 动态语言切换
- 本地化日期格式
- RTL支持预留

### 🎨 现代化UI设计
- 响应式设计，支持移动端
- 玻璃态效果和渐变背景
- 动画过渡效果
- 暗色模式预留
- 可定制主题系统

### ⚡ 性能优化
- 代码分割和懒加载
- 组件缓存策略
- 图片懒加载
- 包体积优化
- CDN资源优化

## 开发环境要求

- Node.js >= 22.0.0
- npm >= 10.0.0

## 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动（已配置代理到后端API）

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/        # 可复用组件
│   │   └── AnimatedContainer.vue  # 动画容器组件
│   ├── layouts/          # 布局组件
│   │   └── MainLayout.vue    # 主布局
│   ├── views/            # 页面组件
│   │   ├── Dashboard.vue     # 仪表板
│   │   ├── Evaluations.vue   # 评价列表
│   │   ├── EvaluationDetail.vue # 评价详情
│   │   ├── NewEvaluation.vue # 新建评价
│   │   ├── Reports.vue       # 报告统计
│   │   ├── Messages.vue      # 消息中心
│   │   ├── Users.vue         # 用户管理
│   │   ├── Profile.vue       # 个人资料
│   │   ├── Login.vue         # 登录页面
│   │   └── NotFound.vue      # 404页面
│   ├── router/           # 路由配置
│   │   └── index.js          # 路由定义和守卫
│   ├── stores/           # Pinia状态管理
│   │   └── auth.js           # 认证状态管理
│   ├── utils/            # 工具函数
│   │   ├── api.js            # API请求封装
│   │   └── charts.js         # 图表工具库
│   ├── locales/          # 国际化文件
│   │   ├── zh.json           # 中文
│   │   ├── en.json           # 英文
│   │   └── ko.json           # 韩文
│   ├── styles/           # 样式文件
│   │   └── global.css        # 全局样式
│   ├── style.css         # 主样式文件
│   ├── main.js           # 应用入口
│   └── App.vue           # 根组件
├── index.html            # HTML模板
├── package.json          # 项目配置
├── vite.config.js        # Vite配置
├── tailwind.config.js    # Tailwind配置
├── postcss.config.js     # PostCSS配置
├── eslint.config.js      # ESLint配置
└── README.md             # 项目文档
```

## 主要页面

- **登录页面** (`/login`) - 用户登录
- **仪表板** (`/`) - 数据概览和快速操作
- **评价管理** (`/evaluations`) - 评价列表和管理
- **新建评价** (`/evaluations/new`) - 创建新的评价项目
- **评价详情** (`/evaluations/:id`) - 查看评价详细信息，包含状态管理按钮组
- **报告统计** (`/reports`) - 数据分析和报告
- **消息中心** (`/messages`) - 系统通知和消息
- **用户管理** (`/users`) - 用户和权限管理
- **个人资料** (`/profile`) - 个人信息设置和密码管理
  - 查看和编辑个人基本信息（姓名、邮箱、部门、职位）
  - 密码修改功能（需验证当前密码）
  - 支持表单验证和国际化

## 开发指南

### 代码规范

项目使用ESLint和Prettier进行代码规范检查：

```bash
# 检查代码规范
npm run lint

# 格式化代码
npm run format
```

### 测试

项目配置了Jest测试框架，支持Vue 3组件测试：

```bash
# 运行测试
npm test

# 监听模式运行测试
npm run test:watch  

# 运行测试并生成覆盖率报告
npm run test:coverage
```

**测试配置特性：**
- **Vue 3兼容性** - 使用vue-jest和babel-jest实现Vue 3组件测试
- **模块解析** - 支持@/路径别名和ES6模块
- **测试环境** - 配置jsdom环境模拟浏览器API
- **国际化模拟** - 内置i18n函数mock支持
- **全局mock** - ResizeObserver等浏览器API的mock支持

测试文件位于 `tests/` 目录下，包含：
- `tests/setup.js` - 测试环境配置和全局mock
- `tests/unit/` - 单元测试文件
- `jest.config.js` - Jest配置文件（Vue 3优化）
- `babel.config.js` - Babel配置支持ES6模块

### 国际化

支持三种语言：
- 中文 (`zh`)
- 英文 (`en`) 
- 韩文 (`ko`)

国际化文件位于 `src/locales/` 目录下。

### 状态管理

使用Pinia进行状态管理，主要store：
- `authStore` - 用户认证状态
  - 用户信息管理
  - Token存储和刷新
  - 权限检查方法
  - 登录/登出操作

### API集成

API调用统一通过 `src/utils/api.js` 进行，已配置：
- 请求/响应拦截器
- 自动添加认证token
- 401错误自动跳转登录
- 统一错误处理和提示
- 请求超时设置（10秒）

### 图表系统

新增的图表工具库 `src/utils/charts.js` 提供：
- `createPieChart()` - 饼图创建
- `createLineChart()` - 折线图创建  
- `createBarChart()` - 柱状图创建
- `makeResponsive()` - 响应式处理
- `disposeChart()` - 资源清理
- `chartUtils.exportToImage()` - 图表导出

## 部署

### 环境变量

开发环境通过 `vite.config.js` 配置代理：
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:5001',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

生产环境需要配置：
- `VITE_API_BASE_URL` - 后端API地址

### 构建部署

```bash
# 构建生产版本
npm run build

# 构建产物在 dist/ 目录下
# 可以部署到任何静态文件服务器（Nginx、Apache等）
```

### Docker部署

项目支持Docker容器化部署，参考根目录的 `docker-compose.yml`

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 许可证

本项目仅供内部使用。 