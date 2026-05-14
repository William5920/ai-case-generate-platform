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

const mockRequirements = [
  {
    id: 'req-1',
    title: '用户登录系统需求',
    status: 'completed',
    statusText: '已完成',
    date: '2026-05-12 14:30',
    testPointCount: 3,
    caseCount: 5,
    source: 'standardization'
  },
  {
    id: 'req-2',
    title: '数据导出功能需求',
    status: 'generating',
    statusText: '生成中',
    date: '2026-05-12 10:15',
    testPointCount: 2,
    caseCount: 3,
    source: 'standardization'
  },
  {
    id: 'req-3',
    title: '用户权限管理需求',
    status: 'pending',
    statusText: '待生成',
    date: '2026-05-11 16:45',
    testPointCount: 0,
    caseCount: 0,
    source: 'standardization'
  },
  {
    id: 'req-4',
    title: '账户安全设置需求',
    status: 'completed',
    statusText: '已完成',
    date: '2026-05-10 09:20',
    testPointCount: 4,
    caseCount: 8,
    source: 'standardization'
  },
  {
    id: 'req-5',
    title: '交易记录查询需求',
    status: 'pending',
    statusText: '待生成',
    date: '2026-05-09 11:30',
    testPointCount: 0,
    caseCount: 0,
    source: 'standardization'
  },
  {
    id: 'req-6',
    title: '系统通知推送需求',
    status: 'completed',
    statusText: '已完成',
    date: '2026-05-08 15:00',
    testPointCount: 2,
    caseCount: 4,
    source: 'standardization'
  },
  {
    id: 'req-7',
    title: '密码重置流程需求',
    status: 'generating',
    statusText: '生成中',
    date: '2026-05-07 08:45',
    testPointCount: 1,
    caseCount: 2,
    source: 'standardization'
  }
]

export const buildCaseNote = (caseData) => {
  const propClass = caseData.caseProperty === '正例' ? 'positive' : 'negative'
  const propLabel = caseData.caseProperty
  const sourceLabel = caseData.source
  const sourceClass = caseData.source === 'AI' ? 'ai' : 'manual'

  let html = '<div class="case-note-popover">'
  if (caseData.caseName) {
    html += `<div class="case-note-name">${caseData.caseName}</div>`
  }
  html += `<div class="case-note-header">
    <span class="case-property-tag tag-${propClass}">${propLabel}</span>
    <span class="case-source-tag tag-${sourceClass}">${sourceLabel}</span>
  </div>`
  html += `<div class="case-note-precondition"><span class="label">前置条件：</span>${caseData.preCondition}</div>`
  html += '<div class="case-note-steps"><div class="label">测试步骤：</div>'
  caseData.steps.forEach((step, idx) => {
    html += `<div class="step-item">
      <span class="step-num">${idx + 1}</span>
      <span class="step-name">${step.name}</span>
      <span class="step-desc">${step.description}</span>
      <span class="step-arrow">→</span>
      <span class="step-expect">${step.stepExpectedResult}</span>
    </div>`
  })
  html += '</div></div>'
  return html
}

const mockTaskStore = {}

