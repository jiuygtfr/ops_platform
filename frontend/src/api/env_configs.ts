import request from '@/utils/request'

export interface EnvConfig {
    id: number
    name: string
    type: 'account' | 'topology'
    content: string
    created_at: string
    updated_at: string
}

export interface CreateEnvConfigReq {
    name: string
    type: 'account' | 'topology'
    content: string
}

export interface UpdateEnvConfigReq {
    name: string
    type: 'account' | 'topology'
    content: string
}

export const getEnvConfigs = (type?: string) => {
    return request.get<any, EnvConfig[]>('/env-configs/', { params: { type } })
}

export const createEnvConfig = (data: CreateEnvConfigReq) => {
    return request.post<any, EnvConfig>('/env-configs/', data)
}

export const updateEnvConfig = (id: number, data: UpdateEnvConfigReq) => {
    return request.put<any, EnvConfig>(`/env-configs/${id}`, data)
}

export const deleteEnvConfig = (id: number) => {
    return request.delete<any, any>(`/env-configs/${id}`)
}
