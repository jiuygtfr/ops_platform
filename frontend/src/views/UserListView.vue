<template>
  <div class="user-list">
    <div class="header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showAddDialog = true">添加用户</el-button>
    </div>

    <el-table :data="users" style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column label="角色">
          <template #default="scope">
              <el-tag :type="scope.row.is_admin ? 'danger' : 'info'">{{ scope.row.is_admin ? '管理员' : '普通用户' }}</el-tag>
          </template>
      </el-table-column>
      <el-table-column label="状态">
          <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'warning'">{{ scope.row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="danger" size="small" @click="handleDelete(scope.row.id)" :disabled="scope.row.username === 'admin'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showAddDialog" title="添加用户">
      <el-form :model="newUser" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="newUser.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newUser.password" type="password" />
        </el-form-item>
        <el-form-item label="管理员">
            <el-switch v-model="newUser.is_admin" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="handleAddUser">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { getUsers, createUser, deleteUser, type User } from '@/api/users'
import { ElMessage, ElMessageBox } from 'element-plus'

const users = ref<User[]>([])
const showAddDialog = ref(false)
const newUser = ref({
  username: '',
  password: '',
  is_admin: false,
  is_active: true
})

const loadUsers = async () => {
  try {
      users.value = await getUsers()
  } catch (e) {
      // ignore
  }
}

const handleAddUser = async () => {
  if (!newUser.value.username || !newUser.value.password) {
      ElMessage.warning('请输入用户名和密码')
      return
  }
  await createUser(newUser.value)
  ElMessage.success('用户创建成功')
  showAddDialog.value = false
  newUser.value = { username: '', password: '', is_admin: false, is_active: true }
  loadUsers()
}

const handleDelete = async (id: number) => {
    try {
        await ElMessageBox.confirm('确定删除该用户吗?', '警告', { type: 'warning' })
        await deleteUser(id)
        ElMessage.success('已删除')
        loadUsers()
    } catch (e) {
        // cancel
    }
}

onMounted(loadUsers)
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
