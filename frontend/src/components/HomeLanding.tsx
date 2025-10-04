import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Grid
} from '@mui/material';
import { PregnantWoman, Description, Assignment } from '@mui/icons-material';

function HomeLanding() {
  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%)' }}>
      <Container maxWidth="lg">
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="100vh"
          textAlign="center"
          py={4}
        >
          <Paper
            elevation={8}
            sx={{
              p: 6,
              maxWidth: 800,
              borderRadius: 3,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            <PregnantWoman sx={{ fontSize: 80, color: 'primary.main', mb: 3 }} />
            
            <Typography 
              variant="h2" 
              component="h1" 
              gutterBottom
              sx={{
                fontWeight: 600,
                background: 'linear-gradient(45deg, #e91e63, #9c27b0)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 3
              }}
            >
              Smart Pregnancy Companion
            </Typography>

            <Typography variant="h5" color="text.secondary" paragraph sx={{ mb: 4 }}>
              Your personalized AI companion for a healthy pregnancy journey
            </Typography>

            <Grid container spacing={4} sx={{ mb: 4, justifyContent: 'center' }}>
              <Grid component="div">
                <Box>
                  <Description sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Medical Document Analysis
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Upload your medical documents and get AI-powered insights and commentary about your health data.
                  </Typography>
                </Box>
              </Grid>

              <Grid component="div">
                <Box>
                  <Assignment sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Personalized Tasks
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Get customized tasks and reminders for your pregnancy journey, from early stages to labor preparation.
                  </Typography>
                </Box>
              </Grid>

              <Grid component="div">
                <Box>
                  <PregnantWoman sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    AI-Powered Support
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Chat with your AI assistant for personalized guidance, questions, and support throughout your pregnancy.
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Typography variant="body1" color="text.secondary">
              Login or Register to get started
            </Typography>
          </Paper>
        </Box>
      </Container>
    </Box>
  );
}

export default HomeLanding;
