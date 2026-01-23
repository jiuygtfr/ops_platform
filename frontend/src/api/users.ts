import request from '@/utils/request'

export interface User {
    id: number;
    username: string;
    is_active: boolean;
    is_admin: boolean;
}

export const getUsers = async () => {
    const res = await request.get<User[]>('/users/')
    return res.data
}

export const createUser = async (data: any) => {
    const res = await request.post<User>('/users/', data)
    return res.data
}

export const deleteUser = async (id: number) => {
    const res = await request.delete(`/users/${id}`)
    return res.data
}
