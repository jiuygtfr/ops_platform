<template>
  <div class="page-container host-list">
    <div class="page-header">
      <h1 class="page-title">主机管理</h1>
      <el-button type="primary" plain @click="handleAdd">添加主机</el-button>
    </div>

    <el-card class="content-card">
      <el-table :data="hosts" style="width: 100%" :header-cell-style="{ background: 'transparent' }">
        <el-table-column prop="name" label="名称">
          <template #default="scope">
            <span class="host-name">{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP 地址" />
        <el-table-column prop="username" label="用户" />
        <el-table-column label="操作" width="100" align="right">
          <template #default="scope">
            <el-dropdown trigger="click">
                <el-button link type="primary" style="color: var(--sf-text-secondary) !important;">
                    <span style="font-size: 18px; line-height: 1;">...</span>
                </el-button>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item @click="openTerminal(scope.row)">连接终端</el-dropdown-item>
                        <el-dropdown-item @click="handleEdit(scope.row)">编辑</el-dropdown-item>
                        <el-dropdown-item divided @click="handleDelete(scope.row)" style="color: #ff3b30;">删除</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 终端对话框/窗口 -->
    <el-dialog
      v-model="terminalVisible"
      title="Web 终端"
      width="90%"
      top="5vh"
      class="terminal-dialog"
      :fullscreen="true"
      :modal="false"
    >
        <el-tabs v-model="activeSessionId" type="card" closable @tab-remove="removeTab" class="terminal-tabs">
            <el-tab-pane
                v-for="item in sessions"
                :key="item.sessionId"
                :label="item.title"
                :name="item.sessionId"
            >
                <div style="height: calc(100vh - 80px);">
                    <TerminalPane :host-id="item.hostId" :session-id="item.sessionId" />
                </div>
            </el-tab-pane>
        </el-tabs>
    </el-dialog>

    <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑主机' : '添加主机'" width="400px" class="apple-dialog">
      <el-form :model="form" label-position="top">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="e.g. Web Server 01" />
        </el-form-item>
        <el-form-item label="IP 地址">
          <el-input v-model="form.ip" placeholder="192.168.1.1" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="root" />
        </el-form-item>
        <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password placeholder="不修改请留空" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive } from 'vue'
import { getHosts, createHost, updateHost, deleteHost, type Host } from '@/api/hosts'
import TerminalPane from '@/components/TerminalPane.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const hosts = ref<Host[]>([])
const showAddDialog = ref(false)
const terminalVisible = ref(false)
const activeSessionId = ref('')
const sessions = ref<{sessionId: string, hostId: number, title: string}[]>([])
const isEdit = ref(false)
const currentId = ref<number | null>(null)

const form = reactive({
  name: '',
  ip: '',
  username: 'root',
  ssh_port: 22,
  auth_type: 'password',
  password: ''
})

const loadHosts = async () => {
  hosts.value = await getHosts()
}

const handleAdd = () => {
    isEdit.value = false
    currentId.value = null
    form.name = ''
    form.ip = ''
    form.username = 'root'
    form.password = ''
    showAddDialog.value = true
}

const handleEdit = (row: Host) => {
    isEdit.value = true
    currentId.value = row.id
    form.name = row.name
    form.ip = row.ip
    form.username = row.username
    form.password = '' // Don't show password
    showAddDialog.value = true
}

const handleDelete = async (row: Host) => {
    try {
        await ElMessageBox.confirm('确定要删除该主机吗？', '提示', {
            type: 'warning'
        })
        await deleteHost(row.id)
        ElMessage.success('删除成功')
        loadHosts()
    } catch (e) {
        // cancel
    }
}

const handleSubmit = async () => {
  try {
      if (isEdit.value && currentId.value) {
          const data = { ...form }
          if (!data.password) delete (data as any).password
          await updateHost(currentId.value, data)
          ElMessage.success('更新成功')
      } else {
          await createHost(form)
          ElMessage.success('添加成功')
      }
      showAddDialog.value = false
      loadHosts()
  } catch (e) {
      ElMessage.error('操作失败')
  }
}

const openTerminal = (host: Host) => {
    const sessionId = Math.random().toString(36).substring(7);
    sessions.value.push({
        sessionId,
        hostId: host.id,
        title: `${host.name}`
    })
    activeSessionId.value = sessionId
    terminalVisible.value = true
}

const removeTab = (targetName: string) => {
    const tabs = sessions.value
    let activeName = activeSessionId.value
    if (activeName === targetName) {
        tabs.forEach((tab, index) => {
            if (tab.sessionId === targetName) {
                const nextTab = tabs[index + 1] || tabs[index - 1]
                if (nextTab) {
                    activeName = nextTab.sessionId
                }
            }
        })
    }
    
    activeSessionId.value = activeName
    sessions.value = tabs.filter(tab => tab.sessionId !== targetName)
    
    if (sessions.value.length === 0) {
        terminalVisible.value = false
    }
}

onMounted(loadHosts)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 40px;
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.host-name {
  font-weight: 600;
  color: var(--sf-text-primary);
}

:deep(.terminal-dialog .el-dialog__body) {
  padding: 0;
  background: #000;
}

:deep(.terminal-dialog .el-dialog__header) {
  display: none;
}
</style>
