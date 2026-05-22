import '@testing-library/jest-dom'

// Provide a minimal ResizeObserver mock for jsdom tests
class ResizeObserverMock {
	constructor(callback: any) {}
	observe() {}
	unobserve() {}
	disconnect() {}
}

(global as any).ResizeObserver = ResizeObserverMock
