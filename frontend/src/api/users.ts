import request from '@/utils/request'

export interface User {
    id: number;
    username: string;
    is_active: boolean;
    is_admin: boolean;
}

export const getUsers = () => {
    return request.get<any, User[]>('/users/')
}

export const createUser = (data: any) => {
    return request.post<any, User>('/users/', data)
}

export const deleteUser = (id: number) => {
    return request.delete<any, any>(`/users/${id}`)
}
