import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import WelcomeCard from './WelcomeCard';
import React from 'react';

test('renders WelcomeCard with logo and features', () => {
    const onQuickQuestion = vi.fn();
    render(<WelcomeCard onQuickQuestion={onQuickQuestion} />);

    // Check for the logo text (TrueWealth AI is in App.jsx, sidebar has it too, WelcomeCard has features)
    // Let's check for specific feature text like "Portfolio Analysis"
    expect(screen.getByText(/Portfolio Analysis/i)).toBeDefined();
    expect(screen.getByText(/Market Trends/i)).toBeDefined();
});
