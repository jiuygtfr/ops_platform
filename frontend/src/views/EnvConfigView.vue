<template>
  <div class="page-container env-config">
    <div class="page-header">
      <h1 class="page-title">环境变量管理</h1>
      <el-button type="primary" @click="handleCreate">
        新建配置
      </el-button>
    </div>

    <el-tabs v-model="activeTab" class="demo-tabs" @tab-change="loadConfigs">
        <el-tab-pane label="账户配置" name="account"></el-tab-pane>
        <el-tab-pane label="拓扑配置" name="topology"></el-tab-pane>
    </el-tabs>

    <el-card class="content-card">
      <el-table :data="configs" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="配置名称" />
        <el-table-column prop="updated_at" label="更新时间" width="180">
            <template #default="{ row }">
                {{ new Date(row.updated_at).toLocaleString() }}
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
                        <el-dropdown-item @click="handleEdit(row)">编辑</el-dropdown-item>
                        <el-dropdown-item divided @click="handleDelete(row)" style="color: #ff3b30;">删除</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? '编辑配置' : '新建配置'"
        width="600px"
    >
        <el-form :model="form" label-width="80px">
            <el-form-item label="名称">
                <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item label="类型">
                <el-select v-model="form.type" disabled>
                    <el-option label="账户配置" value="account" />
                    <el-option label="拓扑配置" value="topology" />
                </el-select>
            </el-form-item>
            <el-form-item label="内容">
                <el-input 
                    v-model="form.content" 
                    type="textarea" 
                    :rows="10" 
                    placeholder="请输入 YAML 格式内容"
                    class="code-input"
                />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleSubmit">
                    确定
                </el-button>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive, watch } from 'vue'
import { getEnvConfigs, createEnvConfig, updateEnvConfig, deleteEnvConfig, type EnvConfig } from '@/api/env_configs'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('account')
const configs = ref<EnvConfig[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref<number | null>(null)

const form = reactive({
    name: '',
    type: 'account',
    content: ''
})

const loadConfigs = async () => {
  loading.value = true
  try {
    configs.value = await getEnvConfigs(activeTab.value)
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
    isEdit.value = false
    currentId.value = null
    Object.assign(form, {
        name: '',
        type: activeTab.value,
        content: ''
    })
    dialogVisible.value = true
}

const handleEdit = (row: EnvConfig) => {
    isEdit.value = true
    currentId.value = row.id
    form.name = row.name
    form.type = row.type
    form.content = row.content
    dialogVisible.value = true
}

const handleDelete = async (row: EnvConfig) => {
    try {
        await ElMessageBox.confirm('确定要删除该配置吗？', '提示', {
            type: 'warning'
        })
        await deleteEnvConfig(row.id)
        ElMessage.success('删除成功')
        loadConfigs()
    } catch (e) {
        // cancel
    }
}

const handleSubmit = async () => {
    if (!form.name || !form.content) {
        ElMessage.warning('请填写完整信息')
        return
    }
    
    try {
        if (isEdit.value && currentId.value) {
            await updateEnvConfig(currentId.value, form as any)
            ElMessage.success('更新成功')
        } else {
            await createEnvConfig(form as any)
            ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadConfigs()
    } catch (e) {
        ElMessage.error('操作失败')
    }
}

watch(activeTab, () => {
    loadConfigs()
})

onMounted(loadConfigs)
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

.code-input :deep(textarea) {
    font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    background-color: #1c1c1e;
    color: #f5f5f7;
    line-height: 1.5;
    padding: 12px;
    border: 1px solid #38383a;
}

.code-input :deep(textarea):focus {
    background-color: #000;
    border-color: var(--sf-accent);
}
</style>
