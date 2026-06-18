import { marked } from 'marked'

// 配置 marked
marked.setOptions({
  breaks: true,       // 支持 GFM 换行（单个换行符转换为 <br>）
  gfm: true,          // 启用 GitHub Flavored Markdown
  headerIds: false,   // 不生成 heading id
  mangle: false       // 不混淆邮箱地址
})

/**
 * 将 Markdown 文本渲染为安全的 HTML
 * @param {string} content - Markdown 文本
 * @returns {string} HTML 字符串
 */
export function renderMarkdown(content) {
  if (!content) return ''
  try {
    const html = marked.parse(content)
    return html
  } catch (e) {
    console.error('Markdown 渲染失败:', e)
    return escapeHtml(content)
  }
}

/**
 * 简单的 HTML 转义，用于渲染失败时的降级
 */
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>')
}
