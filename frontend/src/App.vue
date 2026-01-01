<template>
  <el-container class="layout-container">
    <el-aside width="220px">
      <div class="logo">
        <el-icon><School /></el-icon> 智能阅卷系统
      </div>
      <el-menu
        :default-active="route.name"
        class="el-menu-vertical"
        router
      >
        <el-menu-item index="config" :route="{name: 'config'}">
          <el-icon><Setting /></el-icon>
          <span>考试设置</span>
        </el-menu-item>
        <el-menu-item index="upload" :route="{name: 'upload'}">
          <el-icon><Upload /></el-icon>
          <span>答卷上传 & 阅卷</span>
        </el-menu-item>
        <el-menu-item index="results" :route="{name: 'results'}">
          <el-icon><DataAnalysis /></el-icon>
          <span>批改结果</span>
        </el-menu-item>
        <el-menu-item index="history" :route="{name: 'history'}">
          <el-icon><Files /></el-icon>
          <span>历史记录</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content">
          <h2>{{ pageTitle }}</h2>
        </div>
      </el-header>
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue';
import { RouterView, useRoute } from 'vue-router'

const route = useRoute();

const pageTitle = computed(() => {
  switch(route.name) {
    case 'config': return '考试配置';
    case 'upload': return '上传与阅卷';
    case 'results': return '成绩分析';
    case 'history': return '历史归档';
    default: return '智能阅卷系统';
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
