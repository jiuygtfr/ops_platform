<template>
  <div class="page-container task-list">
    <div class="page-header">
      <h1 class="page-title">任务管理</h1>
      <el-button type="primary" @click="$router.push('/tasks/new')">
        新建任务
      </el-button>
    </div>

    <el-card class="content-card">
      <el-table :data="tasks" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" min-width="150">
            <template #default="{ row }">
                <router-link :to="`/tasks/${row.id}`" class="task-link">{{ row.name }}</router-link>
            </template>
        </el-table-column>
        <el-table-column prop="mode" label="模式" width="100">
            <template #default="{ row }">
                <el-tag :type="row.mode === 'broadcast' ? 'success' : 'warning'">{{ row.mode === 'broadcast' ? '广播' : '分批' }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="host_count" label="主机数" width="80" />
        <el-table-column label="进度" min-width="200">
            <template #default="{ row }">
                <el-progress 
                    :percentage="row.progress" 
                    :status="row.failed_count > 0 ? 'exception' : (row.status === 'completed' ? 'success' : '')"
                >
                    <template #default="{ percentage }">
                        <span class="progress-text">{{ percentage }}%</span>
                    </template>
                </el-progress>
                <div class="task-stats">
                    <span class="stat-item success" v-if="row.success_count > 0">{{ row.success_count }} 成功</span>
                    <span class="stat-item failed" v-if="row.failed_count > 0">{{ row.failed_count }} 失败</span>
                </div>
            </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
                {{ new Date(row.created_at).toLocaleString() }}
            </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click">
                <el-button link type="primary" style="color: var(--sf-text-secondary) !important;">
                    <span style="font-size: 18px; line-height: 1;">...</span>
                </el-button>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item @click="handleRun(row)">运行</el-dropdown-item>
                        <el-dropdown-item @click="$router.push(`/tasks/new?copyId=${row.id}`)">复制</el-dropdown-item>
                        <el-dropdown-item divided @click="handleDelete(row)" style="color: #ff3b30;">删除</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { getTasks, deleteTask, type Task } from '@/api/tasks'
import { ElMessage, ElMessageBox } from 'element-plus'

const tasks = ref<Task[]>([])
const loading = ref(false)

const loadTasks = async () => {
  loading.value = true
  try {
    tasks.value = await getTasks()
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row: Task) => {
    try {
        await ElMessageBox.confirm('确定要删除该任务记录吗？', '提示', {
            type: 'warning'
        })
        await deleteTask(row.id)
        ElMessage.success('删除成功')
        loadTasks()
    } catch (e) {
        // cancel
    }
}

onMounted(loadTasks)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.task-link {
    color: var(--el-color-primary);
    text-decoration: none;
    font-weight: 500;
}

.task-link:hover {
    text-decoration: underline;
}
</style>
