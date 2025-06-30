import React, { useState, useEffect, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './contexts/AuthContext';
import { TaskProvider } from './contexts/TaskContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import PrivateRoute from './components/PrivateRoute';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import AccountCircle from '@mui/icons-material/AccountCircle';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import ListAltIcon from '@mui/icons-material/ListAlt';
import Box from '@mui/material/Box';
import { keyframes } from '@emotion/react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import './App.css';

// Animación de fondo degradado
const animatedGradient = keyframes`
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
`;

function App() {
  // Leer preferencia de modo oscuro de localStorage o del sistema
  const getInitialDarkMode = () => {
    const stored = localStorage.getItem('darkMode');
    if (stored !== null) return stored === 'true';
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  };

  const [darkMode, setDarkMode] = useState(getInitialDarkMode);
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState('');
  const { user } = useContext(AuthContext) || {};

  // Guardar preferencia en localStorage cuando cambie
  useEffect(() => {
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  // Obtener datos del usuario al abrir el diálogo
  useEffect(() => {
    if (profileOpen) {
      const fetchProfile = async () => {
        setProfileLoading(true);
        setProfileError('');
        try {
          const token = localStorage.getItem('access_token');
          const res = await fetch('http://localhost:8000/me', {
            headers: {
              'accept': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          });
          if (!res.ok) throw new Error('No se pudo obtener el perfil');
          const data = await res.json();
          setProfileData(data);
        } catch (err) {
          setProfileError('No se pudo obtener la información de usuario');
        } finally {
          setProfileLoading(false);
        }
      };
      fetchProfile();
    }
  }, [profileOpen]);

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: darkMode ? '#A3A8F7' : '#6C63FF',
        contrastText: '#fff',
      },
      secondary: {
        main: darkMode ? '#FFB6B9' : '#FF6F91',
        contrastText: '#fff',
      },
      text: {
        primary: darkMode ? '#fff' : '#222B45',
        secondary: darkMode ? '#E0E0E0' : '#6B7280',
        disabled: darkMode ? '#A0A0A0' : '#B0B3B8',
      },
      background: {
        default: darkMode ? '#181A1B' : '#F7F8FA',
        paper: darkMode ? 'rgba(36,39,46,0.97)' : 'rgba(255,255,255,0.82)',
      },
      success: {
        main: darkMode ? '#43E97B' : '#43E97B',
      },
      warning: {
        main: darkMode ? '#FFD166' : '#FFB547',
      },
      error: {
        main: darkMode ? '#FF6F91' : '#FF1744',
      },
      divider: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
    },
    typography: {
      fontFamily: 'Inter, SF Pro, Google Sans, Arial, sans-serif',
      fontWeightBold: 800,
      fontWeightMedium: 600,
      fontWeightRegular: 400,
      h1: { fontWeight: 800, fontSize: '2.6rem', letterSpacing: '-1px' },
      h2: { fontWeight: 700, fontSize: '2rem' },
      h3: { fontWeight: 700, fontSize: '1.5rem' },
      h4: { fontWeight: 600, fontSize: '1.2rem' },
      h5: { fontWeight: 600, fontSize: '1.1rem' },
      h6: { fontWeight: 600, fontSize: '1rem' },
      body1: { fontSize: '1.08rem', fontWeight: 400 },
      body2: { fontSize: '0.98rem', fontWeight: 400 },
      button: { fontWeight: 600, letterSpacing: '0.5px' },
    },
    shape: {
      borderRadius: 24,
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundColor: darkMode ? 'rgba(36,39,46,0.97)' : 'rgba(255,255,255,0.82)',
            border: darkMode ? '2px solid #393C44' : '2px solid #E3E6FF',
            boxShadow: darkMode
              ? '0 6px 32px 0 rgba(0,0,0,0.32)'
              : '0 2px 12px 0 rgba(108,99,255,0.10)',
            backdropFilter: 'blur(14px) saturate(180%)',
            WebkitBackdropFilter: 'blur(14px) saturate(180%)',
            padding: '20px 24px',
            overflow: 'visible',
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
            backdropFilter: 'blur(10px) saturate(150%)',
            WebkitBackdropFilter: 'blur(10px) saturate(150%)',
          },
        },
      },
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Fondo animado y fade-in global */}
      <Box
        sx={{
          minHeight: '100vh',
          width: '100vw',
          position: 'fixed',
          zIndex: -1,
          top: 0,
          left: 0,
          animation: `${animatedGradient} 16s ease-in-out infinite`,
          background: darkMode
            ? 'linear-gradient(120deg, #181A1B, #23272A, #23272A, #181A1B)'
            : 'linear-gradient(120deg, #F7F8FA, #E3E6FF, #A3A8F7, #F7F8FA)',
          backgroundSize: '300% 300%',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed',
          transition: 'background 0.5s',
          opacity: 1,
        }}
      />
      {/* Ilustración SVG decorativa en el fondo */}
      <Box sx={{ position: 'fixed', top: 0, right: 0, zIndex: 0, width: { xs: 180, md: 320 }, opacity: 0.18, pointerEvents: 'none' }}>
        <svg viewBox="0 0 400 400" fill="none" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <ellipse cx="200" cy="200" rx="200" ry="120" fill={darkMode ? '#6C63FF' : '#A3A8F7'} />
          <ellipse cx="300" cy="100" rx="80" ry="40" fill={darkMode ? '#FFB6B9' : '#FF6F91'} />
          <ellipse cx="100" cy="80" rx="60" ry="30" fill={darkMode ? '#43E97B' : '#43E97B'} />
        </svg>
      </Box>
      {/* Fade-in global al cargar la app */}
      <Box sx={{ animation: 'fadeIn 1.2s cubic-bezier(.4,0,.2,1)', '@keyframes fadeIn': { from: { opacity: 0 }, to: { opacity: 1 } }, bgcolor: 'transparent', color: 'text.primary', minHeight: '100vh' }}>
        <AppBar position="static" color="primary" elevation={2} sx={{ transition: 'background 0.5s' }}>
          <Toolbar>
            <ListAltIcon sx={{ fontSize: 34, mr: 1, color: '#fff', filter: 'drop-shadow(0 2px 6px rgba(108,99,255,0.25))' }} />
            <Typography
              variant="h4"
              sx={{
                flexGrow: 1,
                fontWeight: 900,
                letterSpacing: '-1px',
                color: '#fff',
                textShadow: '0 2px 8px rgba(108,99,255,0.18)',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              Mi Lista de Tareas
            </Typography>
            <IconButton sx={{ ml: 1 }} onClick={() => setDarkMode(!darkMode)} color="inherit" aria-label="toggle dark mode">
              {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
            <IconButton color="inherit" aria-label="perfil" onClick={() => setProfileOpen(true)}>
              <AccountCircle />
            </IconButton>
          </Toolbar>
        </AppBar>
        {/* Dialog de perfil */}
        <Dialog open={profileOpen} onClose={() => setProfileOpen(false)} maxWidth="xs" fullWidth>
          <DialogTitle>Perfil de Usuario</DialogTitle>
          <DialogContent dividers>
            {profileLoading ? (
              <Typography variant="body1">Cargando...</Typography>
            ) : profileError ? (
              <Typography variant="body1" color="error">{profileError}</Typography>
            ) : profileData ? (
              <>
                <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                  Usuario:
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {profileData.username || 'No disponible'}
                </Typography>
                <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                  Correo:
                </Typography>
                <Typography variant="body1">
                  {profileData.email || 'No disponible'}
                </Typography>
              </>
            ) : (
              <Typography variant="body1">No hay datos de usuario.</Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setProfileOpen(false)} color="primary" variant="contained">Cerrar</Button>
          </DialogActions>
        </Dialog>
        <Box sx={{ p: 2, bgcolor: 'transparent', color: 'text.primary' }}>
          <AuthProvider>
            <TaskProvider>
              <Router>
                <div className="App" style={{ background: 'none', color: 'inherit' }}>
                  <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route 
                      path="/dashboard" 
                      element={
                        <PrivateRoute>
                          <Dashboard />
                        </PrivateRoute>
                      } 
                    />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </div>
              </Router>
            </TaskProvider>
          </AuthProvider>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App; 