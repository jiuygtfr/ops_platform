import request from '@/utils/request'

export interface Host {
  id: number;
  name: string;
  ip: string;
  ssh_port: number;
  username: string;
  auth_type: string;
  tags: string[];
}

export const getHosts = async () => {
  const res = await request.get<Host[]>('/hosts/')
  return res.data
}

export const createHost = async (host: Partial<Host>) => {
  const res = await request.post<Host>('/hosts/', host)
  return res.data
}
