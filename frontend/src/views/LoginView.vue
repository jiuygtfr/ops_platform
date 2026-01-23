<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>Ops Platform Login</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px">
        <el-form-item label="Username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">Login</el-button>
        </el-form-item>
      </el-form>
      <div style="text-align: center; margin-top: 10px;">
          <el-link type="info" @click="tryInitAdmin">Initialize Admin (First Run)</el-link>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, initAdmin } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) return
  
  loading.value = true
  try {
    const res = await login(form.value)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('username', res.username)
    localStorage.setItem('is_admin', res.is_admin ? '1' : '0')
    ElMessage.success('Login success')
    router.push('/')
  } catch (e) {
    // Error handled by interceptor
  } finally {
    loading.value = false
  }
}

const tryInitAdmin = async () => {
    try {
        const res = await initAdmin()
        ElMessage.success(res.data.msg || 'Admin initialized')
    } catch(e) {
        // ignore
    }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
}
.card-header {
  text-align: center;
  font-weight: bold;
}
</style>
