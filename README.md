# 🎓 Smart Grading System Pro

Welcome to the **Smart Grading System Pro** (智能作业批改系统 Pro). This application is a SaaS platform designed for educational institutions to automate exam grading, manage classes, and facilitate collaborative marking.

## 📚 Documentation

*   **[用户手册 (User Manual)](./USER_MANUAL.md)**: Detailed guide on how to use the system features (Exam Config, Grading, Class Management).
*   **[部署指南 (Deployment Guide)](./DEPLOYMENT_GUIDE.md)**: **Start Here!** Step-by-step instructions on how to install, run, and manage the application using Docker. Perfect for beginners.
*   **[系统功能概览 (System Overview)](./docs/system_functional_overview.md)**: Technical architecture and feature breakdown.

## 🚀 Quick Start

1.  **Prerequisites**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2.  **Run**:
    ```bash
    docker-compose up -d
    ```
3.  **Access**: Open [http://localhost](http://localhost) in your browser.
    *   Default Admin: `admin` / `admin123`

## 🛠️ Tech Stack

*   **Frontend**: Vue 3, Element Plus, Vite
*   **Backend**: Python FastAPI, SQLAlchemy, Pydantic
*   **Infrastructure**: Docker, MySQL, Redis, MinIO, Celery

---
*For detailed deployment steps, please refer to the [Deployment Guide](./DEPLOYMENT_GUIDE.md).*
