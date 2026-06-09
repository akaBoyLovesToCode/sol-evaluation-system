const ALLOWED_TAGS = new Set([
  'B',
  'BR',
  'COL',
  'COLGROUP',
  'DIV',
  'EM',
  'I',
  'LI',
  'OL',
  'P',
  'STRONG',
  'TABLE',
  'TBODY',
  'TD',
  'TH',
  'THEAD',
  'TR',
  'U',
  'UL',
])
const BLOCKED_CONTENT_TAGS = new Set(['IFRAME', 'OBJECT', 'SCRIPT', 'STYLE', 'SVG'])
const ALLOWED_ATTRIBUTES = {
  COL: new Set(['width']),
  TD: new Set(['colspan', 'rowspan']),
  TH: new Set(['colspan', 'rowspan']),
}

const cleanNode = (node) => {
  for (const child of [...node.children]) {
    if (BLOCKED_CONTENT_TAGS.has(child.tagName)) {
      child.remove()
      continue
    }

    if (!ALLOWED_TAGS.has(child.tagName)) {
      cleanNode(child)
      child.replaceWith(...child.childNodes)
      continue
    }

    for (const attribute of [...child.attributes]) {
      const isAllowed = ALLOWED_ATTRIBUTES[child.tagName]?.has(attribute.name)
      const number = Number(attribute.value)
      const isValidSpan =
        ['TD', 'TH'].includes(child.tagName) &&
        ['colspan', 'rowspan'].includes(attribute.name) &&
        /^\d+$/.test(attribute.value) &&
        number >= 1 &&
        number <= 100
      const isValidWidth =
        child.tagName === 'COL' &&
        attribute.name === 'width' &&
        /^\d+$/.test(attribute.value) &&
        number >= 40 &&
        number <= 5000
      if (!isAllowed || (!isValidSpan && !isValidWidth)) {
        child.removeAttribute(attribute.name)
      }
    }
    cleanNode(child)
  }
}

export const sanitizeRichText = (html) => {
  if (typeof html !== 'string' || !html.trim()) return ''
  const template = document.createElement('template')
  template.innerHTML = html
  cleanNode(template.content)
  return template.innerHTML.trim()
}
