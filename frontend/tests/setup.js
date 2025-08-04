// Import any global setup for tests
import '@testing-library/jest-dom';
import { config } from '@vue/test-utils';
import { createApp } from 'vue';

// Configure Vue Test Utils
global.Vue = createApp;

// Mock i18n
config.global.mocks = {
  $t: (key) => key,
  $tc: (key, count) => key,
  $te: () => true,
  $d: (date) => date,
  $n: (number) => number,
};

// Mock global objects that might be needed in tests
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock Intersection Observer
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Suppress console errors during tests
console.error = jest.fn();