const mockMindMapData = {
  'req-1': {
    data: {
      text: '用户登录系统需求',
      note: '',
      expand: true,
      _level: 'root',
      _status: 'completed'
    },
    children: [
      {
        data: {
          text: '实现用户登录功能，支持用户名密码验证',
          note: '',
          expand: true,
          _level: 'requirement',
          _status: 'completed'
        },
        children: [
          {
            data: {
              text: '用户名输入验证',
              note: '',
              expand: true,
              _level: 'testPoint',
              _status: 'completed',
              _source: 'AI',
              _marked: false
            },
            children: [
              {
                data: {
                  text: '用户正常登录系统',
                  note: buildCaseNote({
                    caseName: '用户正常登录系统',
                    caseProperty: '正例',
                    preCondition: '用户已注册并拥有有效的账号和密码',
                    source: 'AI',
                    steps: [
                      { name: '输入用户名', description: '在登录页输入正确的用户名', stepExpectedResult: '用户名输入框显示输入的用户名' },
                      { name: '输入密码', description: '在登录页输入正确的密码', stepExpectedResult: '密码输入框显示输入的密码' },
                      { name: '点击登录按钮', description: '点击登录按钮', stepExpectedResult: '系统跳转至用户主页' }
                    ]
                  }),
                  expand: true,
                  _level: 'testCase',
                  _caseProperty: '正例',
                  _source: 'AI',
                  _marked: false
                },
                children: []
              },
              {
                data: {
                  text: '用户登录失败-密码错误',
                  note: buildCaseNote({
                    caseName: '用户登录失败-密码错误',
                    caseProperty: '反例',
                    preCondition: '用户已注册但密码错误',
                    source: 'AI',
                    steps: [
                      { name: '输入用户名', description: '在登录页输入用户名', stepExpectedResult: '用户名输入框显示输入的用户名' },
                      { name: '输入错误密码', description: '在登录页输入错误的密码', stepExpectedResult: '密码输入框显示输入的密码' },
                      { name: '点击登录按钮', description: '点击登录按钮', stepExpectedResult: '系统提示密码错误' }
                    ]
                  }),
                  expand: true,
                  _level: 'testCase',
                  _caseProperty: '反例',
                  _source: 'AI',
                  _marked: false
                },
                children: []
              },
              {
                data: {
                  text: '用户登录失败-用户不存在',
                  note: buildCaseNote({
                    caseName: '用户登录失败-用户不存在',
                    caseProperty: '反例',
                    preCondition: '用户未注册',
                    source: '人工',
                    steps: [
                      { name: '输入用户名', description: '输入不存在的用户名', stepExpectedResult: '用户名输入框显示输入的用户名' },
                      { name: '输入密码', description: '输入任意密码', stepExpectedResult: '密码输入框显示输入的密码' },
                      { name: '点击登录按钮', description: '点击登录按钮', stepExpectedResult: '系统提示用户不存在' }
                    ]
                  }),
                  expand: true,
                  _level: 'testCase',
                  _caseProperty: '反例',
                  _source: '人工',
                  _marked: false
                },
                children: []
              }
            ]
          },
          {
            data: {
              text: '密码输入验证',
              note: '',
              expand: true,
              _level: 'testPoint',
              _status: 'completed',
              _source: 'AI',
              _marked: true
            },
            children: [
              {
                data: {
                  text: '密码为空时登录',
                  note: buildCaseNote({
                    caseName: '密码为空时登录',
                    caseProperty: '反例',
                    preCondition: '用户已注册',
                    source: 'AI',
                    steps: [
                      { name: '输入用户名', description: '输入正确的用户名', stepExpectedResult: '用户名输入框显示输入的用户名' },
                      { name: '密码为空', description: '不输入密码', stepExpectedResult: '密码输入框为空' },
                      { name: '点击登录按钮', description: '点击登录按钮', stepExpectedResult: '系统提示密码不能为空' }
                    ]
                  }),
                  expand: true,
                  _level: 'testCase',
                  _caseProperty: '反例',
                  _source: 'AI',
                  _marked: false
                },
                children: []
              }
            ]
          },
          {
            data: {
              text: '登录按钮状态验证',
              note: '',
              expand: false,
              _level: 'testPoint',
              _status: 'completed',
              _source: '人工',
              _marked: false
            },
            children: []
          }
        ]
      }
    ]
  }
}

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
  },

  applyAiAdjustment: (sessionId, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const { currentMindMapData, markedTestPointTexts, nodeType } = data
        const adjustedData = JSON.parse(JSON.stringify(currentMindMapData))
        const isTestPointLevel = nodeType === 'testPoint'

        if (isTestPointLevel) {
          const newTestCases = [
            { text: '边界值输入验证', _level: 'testCase', _caseProperty: '反例', _source: 'AI', _marked: false },
            { text: '空值处理验证', _level: 'testCase', _caseProperty: '反例', _source: 'AI', _marked: false },
            { text: '正常流程完整验证', _level: 'testCase', _caseProperty: '正例', _source: 'AI', _marked: false }
          ]

          const traverse = (node) => {
            if (!node || !node.children) return
            node.children.forEach((child) => {
              if (child.data && child.data._level === 'testPoint') {
                const preserved = []
                const nonPreserved = []
                ;(child.children || []).forEach(tc => {
                  if (tc.data && tc.data._level === 'testCase') {
                    const isMarked = markedTestPointTexts.includes(tc.data.text)
                    if (isMarked) {
                      preserved.push(tc)
                    } else {
                      nonPreserved.push(tc)
                    }
                  } else {
                    preserved.push(tc)
                  }
                })

                const aiAdded = newTestCases.map(tc => ({
                  data: { ...tc },
                  children: []
                }))

                child.children = [...preserved, ...aiAdded]
              }
              traverse(child)
            })
          }

          traverse(adjustedData)

          resolve({
            success: true,
            code: 200,
            message: 'AI调整完成',
            data: {
              adjustedMindMapData: adjustedData,
              addedCount: newTestCases.length,
              removedCount: 0,
              preservedCount: markedTestPointTexts.length
            }
          })
        } else {
          const newTestPoints = [
            { text: '并发场景验证', _level: 'testPoint', _source: 'AI', _marked: false },
            { text: '超时处理验证', _level: 'testPoint', _source: 'AI', _marked: false },
            { text: '权限校验测试', _level: 'testPoint', _source: 'AI', _marked: false }
          ]

          const traverse = (node) => {
            if (!node || !node.children) return
            node.children.forEach((child, idx) => {
              if (child.data && child.data._level === 'requirement') {
                const preserved = []
                const nonPreserved = []
                ;(child.children || []).forEach(tp => {
                  if (tp.data && tp.data._level === 'testPoint') {
                    const isMarked = markedTestPointTexts.includes(tp.data.text)
                    if (isMarked) {
                      preserved.push(tp)
                    } else {
                      nonPreserved.push(tp)
                    }
                  } else {
                    preserved.push(tp)
                  }
                })

                const aiAdded = newTestPoints.map(tp => ({
                  data: { ...tp },
                  children: []
                }))

                child.children = [...preserved, ...aiAdded]
              }
              traverse(child)
            })
          }

          traverse(adjustedData)

          resolve({
            success: true,
            code: 200,
            message: 'AI调整完成',
            data: {
              adjustedMindMapData: adjustedData,
              addedCount: newTestPoints.length,
              removedCount: 0,
              preservedCount: markedTestPointTexts.length
            }
          })
        }
      }, 1000)
    })
  }
}

