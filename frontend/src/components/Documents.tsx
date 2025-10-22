import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Delete,
  Visibility,
  InsertDriveFile,
  Download
} from '@mui/icons-material';
import { authService } from '../services/authService';

interface MedicalDocument {
  document_id: string;
  document_type: string;
  file_name: string;
  file_path: string;
  upload_date: string;
  status: string;
  summary?: string;
  extracted_data?: any;
}

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<MedicalDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<string>('other');
  const [userId, setUserId] = useState<string>('');
  const [uploadedDocumentSummary, setUploadedDocumentSummary] = useState<string | null>(null);

  useEffect(() => {
    const getCurrentUser = async () => {
      try {
        const user = await authService.getCurrentUser();
        if (user) {
          const id = user.user_id || user;
          setUserId(id);
          await loadDocuments(id);
        } else {
          setError('Please log in to view documents');
        }
      } catch (error) {
        console.error('Error getting current user:', error);
        setError('Failed to get user information');
      }
    };

    getCurrentUser();
  }, []);

  const loadDocuments = async (userId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/users/${userId}/documents`);
      if (!response.ok) {
        throw new Error('Failed to load documents');
      }
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      console.error('Error loading documents:', error);
      setError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setError(null);
      setUploadedDocumentSummary(null); // Clear previous summary
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !userId) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(
        `http://localhost:8000/users/${userId}/documents/full-flow?document_type=${documentType}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error('Failed to upload document');
      }

      const result = await response.json();
      setSuccess('Document uploaded and processed successfully!');
      
      // Show summary if available
      if (result.process_result && result.process_result.summary) {
        setUploadedDocumentSummary(result.process_result.summary);
      }
      
      setSelectedFile(null);
      setDocumentType('other');
      
      // Reset file input
      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      // Reload documents
      await loadDocuments(userId);
    } catch (error) {
      console.error('Error uploading document:', error);
      setError('Failed to upload document. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/users/${userId}/documents/${documentId}`,
        {
          method: 'DELETE',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete document');
      }

      setSuccess('Document deleted successfully');
      await loadDocuments(userId);
    } catch (error) {
      console.error('Error deleting document:', error);
      setError('Failed to delete document');
    }
  };

  const handleViewDocument = (doc: MedicalDocument) => {
    // Open the original document in a new tab
    const fileUrl = `http://localhost:8000/users/${userId}/documents/${doc.document_id}/file`;
    window.open(fileUrl, '_blank');
  };

  const handleDownloadDocument = async (doc: MedicalDocument) => {
    try {
      const response = await fetch(`http://localhost:8000/users/${userId}/documents/${doc.document_id}/file`);
      if (!response.ok) {
        throw new Error('Failed to download document');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = doc.file_name || 'document';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading document:', error);
      setError('Failed to download document');
    }
  };


  const StyledMarkdown = ({ children }: { children: string }) => {
    return (
      <ReactMarkdown
        components={{
          // Style paragraphs
          p: ({ children }) => (
            <Typography component="span" variant="body2" sx={{ display: 'block', mb: 1, lineHeight: 1.6 }}>
              {children}
            </Typography>
          ),
          // Style strong/bold text
          strong: ({ children }) => (
            <strong style={{ fontWeight: 600 }}>{children}</strong>
          ),
          // Style emphasis/italic text
          em: ({ children }) => (
            <em style={{ fontStyle: 'italic' }}>{children}</em>
          ),
          // Style lists
          ul: ({ children }) => (
            <ul style={{ marginLeft: '20px', marginBottom: '8px' }}>
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol style={{ marginLeft: '20px', marginBottom: '8px' }}>
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li style={{ marginBottom: '4px' }}>{children}</li>
          ),
          // Style code
          code: ({ children }) => (
            <code style={{ 
              backgroundColor: 'rgba(0,0,0,0.1)', 
              padding: '2px 6px', 
              borderRadius: '4px',
              fontFamily: 'monospace'
            }}>
              {children}
            </code>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    );
  };

  const getDocumentTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      blood_test: '#e91e63',
      ultrasound: '#9c27b0',
      urine_test: '#3f51b5',
      genetic_test: '#00bcd4',
      other: '#607d8b',
    };
    return colors[type] || colors.other;
  };


  if (!userId) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Please log in to view documents
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, color: '#333', mb: 0.5 }}>
          Medical Documents
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Upload and manage your medical documents
        </Typography>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Document Summary after upload */}
      {uploadedDocumentSummary && (
        <Paper elevation={1} sx={{ p: 3, mb: 3, borderRadius: 2, backgroundColor: '#f8f9fa' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#333' }}>
              Document Summary
            </Typography>
            <IconButton 
              size="small" 
              onClick={() => setUploadedDocumentSummary(null)}
              sx={{ color: '#666' }}
            >
              <Delete />
            </IconButton>
          </Box>
          <Typography variant="body2" sx={{ 
            lineHeight: 1.6, 
            color: '#555',
            whiteSpace: 'pre-wrap',
            maxHeight: '200px',
            overflow: 'auto'
          }}>
            <StyledMarkdown>{uploadedDocumentSummary}</StyledMarkdown>
          </Typography>
        </Paper>
      )}

      {/* Upload Section */}
      <Paper elevation={1} sx={{ p: 2, mb: 3, borderRadius: 2 }}>
        <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 500, color: '#666' }}>
          Upload New Document
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 1.5, alignItems: 'flex-end' }}>
          <Box sx={{ minWidth: 140, maxWidth: 180 }}>
            <FormControl size="small" fullWidth>
              <InputLabel sx={{ fontSize: '0.875rem' }}>Type</InputLabel>
              <Select
                value={documentType}
                label="Type"
                onChange={(e) => setDocumentType(e.target.value)}
                disabled={uploading}
                sx={{ fontSize: '0.875rem' }}
              >
                <MenuItem value="blood_test" sx={{ fontSize: '0.875rem' }}>Blood Test</MenuItem>
                <MenuItem value="ultrasound" sx={{ fontSize: '0.875rem' }}>Ultrasound</MenuItem>
                <MenuItem value="urine_test" sx={{ fontSize: '0.875rem' }}>Urine Test</MenuItem>
                <MenuItem value="genetic_test" sx={{ fontSize: '0.875rem' }}>Genetic Test</MenuItem>
                <MenuItem value="other" sx={{ fontSize: '0.875rem' }}>Other</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ flex: 1, minWidth: 200 }}>
            <Button
              variant="outlined"
              component="label"
              fullWidth
              size="small"
              startIcon={<InsertDriveFile />}
              disabled={uploading}
              sx={{ 
                fontSize: '0.875rem',
                textTransform: 'none',
                height: 40
              }}
            >
              {selectedFile ? (selectedFile.name.length > 20 ? selectedFile.name.substring(0, 20) + '...' : selectedFile.name) : 'Choose File'}
              <input
                id="file-upload"
                type="file"
                hidden
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileSelect}
              />
            </Button>
          </Box>
          <Button
            variant="contained"
            size="small"
            startIcon={uploading ? <CircularProgress size={16} color="inherit" /> : <CloudUpload />}
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            sx={{
              background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
              '&:hover': {
                background: 'linear-gradient(45deg, #c2185b, #7b1fa2)',
              },
              fontSize: '0.875rem',
              textTransform: 'none',
              height: 40,
              minWidth: 120
            }}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </Button>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', fontSize: '0.75rem' }}>
          Supported: PDF, JPG, JPEG, PNG
        </Typography>
      </Paper>

      {/* Documents List */}
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Your Documents ({documents.length})
      </Typography>

      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Loading documents...
          </Typography>
        </Box>
      ) : documents.length === 0 ? (
        <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
          <Description sx={{ fontSize: 64, color: '#e91e63', opacity: 0.3, mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No documents yet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload your first medical document to get started
          </Typography>
        </Paper>
      ) : (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 2 }}>
          {documents.map((doc) => (
            <Box key={doc.document_id}>
              <Card elevation={1} sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                borderRadius: 2,
                border: '1px solid #e0e0e0',
                '&:hover': {
                  boxShadow: 3,
                  transform: 'translateY(-2px)',
                  transition: 'all 0.2s ease-in-out'
                }
              }}>
                <CardContent sx={{ 
                  flexGrow: 1, 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  textAlign: 'center',
                  p: 2
                }}>
                  {/* PDF Icon */}
                  <Box sx={{ 
                    mb: 2, 
                    p: 2, 
                    borderRadius: '50%', 
                    backgroundColor: '#f5f5f5',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <Description sx={{ fontSize: 40, color: '#e91e63' }} />
                  </Box>
                  
                  {/* File name (truncated) */}
                  <Typography variant="body2" sx={{ 
                    mb: 1, 
                    fontWeight: 500,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    width: '100%'
                  }}>
                    {doc.file_name}
                  </Typography>
                  
                  {/* Upload date */}
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 2 }}>
                    {new Date(doc.upload_date).toLocaleDateString()}
                  </Typography>
                  
                  {/* Document type (small) */}
                  <Chip
                    label={doc.document_type.replace('_', ' ')}
                    size="small"
                    sx={{
                      backgroundColor: getDocumentTypeColor(doc.document_type),
                      color: 'white',
                      fontSize: '0.7rem',
                      height: 20,
                      mb: 1
                    }}
                  />
                </CardContent>
                
                <CardActions sx={{ 
                  justifyContent: 'center', 
                  px: 2, 
                  pb: 2,
                  gap: 1
                }}>
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => handleViewDocument(doc)}
                    title="View document"
                  >
                    <Visibility />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => handleDownloadDocument(doc)}
                    title="Download document"
                  >
                    <Download />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete(doc.document_id)}
                    title="Delete document"
                  >
                    <Delete />
                  </IconButton>
                </CardActions>
              </Card>
            </Box>
          ))}
        </Box>
      )}

    </Box>
  );
};

export default Documents;

