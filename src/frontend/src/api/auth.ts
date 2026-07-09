import client from './client'

interface TokenResponse {
  access: string
  refresh: string
}

interface UserProfile {
  id: string
  full_name: string
  email: string
  phone_number: string
}

export const authApi = {
  login: async (email: string, password: string) => {
    const { data } = await client.post<TokenResponse>('/auth/login/', { email, password })
    // simplejwt returns only tokens — fetch user profile separately
    client.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
    const { data: user } = await client.get<UserProfile>('/auth/me/')
    return { access: data.access, user }
  },

  register: async (payload: {
    full_name: string
    email: string
    phone_number: string
    password: string
  }) => {
    await client.post('/auth/register/', payload)
    // Registration returns no token — log in immediately after
    return authApi.login(payload.email, payload.password)
  },

  forgotPassword: (email: string) =>
    client.post('/auth/password-reset/request/', { email }).then((r) => r.data),

  resetPassword: (token: string, password: string) =>
    client.post('/auth/password-reset/confirm/', { token, password }).then((r) => r.data),
}
