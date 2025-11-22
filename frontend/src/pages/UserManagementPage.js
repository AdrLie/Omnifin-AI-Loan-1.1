import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TextField,
  MenuItem,
  Button,
  Chip,
  IconButton,
  Stack,
  Divider,
} from '@mui/material';
import { Delete, Refresh } from '@mui/icons-material';
import { useNotification } from '../contexts/NotificationContext';
import { adminService } from '../services/adminService';

const roleOptions = [
  { value: 'simple', label: 'User' },
  { value: 'admin', label: 'Admin' },
  { value: 'superadmin', label: 'Super Admin' },
];

const initialForm = {
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  phone: '',
  password: '',
  password_confirm: '',
  role: 'simple',
};

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState(initialForm);
  const { showNotification } = useNotification();

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await adminService.getUsers();
      setUsers(response.users || []);
    } catch (error) {
      showNotification('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreateUser = async (event) => {
    event.preventDefault();
    if (!form.email || !form.username || !form.password) {
      showNotification('Please fill required fields', 'warning');
      return;
    }
    if (form.password !== form.password_confirm) {
      showNotification('Passwords do not match', 'warning');
      return;
    }
    try {
      setCreating(true);
      await adminService.createUser(form);
      showNotification('User created successfully', 'success');
      setForm(initialForm);
      await loadUsers();
    } catch (error) {
      showNotification('Failed to create user', 'error');
    } finally {
      setCreating(false);
    }
  };

  const handleRoleUpdate = async (userId, role) => {
    try {
      await adminService.updateUser(userId, { role });
      setUsers((prev) =>
        prev.map((user) => (user.id === userId ? { ...user, role } : user))
      );
      showNotification('Role updated', 'success');
    } catch (error) {
      showNotification('Failed to update role', 'error');
    }
  };

  const handleDeactivate = async (userId) => {
    try {
      await adminService.deleteUser(userId);
      showNotification('User deactivated', 'info');
      await loadUsers();
    } catch (error) {
      showNotification('Failed to deactivate user', 'error');
    }
  };

  return (
    <Box>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
        <Paper sx={{ flex: 1, p: 3, borderRadius: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              Users
            </Typography>
            <IconButton sx={{ ml: 'auto' }} onClick={loadUsers} disabled={loading}>
              <Refresh />
            </IconButton>
          </Box>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{user.full_name || user.username}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {user.phone || 'No phone'}
                    </Typography>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <TextField
                      select
                      size="small"
                      value={user.role}
                      onChange={(event) => handleRoleUpdate(user.id, event.target.value)}
                    >
                      {roleOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </TextField>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.is_active ? 'Active' : 'Inactive'}
                      color={user.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      color="error"
                      onClick={() => handleDeactivate(user.id)}
                      disabled={!user.is_active}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {users.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography color="text.secondary">No users found.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </Paper>

        <Paper sx={{ width: { xs: '100%', md: 360 }, p: 3, borderRadius: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
            Create User
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box component="form" onSubmit={handleCreateUser}>
            <Stack spacing={2}>
              <TextField
                label="First Name"
                name="first_name"
                value={form.first_name}
                onChange={handleFormChange}
                fullWidth
              />
              <TextField
                label="Last Name"
                name="last_name"
                value={form.last_name}
                onChange={handleFormChange}
                fullWidth
              />
              <TextField
                label="Email"
                name="email"
                value={form.email}
                onChange={handleFormChange}
                type="email"
                required
                fullWidth
              />
              <TextField
                label="Username"
                name="username"
                value={form.username}
                onChange={handleFormChange}
                required
                fullWidth
              />
              <TextField
                label="Phone"
                name="phone"
                value={form.phone}
                onChange={handleFormChange}
                fullWidth
              />
              <TextField
                label="Role"
                name="role"
                select
                value={form.role}
                onChange={handleFormChange}
                fullWidth
              >
                {roleOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleFormChange}
                required
                fullWidth
              />
              <TextField
                label="Confirm Password"
                name="password_confirm"
                type="password"
                value={form.password_confirm}
                onChange={handleFormChange}
                required
                fullWidth
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                disabled={creating}
              >
                {creating ? 'Creating...' : 'Create User'}
              </Button>
            </Stack>
          </Box>
        </Paper>
      </Stack>
    </Box>
  );
};

export default UserManagementPage;