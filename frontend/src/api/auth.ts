import request from '@/utils/request'

export const login = (data: any) => {
  // FastAPI OAuth2PasswordRequestForm expects form data, not JSON
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)
  
  return request.post<any, any>('/auth/token', formData)
}

export const initAdmin = () => {
    return request.post<any, any>('/auth/init-admin')
}
