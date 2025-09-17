import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
} from '@mui/material';
import CodeIcon from '@mui/icons-material/Code';
import CompareIcon from '@mui/icons-material/Compare';
import BuildIcon from '@mui/icons-material/Build';
import StorageIcon from '@mui/icons-material/Storage';

const Dashboard = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Online Editor',
      description: 'Edit and view your files with syntax highlighting',
      icon: <CodeIcon fontSize="large" />,
      action: 'Go to Editor',
      path: '/editor',
    },
    {
      title: 'File Comparison',
      description: 'Compare files with regex-based matching',
      icon: <CompareIcon fontSize="large" />,
      action: 'Start Comparing',
      path: '/constructor',
    },
    {
      title: 'Script Registry',
      description: 'Manage your Python comparison scripts',
      icon: <StorageIcon fontSize="large" />,
      action: 'View Scripts',
      path: '/scripts',
    },
    {
      title: 'Comparison Templates',
      description: 'Save and reuse comparison configurations',
      icon: <BuildIcon fontSize="large" />,
      action: 'View Templates',
      path: '/comparisons',
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
        Welcome to FileCompareHub. Select a feature to get started.
      </Typography>
      
      <Grid container spacing={3}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ mb: 2, color: 'primary.main' }}>
                  {feature.icon}
                </Box>
                <Typography gutterBottom variant="h6" component="h2">
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  onClick={() => navigate(feature.path)}
                >
                  {feature.action}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      <Box sx={{ mt: 6 }}>
        <Typography variant="h5" gutterBottom>
          Getting Started
        </Typography>
        <Typography variant="body1" paragraph>
          FileCompareHub is a powerful platform for comparing text-based files using flexible regex patterns. 
          You can upload files, create custom comparison workflows, and manage Python scripts for automated comparisons.
        </Typography>
        <Typography variant="body1" paragraph>
          Start by exploring the online editor to view and edit your files, or go to the comparison constructor 
          to create custom comparison workflows with regex patterns.
        </Typography>
      </Box>
    </Container>
  );
};

export default Dashboard;