import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AppShell,
  ActionIcon,
  Alert,
  Badge,
  Button,
  Card,
  Container,
  Group,
  Loader,
  NumberInput,
  ScrollArea,
  SimpleGrid,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
  useMantineColorScheme,
} from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { useMediaQuery } from '@mantine/hooks';
import {
  IconCheck,
  IconDownload,
  IconEdit,
  IconInfoCircle,
  IconMoon,
  IconSun,
  IconTrash,
  IconX,
} from '@tabler/icons-react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { apiClient, toUserMessage } from './api/client';

export default function App() {
  const { colorScheme, setColorScheme } = useMantineColorScheme();
  const isMobile = useMediaQuery('(max-width: 48em)');

  const [entries, setEntries] = useState([]);
  const [stats, setStats] = useState({});
  const [goal, setGoal] = useState({});
  const [entryDate, setEntryDate] = useState(new Date());
  const [weight, setWeight] = useState(70);
  const [note, setNote] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editingOriginalDate, setEditingOriginalDate] = useState(null);
  const [goalInput, setGoalInput] = useState(70);

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGoalSaving, setIsGoalSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [notification, setNotification] = useState(null);
  const notificationTimeoutRef = useRef(null);

  const showNotification = (type, message) => {
    setNotification({ type, message });
    window.clearTimeout(notificationTimeoutRef.current);
    notificationTimeoutRef.current = window.setTimeout(() => setNotification(null), 3500);
  };

  const loadData = async () => {
    try {
      const [entriesPayload, statsPayload, goalPayload] = await Promise.all([
        apiClient.getEntries(),
        apiClient.getStats(),
        apiClient.getGoal(),
      ]);

      setEntries(entriesPayload);
      setStats(statsPayload);
      setGoal(goalPayload);
      if (goalPayload.goal_weight_kg) {
        setGoalInput(goalPayload.goal_weight_kg);
      }
    } catch (error) {
      showNotification('error', toUserMessage(error, 'Failed to load latest data.'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    return () => {
      window.clearTimeout(notificationTimeoutRef.current);
    };
  }, []);

  const cancelEdit = () => {
    setEditingId(null);
    setEditingOriginalDate(null);
    setEntryDate(new Date());
    setWeight(70);
    setNote('');
    setFormErrors({});
  };

  const submitEntry = async () => {
    setFormErrors({});

    if (!entryDate) {
      showNotification('error', 'Please select a date before saving.');
      return;
    }

    const payload = {
      entry_date: entryDate.toISOString().slice(0, 10),
      weight_kg: Number(weight),
      note: note || null,
    };

    if (payload.weight_kg < 20 || payload.weight_kg > 400) {
      showNotification('error', 'Weight must be between 20 and 400 kg.');
      return;
    }

    const isDateChangeDuringEdit = editingId && editingOriginalDate && payload.entry_date !== editingOriginalDate;
    if (isDateChangeDuringEdit) {
      const confirmed = window.confirm(
        `You changed the date from ${editingOriginalDate} to ${payload.entry_date}. This may overwrite a different day entry. Continue?`,
      );
      if (!confirmed) {
        return;
      }
    }

    setIsSubmitting(true);

    try {
      if (editingId) {
        await apiClient.updateEntry(editingId, payload);
        cancelEdit();
      } else {
        await apiClient.createEntry(payload);
        setNote('');
      }

      await loadData();
      showNotification('success', editingId ? 'Entry updated successfully.' : 'Entry added successfully.');
    } catch (error) {
      if (error instanceof ApiError && error.code === 'VALIDATION_ERROR') {
        setFormErrors(error.fieldErrors);
      }
      showNotification('error', toUserMessage(error, editingId ? 'Failed to update entry.' : 'Failed to add entry.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const saveGoal = async () => {
    setFormErrors((prev) => ({ ...prev, goal_weight_kg: undefined }));
    setIsGoalSaving(true);
    try {
      const goalPayload = await apiClient.updateGoal({ goal_weight_kg: Number(goalInput) });
      setGoal(goalPayload);
      showNotification('success', 'Goal updated.');
    } catch (error) {
      if (error instanceof ApiError && error.code === 'VALIDATION_ERROR') {
        setFormErrors((prev) => ({ ...prev, goal_weight_kg: error.fieldErrors.goal_weight_kg }));
      }
      showNotification('error', toUserMessage(error, 'Could not save goal.'));
    } finally {
      setIsGoalSaving(false);
    }
  };

  const exportCsv = async () => {
    setIsExporting(true);
    try {
      const csvText = await apiClient.exportCsv();
      const blob = new Blob([csvText], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `weight-entries-${new Date().toISOString().slice(0, 10)}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      showNotification('success', 'CSV exported.');
    } catch (error) {
      showNotification('error', toUserMessage(error, 'Could not export CSV.'));
    } finally {
      setIsExporting(false);
    }
  };

  const onEdit = (row) => {
    setEditingId(row.id);
    setEditingOriginalDate(row.entry_date);
    setEntryDate(new Date(row.entry_date));
    setWeight(row.weight_kg);
    setNote(row.note || '');
  };

  const onDelete = async (id) => {
    setDeletingId(id);

    try {
      await apiClient.deleteEntry(id);

      if (editingId === id) {
        cancelEdit();
      }

      await loadData();
      showNotification('success', 'Entry deleted.');
    } catch (error) {
      showNotification('error', toUserMessage(error, 'Unable to delete entry.'));
    } finally {
      setDeletingId(null);
    }
  };

  const chartData = useMemo(() => [...entries].reverse(), [entries]);

  return (
    <AppShell padding="md">
      <Container size="lg" px={isMobile ? 'xs' : 'md'}>
        <Stack gap="md">
          <Group justify="space-between" wrap="nowrap">
            <Title order={isMobile ? 3 : 2}>Weight Tracker MVP</Title>
            <ActionIcon
              variant="default"
              aria-label="Toggle color scheme"
              onClick={() => setColorScheme(colorScheme === 'dark' ? 'light' : 'dark')}
            >
              {colorScheme === 'dark' ? <IconSun size={18} /> : <IconMoon size={18} />}
            </ActionIcon>
          </Group>

          {notification && (
            <Alert
              color={notification.type === 'success' ? 'green' : 'red'}
              icon={notification.type === 'success' ? <IconCheck size={16} /> : <IconX size={16} />}
              withCloseButton
              onClose={() => setNotification(null)}
            >
              {notification.message}
            </Alert>
          )}

          <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="sm">
            <Card withBorder>
              <Text size="sm">Current</Text>
              <Title order={3}>{stats.current_weight ?? '-'} kg</Title>
            </Card>
            <Card withBorder>
              <Text size="sm">Entries</Text>
              <Title order={3}>{stats.entries_count ?? 0}</Title>
            </Card>
            <Card withBorder>
              <Text size="sm">7-day Change</Text>
              <Badge color={(stats.change_last_7 ?? 0) <= 0 ? 'green' : 'orange'}>
                {stats.change_last_7 ?? '-'} kg
              </Badge>
            </Card>
            <Card withBorder>
              <Text size="sm">7-day Avg</Text>
              <Title order={3}>{stats.avg_last_7 ?? '-'} kg</Title>
            </Card>
          </SimpleGrid>

          <Card withBorder>
            <Group justify="space-between" align="end" wrap="wrap">
              <Stack gap={4}>
                <Text size="sm">Goal weight</Text>
                <Group gap="xs">
                  <NumberInput
                    value={goalInput}
                    onChange={(value) => {
                      setGoalInput(value);
                      setFormErrors((prev) => ({ ...prev, goal_weight_kg: undefined }));
                    }}
                    min={20}
                    max={400}
                    step={0.1}
                    w={140}
                    disabled={isGoalSaving}
                    error={formErrors.goal_weight_kg}
                  />
                  <Button size="xs" onClick={saveGoal} loading={isGoalSaving}>Save goal</Button>
                </Group>
              </Stack>
              <Stack gap={2} align="flex-end">
                <Text size="sm">Current: {goal.current_weight ?? '-'} kg</Text>
                <Text size="sm">Goal: {goal.goal_weight_kg ?? '-'} kg</Text>
                <Text size="sm">Remaining: {goal.remaining_kg ?? '-'} kg</Text>
                <Text size="sm">Progress: {goal.progress_percent ?? '-'}%</Text>
              </Stack>
            </Group>
          </Card>

          <Card withBorder>
            <Stack gap="sm">
              {editingId && (
                <Alert color="blue" icon={<IconEdit size={16} />}>
                  <Group justify="space-between" wrap="wrap" gap="xs">
                    <Text size="sm">
                      Editing entry from <strong>{editingOriginalDate}</strong>
                    </Text>
                    <Button variant="subtle" size="xs" onClick={cancelEdit}>
                      Cancel edit
                    </Button>
                  </Group>
                </Alert>
              )}

              <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="sm" verticalSpacing="sm">
                <DateInput
                  label="Date"
                  value={entryDate}
                  onChange={(value) => {
                    setEntryDate(value);
                    setFormErrors((prev) => ({ ...prev, entry_date: undefined }));
                  }}
                  disabled={isSubmitting}
                  error={formErrors.entry_date}
                />
                <NumberInput
                  label="Weight (kg)"
                  value={weight}
                  min={20}
                  max={400}
                  onChange={(value) => {
                    setWeight(value);
                    setFormErrors((prev) => ({ ...prev, weight_kg: undefined }));
                  }}
                  disabled={isSubmitting}
                  error={formErrors.weight_kg}
                />
                <TextInput
                  label="Note (optional)"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  disabled={isSubmitting}
                />
                <Group mt={{ base: 0, sm: 25 }} grow={isMobile} wrap={isMobile ? 'wrap' : 'nowrap'}>
                  <Button onClick={submitEntry} loading={isSubmitting} fullWidth={isMobile}>
                    {editingId ? 'Update' : 'Add'}
                  </Button>
                  {editingId && (
                    <Button
                      variant="default"
                      onClick={cancelEdit}
                      disabled={isSubmitting}
                      fullWidth={isMobile}
                    >
                      Cancel
                    </Button>
                  )}
                </Group>
              </SimpleGrid>
            </Stack>
          </Card>

          <Card withBorder h={isMobile ? 260 : 320}>
            <Group justify="space-between" mb="sm">
              <Title order={4}>Progress</Title>
              <Button
                variant="light"
                size="xs"
                leftSection={<IconDownload size={14} />}
                onClick={exportCsv}
                loading={isExporting}
              >
                Export CSV
              </Button>
            </Group>
            {isLoading ? (
              <Group justify="center" h="85%">
                <Loader size="sm" />
              </Group>
            ) : chartData.length ? (
              <ResponsiveContainer width="100%" height="90%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="entry_date" minTickGap={24} />
                  <YAxis domain={['auto', 'auto']} width={40} />
                  <Tooltip />
                  <Line type="monotone" dataKey="weight_kg" stroke="#4c6ef5" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Group justify="center" h="85%" c="dimmed" gap="xs">
                <IconInfoCircle size={16} />
                <Text size="sm">No data yet. Add your first entry.</Text>
              </Group>
            )}
          </Card>

          <Card withBorder>
            <Title order={4} mb="sm">History</Title>
            {isLoading ? (
              <Group justify="center" py="md">
                <Loader size="sm" />
              </Group>
            ) : isMobile ? (
              <Stack gap="xs">
                {entries.length ? (
                  entries.map((row) => (
                    <Card key={row.id} withBorder p="sm">
                      <Stack gap={6}>
                        <Group justify="space-between" align="center" wrap="nowrap">
                          <Text fw={600}>{row.entry_date}</Text>
                          <Badge variant="light">{row.weight_kg} kg</Badge>
                        </Group>
                        <Text size="sm" c="dimmed">{row.note || 'No note'}</Text>
                        <Group grow>
                          <Button
                            variant="light"
                            leftSection={<IconEdit size={14} />}
                            onClick={() => onEdit(row)}
                            disabled={isSubmitting || deletingId === row.id}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="light"
                            color="red"
                            leftSection={<IconTrash size={14} />}
                            onClick={() => onDelete(row.id)}
                            loading={deletingId === row.id}
                            disabled={isSubmitting}
                          >
                            Delete
                          </Button>
                        </Group>
                      </Stack>
                    </Card>
                  ))
                ) : (
                  <Text c="dimmed" ta="center" py="sm">
                    No entries yet.
                  </Text>
                )}
              </Stack>
            ) : (
              <ScrollArea>
                <Table striped miw={620}>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Date</Table.Th>
                      <Table.Th>Weight</Table.Th>
                      <Table.Th>Note</Table.Th>
                      <Table.Th>Actions</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {entries.length ? (
                      entries.map((row) => (
                        <Table.Tr key={row.id}>
                          <Table.Td>{row.entry_date}</Table.Td>
                          <Table.Td>{row.weight_kg} kg</Table.Td>
                          <Table.Td>{row.note || '-'}</Table.Td>
                          <Table.Td>
                            <Group gap="xs" wrap="nowrap">
                              <ActionIcon
                                variant="light"
                                aria-label={`Edit entry ${row.entry_date}`}
                                onClick={() => onEdit(row)}
                                disabled={isSubmitting || deletingId === row.id}
                              >
                                <IconEdit size={16} />
                              </ActionIcon>
                              <ActionIcon
                                variant="light"
                                color="red"
                                aria-label={`Delete entry ${row.entry_date}`}
                                onClick={() => onDelete(row.id)}
                                loading={deletingId === row.id}
                                disabled={isSubmitting}
                              >
                                <IconTrash size={16} />
                              </ActionIcon>
                            </Group>
                          </Table.Td>
                        </Table.Tr>
                      ))
                    ) : (
                      <Table.Tr>
                        <Table.Td colSpan={4}>
                          <Text c="dimmed" ta="center" py="sm">
                            No entries yet.
                          </Text>
                        </Table.Td>
                      </Table.Tr>
                    )}
                  </Table.Tbody>
                </Table>
              </ScrollArea>
            )}
          </Card>
        </Stack>
      </Container>
    </AppShell>
  );
}
