import React, { useState, useContext, useEffect, useCallback } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { TaskContext } from '../contexts/TaskContext';
import {
  Card, CardContent, Typography, Box, Stack, TextField, Button, IconButton, Chip, Checkbox, Fab, CircularProgress, Divider, Collapse, Tooltip, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import SaveIcon from '@mui/icons-material/Save';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import LowPriorityIcon from '@mui/icons-material/LowPriority';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import SearchIcon from '@mui/icons-material/Search';
import TodayIcon from '@mui/icons-material/Today';
import { AnimatePresence, motion } from 'framer-motion';

const priorityLabels = {
  1: { label: 'Baja', color: 'success', icon: <LowPriorityIcon fontSize="small" /> },
  2: { label: 'Media', color: 'warning', icon: <PriorityHighIcon fontSize="small" /> },
  3: { label: 'Alta', color: 'error', icon: <PriorityHighIcon fontSize="small" /> },
};

const Dashboard = () => {
  const [newTask, setNewTask] = useState('');
  const [newTaskDesc, setNewTaskDesc] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastUpdate, setLastUpdate] = useState(0);
  const [editingTask, setEditingTask] = useState(null);
  const [editTaskTitle, setEditTaskTitle] = useState('');
  const [editTaskDesc, setEditTaskDesc] = useState('');
  const [editTaskPriority, setEditTaskPriority] = useState(1);
  const [showCompleted, setShowCompleted] = useState(false);
  const [search, setSearch] = useState('');
  const [filterPriority, setFilterPriority] = useState(null);
  const [showToday, setShowToday] = useState(false);
  
  const { logout, user } = useContext(AuthContext);
  const { tasks, addTask, updateTask, deleteTask, fetchTasks, error: taskError } = useContext(TaskContext);

  const loadTasks = useCallback(async () => {
    console.log('loadTasks ejecutándose');
    try {
      await fetchTasks();
      setLastUpdate(Date.now());
      console.log('Tareas cargadas exitosamente');
    } catch (err) {
      console.error('Error en loadTasks:', err);
      if (!err.message.includes('Demasiadas solicitudes')) {
        setError(err.message || 'Error al cargar tareas');
      }
    }
  }, [fetchTasks]);

  useEffect(() => {
    console.log('useEffect de loadTasks ejecutándose, lastUpdate:', lastUpdate);
    const now = Date.now();
    // Cargar tareas al inicio (cuando lastUpdate es 0) o si han pasado 5 segundos
    if (lastUpdate === 0 || now - lastUpdate >= 5000) {
      loadTasks();
    }
  }, [loadTasks, lastUpdate]);

  useEffect(() => {
    console.log('Tareas actuales:', tasks);
    console.log('Número de tareas:', tasks.length);
  }, [tasks]);

  useEffect(() => {
    if (taskError) {
      setError(taskError);
    }
  }, [taskError]);

  const handleAddTask = async (e) => {
    console.log('handleAddTask ejecutándose');
    e.preventDefault();
    if (!newTask.trim()) return;

    console.log('Intentando crear tarea:', { 
      titulo: newTask.trim(), 
      descripcion: newTaskDesc.trim() || null,
      prioridad: newTaskPriority 
    });
    setLoading(true);
    setError('');

    try {
      const result = await addTask({ 
        titulo: newTask.trim(),
        descripcion: newTaskDesc.trim() || null,
        prioridad: newTaskPriority
      });
      console.log('Resultado de crear tarea:', result);
      if (result.success) {
        setNewTask('');
        setNewTaskDesc('');
        setNewTaskPriority(1);
        setLastUpdate(Date.now());
      } else {
        setError(result.error);
      }
    } catch (err) {
      console.error('Error al crear tarea:', err);
      if (!err.message.includes('Demasiadas solicitudes')) {
        setError(err.message || 'Error al agregar tarea');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (taskId, completed) => {
    try {
      const result = await updateTask(taskId, { completado: !completed });
      if (!result.success) {
        setError(result.error);
      } else {
        setLastUpdate(Date.now());
      }
    } catch (err) {
      if (!err.message.includes('Demasiadas solicitudes')) {
        setError(err.message || 'Error al actualizar tarea');
      }
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta tarea?')) {
      try {
        const result = await deleteTask(taskId);
        if (!result.success) {
          setError(result.error);
        } else {
          setLastUpdate(Date.now());
        }
      } catch (err) {
        if (!err.message.includes('Demasiadas solicitudes')) {
          setError(err.message || 'Error al eliminar tarea');
        }
      }
    }
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setEditTaskTitle(task.titulo);
    setEditTaskDesc(task.descripcion || '');
    setEditTaskPriority(task.prioridad);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editTaskTitle.trim()) return;

    setLoading(true);
    setError('');

    try {
      const result = await updateTask(editingTask.id, {
        titulo: editTaskTitle.trim(),
        descripcion: editTaskDesc.trim() || null,
        prioridad: editTaskPriority
      });
      
      if (result.success) {
        setEditingTask(null);
        setEditTaskTitle('');
        setEditTaskDesc('');
        setEditTaskPriority(1);
        setLastUpdate(Date.now());
      } else {
        setError(result.error);
      }
    } catch (err) {
      if (!err.message.includes('Demasiadas solicitudes')) {
        setError(err.message || 'Error al actualizar tarea');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
    setEditTaskTitle('');
    setEditTaskDesc('');
    setEditTaskPriority(1);
  };

  const handleLogout = () => {
    logout();
  };

  // Filtrado de tareas
  const filteredTasks = tasks.filter(task => {
    const matchesText =
      task.titulo.toLowerCase().includes(search.toLowerCase()) ||
      (task.descripcion && task.descripcion.toLowerCase().includes(search.toLowerCase()));
    const matchesPriority = filterPriority ? task.prioridad === filterPriority : true;
    // Suponiendo que task.fecha existe y es ISO string, si no, omitir showToday
    const isToday = showToday && task.fecha ? (new Date(task.fecha)).toDateString() === (new Date()).toDateString() : true;
    return matchesText && matchesPriority && isToday;
  });

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4, mb: 10 }}>
      <Card elevation={3} sx={{ mb: 3, borderRadius: 4 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5" fontWeight={800} color="text.primary" sx={{ color: '#fff' }}>
              Dashboard de Tareas
            </Typography>
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="body1" color="text.primary" sx={{ color: '#fff' }}>
                Hola, {user?.username || 'Usuario'}
              </Typography>
              <Button onClick={handleLogout} variant="outlined" color="secondary" size="small">
                Cerrar Sesión
              </Button>
            </Stack>
          </Stack>

          {error && (
            <Box mb={2}>
              <Card sx={{ bgcolor: 'error.light', color: 'error.contrastText', p: 1, borderRadius: 2 }}>
                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2">{error}</Typography>
                  <IconButton size="small" onClick={() => setError('')}><CancelIcon fontSize="small" /></IconButton>
                </Stack>
              </Card>
            </Box>
          )}

          {/* Barra de búsqueda y filtros */}
          <Card elevation={1} sx={{ mb: 2, borderRadius: 3 }}>
            <CardContent sx={{ overflow: 'hidden', boxSizing: 'border-box', px: { xs: 1, sm: 3 }, py: { xs: 1, sm: 2 } }}>
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={2}
                alignItems="center"
                justifyContent="space-between"
                flexWrap="wrap"
                gap={{ xs: 1, sm: 2 }}
              >
                <TextField
                  variant="outlined"
                  size="small"
                  placeholder="Buscar tarea..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  InputProps={{ startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} /> }}
                  sx={{ flex: 2, minWidth: 180 }}
                />
                <Stack direction="row" spacing={1}>
                  <Chip
                    label="Todas"
                    color={!filterPriority ? 'primary' : 'default'}
                    onClick={() => setFilterPriority(null)}
                    clickable
                  />
                  <Chip
                    label="Baja"
                    color={filterPriority === 1 ? 'success' : 'default'}
                    onClick={() => setFilterPriority(1)}
                    clickable
                  />
                  <Chip
                    label="Media"
                    color={filterPriority === 2 ? 'warning' : 'default'}
                    onClick={() => setFilterPriority(2)}
                    clickable
                  />
                  <Chip
                    label="Alta"
                    color={filterPriority === 3 ? 'error' : 'default'}
                    onClick={() => setFilterPriority(3)}
                    clickable
                  />
                  <Chip
                    icon={<TodayIcon />}
                    label="Hoy"
                    color={showToday ? 'secondary' : 'default'}
                    onClick={() => setShowToday(v => !v)}
                    clickable
                  />
                </Stack>
              </Stack>
            </CardContent>
          </Card>

          <Stack spacing={2}>
            {filteredTasks && filteredTasks.filter(t => !t.completado).length === 0 && (
              <Typography color="text.secondary" align="center">No tienes tareas pendientes.</Typography>
            )}
            <AnimatePresence>
              {filteredTasks && filteredTasks.filter(t => !t.completado).map(task => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  layout
                >
                  <Card sx={{ borderRadius: 3, boxShadow: 2, bgcolor: (theme) => theme.palette.mode === 'dark' ? '#23263a' : '#fff', color: (theme) => theme.palette.mode === 'dark' ? '#fff' : '#222B45', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 6 } }}>
                    <CardContent>
                      <Stack direction="row" alignItems="center" spacing={2}>
                        <Checkbox
                          checked={task.completado}
                          onChange={() => handleToggleTask(task.id, task.completado)}
                          color="primary"
                          icon={<CheckCircleIcon sx={{ opacity: 0.3 }} />}
                          checkedIcon={<CheckCircleIcon />}
                          inputProps={{ 'aria-label': 'Completar tarea' }}
                        />
                        <Box flex={1}>
                          <Typography variant="subtitle1" fontWeight={700} sx={{ color: (theme) => theme.palette.mode === 'dark' ? '#fff' : '#222B45' }}>{task.titulo}</Typography>
                          <Typography variant="body2" sx={{ color: (theme) => theme.palette.mode === 'dark' ? '#E0E0E0' : '#333', fontStyle: 'italic', fontWeight: 500 }}>{task.descripcion}</Typography>
                          <Stack direction="row" spacing={1} mt={1}>
                            <Chip
                              label={priorityLabels[task.prioridad]?.label || 'Desconocida'}
                              color={priorityLabels[task.prioridad]?.color || 'default'}
                              size="small"
                              icon={priorityLabels[task.prioridad]?.icon}
                            />
                          </Stack>
                        </Box>
                        <Stack direction="row" spacing={1}>
                          <Tooltip title="Editar">
                            <IconButton color="primary" onClick={() => handleEditTask(task)}><EditIcon /></IconButton>
                          </Tooltip>
                          <Tooltip title="Eliminar">
                            <IconButton color="error" onClick={() => handleDeleteTask(task.id)}><DeleteIcon /></IconButton>
                          </Tooltip>
                        </Stack>
                      </Stack>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </Stack>
        </CardContent>
      </Card>

      {/* Sección de tareas completadas plegable */}
      <Card elevation={2} sx={{ mb: 3, borderRadius: 4, bgcolor: 'background.paper' }}>
        <CardContent>
          <Stack direction="row" alignItems="center" justifyContent="space-between" onClick={() => setShowCompleted(v => !v)} sx={{ cursor: 'pointer' }}>
            <Stack direction="row" alignItems="center" spacing={1}>
              <Typography variant="subtitle1" fontWeight={700} sx={{ color: (theme) => theme.palette.mode === 'dark' ? '#fff' : '#222B45' }}>
                Tareas Completadas
              </Typography>
              <Chip label={tasks.filter(t => t.completado).length} color="success" size="small" />
            </Stack>
            <IconButton size="small">
              {showCompleted ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Stack>
          <Collapse in={showCompleted} timeout="auto" unmountOnExit>
            <Stack spacing={2} mt={2}>
              {filteredTasks && filteredTasks.filter(t => t.completado).length === 0 && (
                <Typography color="text.secondary" align="center">No hay tareas completadas.</Typography>
              )}
              <AnimatePresence>
                {filteredTasks && filteredTasks.filter(t => t.completado).map(task => (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, x: 40 }}
                    animate={{ opacity: 0.85, x: 0 }}
                    exit={{ opacity: 0, x: -40 }}
                    transition={{ duration: 0.3 }}
                    layout
                  >
                    <Card sx={{ borderRadius: 3, boxShadow: 1, bgcolor: 'background.paper', color: 'text.primary' }}>
                      <CardContent>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Checkbox
                            checked={task.completado}
                            onChange={() => handleToggleTask(task.id, task.completado)}
                            color="success"
                            icon={<CheckCircleIcon sx={{ opacity: 0.5 }} />}
                            checkedIcon={<CheckCircleIcon />}
                            inputProps={{ 'aria-label': 'Desmarcar tarea completada' }}
                          />
                          <Box flex={1}>
                            <Typography variant="subtitle1" fontWeight={700} color="text.primary" sx={{ color: '#fff' }}>{task.titulo}</Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ color: '#E0E0E0', fontStyle: 'italic' }}>{task.descripcion}</Typography>
                            <Stack direction="row" spacing={1} mt={1}>
                              <Chip
                                label={priorityLabels[task.prioridad]?.label || 'Desconocida'}
                                color={priorityLabels[task.prioridad]?.color || 'default'}
                                size="small"
                                icon={priorityLabels[task.prioridad]?.icon}
                                sx={{ color: 'text.primary', bgcolor: 'background.default', fontWeight: 600 }}
                              />
                            </Stack>
                          </Box>
                          <Stack direction="row" spacing={1}>
                            <Tooltip title="Eliminar">
                              <IconButton color="error" onClick={() => handleDeleteTask(task.id)}><DeleteIcon /></IconButton>
                            </Tooltip>
                          </Stack>
                        </Stack>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            </Stack>
          </Collapse>
        </CardContent>
      </Card>

      {/* Modal de edición de tarea */}
      <Dialog open={!!editingTask} onClose={handleCancelEdit} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Tarea</DialogTitle>
        <form onSubmit={handleSaveEdit}>
          <DialogContent dividers>
            <Stack spacing={2}>
              <TextField
                label="Título"
                value={editTaskTitle}
                onChange={e => setEditTaskTitle(e.target.value)}
                required
                fullWidth
                autoFocus
              />
              <TextField
                label="Descripción (opcional)"
                value={editTaskDesc}
                onChange={e => setEditTaskDesc(e.target.value)}
                fullWidth
                multiline
                minRows={2}
              />
              <TextField
                label="Prioridad"
                select
                value={editTaskPriority}
                onChange={e => setEditTaskPriority(Number(e.target.value))}
                SelectProps={{ native: true }}
                fullWidth
              >
                <option value={1}>Baja</option>
                <option value={2}>Media</option>
                <option value={3}>Alta</option>
              </TextField>
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCancelEdit} color="secondary" startIcon={<CancelIcon />}>Cancelar</Button>
            <Button type="submit" color="primary" variant="contained" startIcon={<SaveIcon />} disabled={loading}>
              {loading ? <CircularProgress size={20} color="inherit" /> : 'Guardar'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Input de nueva tarea - barra fija inferior */}
      <Box sx={{ position: 'fixed', left: 0, bottom: 0, width: '100%', bgcolor: 'background.paper', boxShadow: 3, py: 2, px: { xs: 2, sm: 10 }, zIndex: 1200 }}>
        <form onSubmit={handleAddTask} style={{ display: 'flex', gap: 8, alignItems: 'center', maxWidth: 600, margin: '0 auto' }}>
          <TextField
            label="Título de la tarea"
            value={newTask}
            onChange={e => setNewTask(e.target.value)}
            required
            fullWidth
            size="small"
            sx={{ flex: 2 }}
          />
          <TextField
            label="Descripción (opcional)"
            value={newTaskDesc}
            onChange={e => setNewTaskDesc(e.target.value)}
            size="small"
            sx={{ flex: 3 }}
          />
          <TextField
            label="Prioridad"
            select
            value={newTaskPriority}
            onChange={e => setNewTaskPriority(Number(e.target.value))}
            SelectProps={{ native: true }}
            size="small"
            sx={{ width: 110 }}
          >
            <option value={1}>Baja</option>
            <option value={2}>Media</option>
            <option value={3}>Alta</option>
          </TextField>
          <Fab color="primary" type="submit" aria-label="Agregar tarea" size="medium" disabled={loading} sx={{ ml: 1 }}>
            {loading ? <CircularProgress size={24} color="inherit" /> : <AddIcon />}
          </Fab>
        </form>
      </Box>
    </Box>
  );
};

export default Dashboard; 