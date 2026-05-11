/**
 * 需求文档质量评分工具
 * 从完整性、清晰度、一致性三个维度评估文档质量
 */

const REQUIRED_SECTIONS = [
  { key: '引言', label: '引言', weight: 15 },
  { key: '需求概述', label: '需求概述', weight: 15 },
  { key: '功能需求', label: '功能需求', weight: 20 },
  { key: '非功能需求', label: '非功能需求', weight: 20 },
  { key: '约束条件', label: '约束条件', weight: 15 },
  { key: '异常场景', label: '异常场景处理', weight: 15 }
]

const VAGUE_WORDS = ['大概', '可能', '差不多', '也许', '应该', '尽量', '基本上', '一般', '左右', '大约', '差不多']

function extractSections(content) {
  const sections = {}
  const lines = content.split('\n')
  let currentSection = null
  let currentContent = []

  lines.forEach(line => {
    const h2Match = line.match(/^##\s+(.+)/)
    if (h2Match) {
      if (currentSection) {
        sections[currentSection] = currentContent.join('\n').trim()
      }
      currentSection = h2Match[1].trim()
      currentContent = []
    } else if (currentSection) {
      currentContent.push(line)
    }
  })

  if (currentSection) {
    sections[currentSection] = currentContent.join('\n').trim()
  }

  return sections
}

function scoreCompleteness(sections) {
  let score = 0
  const details = []

  REQUIRED_SECTIONS.forEach(section => {
    const content = sections[section.key]
    const hasContent = content && content.length > 10 && !content.startsWith('>')

    if (hasContent) {
      score += section.weight
      details.push({ section: section.label, ok: true })
    } else {
      details.push({ section: section.label, ok: false, suggestion: `「${section.label}」章节内容为空或仅有占位提示，建议补充具体内容` })
    }
  })

  return { score, details }
}

function scoreClarity(content) {
  let score = 100
  const issues = []

  VAGUE_WORDS.forEach(word => {
    const regex = new RegExp(word, 'g')
    const matches = content.match(regex)
    if (matches && matches.length > 0) {
      score -= matches.length * 5
      issues.push(`发现 ${matches.length} 处模糊表述「${word}」，建议替换为具体描述`)
    }
  })

  const hasMetrics = /\d+\s*(秒|分钟|小时|%|次|人|MB|GB|ms|TPS|QPS)/.test(content)
  if (!hasMetrics) {
    score -= 15
    issues.push('未发现明确的量化指标，建议补充具体的性能、容量等数值指标')
  }

  const hasExamples = /例如|比如|示例/.test(content)
  if (!hasExamples) {
    score -= 5
    issues.push('建议添加具体示例帮助理解需求')
  }

  return { score: Math.max(0, score), issues }
}

function scoreConsistency(content) {
  let score = 100
  const issues = []

  const sections = extractSections(content)
  const allText = Object.values(sections).join(' ')

  const termPairs = [
    { a: '登录', b: '登陆' },
    { a: '账号', b: '帐号' },
    { a: '权限', b: '权力' }
  ]

  termPairs.forEach(pair => {
    const hasA = allText.includes(pair.a)
    const hasB = allText.includes(pair.b)
    if (hasA && hasB) {
      score -= 10
      issues.push(`术语不一致：同时使用了「${pair.a}」和「${pair.b}」，建议统一`)
    }
  })

  const hasConflict = /但是|然而|不过|矛盾|冲突/.test(content)
  if (hasConflict) {
    score -= 5
    issues.push('文档中可能存在矛盾描述，建议核实相关内容的逻辑一致性')
  }

  return { score: Math.max(0, score), issues }
}

export function analyzeQuality(content) {
  if (!content || content.trim().length === 0) {
    return {
      overall: 0,
      completeness: { score: 0, details: [] },
      clarity: { score: 0, issues: ['文档内容为空'] },
      consistency: { score: 0, issues: [] },
      suggestions: ['请先完成文档标准化后再查看质量评分'],
      level: 'empty'
    }
  }

  const sections = extractSections(content)
  const completeness = scoreCompleteness(sections)
  const clarity = scoreClarity(content)
  const consistency = scoreConsistency(content)

  const overall = Math.round(
    completeness.score * 0.45 +
    Math.max(0, clarity.score) * 0.35 +
    Math.max(0, consistency.score) * 0.20
  )

  let level = 'poor'
  if (overall >= 80) level = 'good'
  else if (overall >= 60) level = 'medium'

  const suggestions = []

  completeness.details
    .filter(d => !d.ok)
    .forEach(d => suggestions.push(d.suggestion))

  clarity.issues.forEach(i => suggestions.push(i))
  consistency.issues.forEach(i => suggestions.push(i))

  return {
    overall,
    completeness,
    clarity,
    consistency,
    suggestions,
    level
  }
}

export function getLevelConfig(level) {
  const configs = {
    good: {
      label: '良好',
      color: '#10B981',
      bg: 'bg-green-50',
      text: 'text-green-600',
      ring: '#10B981',
      trail: '#D1FAE5'
    },
    medium: {
      label: '一般',
      color: '#F59E0B',
      bg: 'bg-yellow-50',
      text: 'text-yellow-600',
      ring: '#F59E0B',
      trail: '#FEF3C7'
    },
    poor: {
      label: '需改进',
      color: '#EF4444',
      bg: 'bg-red-50',
      text: 'text-red-600',
      ring: '#EF4444',
      trail: '#FEE2E2'
    },
    empty: {
      label: '无数据',
      color: '#9CA3AF',
      bg: 'bg-gray-50',
      text: 'text-gray-400',
      ring: '#D1D5DB',
      trail: '#F3F4F6'
    }
  }
  return configs[level] || configs.empty
}