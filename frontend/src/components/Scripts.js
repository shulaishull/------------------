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
} from '@mui/icons-material';
import { getScripts, createScript, updateScript, deleteScript } from '../services/api';

const Scripts = () => {
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('create'); // 'create' or 'edit'
  const [currentScript, setCurrentScript] = useState({
    id: null,
    name: '',
    description: '',
    content: '',
    supported_formats: [],
  });
  const [formatInput, setFormatInput] = useState('');

  useEffect(() => {
    fetchScripts();
  }, []);

  const fetchScripts = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await getScripts();
      setScripts(response.data);
    } catch (err) {
      setError('Failed to fetch scripts: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    setCurrentScript({
      id: null,
      name: '',
      description: '',
      content: '',
      supported_formats: [],
    });
    setDialogMode('create');
    setOpenDialog(true);
  };

  const handleOpenEdit = (script) => {
    setCurrentScript(script);
    setDialogMode('edit');
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleSaveScript = async () => {
    try {
      if (dialogMode === 'create') {
        await createScript({
          name: currentScript.name,
          description: currentScript.description,
          content: currentScript.content,
          supported_formats: JSON.stringify(currentScript.supported_formats),
        });
      } else {
        await updateScript(currentScript.id, {
          name: currentScript.name,
          description: currentScript.description,
          content: currentScript.content,
          supported_formats: JSON.stringify(currentScript.supported_formats),
        });
      }
      
      handleCloseDialog();
      fetchScripts();
    } catch (err) {
      setError('Failed to save script: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeleteScript = async (id) => {
    try {
      await deleteScript(id);
      fetchScripts();
    } catch (err) {
      setError('Failed to delete script: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleAddFormat = () => {
    if (formatInput && !currentScript.supported_formats.includes(formatInput)) {
      setCurrentScript({
        ...currentScript,
        supported_formats: [...currentScript.supported_formats, formatInput],
      });
      setFormatInput('');
    }
  };

  const handleRemoveFormat = (format) => {
    setCurrentScript({
      ...currentScript,
      supported_formats: currentScript.supported_formats.filter(f => f !== format),
    });
  };

  const filteredScripts = scripts.filter(script =>
    script.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    script.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Script Registry
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Search scripts"
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
            Add Script
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
                  <TableCell>Description</TableCell>
                  <TableCell>Supported Formats</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredScripts.map((script) => (
                  <TableRow key={script.id}>
                    <TableCell>{script.name}</TableCell>
                    <TableCell>{script.description}</TableCell>
                    <TableCell>
                      {script.supported_formats.map((format, index) => (
                        <Chip
                          key={index}
                          label={format}
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      ))}
                    </TableCell>
                    <TableCell>
                      {new Date(script.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleOpenEdit(script)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDeleteScript(script.id)}>
                        <DeleteIcon />
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
          {dialogMode === 'create' ? 'Create New Script' : 'Edit Script'}
        </DialogTitle>
        <DialogContent>
          <TextField
            label="Script Name"
            fullWidth
            margin="normal"
            value={currentScript.name}
            onChange={(e) => setCurrentScript({...currentScript, name: e.target.value})}
          />
          <TextField
            label="Description"
            fullWidth
            margin="normal"
            multiline
            rows={2}
            value={currentScript.description}
            onChange={(e) => setCurrentScript({...currentScript, description: e.target.value})}
          />
          <TextField
            label="Supported Formats"
            fullWidth
            margin="normal"
            value={formatInput}
            onChange={(e) => setFormatInput(e.target.value)}
            helperText="Press Enter or click Add to include a format"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleAddFormat();
              }
            }}
            InputProps={{
              endAdornment: (
                <Button onClick={handleAddFormat}>Add</Button>
              ),
            }}
          />
          <Box sx={{ mt: 1, mb: 2 }}>
            {currentScript.supported_formats.map((format, index) => (
              <Chip
                key={index}
                label={format}
                onDelete={() => handleRemoveFormat(format)}
                sx={{ mr: 0.5, mb: 0.5 }}
              />
            ))}
          </Box>
          <TextField
            label="Script Content"
            fullWidth
            margin="normal"
            multiline
            rows={15}
            value={currentScript.content}
            onChange={(e) => setCurrentScript({...currentScript, content: e.target.value})}
            sx={{ fontFamily: 'monospace' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveScript} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Scripts;