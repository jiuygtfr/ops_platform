import request from '@/utils/request'

export interface Task {
  id: number;
  name: string;
  command: string;
  mode: string;
  hosts?: any[];
}

export const createTask = async (data: any) => {
  const res = await request.post('/tasks/', data)
  return res.data
}

export const getTask = async (id: number) => {
  const res = await request.get(`/tasks/${id}`)
  return res.data
}
