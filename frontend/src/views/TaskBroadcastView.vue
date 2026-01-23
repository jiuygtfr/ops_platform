<template>
  <div class="page-container task-broadcast">
    <div class="page-header">
      <h1 class="page-title">任务下发</h1>
    </div>
    
    <div class="grid-layout">
        <section class="config-section">
            <h2 class="section-title">选择主机</h2>
            <el-card class="content-card host-selection">
                <el-table 
                  :data="hosts" 
                  @selection-change="handleSelectionChange" 
                  style="width: 100%"
                  height="300"
                >
                    <el-table-column type="selection" width="55" />
                    <el-table-column prop="name" label="名称">
                        <template #default="scope">
                            <span class="host-name">{{ scope.row.name }}</span>
                        </template>
                    </el-table-column>
                    <el-table-column prop="ip" label="IP" />
                </el-table>
                <div class="selection-footer">
                    已选择 {{ selectedHosts.length }} 台主机
                </div>
            </el-card>
        </section>

        <section class="command-section">
            <h2 class="section-title">任务配置</h2>
            <el-card class="content-card form-card">
                <el-form label-position="top">
                    <el-form-item label="任务名称">
                        <el-input v-model="taskName" placeholder="例如：批量更新配置" />
                    </el-form-item>
                    <el-form-item label="执行命令">
                        <el-input 
                          v-model="command" 
                          type="textarea" 
                          :rows="6" 
                          placeholder="#!/bin/bash&#10;echo 'Hello World'" 
                          class="code-input"
                        />
                    </el-form-item>
                    <el-form-item label="执行模式">
                        <el-radio-group v-model="mode" class="mode-selector">
                            <el-radio-button label="broadcast">广播模式</el-radio-button>
                            <el-radio-button label="batch">分批执行</el-radio-button>
                        </el-radio-group>
                    </el-form-item>
                    
                    <div v-if="mode === 'batch'" class="batch-options">
                        <el-row :gutter="20">
                            <el-col :span="8">
                                <el-form-item label="每批数量">
                                    <el-input-number v-model="batchSize" :min="1" controls-position="right" style="width: 100%" />
                                </el-form-item>
                            </el-col>
                            <el-col :span="8">
                                <el-form-item label="批次间隔 (秒)">
                                    <el-input-number v-model="batchInterval" :min="0" controls-position="right" style="width: 100%" />
                                </el-form-item>
                            </el-col>
                            <el-col :span="8">
                                <el-form-item label="失败策略">
                                    <el-select v-model="onBatchFailStrategy" style="width: 100%">
                                        <el-option label="继续执行" value="continue" />
                                        <el-option label="暂停等待" value="pause_on_fail" />
                                    </el-select>
                                </el-form-item>
                            </el-col>
                        </el-row>
                    </div>
                    
                    <div class="form-actions">
                        <el-button 
                          type="primary" 
                          size="large" 
                          @click="submitTask" 
                          :disabled="selectedHosts.length === 0 || !command"
                          class="submit-btn"
                        >
                            开始执行
                        </el-button>
                    </div>
                </el-form>
            </el-card>
        </section>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getHosts, type Host } from "@/api/hosts";
import { createTask } from "@/api/tasks";
import { ElMessage } from 'element-plus';

const router = useRouter();
const hosts = ref<Host[]>([]);
const selectedHosts = ref<Host[]>([]);

const taskName = ref("");
const command = ref("");
const mode = ref("broadcast");
const batchSize = ref(2);
const batchInterval = ref(5);
const onBatchFailStrategy = ref("continue");

const loadHosts = async () => {
  hosts.value = await getHosts();
};

const handleSelectionChange = (val: Host[]) => {
  selectedHosts.value = val;
};

const submitTask = async () => {
    try {
        const res = await createTask({
            name: taskName.value || `Task-${new Date().getTime()}`,
            command: command.value,
            host_ids: selectedHosts.value.map(h => h.id),
            mode: mode.value,
            batch_size: mode.value === 'batch' ? batchSize.value : null,
            batch_interval: mode.value === 'batch' ? batchInterval.value : null,
            on_batch_fail_strategy: mode.value === 'batch' ? onBatchFailStrategy.value : null,
        });
        
        ElMessage.success('任务已创建');
        router.push(`/tasks/${res.task_id}`);
    } catch (e) {
        ElMessage.error('任务创建失败');
    }
};

onMounted(loadHosts);
</script>

<style scoped>
.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: 40px;
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.grid-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 40px;
}

@media (min-width: 768px) {
    .grid-layout {
        grid-template-columns: 350px 1fr;
    }
}

.section-title {
    font-size: 24px;
    margin-bottom: 20px;
    letter-spacing: -0.01em;
}

.host-name {
    font-weight: 600;
    color: var(--sf-text-primary);
}

.selection-footer {
    padding: 12px 0 0;
    text-align: right;
    font-size: 12px;
    color: var(--sf-text-secondary);
}

.code-input :deep(textarea) {
    font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    background-color: #fafafa;
}

.batch-options {
    background-color: #f5f5f7;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 24px;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 30px;
}

.submit-btn {
    padding: 12px 40px;
    font-size: 16px;
}
</style>
