import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { Analytics } from '@mui/icons-material';

const AnalyticsPage = () => {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive analytics and reporting for your platform
        </Typography>
      </Box>

      <Paper sx={{ p: 4, borderRadius: 3, textAlign: 'center' }}>
        <Analytics sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Advanced analytics features are coming soon. This will include:
        </Typography>
        <ul style={{ textAlign: 'left', maxWidth: 400, margin: '20px auto' }}>
          <li>User engagement metrics</li>
          <li>Conversation analytics</li>
          <li>Order processing statistics</li>
          <li>AI performance metrics</li>
          <li>Interactive charts and graphs</li>
          <li>Exportable reports</li>
        </ul>
      </Paper>
    </Box>
  );
};

export default AnalyticsPage;