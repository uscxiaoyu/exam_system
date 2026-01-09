<template>
  <div v-if="isLogin" class="full-screen">
    <RouterView />
  </div>
  <div v-else-if="isStudent" class="full-screen-student">
    <el-container class="layout-container">
      <el-header
        style="
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #fff;
        "
      >
        <div class="logo">
          <el-icon><School /></el-icon> Online Exam System (Student)
        </div>
        <el-button @click="logout">Logout</el-button>
      </el-header>
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </div>
  <el-container v-else class="layout-container">
    <el-aside width="220px">
      <div class="logo">
        <el-icon><School /></el-icon> 智能阅卷系统
      </div>
      <el-menu :default-active="route.name" class="el-menu-vertical" router>
        <el-menu-item index="upload" :route="{ name: 'upload' }">
          <el-icon><Upload /></el-icon>
          <span>学生答卷上传</span>
        </el-menu-item>
        <el-menu-item index="exams" :route="{ name: 'exams' }">
          <el-icon><Monitor /></el-icon>
          <span>在线考试管理</span>
        </el-menu-item>
        <el-menu-item index="objective" :route="{ name: 'objective' }">
          <el-icon><CircleCheck /></el-icon>
          <span>客观题阅卷</span>
        </el-menu-item>
        <el-menu-item index="classes" :route="{ name: 'classes' }">
          <el-icon><User /></el-icon>
          <span>班级管理</span>
        </el-menu-item>
        <el-menu-item index="tasks" :route="{ name: 'tasks' }">
          <el-icon><List /></el-icon>
          <span>任务分配</span>
        </el-menu-item>
        <el-menu-item index="subjective" :route="{ name: 'subjective' }">
          <el-icon><EditPen /></el-icon>
          <span>主观题阅卷</span>
        </el-menu-item>
        <el-menu-item index="results" :route="{ name: 'results' }">
          <el-icon><DataAnalysis /></el-icon>
          <span>批改结果</span>
        </el-menu-item>
        <el-menu-item index="history" :route="{ name: 'history' }">
          <el-icon><Files /></el-icon>
          <span>历史记录</span>
        </el-menu-item>
        <el-menu-item index="settings" :route="{ name: 'settings' }">
          <el-icon><Setting /></el-icon>
          <span>系统配置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div
          class="header-content"
          style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
          "
        >
          <h2>{{ pageTitle }}</h2>
          <el-button type="danger" plain size="small" @click="logout">
            <el-icon style="margin-right: 5px"><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </el-header>
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from "vue";
import { RouterView, useRoute, useRouter } from "vue-router";
import { useUserStore } from "./stores/user";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isLogin = computed(() => route.name === "login");
const isStudent = computed(
  () => userStore.user && userStore.user.role === "student"
);

const logout = () => {
  userStore.setToken("");
  userStore.setUser(null);
  router.push("/login");
};

const pageTitle = computed(() => {
  switch (route.name) {
    case "upload":
      return "学生答卷上传";
    case "exams":
      return "在线考试管理";
    case "objective":
      return "客观题阅卷";
    case "classes":
      return "班级与学生管理";
    case "tasks":
      return "阅卷任务分配";
    case "subjective":
      return "主观题智能阅卷";
    case "results":
      return "成绩分析";
    case "history":
      return "历史归档";
    case "settings":
      return "系统配置";
    default:
      return "智能阅卷系统";
  }
});
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #f8f9fa;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
  border-bottom: 1px solid #e6e6e6;
  gap: 8px;
}

.el-menu {
  border-right: none;
  background-color: transparent;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
