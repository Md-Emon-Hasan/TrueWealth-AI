import { render, screen, fireEvent } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import ChatInterface from './ChatInterface';
import App from '../App';
import React from 'react';

// Mock axios client
vi.mock('../api/client', () => ({
    default: {
        post: vi.fn(() => Promise.resolve({ data: { response: 'AI Response', source: 'test' } })),
        get: vi.fn(() => Promise.resolve({ data: { status: 'healthy' } })),
    },
}));

test('renders ChatInterface and handles input', async () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/Ask detailed questions/i);
    const sendBtn = screen.getByRole('button', { name: /send message/i });

    fireEvent.change(input, { target: { value: 'Hello AI' } });
    fireEvent.click(sendBtn);

    // Verify user message appears - use findByText as it's likely async
    expect(await screen.findByText(/Hello AI/i)).toBeInTheDocument();
});


test('renders App with Sidebar and Chat', async () => {
    render(<App />);
    expect(await screen.findAllByText(/TrueWealth AI/i)).not.toHaveLength(0);
});

