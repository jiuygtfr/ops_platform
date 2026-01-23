<template>
  <div class="app-container">
    <header class="app-header" v-if="!isLoginPage">
      <div class="header-content">
        <div class="logo">
          <!-- <span class="logo-icon"></span> -->
          <img src="https://coresg-normal.trae.ai/api/ide/v1/text_to_image?prompt=Cute%20robot%20icon%20futuristic%20tech%20style%20blue%20and%20white%20minimalist%20vector&image_size=square" alt="Robot" class="logo-img" />
          <span class="logo-text">Ops Platform</span>
        </div>
        <nav class="nav-links">
          <router-link to="/" class="nav-item" active-class="active">主机管理</router-link>
          <router-link to="/tasks" class="nav-item" active-class="active">任务下发</router-link>
          <router-link to="/users" class="nav-item" active-class="active" v-if="isAdmin">用户管理</router-link>
        </nav>
        <div class="user-actions">
           <!-- <span class="user-name">Admin</span> -->
           <!-- <a @click="logout" class="logout-link">退出</a> -->
        </div>
      </div>
    </header>

    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const isLoginPage = computed(() => route.path === '/login')
const isAdmin = computed(() => localStorage.getItem('is_admin') === '1')

const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('is_admin')
    router.push('/login')
}
</script>

<style src="@/assets/main.css"></style>
<style scoped>
.app-container {
  min-height: 100vh;
  background-color: var(--sf-bg-primary);
  display: flex;
  flex-direction: column;
}

.app-header {
  height: 44px;
  background-color: rgba(22, 22, 23, 0.8);
  backdrop-filter: blur(20px);
  position: sticky;
  top: 0;
  z-index: 9999;
  width: 100%;
}

.header-content {
  max-width: 980px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 22px;
}

.logo {
  display: flex;
  align-items: center;
  color: #f5f5f7;
  font-size: 14px;
  font-weight: 600;
  cursor: default;
}

.logo-icon {
  font-size: 18px;
  margin-right: 8px;
  margin-bottom: 2px;
}

.logo-img {
  width: 24px;
  height: 24px;
  margin-right: 8px;
  border-radius: 4px;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-item {
  color: #e8e8ed;
  text-decoration: none;
  font-size: 12px;
  opacity: 0.8;
  transition: opacity 0.3s;
  letter-spacing: -0.01em;
}

.nav-item:hover {
  opacity: 1;
}

.nav-item.active {
  opacity: 1;
  color: #fff;
}

.app-main {
  flex: 1;
  max-width: 980px;
  width: 100%;
  margin: 40px auto;
  padding: 0 22px;
  box-sizing: border-box;
}
</style>
