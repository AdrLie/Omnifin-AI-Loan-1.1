import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
} from '@mui/material';
import {
  Chat,
  Mic,
  People,
  Analytics,
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Security,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { dashboardService } from '../services/dashboardService';

const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { showNotification } = useNotification();
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsData, activityData] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getRecentActivity(),
      ]);
      setStats(statsData);
      setRecentActivity(activityData.results || activityData);
    } catch (error) {
      showNotification('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Start Chat',
      description: 'Chat with AI assistant for loans',
      icon: <Chat />,
      action: () => navigate('/chat'),
      color: 'primary',
    },
    {
      title: 'Voice Chat',
      description: 'Talk to AI assistant',
      icon: <Mic />,
      action: () => navigate('/voice-chat'),
      color: 'secondary',
    },
  ];

  const adminActions = [
    {
      title: 'User Management',
      description: 'Manage users and permissions',
      icon: <People />,
      action: () => navigate('/users'),
      color: 'info',
    },
    {
      title: 'Analytics',
      description: 'View system analytics',
      icon: <Analytics />,
      action: () => navigate('/analytics'),
      color: 'success',
    },
  ];

  // Helper functions for activity rendering
  const getActivityIcon = (action) => {
    const iconMap = {
      'login': <Security color="info" />,
      'logout': <Security color="action" />,
      'chat_start': <Chat color="primary" />,
      'chat_message': <Chat color="primary" />,
      'voice_start': <Mic color="secondary" />,
      'order_created': <AttachMoney color="success" />,
      'order_updated': <AttachMoney color="success" />,
      'create': <TrendingUp color="success" />,
      'update': <TrendingUp color="info" />,
      'view': <Analytics color="info" />,
    };
    return iconMap[action] || <Analytics color="action" />;
  };

  const getActivityTitle = (action, resourceType) => {
    const titleMap = {
      'login': 'User logged in',
      'logout': 'User logged out',
      'chat_start': 'New chat conversation started',
      'chat_message': 'Chat message sent',
      'voice_start': 'Voice chat session started',
      'order_created': 'New loan application submitted',
      'order_updated': 'Loan application updated',
      'create': `New ${resourceType || 'item'} created`,
      'update': `${resourceType || 'Item'} updated`,
      'view': `${resourceType || 'Content'} viewed`,
    };
    return titleMap[action] || `${action} action performed`;
  };

  const getActivityLabel = (action) => {
    if (action.includes('chat')) return 'Chat';
    if (action.includes('voice')) return 'Voice';
    if (action.includes('order')) return 'Order';
    if (action.includes('login') || action.includes('logout')) return 'Auth';
    return 'Activity';
  };

  const getActivityColor = (action) => {
    if (action.includes('chat')) return 'primary';
    if (action.includes('voice')) return 'secondary';
    if (action.includes('order')) return 'success';
    if (action.includes('login') || action.includes('logout')) return 'info';
    return 'default';
  };

  const formatActivityTime = (timestamp) => {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffInSeconds = Math.floor((now - activityTime) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    return activityTime.toLocaleDateString();
  };

  const StatCard = ({ title, value, icon, trend, color = 'primary' }) => (
    <Card sx={{ height: '100%', borderRadius: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
              {value}
            </Typography>
          </Box>
          <Box sx={{ color: `${color}.main`, fontSize: 40 }}>
            {icon}
          </Box>
        </Box>
        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            {trend > 0 ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
            <Typography variant="body2" color={trend > 0 ? 'success.main' : 'error.main'} sx={{ ml: 1 }}>
              {Math.abs(trend)}%
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Welcome back, {user?.first_name || user?.email}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your financial services today.
        </Typography>
      </Box>

      {/* Stats Grid */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Users"
              value={stats.users.total}
              icon={<People />}
              trend={12}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Active Orders"
              value={stats.orders.total}
              icon={<AttachMoney />}
              trend={8}
              color="success"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Conversations"
              value={stats.conversations.total}
              icon={<Chat />}
              trend={-3}
              color="info"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Insurance Claims"
              value={stats.orders.status_distribution?.insurance || 0}
              icon={<Security />}
              color="warning"
            />
          </Grid>
        </Grid>
      )}

      {/* Quick Actions */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom sx={{ fontWeight: 'bold' }}>
          Quick Actions
        </Typography>
        <Grid container spacing={3}>
          {quickActions.map((action) => (
            <Grid item xs={12} sm={6} md={4} key={action.title}>
              <Card sx={{ cursor: 'pointer', borderRadius: 3, '&:hover': { boxShadow: 6 } }}>
                <CardContent onClick={action.action}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ color: `${action.color}.main`, mr: 2, fontSize: 32 }}>
                      {action.icon}
                    </Box>
                    <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                      {action.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {action.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Admin Actions */}
      {(user?.role === 'admin' || user?.role === 'superadmin') && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom sx={{ fontWeight: 'bold' }}>
            Admin Actions
          </Typography>
          <Grid container spacing={3}>
            {adminActions.map((action) => (
              <Grid item xs={12} sm={6} md={4} key={action.title}>
                <Card sx={{ cursor: 'pointer', borderRadius: 3, '&:hover': { boxShadow: 6 } }}>
                  <CardContent onClick={action.action}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ color: `${action.color}.main`, mr: 2, fontSize: 32 }}>
                        {action.icon}
                      </Box>
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                        {action.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {action.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Recent Activity */}
      <Box>
        <Typography variant="h5" component="h2" gutterBottom sx={{ fontWeight: 'bold' }}>
          Recent Activity
        </Typography>
        <Paper sx={{ borderRadius: 3 }}>
          <List>
            {recentActivity.length > 0 ? (
              recentActivity.slice(0, 5).map((activity, index) => (
                <React.Fragment key={activity.id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemIcon>
                      {getActivityIcon(activity.action)}
                    </ListItemIcon>
                    <ListItemText
                      primary={getActivityTitle(activity.action, activity.resource_type)}
                      secondary={formatActivityTime(activity.created_at)}
                    />
                    <Chip 
                      label={getActivityLabel(activity.action)} 
                      size="small" 
                      color={getActivityColor(activity.action)} 
                    />
                  </ListItem>
                </React.Fragment>
              ))
            ) : (
              <ListItem>
                <ListItemText 
                  primary="No recent activity" 
                  secondary="Activity will appear here once you start using the system"
                />
              </ListItem>
            )}
          </List>
        </Paper>
      </Box>
    </Box>
  );
};

export default DashboardPage;