# 🛠️ 智能阅卷系统 Pro - 部署与运维手册 (新手向)

👋 你好！这份指南专为**前端新手**或**非技术背景**的用户设计。我们将手把手教你如何在本地电脑上把这个系统“跑起来”。

不需要复杂的代码知识，你只需要按照步骤操作即可。

---

## 1. 准备工作 (Prerequisites)

在开始之前，你需要安装两个核心工具。它们就像是运行这个系统的“地基”。

### 🐳 安装 Docker Desktop
这个系统被打包在“容器”里，就像集装箱一样，Docker 负责搬运和运行这些集装箱。

1.  **下载**：访问 [Docker 官网下载页面](https://www.docker.com/products/docker-desktop/)。
2.  **安装**：下载对应你电脑系统（Windows/Mac/Linux）的版本并安装。
    *   *Windows 用户提示*：安装过程中如果提示启用 WSL 2 (Windows Subsystem for Linux)，请勾选并同意，这是 Docker 在 Windows 上运行必须的组件。
3.  **启动**：安装完成后，双击桌面的 Docker Desktop 图标启动它。
    *   👀 **检查**：看到 Docker 的小鲸鱼图标出现在任务栏，且状态显示为 "Engine running" (绿色)，说明准备好了。

### 🐙 安装 Git (可选，推荐)
用于下载本系统的代码。
1.  **下载**：访问 [Git 官网](https://git-scm.com/downloads) 下载并安装。
2.  **验证**：打开命令行工具（Windows 下是 PowerShell 或 CMD，Mac 下是 Terminal），输入 `git --version`，能看到版本号即可。
    *   *如果不安装 Git*：你也可以直接在 GitHub/GitLab 页面点击 "Download ZIP" 下载代码包并解压。

---

## 2. 获取代码与配置

### 第一步：下载项目
打开你的命令行工具（Terminal/PowerShell），输入以下命令把代码下载到本地：

```bash
git clone <项目仓库地址> grade-system-pro
cd grade-system-pro
```
*(如果你是下载的 ZIP 包，请解压后，在文件夹内右键选择“在终端打开”)*

### 第二步：配置文件 (.env)
系统需要一些密码和设置才能运行。虽然我们提供了默认设置，但创建一个配置文件是好习惯。

1.  在项目根目录下（就是能看到 `docker-compose.yml` 的那个文件夹），创建一个新文件名为 `.env`。
2.  **复制以下内容** 粘贴进去并保存：

```ini
# --- 数据库配置 ---
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=grade_system

# --- 对象存储 (MinIO) ---
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# --- 后端配置 ---
# 注意：在 Docker 中访问其他容器要用服务名 (db, redis, minio)，不要用 localhost
DB_HOST=db
DB_USER=root
DB_PASSWORD=root
DB_NAME=grade_system
REDIS_URL=redis://redis:6379/0
STORAGE_TYPE=minio
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=grade-bucket
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

> 💡 **新手提示**：如果你不想改配置，直接跳过这一步也能运行！我们在 `docker-compose.yml` 里已经内置了这套默认配置。

---

## 3. 启动应用 (Start) 🚀

这是最激动人心的一步！

在命令行中（确保你在项目文件夹下），输入：

```bash
docker-compose up -d
```

*   `up`：启动的意思。
*   `-d`：表示在后台运行（Detached），这样你的命令行窗口不会被占满日志。

**第一次运行会发生什么？**
1.  Docker 会开始下载需要的“镜像” (Images)，包括 Python、Node、MySQL、Redis 等。这可能需要几分钟，取决于你的网速，请耐心等待 ☕。
2.  下载完成后，它会自动启动 6 个服务：
    *   `grade_system_db` (数据库)
    *   `grade_system_redis` (缓存)
    *   `grade_system_minio` (文件存储)
    *   `grade_system_backend` (后端 API)
    *   `grade_system_worker` (后台任务处理)
    *   `grade_system_frontend` (前端网页)

**怎么知道启动成功了？**
输入命令：
```bash
docker-compose ps
```
如果你看到所有服务的状态 (State) 都是 `Up`，那就大功告成了！🎉

---

## 4. 访问应用 🌐

打开你的浏览器（Chrome/Edge/Safari），访问：

*   **http://localhost**

你应该能看到系统的登录页面。

*   **默认管理员账号**：`admin`
*   **默认密码**：`admin123`

---

## 5. 日常操作指南

### ⏸️ 暂停应用 (Pause)
如果你想暂时释放电脑资源，但不想丢失运行状态（比如数据库里的临时数据），可以暂停：

```bash
docker-compose pause
```
*   恢复运行使用：`docker-compose unpause`

### 🛑 停止应用 (Stop)
如果你今天不用了，想关闭系统：

```bash
docker-compose stop
```
这会停止所有容器，但**不会删除数据**。下次使用 `docker-compose up -d` 可以瞬间恢复。

### ♻️ 重启应用 (Restart)
如果系统卡住了，或者你修改了代码想要生效：

```bash
docker-compose restart
```
或者单独重启某一个服务（比如后端）：
```bash
docker-compose restart backend
```

### 🧹 彻底移除 (Teardown)
**⚠️ 警告**：这将删除所有容器和**所有数据**（数据库、上传的文件等都会清空）。仅在你想彻底重置环境时使用。

```bash
docker-compose down -v
```
*   `-v`：表示同时删除数据卷 (Volumes)。

---

## 6. 常见问题 (Troubleshooting)

**Q1: 启动时报错 "Port already in use" (端口被占用)**
*   **原因**：你电脑上可能已经运行了 MySQL (3306端口) 或其他占用 80/8000 端口的程序。
*   **解决**：
    1.  关闭占用端口的程序。
    2.  或者修改 `docker-compose.yml` 文件。例如把 `3306:3306` 改成 `3307:3306`（冒号左边是对外端口，随便改）。

**Q2: 浏览器访问 localhost 显示 "无法连接"**
*   **原因**：后端服务还没完全启动（Python 启动需要几秒钟）。
*   **解决**：
    1.  等几十秒再刷新。
    2.  查看后端日志检查有无报错：`docker-compose logs backend`

**Q3: 登录提示 "Network Error"**
*   **原因**：前端连接不上后端 API。
*   **解决**：
    1.  确保后端容器正在运行 (`docker-compose ps`)。
    2.  检查浏览器控制台 (F12) 的网络请求，看 API 地址是否正确指向了 `localhost:8000`。

---

祝你使用愉快！如有其他问题，请联系开发团队。
