import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import Sidebar from './Sidebar';
import StatusBar from './StatusBar';
import React from 'react';

// Basic component tests
test('renders Sidebar with navigation links', async () => {
    render(<Sidebar isOpen={true} onClose={() => { }} onNewChat={() => { }} />);
    // Increase timeout for async rendering and handle multiple matches
    const brandElements = await screen.findAllByText(/TrueWealth AI/i, {}, { timeout: 5000 });
    expect(brandElements.length).toBeGreaterThan(0);
    expect(await screen.findByText(/New Chat/i, {}, { timeout: 5000 })).toBeInTheDocument();
});


test('renders StatusBar', () => {
    render(<StatusBar />);
    expect(screen.getByText(/System Online/i)).toBeInTheDocument();
});

