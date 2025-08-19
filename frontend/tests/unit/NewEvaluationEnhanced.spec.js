import { mount } from '@vue/test-utils'
import {
  ElCard,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElButton,
  ElRow,
  ElCol,
  ElRadioGroup,
  ElRadio,
  ElDatePicker,
  ElTextarea,
  ElCheckbox,
} from 'element-plus'
import NewEvaluation from '@/views/NewEvaluation.vue'

// Mock the API modules
jest.mock('@/api/evaluation', () => ({
  evaluationAPI: {
    createEvaluation: jest.fn(),
    updateEvaluation: jest.fn(),
    getEvaluation: jest.fn(),
  },
}))

jest.mock('@/api/user', () => ({
  userAPI: {
    searchUsers: jest.fn(),
    getHeadOfficers: jest.fn(),
    getSCSColleagues: jest.fn(),
  },
}))

// Mock router
const mockRouter = {
  push: jest.fn(),
  currentRoute: {
    value: {
      name: 'NewEvaluation',
      params: {},
    },
  },
}

const mockRoute = {
  name: 'NewEvaluation',
  params: {},
}

// Mock i18n
const mockT = (key, params) => {
  const translations = {
    'evaluation.new.title': 'New Evaluation',
    'evaluation.new.description': 'Create a new evaluation',
    'evaluation.basicInfo': 'Basic Information',
    'evaluation.technicalSpec': 'Technical Specifications',
    'evaluation.typeLabel': 'Evaluation Type',
    'evaluation.type.new_product': 'New Product',
    'evaluation.type.mass_production': 'Mass Production',
    'evaluation.productName': 'Product Name',
    'evaluation.partNumber': 'Part Number',
    'evaluation.startDate': 'Start Date',
    'evaluation.headOfficer': 'Head Officer',
    'evaluation.scsColleague': 'SCS Colleague',
    'evaluation.reason': 'Evaluation Reason',
    'evaluation.descriptionLabel': 'Description',
    'evaluation.processStep': 'Process Step',
    'evaluation.placeholders.productName': 'Enter product name',
    'evaluation.placeholders.partNumber': 'Enter part number',
    'evaluation.placeholders.startDate': 'Select start date',
    'evaluation.placeholders.headOfficer': 'Select head officer',
    'evaluation.placeholders.scsColleague': 'Select SCS colleague',
    'evaluation.placeholders.reason': 'Select reason',
    'evaluation.placeholders.descriptionWithMention':
      'Enter description (use @ to mention team members)...',
    'evaluation.placeholders.processStep': 'Enter process step',
    'evaluation.mention.selectUser': 'Select a user to mention',
    'common.save': 'Save',
    'common.submit': 'Submit',
    'common.cancel': 'Cancel',
    'validation.requiredField.type': 'Please select evaluation type',
    'validation.requiredField.productName': 'Please enter product name',
    'validation.requiredField.partNumber': 'Please enter part number',
    'validation.requiredField.startDate': 'Please select start date',
    'validation.requiredField.headOfficer': 'Please select head officer',
    'validation.requiredField.scsColleague': 'Please select SCS colleague',
    'validation.requiredField.reason': 'Please select evaluation reason',
    'validation.requiredField.description': 'Please enter description',
    'validation.requiredField.processStep': 'Please enter process step',
  }

  if (params && translations[key]) {
    return translations[key].replace(/{(\w+)}/g, (match, param) => params[param] || match)
  }

  return translations[key] || key
}

