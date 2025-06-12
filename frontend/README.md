# 产品评估管理系统 - 前端

基于Vue 3 + Element Plus + Tailwind CSS构建的产品评估管理系统前端应用。

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - Vue 3组件库
- **Tailwind CSS** - 实用优先的CSS框架
- **Vue Router** - Vue.js官方路由管理器
- **Pinia** - Vue状态管理库
- **Vue I18n** - 国际化插件
- **Axios** - HTTP客户端
- **ECharts** - 数据可视化图表库
- **Vite** - 前端构建工具

## 功能特性

- 🔐 用户认证和权限管理
- 📊 仪表板数据可视化
- 📝 评估流程管理
- 🔍 高级搜索和筛选
- 📱 响应式设计
- 🌍 多语言支持（中文/英文/韩文）
- 🎨 现代化UI设计

## 开发环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0

## 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动

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
│   ├── layouts/          # 布局组件
│   ├── views/            # 页面组件
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia状态管理
│   ├── utils/            # 工具函数
│   ├── locales/          # 国际化文件
│   ├── style.css         # 全局样式
│   ├── main.js           # 应用入口
│   └── App.vue           # 根组件
├── index.html            # HTML模板
├── package.json          # 项目配置
├── vite.config.js        # Vite配置
├── tailwind.config.js    # Tailwind配置
└── postcss.config.js     # PostCSS配置
```

## 主要页面

- **登录页面** (`/login`) - 用户登录
- **仪表板** (`/`) - 数据概览和快速操作
- **评估管理** (`/evaluations`) - 评估列表和管理
- **新建评估** (`/evaluations/new`) - 创建新的评估项目
- **评估详情** (`/evaluations/:id`) - 查看评估详细信息
- **报告统计** (`/reports`) - 数据分析和报告
- **消息中心** (`/messages`) - 系统通知和消息
- **用户管理** (`/users`) - 用户和权限管理
- **个人资料** (`/profile`) - 个人信息设置

## 开发指南

### 代码规范

项目使用ESLint和Prettier进行代码规范检查：

```bash
# 检查代码规范
npm run lint

# 格式化代码
npm run format
```

### 国际化

支持三种语言：
- 中文 (`zh`)
- 英文 (`en`) 
- 韩文 (`ko`)

国际化文件位于 `src/locales/` 目录下。

### 状态管理

使用Pinia进行状态管理，主要store：
- `authStore` - 用户认证状态
- 其他业务相关store根据需要添加

### API集成

API调用统一通过 `src/utils/api.js` 进行，已配置：
- 请求/响应拦截器
- 自动添加认证token
- 错误处理

## 部署

### 环境变量

生产环境需要配置以下环境变量：
- `VITE_API_BASE_URL` - 后端API地址

### 构建部署

```bash
# 构建生产版本
npm run build

# 构建产物在 dist/ 目录下
# 可以部署到任何静态文件服务器
```

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 许可证

本项目仅供内部使用。 