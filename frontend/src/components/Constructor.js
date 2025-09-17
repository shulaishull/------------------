import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import { compareFiles } from '../services/api';

const Constructor = () => {
  const [tabValue, setTabValue] = useState(0);
  const [file1Content, setFile1Content] = useState('');
  const [file2Content, setFile2Content] = useState('');
  const [regexPattern, setRegexPattern] = useState('');
  const [filterPattern, setFilterPattern] = useState('');
  const [groupByPattern, setGroupByPattern] = useState('');
  const [comparing, setComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [error, setError] = useState('');

  const handleCompare = async () => {
    if (!file1Content || !file2Content) {
      setError('Please provide content for both files');
      return;
    }

    setComparing(true);
    setError('');
    setComparisonResult(null);

    try {
      const response = await compareFiles({
        file1_content: file1Content,
        file2_content: file2Content,
        regex_pattern: regexPattern || null,
        filter_pattern: filterPattern || null,
        group_by: groupByPattern || null,
      });
      
      setComparisonResult(response.data);
    } catch (err) {
      setError('Failed to compare files: ' + (err.response?.data?.detail || err.message));
    } finally {
      setComparing(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const renderResult = () => {
    if (!comparisonResult) return null;

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Comparison Results
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1">
            Statistics:
          </Typography>
          <Typography variant="body2">
            Lines added: {comparisonResult.stats.lines_added}
          </Typography>
          <Typography variant="body2">
            Lines removed: {comparisonResult.stats.lines_removed}
          </Typography>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="subtitle1" gutterBottom>
          Differences:
        </Typography>
        <Paper sx={{ p: 2, maxHeight: 400, overflow: 'auto', backgroundColor: '#1e1e1e' }}>
          <pre style={{ color: '#ffffff', fontSize: '14px', lineHeight: '1.4' }}>
            {comparisonResult.diff.map((line, index) => {
              let color = '#ffffff';
              if (line.startsWith('+')) color = '#4caf50';
              else if (line.startsWith('-')) color = '#f44336';
              else if (line.startsWith('@')) color = '#2196f3';
              
              return (
                <div key={index} style={{ color }}>
                  {line}
                </div>
              );
            })}
          </pre>
        </Paper>
      </Box>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Comparison Constructor
      </Typography>
      
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} centered>
          <Tab label="File Inputs" />
          <Tab label="Comparison Rules" />
          <Tab label="Results" />
        </Tabs>
        
        <Box sx={{ p: 3 }}>
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                File Contents
              </Typography>
              
              <TextField
                label="File 1 Content"
                multiline
                rows={10}
                fullWidth
                value={file1Content}
                onChange={(e) => setFile1Content(e.target.value)}
                sx={{ mb: 3 }}
              />
              
              <TextField
                label="File 2 Content"
                multiline
                rows={10}
                fullWidth
                value={file2Content}
                onChange={(e) => setFile2Content(e.target.value)}
                sx={{ mb: 3 }}
              />
            </Box>
          )}
          
          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Comparison Rules
              </Typography>
              
              <TextField
                label="Regex Pattern (Optional)"
                fullWidth
                value={regexPattern}
                onChange={(e) => setRegexPattern(e.target.value)}
                helperText="Pattern to extract specific content from files for comparison"
                sx={{ mb: 3 }}
              />
              
              <TextField
                label="Filter Pattern (Optional)"
                fullWidth
                value={filterPattern}
                onChange={(e) => setFilterPattern(e.target.value)}
                helperText="Regex pattern to exclude matching lines from comparison"
                sx={{ mb: 3 }}
              />
              
              <TextField
                label="Group By Pattern (Optional)"
                fullWidth
                value={groupByPattern}
                onChange={(e) => setGroupByPattern(e.target.value)}
                helperText="Regex pattern to group differences (first capturing group will be used as key)"
                sx={{ mb: 3 }}
              />
              
              <FormGroup>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Case Sensitive"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Ignore Whitespace"
                />
              </FormGroup>
            </Box>
          )}
          
          {tabValue === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Comparison Results
              </Typography>
              
              {renderResult()}
            </Box>
          )}
          
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              onClick={handleCompare}
              disabled={comparing}
              startIcon={comparing ? <CircularProgress size={20} /> : null}
            >
              {comparing ? 'Comparing...' : 'Run Comparison'}
            </Button>
          </Box>
        </Box>
      </Paper>
      
      {comparisonResult && tabValue !== 2 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Comparison completed successfully. Switch to the Results tab to view details.
        </Alert>
      )}
    </Container>
  );
};

export default Constructor;