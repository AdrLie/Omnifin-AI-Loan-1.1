import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { Settings } from '@mui/icons-material';

const SettingsPage = () => {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          System Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure system-wide settings and API integrations
        </Typography>
      </Box>

      <Paper sx={{ p: 4, borderRadius: 3, textAlign: 'center' }}>
        <Settings sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          System Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Settings management is coming soon. This will include:
        </Typography>
        <ul style={{ textAlign: 'left', maxWidth: 400, margin: '20px auto' }}>
          <li>API configuration management</li>
          <li>LLM provider settings</li>
          <li>Voice AI configuration</li>
          <li>External system integrations</li>
          <li>Security settings</li>
          <li>System preferences</li>
        </ul>
      </Paper>
    </Box>
  );
};

export default SettingsPage;