import request from '@/utils/request'

export const login = async (data: any) => {
  // FastAPI OAuth2PasswordRequestForm expects form data, not JSON
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)
  
  const res = await request.post('/auth/token', formData)
  return res.data
}

export const initAdmin = async () => {
    return await request.post('/auth/init-admin')
}
