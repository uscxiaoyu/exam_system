# 多用户在线阅卷系统扩展规划

## 1. 扩展目标
将当前的单机版个人辅助工具，升级为支持多位教师在线协作、数据隔离与共享的 SaaS (Software as a Service) 平台。系统需满足学校或教研组层面的统一管理需求，支持多人同时阅卷、班级管理及跨教师的数据分析。

## 2. 核心架构变更
由 **Client-Side (Local)** 架构向 **Browser/Server (Cloud)** 架构转型。

*   **前端**：保持 Vue3 技术栈，增加路由权限控制 (Permission Guards) 和用户会话管理 (Pinia User Store)。
*   **后端**：
    *   引入 **JWT (JSON Web Token)** 认证机制。
    *   数据库层增加 **多租户 (Multi-Tenancy)** 设计，所有数据表增加 `owner_id` 或 `school_id` 字段。
    *   文件存储从本地文件系统迁移至 **对象存储 (OSS/S3)**。

## 3. 新增功能模块

### 3.1 用户与权限中心 (User & Auth Module)
*   **注册/登录**：支持账号密码登录、微信扫码登录。
*   **角色管理 (RBAC)**：
    *   **超级管理员**：管理学校租户、系统全局配置。
    *   **教务管理员**：管理本校教师、班级、统考任务。
    *   **普通教师**：创建考试、上传答卷、阅卷、查看自己班级报表。
*   **个人中心**：修改密码、绑定 LLM Key (支持个人 Key 或学校统一 Key)。

### 3.2 班级与学生管理 (Class & Student Module)
*   不再依赖单纯的“答题卡解析”来建立对应关系，而是预先导入学生名单。
*   **班级管理**：创建/编辑班级，导入学生花名册。
*   **考号绑定**：系统维护“学号-考号-姓名”的映射关系，解决答题卡 OCR 识别姓名错误无法匹配的问题。

### 3.3 协同阅卷 (Collaborative Grading)
*   **流水线阅卷**：支持一场考试由多位教师共同批改。
    *   **题块分配**：将主观题按题号分配给不同老师（例如：张老师改第一题，李老师改第二题）。
    *   **任务分发**：系统自动将学生答卷切片，分发给对应阅卷老师。
*   **仲裁机制**：对于争议试卷（如 AI 评分与人工评分差异过大），支持提交给“阅卷组长”复核。

### 3.4 考试任务管理 (Exam Task Module)
*   **考试创建**：支持“个人练习”和“年级统考”两种模式。
*   **试卷库**：标准答案和评分标准支持存入库中复用。
*   **状态机管理**：未开始 -> 答卷上传中 -> 阅卷中 -> 成绩发布 -> 归档。

## 4. 扩展架构图 (Mermaid)

```mermaid
graph TD
    User[教师/管理员] -->|HTTPS| Nginx[负载均衡/网关]
    Nginx --> WebApp[前端 SPA (Vue3)]
    
    subgraph "应用服务层 (Backend Cluster)"
        API_Auth[认证服务]
        API_Core[核心业务服务]
        API_Grade[阅卷计算服务]
    end
    
    WebApp -->|REST/WS| API_Auth
    WebApp -->|REST| API_Core
    WebApp -->|REST| API_Grade
    
    subgraph "存储与计算层"
        MySQL[(关系型数据库)]
        Redis[(缓存/会话)]
        OSS[对象存储 (答卷图片/文件)]
        LLM[大模型接口]
        Queue[任务队列 (Celery/RabbitMQ)]
    end
    
    API_Auth --> MySQL
    API_Auth --> Redis
    
    API_Core --> MySQL
    API_Core --> OSS
    
    API_Grade --> Queue
    Queue --> LLM
    Queue --> MySQL
```

## 5. 数据库设计变更概览

| 表名 (Table) | 变更点 (Changes) | 说明 |
| :--- | :--- | :--- |
| `users` | **[New]** | 存储用户账号、密码哈希、角色、所属学校ID |
| `schools` | **[New]** | 租户表，存储学校信息 |
| `exams` | Add `creator_id`, `school_id`, `status` | 增加归属权和状态流转 |
| `exam_sections` | Add `marker_id` | 指定该题型的阅卷责任人 (实现流水阅卷) |
| `students` | **[New]** (Standalone Table) | 独立的班级学生库，而非依附于某场考试 |
| `student_exams` | **[New]** | 关联表，记录某学生参加某场考试的原始答卷路径 |
| `grades` | Add `marker_id`, `audit_status` | 记录是谁批改的，以及审核状态 |

## 6. 实施路线图

1.  **阶段一：用户体系构建** (P0)
    *   实现 Login 页面与 JWT 后端认证。
    *   建立 Users 表，将现有所有 API 加上 `Depends(get_current_user)` 鉴权。
2.  **阶段二：数据模型迁移** (P0)
    *   重构数据库模型，引入 `owner_id` 字段。
    *   提供迁移脚本，将本地 SQLite 数据迁移至云端 MySQL。
3.  **阶段三：班级管理功能** (P1) [✅ Frontend Ready]
    *   开发班级与学生名册管理模块。(UI已在侧边栏上线 /classes)
    *   优化上传逻辑，支持上传时校验班级名单。
4.  **阶段四：协同功能** (P2) [✅ Frontend Ready]
    *   开发任务分配界面。(UI已在侧边栏上线 /tasks)
    *   实现题目级别的阅卷权限控制。
