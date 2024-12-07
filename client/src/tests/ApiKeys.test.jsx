import { render, screen, fireEvent } from '@testing-library/react';
import ApiKeys from '../components/ApiKeys';
import { AuthProvider } from '../contexts/AuthContext';

describe('ApiKeys Component', () => {
  test('renders create key form', () => {
    render(
      <AuthProvider>
        <ApiKeys />
      </AuthProvider>
    );

    expect(screen.getByPlaceholderText('API Key Name')).toBeInTheDocument();
    expect(screen.getByText('Create Key')).toBeInTheDocument();
  });

  test('displays API keys list', async () => {
    const mockKeys = [
      { id: 1, name: 'Test Key', key: 'sk_test123' }
    ];

    // Mock API call
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve(mockKeys)
      })
    );

    render(
      <AuthProvider>
        <ApiKeys />
      </AuthProvider>
    );

    expect(await screen.findByText('Test Key')).toBeInTheDocument();
  });
});