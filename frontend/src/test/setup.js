import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock browser APIs that are missing/broken in JSDOM
window.HTMLElement.prototype.scrollIntoView = vi.fn();
window.IntersectionObserver = vi.fn(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
}));

// Mock ResizeObserver
window.ResizeObserver = vi.fn(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
}));
