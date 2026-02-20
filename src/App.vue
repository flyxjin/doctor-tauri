<template>
  <div class="app-container">
    <!-- 头部导航 -->
    <header class="app-header">
      <h1>中药材销售管理系统</h1>
      <div class="user-info">
        <span>欢迎使用</span>
      </div>
    </header>
    
    <!-- 侧边栏菜单 -->
    <aside class="app-sidebar">
      <nav>
        <ul>
          <li :class="{ active: currentRoute === 'medicines' }">
            <router-link to="/medicines">药材管理</router-link>
          </li>
          <li :class="{ active: currentRoute === 'prescribe' }">
            <router-link to="/prescribe">开处方</router-link>
          </li>
          <li :class="{ active: currentRoute === 'inventory' }">
            <router-link to="/inventory">库存管理</router-link>
          </li>
          <li :class="{ active: currentRoute === 'history' }">
            <router-link to="/history">处方历史</router-link>
          </li>
        </ul>
      </nav>
    </aside>
    
    <!-- 主内容区 -->
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const currentRoute = computed(() => route.name);
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  background-color: #f5f7fa;
}

/* 应用容器 */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* 头部导航 */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background-color: #1890ff;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 18px;
  font-weight: 600;
}

.user-info {
  font-size: 14px;
}

/* 侧边栏菜单 */
.app-sidebar {
  width: 150px;
  background-color: #fff;
  border-right: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.app-sidebar nav ul {
  list-style: none;
}

.app-sidebar nav ul li {
  margin: 0;
}

.app-sidebar nav ul li a {
  display: block;
  padding: 15px 20px;
  color: #333;
  text-decoration: none;
  transition: all 0.3s;
  border-left: 3px solid transparent;
  font-size: 14px;
}

.app-sidebar nav ul li a:hover {
  background-color: #f0f2f5;
  color: #1890ff;
}

.app-sidebar nav ul li.active a {
  background-color: #e6f7ff;
  color: #1890ff;
  border-left-color: #1890ff;
}

/* 主内容区 */
.app-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 页面容器样式 */
.page-container {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  padding: 20px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
  color: #333;
}

/* 表单样式 */
.form-item {
  margin-bottom: 16px;
}

.form-label {
  display: inline-block;
  width: 100px;
  text-align: right;
  margin-right: 12px;
  font-weight: 500;
}

.form-control {
  width: 300px;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 按钮样式 */
.btn {
  display: inline-block;
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  text-align: center;
}

.btn-primary {
  background-color: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.btn-primary:hover {
  background-color: #40a9ff;
  border-color: #40a9ff;
}

.btn-success {
  background-color: #52c41a;
  border-color: #52c41a;
  color: #fff;
}

.btn-success:hover {
  background-color: #73d13d;
  border-color: #73d13d;
}

.btn-danger {
  background-color: #ff4d4f;
  border-color: #ff4d4f;
  color: #fff;
}

.btn-danger:hover {
  background-color: #ff7875;
  border-color: #ff7875;
}

.btn-default {
  background-color: #fff;
  border-color: #d9d9d9;
  color: #333;
}

.btn-default:hover {
  background-color: #f5f5f5;
  border-color: #1890ff;
  color: #1890ff;
}

/* 表格样式 */
.table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.table th,
.table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.table th {
  background-color: #fafafa;
  font-weight: 600;
  color: #333;
}

.table tr:hover {
  background-color: #f5f5f5;
}

/* 卡片样式 */
.card {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  padding: 20px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid #e8e8e8;
  }
  
  .app-main {
    padding: 10px;
  }
  
  .form-label {
    width: 80px;
  }
  
  .form-control {
    width: 200px;
  }
}
</style>