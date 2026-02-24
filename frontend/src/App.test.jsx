import { MantineProvider } from '@mantine/core';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { ApiError, apiClient } from './api/client';

vi.mock('./api/client', async () => {
  const actual = await vi.importActual('./api/client');
  return {
    ...actual,
    apiClient: {
      getEntries: vi.fn(),
      getStats: vi.fn(),
      getGoal: vi.fn(),
      createEntry: vi.fn(),
      updateEntry: vi.fn(),
      deleteEntry: vi.fn(),
      updateGoal: vi.fn(),
      exportCsv: vi.fn(),
    },
  };
});

function renderApp() {
  return render(
    <MantineProvider>
      <App />
    </MantineProvider>
  );
}

function mockLoad({ entries = [], stats = {}, goal = {} } = {}) {
  apiClient.getEntries.mockResolvedValue(entries);
  apiClient.getStats.mockResolvedValue(stats);
  apiClient.getGoal.mockResolvedValue(goal);
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLoad();
  });

  it('renders and loads initial data', async () => {
    renderApp();

    expect(screen.getAllByText(/weight tracker mvp/i)[0]).toBeInTheDocument();

    await waitFor(() => {
      expect(apiClient.getEntries).toHaveBeenCalledTimes(1);
      expect(apiClient.getStats).toHaveBeenCalledTimes(1);
      expect(apiClient.getGoal).toHaveBeenCalledTimes(1);
    });
  });

  it('adds entry successfully', async () => {
    const user = userEvent.setup();
    apiClient.createEntry.mockResolvedValue({ id: 1 });

    renderApp();
    await waitFor(() => expect(apiClient.getEntries).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole('button', { name: 'Add' }));

    await waitFor(() => {
      expect(apiClient.createEntry).toHaveBeenCalledTimes(1);
      expect(screen.getByText('Entry added successfully.')).toBeInTheDocument();
      expect(apiClient.getEntries).toHaveBeenCalledTimes(2);
    });
  });

  it('shows duplicate date conflict message', async () => {
    const user = userEvent.setup();
    apiClient.createEntry.mockRejectedValue(
      new ApiError({ code: 'ENTRY_DATE_EXISTS', message: 'An entry already exists for this date', status: 409 })
    );

    renderApp();
    await waitFor(() => expect(apiClient.getEntries).toHaveBeenCalledTimes(1));

    await user.click(screen.getByRole('button', { name: 'Add' }));

    expect(await screen.findByText('An entry already exists for this date. Edit that date instead.')).toBeInTheDocument();
  });

  it('supports edit and delete transitions', async () => {
    const user = userEvent.setup();
    mockLoad({
      entries: [{ id: 7, entry_date: '2026-02-22', weight_kg: 78.2, note: 'before' }],
      stats: { entries_count: 1 },
    });

    apiClient.updateEntry.mockResolvedValue({ id: 7, entry_date: '2026-02-22', weight_kg: 77.9 });
    apiClient.deleteEntry.mockResolvedValue({ ok: true });

    renderApp();
    await screen.findByText('2026-02-22');

    await user.click(screen.getByLabelText('Edit entry 2026-02-22'));
    await user.click(screen.getByRole('button', { name: 'Update' }));

    await waitFor(() => expect(apiClient.updateEntry).toHaveBeenCalledTimes(1));
    expect(screen.getByText('Entry updated successfully.')).toBeInTheDocument();

    await user.click(screen.getByLabelText('Delete entry 2026-02-22'));

    await waitFor(() => expect(apiClient.deleteEntry).toHaveBeenCalledWith(7));
    expect(screen.getByText('Entry deleted.')).toBeInTheDocument();
  });
});
