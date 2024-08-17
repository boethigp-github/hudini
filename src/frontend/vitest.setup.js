
import { vi } from 'vitest'

// Mock the import.meta.env
vi.mock('import.meta', () => ({
    env: {
        VITE_SERVER_URL: 'http://test-server.com',
        // Add any other environment variables your app uses
    },
}))
