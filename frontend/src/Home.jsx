import React, { useState } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Card,
  CardHeader,
  CardContent,
  CardActions,
  TextField,
  InputAdornment,
  Drawer,
  Grid,
  Container,
  List,
  ListItem,
  ListItemText,
  Box,
} from '@mui/material'
import {
  Message,
  Notifications,
  Menu as MenuIcon,
  Search,
  CalendarToday,
  Chat,
  Notifications as NotificationsIcon,
  PersonAdd,
  Login,
  FileCopy,
  HealthAndSafety,
  Medication,
} from '@mui/icons-material'

export default function Home() {
  const [chatOpen, setChatOpen] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const sendMessage = () => {
    if (inputMessage.trim()) {
      setChatMessages([...chatMessages, `You: ${inputMessage}`])
      setChatMessages((prev) => [...prev, "AI: I'm an AI assistant. How can I help you with your healthcare needs?"])
      setInputMessage('')
    }
  }

  return (
    <div>
      {/* Header */}
      <AppBar position="static" color="default">
        <Toolbar>
          <Typography variant="h6" color="primary" sx={{ flexGrow: 1 }}>
            ClinicQ
          </Typography>
          <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
            <Button color="inherit">Home</Button>
            <Button color="inherit">Services</Button>
            <Button color="inherit">Doctors</Button>
            <Button color="inherit">About</Button>
          </Box>
          <IconButton color="inherit" onClick={() => setMobileMenuOpen(true)}>
            <MenuIcon />
          </IconButton>
          <Drawer anchor="right" open={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)}>
            <List>
              <ListItem button><ListItemText primary="Home" /></ListItem>
              <ListItem button><ListItemText primary="Services" /></ListItem>
              <ListItem button><ListItemText primary="Doctors" /></ListItem>
              <ListItem button><ListItemText primary="About" /></ListItem>
            </List>
          </Drawer>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container>
        <Box textAlign="center" py={5}>
          <Typography variant="h2" gutterBottom>Your Health, Our Priority</Typography>
          <Typography variant="h6" color="textSecondary" paragraph>
            Get instant medical advice and connect with top doctors online.
          </Typography>
          <Button variant="contained" color="primary" startIcon={<PersonAdd />}>Sign Up</Button>
          <Button variant="outlined" color="primary" startIcon={<Login />} sx={{ ml: 2 }}>Login</Button>
        </Box>

        {/* Key Features */}
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: 'primary.main', color: 'white' }}>
              <CardHeader
                avatar={<CalendarToday />}
                title="Schedule Appointment"
              />
              <CardContent>Book your next doctor's visit with ease.</CardContent>
              <CardActions>
                <Button fullWidth color="secondary" variant="contained">Schedule Now</Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: 'success.main', color: 'white' }}>
              <CardHeader
                avatar={<Chat />}
                title="Message Doctor"
              />
              <CardContent>Communicate directly with your healthcare provider.</CardContent>
              <CardActions>
                <Button fullWidth color="secondary" variant="contained">Start Chat</Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: 'secondary.main', color: 'white' }}>
              <CardHeader
                avatar={<NotificationsIcon />}
                title="Health Reminders"
              />
              <CardContent>Stay on top of your health with personalized reminders.</CardContent>
              <CardActions>
                <Button fullWidth color="secondary" variant="contained">Set Reminders</Button>
              </CardActions>
            </Card>
          </Grid>
        </Grid>

        {/* Search Bar */}
        <Box my={5} maxWidth="md" mx="auto">
          <TextField
            variant="outlined"
            fullWidth
            placeholder="Search for doctors, specialties, or health issues..."
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {/* Additional Services */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader title="Medical Records" avatar={<FileCopy color="primary" />} />
              <CardContent>Access and manage your medical records securely online.</CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader title="Prescription Refills" avatar={<Medication color="primary" />} />
              <CardContent>Request prescription refills and manage your medications easily.</CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader title="Health Monitoring" avatar={<HealthAndSafety color="primary" />} />
              <CardContent>Track your health metrics and receive personalized insights.</CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Chat Window */}
        {chatOpen && (
          <Card sx={{ position: 'fixed', bottom: 16, right: 16, width: 300 }}>
            <CardHeader title="AI Health Assistant" />
            <CardContent>
              <Box maxHeight="300px" overflow="auto">
                {chatMessages.map((message, index) => (
                  <Typography key={index} sx={{ backgroundColor: '#f1f1f1', p: 1, borderRadius: 1 }}>{message}</Typography>
                ))}
              </Box>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Type your message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={sendMessage}><Message /></IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </CardContent>
          </Card>
        )}
      </Container>

      {/* Footer */}
      <Box bgcolor="text.secondary" color="white" py={5} mt={5}>
        <Container>
          <Grid container spacing={4}>
            <Grid item xs={12} md={3}>
              <Typography variant="h6">ClinicQ</Typography>
              <Typography>&copy; 2023 ClinicQ. All rights reserved.</Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h6">Quick Links</Typography>
              <List>
                <ListItem><ListItemText primary="About Us" /></ListItem>
                <ListItem><ListItemText primary="Services" /></ListItem>
                <ListItem><ListItemText primary="Contact" /></ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h6">Legal</Typography>
              <List>
                <ListItem><ListItemText primary="Privacy Policy" /></ListItem>
                <ListItem><ListItemText primary="Terms of Service" /></ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h6">Find a Specialist</Typography>
              <Typography paragraph>Looking for a specific medical specialist? Use our advanced search tool.</Typography>
              <Button color="primary" variant="contained">Find Specialist</Button>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </div>
  )
}
