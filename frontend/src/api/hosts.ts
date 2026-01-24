import request from '@/utils/request'

export interface Host {
    id: number
    name: string
    ip: string
    ssh_port: number
    username: string
    auth_type: string
    tags: string[]
}

export const getHosts = () => {
    return request.get<any, Host[]>('/hosts/')
}

export const createHost = (data: any) => {
    return request.post<any, Host>('/hosts/', data)
}

export const updateHost = (id: number, data: any) => {
    return request.put<any, Host>(`/hosts/${id}`, data)
}

export const deleteHost = (id: number) => {
    return request.delete<any, any>(`/hosts/${id}`)
}
