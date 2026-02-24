import { useEffect, useMemo, useState } from 'react';
import {
  AppShell,
  Button,
  Card,
  Container,
  Group,
  NumberInput,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
  ActionIcon,
  useMantineColorScheme,
  Badge,
} from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { IconMoon, IconSun, IconTrash, IconEdit } from '@tabler/icons-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

const API = 'http://127.0.0.1:8000';

export default function App() {
  const { colorScheme, setColorScheme } = useMantineColorScheme();
  const [entries, setEntries] = useState([]);
  const [stats, setStats] = useState({});
  const [entryDate, setEntryDate] = useState(new Date());
  const [weight, setWeight] = useState(70);
  const [note, setNote] = useState('');
  const [editingId, setEditingId] = useState(null);

  const loadData = async () => {
    const [entriesRes, statsRes] = await Promise.all([
      fetch(`${API}/entries`),
      fetch(`${API}/stats`),
    ]);
    setEntries(await entriesRes.json());
    setStats(await statsRes.json());
  };

  useEffect(() => {
    loadData();
  }, []);

  const submitEntry = async () => {
    const payload = {
      entry_date: entryDate.toISOString().slice(0, 10),
      weight_kg: Number(weight),
      note: note || null,
    };

    if (payload.weight_kg < 20 || payload.weight_kg > 400) {
      alert('Weight must be between 20 and 400 kg');
      return;
    }

    if (editingId) {
      await fetch(`${API}/entries/${editingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      setEditingId(null);
    } else {
      await fetch(`${API}/entries`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    }

    setNote('');
    await loadData();
  };

  const onEdit = (row) => {
    setEditingId(row.id);
    setEntryDate(new Date(row.entry_date));
    setWeight(row.weight_kg);
    setNote(row.note || '');
  };

  const onDelete = async (id) => {
    await fetch(`${API}/entries/${id}`, { method: 'DELETE' });
    await loadData();
  };

  const chartData = useMemo(() => [...entries].reverse(), [entries]);

  return (
    <AppShell padding="md">
      <Container size="lg">
        <Stack>
          <Group justify="space-between">
            <Title order={2}>Weight Tracker MVP</Title>
            <ActionIcon
              variant="default"
              onClick={() => setColorScheme(colorScheme === 'dark' ? 'light' : 'dark')}
            >
              {colorScheme === 'dark' ? <IconSun size={18} /> : <IconMoon size={18} />}
            </ActionIcon>
          </Group>

          <Group grow>
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
          </Group>

          <Card withBorder>
            <Group align="end">
              <DateInput label="Date" value={entryDate} onChange={setEntryDate} />
              <NumberInput
                label="Weight (kg)"
                value={weight}
                min={20}
                max={400}
                onChange={setWeight}
              />
              <TextInput label="Note (optional)" value={note} onChange={(e) => setNote(e.target.value)} />
              <Button onClick={submitEntry}>{editingId ? 'Update' : 'Add'}</Button>
            </Group>
          </Card>

          <Card withBorder h={320}>
            <Title order={4} mb="sm">Progress</Title>
            <ResponsiveContainer width="100%" height="90%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="entry_date" />
                <YAxis domain={['auto', 'auto']} />
                <Tooltip />
                <Line type="monotone" dataKey="weight_kg" stroke="#4c6ef5" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card withBorder>
            <Title order={4} mb="sm">History</Title>
            <Table striped>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Date</Table.Th>
                  <Table.Th>Weight</Table.Th>
                  <Table.Th>Note</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {entries.map((row) => (
                  <Table.Tr key={row.id}>
                    <Table.Td>{row.entry_date}</Table.Td>
                    <Table.Td>{row.weight_kg} kg</Table.Td>
                    <Table.Td>{row.note || '-'}</Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <ActionIcon variant="light" onClick={() => onEdit(row)}>
                          <IconEdit size={16} />
                        </ActionIcon>
                        <ActionIcon variant="light" color="red" onClick={() => onDelete(row.id)}>
                          <IconTrash size={16} />
                        </ActionIcon>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Card>
        </Stack>
      </Container>
    </AppShell>
  );
}
