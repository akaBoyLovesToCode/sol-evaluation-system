import { mount } from '@vue/test-utils';
import { describe, it, expect, beforeEach, vi } from 'jest';
import { nextTick } from 'vue';
import { useI18n } from '../mocks/i18n';

// Mock the components and dependencies
vi.mock('vue-i18n', () => ({
  useI18n: () => useI18n(),
}));

// Mock the auth store
const mockAuthStore = {
  user: {
    fullName: 'Test User',
    email: 'test@example.com',
    department: 'Engineering',
    position: 'Developer',
    role: 'user',
  },
  updateProfile: vi.fn().mockResolvedValue({ success: true }),
  changePassword: vi.fn().mockResolvedValue({ success: true }),
  checkAuth: vi.fn().mockResolvedValue(true),
};

vi.mock('../stores/auth', () => ({
  useAuthStore: () => mockAuthStore,
}));

// Mock Element Plus components
const mockElMessage = {
  success: vi.fn(),
  error: vi.fn(),
};

vi.mock('element-plus', () => ({
  ElMessage: mockElMessage,
}));

// Import the component after mocking dependencies
import Profile from '../../src/views/Profile.vue';

describe('Profile.vue', () => {
  let wrapper;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    
    // Mount the component
    wrapper = mount(Profile, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
        },
      },
    });
  });

  it('renders the profile page with correct title', () => {
    expect(wrapper.find('h1').text()).toBe('profile.title');
    expect(wrapper.find('p').text()).toBe('profile.description');
  });

  it('loads user data on mount', async () => {
    await nextTick();
    
    const personalInfo = wrapper.vm.personalInfo;
    expect(personalInfo.fullName).toBe('Test User');
    expect(personalInfo.email).toBe('test@example.com');
    expect(personalInfo.department).toBe('Engineering');
    expect(personalInfo.position).toBe('Developer');
    expect(personalInfo.role).toBe('user');
  });

  it('toggles edit mode when edit button is clicked', async () => {
    expect(wrapper.vm.editPersonalInfo).toBe(false);
    
    // Find and click the edit button
    const editButton = wrapper.find('button[type="primary"]');
    await editButton.trigger('click');
    
    expect(wrapper.vm.editPersonalInfo).toBe(true);
  });

  it('calls updateProfile when form is submitted', async () => {
    // Set edit mode to true
    wrapper.vm.editPersonalInfo = true;
    await nextTick();
    
    // Mock the form validation
    wrapper.vm.personalInfoForm = {
      validate: (callback) => callback(true),
    };
    
    // Call the update method
    await wrapper.vm.updatePersonalInfo();
    
    // Check if the store method was called
    expect(mockAuthStore.updateProfile).toHaveBeenCalledWith({
      fullName: 'Test User',
      email: 'test@example.com',
      department: 'Engineering',
      position: 'Developer',
    });
    
    // Check if success message was shown
    expect(mockElMessage.success).toHaveBeenCalled();
    
    // Check if edit mode was turned off
    expect(wrapper.vm.editPersonalInfo).toBe(false);
  });

  it('calls changePassword when password form is submitted', async () => {
    // Set password data
    wrapper.vm.passwordData.currentPassword = 'CurrentPass123';
    wrapper.vm.passwordData.newPassword = 'NewPass123';
    wrapper.vm.passwordData.confirmPassword = 'NewPass123';
    
    // Mock the form validation
    wrapper.vm.passwordForm = {
      validate: (callback) => callback(true),
      resetFields: vi.fn(),
    };
    
    // Call the change password method
    await wrapper.vm.changePassword();
    
    // Check if the store method was called
    expect(mockAuthStore.changePassword).toHaveBeenCalledWith({
      currentPassword: 'CurrentPass123',
      newPassword: 'NewPass123',
    });
    
    // Check if success message was shown
    expect(mockElMessage.success).toHaveBeenCalled();
    
    // Check if form was reset
    expect(wrapper.vm.passwordData.currentPassword).toBe('');
    expect(wrapper.vm.passwordData.newPassword).toBe('');
    expect(wrapper.vm.passwordData.confirmPassword).toBe('');
    expect(wrapper.vm.passwordForm.resetFields).toHaveBeenCalled();
  });

  it('shows error when passwords do not match', async () => {
    // Set password data with mismatched passwords
    wrapper.vm.passwordData.currentPassword = 'CurrentPass123';
    wrapper.vm.passwordData.newPassword = 'NewPass123';
    wrapper.vm.passwordData.confirmPassword = 'DifferentPass123';
    
    // Mock the form validation
    wrapper.vm.passwordForm = {
      validate: (callback) => callback(true),
    };
    
    // Call the change password method
    await wrapper.vm.changePassword();
    
    // Check if error message was shown
    expect(mockElMessage.error).toHaveBeenCalled();
    
    // Check that the store method was not called
    expect(mockAuthStore.changePassword).not.toHaveBeenCalled();
  });
});