export const mockTestDesignAPI = {
  getRequirementList: (params = {}) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        let list = [...mockRequirements]
        const { keyword, status, page = 1, pageSize = 20 } = params

        if (keyword) {
          const kw = keyword.toLowerCase()
          list = list.filter(item => item.title.toLowerCase().includes(kw))
        }

        if (status) {
          list = list.filter(item => item.status === status)
        }

        const total = list.length
        const start = (page - 1) * pageSize
        const pagedList = list.slice(start, start + pageSize)

        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            list: pagedList,
            total,
            page,
            pageSize
          }
        })
      }, 300)
    })
  },

  getMindMapData: (requirementId) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const data = mockMindMapData[requirementId]
        if (data) {
          resolve({
            success: true,
            code: 200,
            message: '操作成功',
            data
          })
        } else {
          resolve({
            success: true,
            code: 200,
            message: '操作成功',
            data: {
              data: {
                text: mockRequirements.find(r => r.id === requirementId)?.title || '未知需求',
                expand: true,
                _level: 'root',
                _status: 'pending'
              },
              children: []
            }
          })
        }
      }, 200)
    })
  },

  generate: (requirementId, options = {}) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const taskId = `task-${Date.now()}`
        mockTaskStore[taskId] = {
          requirementId,
          useKnowledgeBase: options.useKnowledgeBase || false,
          status: 'running',
          progress: 0,
          progressText: '正在初始化...',
          startTime: Date.now()
        }
        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            taskId
          }
        })
      }, 300)
    })
  },

  getTaskStatus: (taskId) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const task = mockTaskStore[taskId]
        if (!task) {
          resolve({
            success: true,
            code: 200,
            message: '操作成功',
            data: {
              taskId,
              status: 'failed',
              progress: 0,
              progressText: '任务不存在'
            }
          })
          return
        }

        if (task.status === 'cancelled') {
          resolve({
            success: true,
            code: 200,
            message: '操作成功',
            data: {
              taskId,
              status: 'cancelled',
              progress: task.progress,
              progressText: '任务已取消'
            }
          })
          return
        }

        const progressSteps = [
          { text: '正在分析需求结构...', target: 15 },
          { text: '正在生成测试点：用户名输入验证', target: 30 },
          { text: '正在生成测试点：密码输入验证', target: 45 },
          { text: '正在生成测试点：登录按钮状态验证', target: 55 },
          { text: '正在生成测试用例：用户正常登录系统', target: 65 },
          { text: '正在生成测试用例：密码错误登录', target: 75 },
          { text: '正在生成测试用例：用户不存在登录', target: 85 },
          { text: '正在整理生成结果...', target: 95 }
        ]

        const elapsed = Date.now() - task.startTime
        const stepDuration = 1500
        const currentStep = Math.min(Math.floor(elapsed / stepDuration), progressSteps.length - 1)
        const stepProgress = Math.min((elapsed % stepDuration) / stepDuration, 1)

        const prevTarget = currentStep > 0 ? progressSteps[currentStep - 1].target : 0
        const currentTarget = progressSteps[currentStep].target
        const progress = Math.round(prevTarget + (currentTarget - prevTarget) * stepProgress)

        task.progress = progress
        task.progressText = progressSteps[currentStep].text

        if (progress >= 95 && elapsed > progressSteps.length * stepDuration + 500) {
          task.status = 'completed'
          task.progress = 100
          task.progressText = '生成完成'
        }

        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            taskId,
            status: task.status,
            progress: task.progress,
            progressText: task.progressText
          }
        })
      }, 200)
    })
  },

  cancelTask: (taskId) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const task = mockTaskStore[taskId]
        if (task) {
          task.status = 'cancelled'
        }
        resolve({
          success: true,
          code: 200,
          message: '任务已取消',
          data: null
        })
      }, 200)
    })
  },

  addTestPoint: (requirementId, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            id: `tp-${Date.now()}`,
            text: data.text,
            description: data.description || '',
            _source: '人工'
          }
        })
      }, 200)
    })
  },

  editTestPoint: (requirementId, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            id: `tp-${Date.now()}`,
            text: data.text,
            description: data.description || ''
          }
        })
      }, 200)
    })
  },

  deleteTestPoint: (requirementId) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          code: 200,
          message: '删除成功',
          data: null
        })
      }, 200)
    })
  },

  addTestCase: (requirementId, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            id: `tc-${Date.now()}`,
            text: data.text,
            caseProperty: data.caseProperty,
            preCondition: data.preCondition || '',
            steps: data.steps || [],
            _source: '人工'
          }
        })
      }, 200)
    })
  },

  deleteTestCase: (requirementId) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          code: 200,
          message: '删除成功',
          data: null
        })
      }, 200)
    })
  },

  editTestCase: (requirementId, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            id: `tc-${Date.now()}`,
            text: data.text,
            caseProperty: data.caseProperty,
            preCondition: data.preCondition || '',
            steps: data.steps || []
          }
        })
      }, 200)
    })
  },

  markTestCase: (testCaseId, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: null
        })
      }, 200)
    })
  },

  createAiSession: (data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const isTestPointLevel = data.nodeType === 'testPoint'
        const markLabel = isTestPointLevel ? '测试用例' : '测试点'
        const markedInfo = data.markedNodeIds && data.markedNodeIds.length > 0
          ? `\n\n已识别到 ${data.markedNodeIds.length} 个标记保留的${markLabel}，调整时将保留这些节点。`
          : ''
        const nodeLabel = isTestPointLevel ? '测试点' : '需求'
        const childLabel = isTestPointLevel ? '测试用例' : '测试点或用例'
        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            sessionId: `session-${Date.now()}`,
            messages: [
              {
                id: 'msg-1',
                role: 'assistant',
                content: `你好！我是AI测试设计助手。\n\n当前正在对「${nodeLabel}」节点进行调整。${markedInfo}\n\n请告诉我你希望如何调整${childLabel}，例如：\n- "增加边界值测试用例"\n- "补充异常场景的测试${isTestPointLevel ? '用例' : '点'}"\n- "优化测试用例的步骤描述"\n- "删除冗余的测试${isTestPointLevel ? '用例' : '点'}"`,
                timestamp: new Date().toISOString()
              }
            ]
          }
        })
      }, 300)
    })
  },

  sendAiMessage: (sessionId, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const aiResponses = [
          {
            content: '好的，我理解你的需求。我会根据你的要求对测试点进行调整，包括：\n\n1. **新增测试点**：补充你提到的场景覆盖\n2. **优化现有用例**：调整用例属性和步骤描述\n3. **删除冗余内容**：移除不必要的测试点\n\n调整完成后会更新脑图，请确认是否执行？',
            type: 'proposal',
            pendingMindMapData: null
          },
          {
            content: '收到！我已经分析了当前的测试设计结构，建议进行以下优化：\n\n- 增加「并发场景」测试点\n- 将「输入验证」拆分为更细粒度的测试点\n- 补充「超时处理」相关用例\n\n是否按此方案执行调整？',
            type: 'proposal',
            pendingMindMapData: null
          },
          {
            content: '分析完成。当前测试设计存在以下可优化点：\n\n1. 缺少「权限校验」相关测试点\n2. 「异常处理」场景覆盖不足\n3. 部分用例步骤描述可以更详细\n\n需要我按照以上分析进行调整吗？',
            type: 'proposal',
            pendingMindMapData: null
          }
        ]
        const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)]

        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            id: `msg-${Date.now()}`,
            role: 'assistant',
            content: randomResponse.content,
            type: randomResponse.type,
            pendingMindMapData: randomResponse.pendingMindMapData,
            timestamp: new Date().toISOString()
          }
        })
      }, 800)
    })
  },

  getAiHistory: (sessionId) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          code: 200,
          message: '操作成功',
          data: {
            sessionId,
            messages: [
              {
                id: 'msg-1',
                role: 'assistant',
                content: '你好！我是AI测试设计助手，请告诉我你希望如何调整测试点或用例。',
                timestamp: new Date(Date.now() - 60000).toISOString()
              }
            ]
          }
        })
      }, 200)
    })
  }
}
