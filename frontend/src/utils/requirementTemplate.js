export const TEMPLATES = [
  {
    id: 'srs',
    name: 'SRS 需求规格说明书',
    description: '适用于瀑布式开发，基于 IEEE 830 标准，文档完整详细',
    icon: '📋',
    tags: ['瀑布式', '详细', '完整'],
    dimensions: [
      { key: 'purpose', label: '编写目的', question: '这份需求文档的编写目的是什么？主要面向哪些读者？' },
      { key: 'background', label: '项目背景', question: '请描述项目的业务背景和要解决的问题？' },
      { key: 'terms', label: '术语定义', question: '项目中是否有需要统一定义的专业术语或缩写？' },
      { key: 'goal', label: '业务目标', question: '本需求要达成的核心业务目标是什么？' },
      { key: 'role', label: '用户角色', question: '系统涉及哪些用户角色？各角色的职责是什么？' },
      { key: 'flow', label: '核心业务流程', question: '请描述核心业务流程的主要步骤？' },
      { key: 'functional', label: '功能需求', question: '系统需要实现哪些具体功能？请逐一描述。' },
      { key: 'performance', label: '性能需求', question: '对系统性能有什么要求？如响应时间、并发量、吞吐量等。' },
      { key: 'security', label: '安全性需求', question: '对数据安全、访问控制、审计日志等有什么要求？' },
      { key: 'availability', label: '可用性需求', question: '对系统可用率、故障恢复时间等有什么要求？' },
      { key: 'compatibility', label: '兼容性需求', question: '需要兼容哪些浏览器、操作系统或设备？' },
      { key: 'tech_constraint', label: '技术约束', question: '是否有技术栈、框架、部署环境等技术限制？' },
      { key: 'business_constraint', label: '业务约束', question: '是否有合规要求、行业标准等业务限制？' },
      { key: 'regulatory', label: '法规约束', question: '是否需要遵守数据保护法、行业监管等法规？' },
      { key: 'exception', label: '异常场景', question: '需要处理哪些异常场景？如网络超时、数据校验失败等。' }
    ],
    sections: [
      {
        id: 'intro',
        title: '1. 引言',
        required: true,
        children: [
          { id: 'intro-purpose', title: '1.1 编写目的', placeholder: '说明本文档的编写目的和预期读者' },
          { id: 'intro-background', title: '1.2 项目背景', placeholder: '描述项目背景、业务场景和要解决的问题' },
          { id: 'intro-terms', title: '1.3 术语定义', placeholder: '定义文档中使用的专业术语和缩写' }
        ]
      },
      {
        id: 'overview',
        title: '2. 需求概述',
        required: true,
        children: [
          { id: 'overview-goal', title: '2.1 业务目标', placeholder: '描述本需求要达成的业务目标' },
          { id: 'overview-role', title: '2.2 用户角色', placeholder: '列出涉及的用户角色及其职责' },
          { id: 'overview-flow', title: '2.3 核心业务流程', placeholder: '描述核心业务流程的主要步骤' }
        ]
      },
      {
        id: 'functional',
        title: '3. 功能需求',
        required: true,
        children: [
          { id: 'func-module-1', title: '3.1 功能模块一', placeholder: '描述第一个功能模块的详细需求' },
          { id: 'func-module-2', title: '3.2 功能模块二', placeholder: '描述第二个功能模块的详细需求' }
        ]
      },
      {
        id: 'non-functional',
        title: '4. 非功能需求',
        required: true,
        children: [
          { id: 'nf-performance', title: '4.1 性能需求', placeholder: '如响应时间、并发量、吞吐量等指标' },
          { id: 'nf-security', title: '4.2 安全性需求', placeholder: '如数据加密、访问控制、审计日志等' },
          { id: 'nf-availability', title: '4.3 可用性需求', placeholder: '如系统可用率、故障恢复时间等' },
          { id: 'nf-compatibility', title: '4.4 兼容性需求', placeholder: '如浏览器兼容、操作系统兼容等' }
        ]
      },
      {
        id: 'constraints',
        title: '5. 约束条件',
        required: true,
        children: [
          { id: 'const-tech', title: '5.1 技术约束', placeholder: '如开发语言、框架、部署环境等技术限制' },
          { id: 'const-business', title: '5.2 业务约束', placeholder: '如合规要求、行业标准等业务限制' },
          { id: 'const-regulatory', title: '5.3 法规约束', placeholder: '如数据保护法、行业监管要求等法规限制' }
        ]
      },
      {
        id: 'exceptions',
        title: '6. 异常场景处理',
        required: true,
        children: [
          { id: 'exc-1', title: '6.1 异常场景一', placeholder: '描述异常场景及处理方式' },
          { id: 'exc-2', title: '6.2 异常场景二', placeholder: '描述异常场景及处理方式' }
        ]
      }
    ],
    generateContent(userInput, exploreData) {
      const exploreMap = {}
      if (exploreData && exploreData.length > 0) {
        exploreData.forEach(item => {
          if (item.dimensionKey && item.content) {
            exploreMap[item.dimensionKey] = item.content
          }
        })
      }
      const lines = ['# 需求规格说明书', '']
      if (userInput) {
        lines.push('> 基于用户原始需求生成，请根据实际情况补充和完善各章节内容。')
        lines.push('')
      }
      this.sections.forEach(section => {
        lines.push(`## ${section.title}`)
        lines.push('')
        section.children.forEach(child => {
          lines.push(`### ${child.title}`)
          lines.push('')
          const sectionKey = child.id.replace(/[^a-z]/gi, '_')
          let filled = false
          for (const [key, value] of Object.entries(exploreMap)) {
            if (sectionKey.includes(key) || child.title.includes(this.getDimensionLabelByKey(key))) {
              lines.push(value)
              filled = true
              break
            }
          }
          if (!filled) {
            lines.push(`> ${child.placeholder}`)
          }
          lines.push('')
        })
      })
      return lines.join('\n')
    },
    getDimensionLabelByKey(key) {
      const dim = this.dimensions.find(d => d.key === key)
      return dim ? dim.label : ''
    },
    generateEmptyContent() {
      const lines = ['# 需求规格说明书', '']
      this.sections.forEach(section => {
        lines.push(`## ${section.title}`)
        lines.push('')
        section.children.forEach(child => {
          lines.push(`### ${child.title}`)
          lines.push('')
          lines.push('')
        })
      })
      return lines.join('\n')
    }
  },
  {
    id: 'user-story',
    name: '用户故事需求文档',
    description: '适用于敏捷式开发，以用户故事为核心，文档简洁聚焦',
    icon: '📝',
    tags: ['敏捷式', '简洁', '聚焦'],
    dimensions: [
      { key: 'background', label: '背景与目标', question: '请描述项目的背景和要达成的目标？' },
      { key: 'scope', label: '范围与优先级', question: '本次需求的范围是什么？哪些功能优先级最高？' },
      { key: 'role', label: '用户角色', question: '系统涉及哪些用户角色？请描述各角色的特征。' },
      { key: 'story', label: '用户故事', question: '请描述核心的用户故事：作为XX，我希望XX，以便XX。' },
      { key: 'acceptance', label: '验收标准', question: '每个用户故事的验收标准是什么？怎样算完成？' },
      { key: 'rule', label: '业务规则', question: '有哪些业务规则需要遵守？如计算逻辑、状态流转等。' },
      { key: 'data', label: '数据需求', question: '涉及哪些核心数据实体？数据之间的关系是什么？' },
      { key: 'non-functional', label: '非功能需求', question: '对性能、安全性、可用性等有什么关键要求？' },
      { key: 'dependency', label: '依赖与假设', question: '有哪些外部依赖？做了哪些假设条件？' }
    ],
    sections: [
      {
        id: 'overview',
        title: '1. 需求概述',
        required: true,
        children: [
          { id: 'ov-background', title: '1.1 背景与目标', placeholder: '描述项目背景和要达成的目标' },
          { id: 'ov-scope', title: '1.2 范围与优先级', placeholder: '明确需求范围和优先级排序' }
        ]
      },
      {
        id: 'roles',
        title: '2. 用户角色',
        required: true,
        children: [
          { id: 'role-1', title: '2.1 角色一', placeholder: '描述用户角色的特征和职责' },
          { id: 'role-2', title: '2.2 角色二', placeholder: '描述用户角色的特征和职责' }
        ]
      },
      {
        id: 'stories',
        title: '3. 用户故事',
        required: true,
        children: [
          { id: 'story-1', title: '3.1 用户故事一', placeholder: '作为XX，我希望XX，以便XX' },
          { id: 'story-1-acceptance', title: '3.1.1 验收标准', placeholder: '列出验收标准，怎样算完成' },
          { id: 'story-2', title: '3.2 用户故事二', placeholder: '作为XX，我希望XX，以便XX' },
          { id: 'story-2-acceptance', title: '3.2.2 验收标准', placeholder: '列出验收标准，怎样算完成' }
        ]
      },
      {
        id: 'rules',
        title: '4. 业务规则',
        required: true,
        children: [
          { id: 'rule-1', title: '4.1 业务规则一', placeholder: '描述业务规则，如计算逻辑、状态流转等' },
          { id: 'rule-2', title: '4.2 业务规则二', placeholder: '描述业务规则' }
        ]
      },
      {
        id: 'data',
        title: '5. 数据需求',
        required: true,
        children: [
          { id: 'data-entity', title: '5.1 核心数据实体', placeholder: '列出核心数据实体及其属性' },
          { id: 'data-relation', title: '5.2 数据关系', placeholder: '描述数据实体之间的关系' }
        ]
      },
      {
        id: 'non-functional',
        title: '6. 非功能需求',
        required: false,
        children: [
          { id: 'nf-key', title: '6.1 关键非功能需求', placeholder: '列出关键的性能、安全、可用性要求' }
        ]
      },
      {
        id: 'dependencies',
        title: '7. 依赖与假设',
        required: false,
        children: [
          { id: 'dep-external', title: '7.1 外部依赖', placeholder: '列出外部系统或服务依赖' },
          { id: 'dep-assumption', title: '7.2 假设条件', placeholder: '列出已做的假设条件' }
        ]
      }
    ],
    generateContent(userInput, exploreData) {
      const exploreMap = {}
      if (exploreData && exploreData.length > 0) {
        exploreData.forEach(item => {
          if (item.dimensionKey && item.content) {
            exploreMap[item.dimensionKey] = item.content
          }
        })
      }
      const lines = ['# 需求文档（敏捷版）', '']
      if (userInput) {
        lines.push('> 基于用户原始需求生成，请根据实际情况补充和完善各章节内容。')
        lines.push('')
      }
      this.sections.forEach(section => {
        lines.push(`## ${section.title}`)
        lines.push('')
        section.children.forEach(child => {
          lines.push(`### ${child.title}`)
          lines.push('')
          const sectionKey = child.id.replace(/[^a-z]/gi, '_')
          let filled = false
          for (const [key, value] of Object.entries(exploreMap)) {
            if (sectionKey.includes(key) || child.title.includes(this.getDimensionLabelByKey(key))) {
              lines.push(value)
              filled = true
              break
            }
          }
          if (!filled) {
            lines.push(`> ${child.placeholder}`)
          }
          lines.push('')
        })
      })
      return lines.join('\n')
    },
    getDimensionLabelByKey(key) {
      const dim = this.dimensions.find(d => d.key === key)
      return dim ? dim.label : ''
    },
    generateEmptyContent() {
      const lines = ['# 需求文档（敏捷版）', '']
      this.sections.forEach(section => {
        lines.push(`## ${section.title}`)
        lines.push('')
        section.children.forEach(child => {
          lines.push(`### ${child.title}`)
          lines.push('')
          lines.push('')
        })
      })
      return lines.join('\n')
    }
  }
]

export function getTemplateById(id) {
  return TEMPLATES.find(t => t.id === id) || TEMPLATES[0]
}

export function recommendTemplate(content) {
  if (!content) return 'srs'
  const agileKeywords = ['迭代', 'sprint', '用户故事', '敏捷', 'scrum', '看板', 'backlog', 'MVP', '增量']
  const waterfallKeywords = ['规格', '阶段', '里程碑', '评审', '基线', '配置管理', '验收测试', 'SRS']
  let agileScore = 0
  let waterfallScore = 0
  const lower = content.toLowerCase()
  agileKeywords.forEach(kw => { if (lower.includes(kw.toLowerCase())) agileScore++ })
  waterfallKeywords.forEach(kw => { if (lower.includes(kw.toLowerCase())) waterfallScore++ })
  return agileScore > waterfallScore ? 'user-story' : 'srs'
}
