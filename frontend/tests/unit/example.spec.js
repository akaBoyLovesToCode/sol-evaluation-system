import { mount } from '@vue/test-utils'

// A simple Vue component for testing
const SimpleComponent = {
  template: '<div>{{ message }}</div>',
  props: {
    message: {
      type: String,
      default: 'Hello World',
    },
  },
}

describe('Example Test', () => {
  it('renders a message', () => {
    const message = 'Hello from tests'
    const wrapper = mount(SimpleComponent, {
      props: { message },
    })

    expect(wrapper.text()).toContain(message)
  })
})
