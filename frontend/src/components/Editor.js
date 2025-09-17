import React, { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material';
import { uploadFile } from '../services/api';

const EditorComponent = () => {
  const [code, setCode] = useState('// Start typing or upload a file...\n');
  const [fileName, setFileName] = useState('untitled.txt');
  const [language, setLanguage] = useState('plaintext');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleEditorChange = (value) => {
    setCode(value);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setError('');
    setUploadResult(null);

    try {
      const response = await uploadFile(file);
      const { filename, content } = response.data;
      
      setCode(content);
      setFileName(filename);
      
      // Set language based on file extension
      const ext = filename.split('.').pop().toLowerCase();
      if (ext === 'py') setLanguage('python');
      else if (ext === 'js') setLanguage('javascript');
      else if (ext === 'json') setLanguage('json');
      else if (ext === 'xml') setLanguage('xml');
      else if (ext === 'html') setLanguage('html');
      else setLanguage('plaintext');
      
      setUploadResult(`File "${filename}" loaded successfully`);
    } catch (err) {
      setError('Failed to upload file: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  const handleSave = () => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const languageOptions = [
    { value: 'plaintext', label: 'Plain Text' },
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'json', label: 'JSON' },
    { value: 'xml', label: 'XML' },
    { value: 'html', label: 'HTML' },
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Online Editor
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <TextField
            label="File Name"
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Language</InputLabel>
            <Select
              value={language}
              label="Language"
              onChange={(e) => setLanguage(e.target.value)}
            >
              {languageOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button
            variant="contained"
            component="label"
            disabled={uploading}
          >
            {uploading ? <CircularProgress size={24} /> : 'Upload File'}
            <input
              type="file"
              hidden
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".txt,.py,.js,.json,.xml,.html,.csv,.mif,.xlsx"
            />
          </Button>
          
          <Button
            variant="outlined"
            onClick={handleSave}
          >
            Save File
          </Button>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {uploadResult && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {uploadResult}
          </Alert>
        )}
      </Paper>
      
      <Paper sx={{ height: '70vh' }}>
        <Editor
          height="100%"
          language={language}
          value={code}
          onChange={handleEditorChange}
          theme="vs-dark"
          options={{
            minimap: { enabled: true },
            fontSize: 14,
            scrollBeyondLastLine: false,
            automaticLayout: true,
          }}
        />
      </Paper>
    </Container>
  );
};

export default EditorComponent;