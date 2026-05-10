const mockUsers = [
  {
    id: '1',
    username: 'admin',
    password: 'admin123',
    email: 'admin@example.com',
    name: '管理员'
  },
  {
    id: '2',
    username: 'user',
    password: 'user123',
    email: 'user@example.com',
    name: '普通用户'
  }
]

export const mockAuthAPI = {
  login: (data) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const user = mockUsers.find(
          u => u.username === data.username && u.password === data.password
        )
        if (user) {
          resolve({
            token: `mock-token-${user.id}-${Date.now()}`,
            user: {
              id: user.id,
              username: user.username,
              email: user.email,
              name: user.name
            }
          })
        } else {
          reject({
            response: {
              data: {
                message: '用户名或密码错误'
              },
              status: 401
            }
          })
        }
      }, 500)
    })
  },
  register: (data) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const exists = mockUsers.some(u => u.username === data.username)
        if (exists) {
          reject({
            response: {
              data: {
                message: '用户名已存在'
              },
              status: 400
            }
          })
        } else {
          const newUser = {
            id: String(mockUsers.length + 1),
            username: data.username,
            password: data.password,
            email: data.email,
            name: data.name || data.username
          }
          mockUsers.push(newUser)
          resolve({
            token: `mock-token-${newUser.id}-${Date.now()}`,
            user: {
              id: newUser.id,
              username: newUser.username,
              email: newUser.email,
              name: newUser.name
            }
          })
        }
      }, 500)
    })
  }
}
