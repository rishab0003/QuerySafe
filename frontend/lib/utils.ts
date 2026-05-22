import clsx from 'clsx'

export function cn(...args: any[]) {
  return args.filter(Boolean).join(' ')
}

/** Format a timestamp to HH:MM */
export function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

/** Truncate text with ellipsis */
export function truncate(str: string, max: number): string {
  if (str.length <= max) return str
  return str.slice(0, max) + '…'
}

/** Basic SQL syntax highlighting returning HTML */
export function highlightSQL(sql: string): string {
  const keywords = [
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE',
    'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AS',
    'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET',
    'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE',
    'CREATE', 'TABLE', 'ALTER', 'DROP', 'INDEX', 'VIEW',
    'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT', 'BETWEEN',
    'IS', 'NULL', 'ASC', 'DESC', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
    'UNION', 'ALL', 'EXISTS', 'WITH', 'RECURSIVE',
  ]

  let highlighted = escapeHtml(sql)

  // Highlight keywords
  keywords.forEach((kw) => {
    const regex = new RegExp(`\\b(${kw})\\b`, 'gi')
    highlighted = highlighted.replace(regex, '<span class="keyword">$1</span>')
  })

  // Highlight strings
  highlighted = highlighted.replace(/'([^']*)'/g, '<span class="string">\'$1\'</span>')

  // Highlight numbers
  highlighted = highlighted.replace(/\b(\d+)\b/g, '<span class="number">$1</span>')

  return highlighted
}

/** Escape HTML entities */
export function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/** Generate a unique ID */
export function uid(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

/** Render basic markdown to HTML (safe subset) */
export function renderMarkdown(text: string): string {
  if (!text) return ''
  return text
    .replace(/```([\s\S]*?)```/g, '<pre class="sql-block"><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="qs-chip-jade" style="padding:1px 6px;border-radius:4px;">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h3 style="font-size:14px;font-weight:600;margin:8px 0 4px;color:#B0B0C8;">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 style="font-size:15px;font-weight:600;margin:10px 0 4px;color:#D0D0E0;">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 style="font-size:16px;font-weight:700;margin:12px 0 6px;color:#fff;">$1</h1>')
    .replace(/^[-•] (.+)$/gm, '<li style="margin:2px 0;font-size:13px;">$1</li>')
    .replace(/\n{2,}/g, '<br/><br/>')
    .replace(/\n/g, '<br/>')
}
