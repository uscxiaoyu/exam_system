# 系统开发任务清单 (Development Checklist)

本清单基于 [多用户在线阅卷系统扩展规划](./multi_user_extension_plan.md) 制定，用于指导后续开发工作的实施顺序。

## 阶段一：基础架构与认证体系 (Infrastructure & Auth)
- [ ] **后端项目重构**
    - [ ] 调整目录结构以支持大型应用 (Controllers/Services/Models 分层)
    - [ ] 引入 `SQLAlchemy` 或 `Tortoise-ORM` 替代简单的 SQL 操作 (为迁移 MySQL 做准备)
- [ ] **用户鉴权模块 (Auth)**
    - [ ] 设计 `User` 表结构 (username, password_hash, role, school_id)
    - [ ] 实现 `POST /api/auth/login` (生成 JWT Token)
    - [ ] 实现 `GET /api/auth/me` (获取当前用户信息)
    - [ ] 实现全局依赖 `get_current_user`，为 API 添加鉴权保护
- [ ] **前端登录改造**
    - [ ] 新增 `LoginView.vue` 页面
    - [ ] 集成 `Pinia UserStore` 管理登录状态
    - [ ] 配置 Axios 拦截器，自动携带 `Authorization: Bearer Token`
    - [ ] 添加路由守卫 (Navigation Guard)，未登录重定向至登录页

## 阶段二：数据模型迁移与多租户 (Data Migration & Multi-tenancy)
- [ ] **数据库迁移**
    - [ ] 部署 MySQL 开发环境
    - [ ] 设计 `Schools` (租户) 表
    - [ ] 现有表结构改造：添加 `owner_id` / `school_id` 字段 (`exams`, `students` 等)
    - [ ] 编写数据迁移脚本 (SQLite -> MySQL)
- [ ] **对象存储接入**
    - [ ] 引入 S3/OSS SDK (如 `boto3` 或 `minio`)
    - [ ] 改造文件上传接口：文件流直接上传至 OSS，数据库仅存 URL
    - [ ] 改造前端图片加载逻辑

## 阶段三：核心业务逻辑升级 (Core Logic Upgrade)
- [ ] **班级与学生管理**
    - [ ] 新增 `Classes` 表与 `Students` 表 (独立于考试)
    - [ ] 开发学生花名册导入/管理接口
    - [ ] 改造答卷匹配逻辑：基于学号/考号从 Student 库中匹配信息
- [ ] **考试任务管理**
    - [ ] 改造 `Exam` 创建流程，支持关联班级
    - [ ] 实现考试状态机 (Draft -> Publishing -> Grading -> Finished)
    - [ ] 开发“我的考试”列表页，区分我创建的和我参与阅卷的

## 阶段四：协同阅卷功能 (Collaborative Grading)
- [ ] **协同基础**
    - [ ] 数据库新增 `ExamSection` 的 `marker_id` (阅卷人) 字段
    - [ ] 开发“任务分配”界面：将题目分配给指定教师
- [ ] **阅卷界面改造**
    - [ ] 改造 `SubjectiveGradingView`，支持根据当前用户权限筛选题目
    - [ ] 实现阅卷进度实时同步 (WebSocket 或 轮询)
    - [ ] 实现“仲裁/复核”标记功能

## 阶段五：部署与优化 (Deployment & Optimization)
- [ ] **容器化部署**
    - [ ] 编写 `Dockerfile` (Frontend & Backend)
    - [ ] 编写 `docker-compose.yml` (App, MySQL, Redis, MinIO)
- [ ] **性能优化**
    - [ ] 引入 Redis 缓存高频配置数据
    - [ ] 引入 Celery 处理耗时任务 (如批量 OCR 解析、LLM 批量批改)
