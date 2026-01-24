import request from '@/utils/request'

export interface Task {
    id: number
    name: string
    command: string
    mode: string
    created_at: string
    host_count: number
    success_count: number
    failed_count: number
    progress: number
    status: string
}

export interface TaskDetail {
    id: number
    name: string
    mode: string
    created_at?: string
    command?: string
    batch_size?: number
    batch_interval?: number
    on_batch_fail_strategy?: string
    hosts: {
        host_id: number
        status: string
        exit_code: number | null
        error: string | null
    }[]
}

export interface CreateTaskReq {
    name: string
    command: string
    host_ids: number[]
    mode: string
    batch_size?: number | null
    batch_interval?: number | null
    on_batch_fail_strategy?: string | null
}

export const getTasks = () => {
    return request.get<any, Task[]>('/tasks/')
}

export const getTask = (id: number) => {
    return request.get<any, TaskDetail>(`/tasks/${id}`)
}

export const createTask = (data: CreateTaskReq) => {
    return request.post<any, { task_id: number }>('/tasks/', data)
}

export const deleteTask = (id: number) => {
    return request.delete<any, any>(`/tasks/${id}`)
}

export const runTaskAgain = (id: number) => {
    return request.post<any, { task_id: number }>(`/tasks/${id}/run`)
}
