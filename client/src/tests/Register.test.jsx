import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Register from '../pages/Register';
import { validatePassword } from '../utils/validation';

describe('Register Component', () => {
  test('validates password strength', () => {
    expect(validatePassword('weak')).toBe(false);
    expect(validatePassword('StrongPass123!')).toBe(true);
  });

  test('shows validation errors', async () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    );

    const submitButton = screen.getByText('Create Account');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
    });
  });
});