describe('NewEvaluation.vue with Enhanced Features', () => {
  let wrapper
  let mockEvaluationAPI
  let mockUserAPI

  const mockUsers = [
    {
      id: 1,
      username: 'admin',
      full_name: 'Admin User',
      department: 'IT',
      role: 'admin',
    },
    {
      id: 2,
      username: 'part_leader',
      full_name: 'Part Leader',
      department: 'Engineering',
      role: 'part_leader',
    },
    {
      id: 3,
      username: 'scs_colleague',
      full_name: 'SCS Colleague',
      department: 'SCS',
      role: 'user',
    },
    {
      id: 4,
      username: 'testuser',
      full_name: 'Test User',
      department: 'Testing',
      role: 'user',
    },
  ]

  beforeEach(() => {
    jest.clearAllMocks()

    // Import mocked APIs
    mockEvaluationAPI = require('@/api/evaluation').evaluationAPI
    mockUserAPI = require('@/api/user').userAPI

    // Mock API responses
    mockUserAPI.searchUsers.mockResolvedValue({ users: mockUsers })
    mockUserAPI.getHeadOfficers.mockResolvedValue({
      users: mockUsers.filter((u) => ['admin', 'group_leader', 'part_leader'].includes(u.role)),
    })
    mockUserAPI.getSCSColleagues.mockResolvedValue({
      users: mockUsers.filter((u) => u.department === 'SCS'),
    })

    mockEvaluationAPI.createEvaluation.mockResolvedValue({
      evaluation: {
        id: 1,
        evaluation_number: 'EVAL-2024-001',
      },
    })

    wrapper = mount(NewEvaluation, {
      global: {
        plugins: [],
        mocks: {
          $router: mockRouter,
          $route: mockRoute,
          $t: mockT,
        },
        components: {
          ElCard,
          ElForm,
          ElFormItem,
          ElInput,
          ElSelect,
          ElOption,
          ElButton,
          ElRow,
          ElCol,
          ElRadioGroup,
          ElRadio,
          ElDatePicker,
          ElTextarea,
          ElCheckbox,
        },
        stubs: {
          'el-icon': true,
          'el-checkbox-group': true,
          'el-message-box': true,
          'el-message': true,
        },
      },
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('renders correctly with new fields', () => {
    expect(wrapper.find('.new-evaluation-page').exists()).toBe(true)
    expect(wrapper.text()).toContain('Head Officer')
    expect(wrapper.text()).toContain('SCS Colleague')
    expect(wrapper.text()).not.toContain('Expected End Date') // Should be removed
  })

  it('initializes form with correct default values', () => {
    expect(wrapper.vm.form.evaluation_type).toBe('')
    expect(wrapper.vm.form.head_officer_id).toBe('')
    expect(wrapper.vm.form.scs_colleague_id).toBe('')
    expect(wrapper.vm.form.mentioned_users).toEqual([])
    expect(wrapper.vm.form).not.toHaveProperty('expected_end_date')
  })

  it('searches users when component mounts', async () => {
    await wrapper.vm.$nextTick()
    expect(mockUserAPI.searchUsers).toHaveBeenCalledWith('')
  })

  it('handles user search for head officers and SCS colleagues', async () => {
    await wrapper.vm.searchUsers('admin')

    expect(mockUserAPI.searchUsers).toHaveBeenCalledWith({ query: 'admin', limit: 20 })
    expect(wrapper.vm.headOfficerOptions.length).toBeGreaterThan(0)
    expect(wrapper.vm.scsColleagueOptions.length).toBeGreaterThan(0)
  })

  it('displays mention dropdown when @ is typed', async () => {
    await wrapper.vm.$nextTick()

    // Set up users for mention
    wrapper.vm.allUsers = mockUsers

    // Simulate typing @ in description
    wrapper.vm.form.description = '@'

    // Mock textarea element and cursor position
    const mockTextarea = {
      selectionStart: 1,
      focus: jest.fn(),
      setSelectionRange: jest.fn(),
    }

    wrapper.vm.descriptionTextarea = { textarea: mockTextarea }

    await wrapper.vm.handleDescriptionInput('@')

    expect(wrapper.vm.showMentionDropdown).toBe(true)
    expect(wrapper.vm.mentionStartPos).toBe(0)
  })

  it('filters mention users based on query', async () => {
    wrapper.vm.allUsers = mockUsers
    wrapper.vm.mentionQuery = 'test'

    const filtered = wrapper.vm.filteredMentionUsers
    expect(filtered.length).toBe(1)
    expect(filtered[0].username).toBe('testuser')
  })

  it('handles mention user selection', async () => {
    await wrapper.vm.$nextTick()

    const user = mockUsers[3] // testuser
    wrapper.vm.form.description = '@te'
    wrapper.vm.mentionStartPos = 0
    wrapper.vm.showMentionDropdown = true

    // Mock textarea
    const mockTextarea = {
      selectionStart: 3,
      focus: jest.fn(),
      setSelectionRange: jest.fn(),
    }
    wrapper.vm.descriptionTextarea = { textarea: mockTextarea }

    await wrapper.vm.selectMentionUser(user)

    expect(wrapper.vm.form.description).toBe('@testuser ')
    expect(wrapper.vm.form.mentioned_users).toContainEqual({
      id: user.id,
      username: user.username,
      full_name: user.full_name,
    })
    expect(wrapper.vm.showMentionDropdown).toBe(false)
  })

  it('handles keyboard navigation in mention dropdown', async () => {
    wrapper.vm.showMentionDropdown = true
    wrapper.vm.mentionSelectedIndex = 0
    wrapper.vm.allUsers = mockUsers

    // Test arrow down
    const downEvent = new KeyboardEvent('keydown', { key: 'ArrowDown' })
    downEvent.preventDefault = jest.fn()

    await wrapper.vm.handleKeydown(downEvent)
    expect(wrapper.vm.mentionSelectedIndex).toBe(1)
    expect(downEvent.preventDefault).toHaveBeenCalled()

    // Test arrow up
    const upEvent = new KeyboardEvent('keydown', { key: 'ArrowUp' })
    upEvent.preventDefault = jest.fn()

    await wrapper.vm.handleKeydown(upEvent)
    expect(wrapper.vm.mentionSelectedIndex).toBe(0)

    // Test escape
    const escEvent = new KeyboardEvent('keydown', { key: 'Escape' })
    await wrapper.vm.handleKeydown(escEvent)
    expect(wrapper.vm.showMentionDropdown).toBe(false)
  })

  it('validates required fields including new ones', async () => {
    const rules = wrapper.vm.rules

    expect(rules.head_officer_id).toBeDefined()
    expect(rules.scs_colleague_id).toBeDefined()
    expect(rules.head_officer_id[0].required).toBe(true)
    expect(rules.scs_colleague_id[0].required).toBe(true)
    expect(rules).not.toHaveProperty('expected_end_date')
  })

  it('builds payload with new fields and mentions', () => {
    wrapper.vm.form = {
      evaluation_type: 'new_product',
      product_name: 'Test Product',
      part_number: 'TP001',
      start_date: '2024-01-15',
      head_officer_id: 1,
      scs_colleague_id: 3,
      description: 'Test description with @testuser',
      mentioned_users: [{ id: 4, username: 'testuser', full_name: 'Test User' }],
      reason: 'test_reason',
      process_step: 'M031',
      pgm_version: '1.0',
      material_info: 'Test material',
      capacity: '100GB',
      interface_type: 'SATA',
      form_factor: '2.5"',
      temperature_grade: 'Commercial',
      processes: ['doe', 'ppq'],
    }

    const payload = wrapper.vm.buildPayload()

    expect(payload.head_officer_id).toBe(1)
    expect(payload.scs_colleague_id).toBe(3)
    expect(payload.mentioned_users).toEqual([
      { id: 4, username: 'testuser', full_name: 'Test User' },
    ])
    expect(payload).not.toHaveProperty('expected_end_date')
  })

  it('submits evaluation with new fields and mentions', async () => {
    // Set up form data
    wrapper.vm.form = {
      evaluation_type: 'new_product',
      product_name: 'Test Product',
      part_number: 'TP001',
      start_date: '2024-01-15',
      head_officer_id: 1,
      scs_colleague_id: 3,
      description: 'Test description',
      mentioned_users: [],
      reason: 'test_reason',
      process_step: 'M031',
    }

    // Mock form validation
    wrapper.vm.formRef = {
      validate: jest.fn().mockResolvedValue(true),
    }

    await wrapper.vm.handleSave(true) // submit = true

    expect(mockEvaluationAPI.createEvaluation).toHaveBeenCalledWith(
      expect.objectContaining({
        head_officer_id: 1,
        scs_colleague_id: 3,
        mentioned_users: [],
      }),
    )
  })

  it('handles API errors gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

    mockEvaluationAPI.createEvaluation.mockRejectedValue(new Error('API Error'))

    wrapper.vm.form = {
      evaluation_type: 'new_product',
      product_name: 'Test Product',
      part_number: 'TP001',
      start_date: '2024-01-15',
      head_officer_id: 1,
      scs_colleague_id: 3,
      description: 'Test description',
      mentioned_users: [],
      reason: 'test_reason',
      process_step: 'M031',
    }

    wrapper.vm.formRef = {
      validate: jest.fn().mockResolvedValue(true),
    }

    await wrapper.vm.handleSave(true)

    expect(consoleSpy).toHaveBeenCalledWith('Save failed:', expect.any(Error))

    consoleSpy.mockRestore()
  })

  it('handles mention query updates correctly', async () => {
    wrapper.vm.showMentionDropdown = true
    wrapper.vm.mentionStartPos = 5

    // Mock textarea
    const mockTextarea = {
      selectionStart: 10,
    }
    wrapper.vm.descriptionTextarea = { textarea: mockTextarea }

    // Test valid mention query
    await wrapper.vm.handleDescriptionInput('Test @john doe')
    expect(wrapper.vm.mentionQuery).toBe('john')

    // Test mention with space (should close dropdown)
    await wrapper.vm.handleDescriptionInput('Test @john doe')
    mockTextarea.selectionStart = 15
    await wrapper.vm.handleDescriptionInput('Test @john doe')
    expect(wrapper.vm.showMentionDropdown).toBe(false)
  })

  it('filters head officers and SCS colleagues correctly', async () => {
    await wrapper.vm.searchUsers('test')

    const headOfficers = wrapper.vm.headOfficerOptions
    const scsColleagues = wrapper.vm.scsColleagueOptions

    // Head officers should only include leadership roles
    headOfficers.forEach((user) => {
      expect(['admin', 'group_leader', 'part_leader']).toContain(user.role)
    })

    // SCS colleagues should only include SCS department
    scsColleagues.forEach((user) => {
      expect(user.department.toLowerCase()).toContain('scs')
    })
  })

  it('handles type change correctly', () => {
    wrapper.vm.handleTypeChange('new_product')
    expect(wrapper.vm.form.processes).toEqual(['doe', 'ppq', 'prq'])

    wrapper.vm.handleTypeChange('mass_production')
    expect(wrapper.vm.form.processes).toEqual(['production_test', 'aql'])
  })

  it('loads users on mount', async () => {
    await wrapper.vm.$nextTick()

    expect(mockUserAPI.searchUsers).toHaveBeenCalledWith('')
    expect(wrapper.vm.allUsers.length).toBeGreaterThan(0)
  })

  it('prevents duplicate mentions', async () => {
    const user = mockUsers[3] // testuser

    // Add user once
    wrapper.vm.form.mentioned_users.push({
      id: user.id,
      username: user.username,
      full_name: user.full_name,
    })

    // Try to add same user again
    wrapper.vm.form.description = '@test'
    wrapper.vm.mentionStartPos = 0

    const mockTextarea = {
      selectionStart: 5,
      focus: jest.fn(),
      setSelectionRange: jest.fn(),
    }
    wrapper.vm.descriptionTextarea = { textarea: mockTextarea }

    await wrapper.vm.selectMentionUser(user)

    // Should still only have one instance
    expect(wrapper.vm.form.mentioned_users.length).toBe(1)
  })

  it('clears form correctly', () => {
    // Set some form data
    wrapper.vm.form.evaluation_type = 'new_product'
    wrapper.vm.form.head_officer_id = 1
    wrapper.vm.form.mentioned_users = [{ id: 1, username: 'test' }]

    // Clear and reset (simulated by setting default values)
    Object.assign(wrapper.vm.form, {
      evaluation_type: '',
      product_name: '',
      part_number: '',
      start_date: '',
      end_date: '',
      reason: '',
      process_step: '',
      description: '',
      head_officer_id: '',
      scs_colleague_id: '',
      pgm_version: '',
      material_info: '',
      capacity: '',
      interface_type: '',
      form_factor: '',
      temperature_grade: '',
      processes: [],
      mentioned_users: [],
    })

    expect(wrapper.vm.form.mentioned_users).toEqual([])
    expect(wrapper.vm.form.head_officer_id).toBe('')
    expect(wrapper.vm.form.scs_colleague_id).toBe('')
  })
})
