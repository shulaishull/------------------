import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';
import { getComparisons, createComparison, updateComparison, deleteComparison } from '../services/api';

const Comparisons = () => {
  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('create'); // 'create' or 'edit'
  const [currentComparison, setCurrentComparison] = useState({
    id: null,
    name: '',
    config: {},
  });

  useEffect(() => {
    fetchComparisons();
  }, []);

  const fetchComparisons = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await getComparisons();
      setComparisons(response.data);
    } catch (err) {
      setError('Failed to fetch comparisons: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    setCurrentComparison({
      id: null,
      name: '',
      config: {
        file1: '',
        file2: '',
        regex_pattern: '',
        filter_pattern: '',
        group_by: '',
      },
    });
    setDialogMode('create');
    setOpenDialog(true);
  };

  const handleOpenEdit = (comparison) => {
    setCurrentComparison(comparison);
    setDialogMode('edit');
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleSaveComparison = async () => {
    try {
      if (dialogMode === 'create') {
        await createComparison({
          name: currentComparison.name,
          config: JSON.stringify(currentComparison.config),
        });
      } else {
        await updateComparison(currentComparison.id, {
          name: currentComparison.name,
          config: JSON.stringify(currentComparison.config),
        });
      }
      
      handleCloseDialog();
      fetchComparisons();
    } catch (err) {
      setError('Failed to save comparison: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeleteComparison = async (id) => {
    try {
      await deleteComparison(id);
      fetchComparisons();
    } catch (err) {
      setError('Failed to delete comparison: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleConfigChange = (field, value) => {
    setCurrentComparison({
      ...currentComparison,
      config: {
        ...currentComparison.config,
        [field]: value,
      },
    });
  };

  const filteredComparisons = comparisons.filter(comparison =>
    comparison.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Comparison Templates
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Search templates"
            variant="outlined"
            size="small"
            fullWidth
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              endAdornment: <SearchIcon />,
            }}
          />
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenCreate}
          >
            Add Template
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Configuration</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredComparisons.map((comparison) => (
                  <TableRow key={comparison.id}>
                    <TableCell>{comparison.name}</TableCell>
                    <TableCell>
                      <Chip label={`Files: 2`} size="small" sx={{ mr: 0.5 }} />
                      {comparison.config.regex_pattern && (
                        <Chip label="Regex" size="small" sx={{ mr: 0.5 }} />
                      )}
                      {comparison.config.filter_pattern && (
                        <Chip label="Filter" size="small" sx={{ mr: 0.5 }} />
                      )}
                    </TableCell>
                    <TableCell>
                      {new Date(comparison.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleOpenEdit(comparison)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDeleteComparison(comparison.id)}>
                        <DeleteIcon />
                      </IconButton>
                      <IconButton>
                        <PlayIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'create' ? 'Create New Template' : 'Edit Template'}
        </DialogTitle>
        <DialogContent>
          <TextField
            label="Template Name"
            fullWidth
            margin="normal"
            value={currentComparison.name}
            onChange={(e) => setCurrentComparison({...currentComparison, name: e.target.value})}
          />
          
          <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
            Configuration
          </Typography>
          
          <TextField
            label="File 1 Path/Content"
            fullWidth
            margin="normal"
            value={currentComparison.config.file1 || ''}
            onChange={(e) => handleConfigChange('file1', e.target.value)}
          />
          
          <TextField
            label="File 2 Path/Content"
            fullWidth
            margin="normal"
            value={currentComparison.config.file2 || ''}
            onChange={(e) => handleConfigChange('file2', e.target.value)}
          />
          
          <TextField
            label="Regex Pattern (Optional)"
            fullWidth
            margin="normal"
            value={currentComparison.config.regex_pattern || ''}
            onChange={(e) => handleConfigChange('regex_pattern', e.target.value)}
            helperText="Pattern to extract specific content from files for comparison"
          />
          
          <TextField
            label="Filter Pattern (Optional)"
            fullWidth
            margin="normal"
            value={currentComparison.config.filter_pattern || ''}
            onChange={(e) => handleConfigChange('filter_pattern', e.target.value)}
            helperText="Regex pattern to exclude matching lines from comparison"
          />
          
          <TextField
            label="Group By Pattern (Optional)"
            fullWidth
            margin="normal"
            value={currentComparison.config.group_by || ''}
            onChange={(e) => handleConfigChange('group_by', e.target.value)}
            helperText="Regex pattern to group differences (first capturing group will be used as key)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveComparison} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Comparisons;