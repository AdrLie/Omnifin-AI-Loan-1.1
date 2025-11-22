import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { School } from '@mui/icons-material';

const KnowledgeBasePage = () => {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Knowledge Base
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage AI knowledge and prompts
        </Typography>
      </Box>

      <Paper sx={{ p: 4, borderRadius: 3, textAlign: 'center' }}>
        <School sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Knowledge Base Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Knowledge base features are coming soon. This will include:
        </Typography>
        <ul style={{ textAlign: 'left', maxWidth: 400, margin: '20px auto' }}>
          <li>Knowledge entry management</li>
          <li>LLM prompt management</li>
          <li>Version control for prompts</li>
          <li>AI training data management</li>
          <li>FAQ management</li>
          <li>Search and filter functionality</li>
        </ul>
      </Paper>
    </Box>
  );
};

export default KnowledgeBasePage;