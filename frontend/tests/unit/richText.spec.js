import { sanitizeRichText } from '../../src/utils/richText'

describe('sanitizeRichText', () => {
  it('keeps supported formatting and tables', () => {
    const html =
      '<p><strong>Summary</strong></p><table><colgroup><col width="120"><col width="240"></colgroup><tbody><tr><td>PPM</td><td>0</td></tr></tbody></table>'

    expect(sanitizeRichText(html)).toBe(html)
  })

  it('removes invalid table column widths', () => {
    const html =
      '<table><colgroup><col width="20"><col width="6000"><col width="240px"><col width="240"></colgroup><tbody><tr><td>A</td><td>B</td><td>C</td><td>D</td></tr></tbody></table>'

    expect(sanitizeRichText(html)).toBe(
      '<table><colgroup><col><col><col><col width="240"></colgroup><tbody><tr><td>A</td><td>B</td><td>C</td><td>D</td></tr></tbody></table>',
    )
  })

  it('removes unsafe elements and attributes', () => {
    const html =
      '<div class="ignored">Safe<script>alert("bad")</script><span>Text</span><table><tbody><tr><td onclick="bad()">0</td></tr></tbody></table></div>'

    expect(sanitizeRichText(html)).toBe(
      '<div>SafeText<table><tbody><tr><td>0</td></tr></tbody></table></div>',
    )
  })
})
