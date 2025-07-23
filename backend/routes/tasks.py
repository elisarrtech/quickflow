// ✅ TAREAS.JSX CON CATEGORÍA Y SUBTAREAS INTEGRADAS
import React, { useState, useEffect } from 'react';
import { FaCheckCircle, FaEdit, FaTrashAlt, FaRedo, FaArrowLeft } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const Tareas = () => {
  const [tareas, setTareas] = useState([]);
  const [titulo, setTitulo] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [fecha, setFecha] = useState('');
  const [categoria, setCategoria] = useState('');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(true);
  const [modoEdicion, setModoEdicion] = useState(null);
  const [editData, setEditData] = useState({ titulo: '', descripcion: '', fecha: '', categoria: '' });
  const API = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();

  useEffect(() => {
    const obtenerTareas = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/api/tasks`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (res.ok) {
          const ordenadas = data.sort((a, b) => {
            if (a.estado !== b.estado) return a.estado === 'pendiente' ? -1 : 1;
            return new Date(a.fecha) - new Date(b.fecha);
          });
          setTareas(ordenadas);
        } else {
          setError(data.error || 'No se pudieron cargar las tareas.');
        }
      } catch (err) {
        setError('Error al conectar con el servidor.');
      } finally {
        setCargando(false);
      }
    };
    obtenerTareas();
  }, []);

  const crearTarea = async () => {
    const token = localStorage.getItem('token');
    if (!titulo.trim()) return setError('El título es obligatorio.');
    try {
      const res = await fetch(`${API}/api/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ titulo, descripcion, fecha, categoria, subtareas: [] }),
      });
      const data = await res.json();
      if (res.ok) {
        setTareas(prev => [...prev, data]);
        setTitulo('');
        setDescripcion('');
        setFecha('');
        setCategoria('');
        setError('');
      } else {
        setError(data.error || 'Error al crear tarea.');
      }
    } catch (err) {
      setError('Error de red.');
    }
  };

  const eliminarTarea = async (id) => {
    const token = localStorage.getItem('token');
    await fetch(`${API}/api/tasks/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    setTareas(prev => prev.filter(t => t._id !== id));
  };

  const toggleEstado = async (tarea) => {
    const token = localStorage.getItem('token');
    const nuevoEstado = tarea.estado === 'pendiente' ? 'completada' : 'pendiente';
    await fetch(`${API}/api/tasks/${tarea._id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ estado: nuevoEstado }),
    });
    setTareas(prev => prev.map(t => t._id === tarea._id ? { ...t, estado: nuevoEstado } : t));
  };

  const guardarEdicion = async (id) => {
    const token = localStorage.getItem('token');
    await fetch(`${API}/api/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(editData),
    });
    setTareas(prev => prev.map(t => t._id === id ? { ...t, ...editData } : t));
    setModoEdicion(null);
  };

  return (
    <div className="bg-gray-800 p-4 md:p-6 rounded-lg shadow-md mt-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-white">📋 Tareas</h2>
        <button onClick={() => navigate('/dashboard')} className="flex items-center gap-2 text-sm text-white hover:text-blue-400">
          <FaArrowLeft /> Volver
        </button>
      </div>
      <div className="mb-6 space-y-3">
        <input type="text" value={titulo} onChange={e => setTitulo(e.target.value)} placeholder="Título" className="w-full p-2 rounded bg-gray-700 text-white" />
        <input type="text" value={descripcion} onChange={e => setDescripcion(e.target.value)} placeholder="Descripción" className="w-full p-2 rounded bg-gray-700 text-white" />
        <input type="date" value={fecha} onChange={e => setFecha(e.target.value)} className="w-full p-2 rounded bg-gray-700 text-white" />
        <input type="text" value={categoria} onChange={e => setCategoria(e.target.value)} placeholder="Categoría (opcional)" className="w-full p-2 rounded bg-gray-700 text-white" />
        <button onClick={crearTarea} className="w-full bg-blue-600 hover:bg-blue-700 text-white p-2 rounded font-semibold">Crear Tarea</button>
      </div>
      {error && <p className="text-red-400 mb-4 font-medium">{error}</p>}
      {cargando ? (
        <p className="text-gray-400">Cargando tareas...</p>
      ) : (
        tareas.map(t => (
          <div key={t._id} className={`bg-gray-700 p-4 rounded mb-4 ${t.estado === 'completada' ? 'opacity-70' : ''}`}>
            {modoEdicion === t._id ? (
              <>
                <input value={editData.titulo} onChange={e => setEditData({ ...editData, titulo: e.target.value })} className="w-full mb-1 p-1 bg-gray-600 text-white" />
                <input value={editData.descripcion} onChange={e => setEditData({ ...editData, descripcion: e.target.value })} className="w-full mb-1 p-1 bg-gray-600 text-white" />
                <input type="date" value={editData.fecha} onChange={e => setEditData({ ...editData, fecha: e.target.value })} className="w-full mb-2 p-1 bg-gray-600 text-white" />
                <input value={editData.categoria} onChange={e => setEditData({ ...editData, categoria: e.target.value })} placeholder="Categoría" className="w-full mb-2 p-1 bg-gray-600 text-white" />
                <div className="flex flex-wrap gap-2">
                  <button onClick={() => guardarEdicion(t._id)} className="bg-green-600 px-3 py-1 rounded text-white">Guardar</button>
                  <button onClick={() => setModoEdicion(null)} className="bg-gray-500 px-3 py-1 rounded text-white">Cancelar</button>
                </div>
              </>
            ) : (
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
                <div>
                  <h4 className="text-lg font-bold text-white uppercase">{t.titulo}</h4>
                  <p className="text-sm text-gray-300">{t.descripcion}</p>
                  <p className="text-xs text-gray-400 mt-1">Vence: {t.fecha}</p>
                  {t.categoria && <p className="text-xs text-blue-300 font-semibold">Categoría: {t.categoria}</p>}
                  <p className={`text-xs font-semibold ${t.estado === 'completada' ? 'text-green-400' : 'text-yellow-400'}`}>{t.estado}</p>
                  {Array.isArray(t.subtareas) && t.subtareas.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {t.subtareas.map((sub, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-gray-200">
                          <input type="checkbox" checked={sub.completada} readOnly className="accent-green-500" />
                          <span className={sub.completada ? 'line-through text-gray-400' : ''}>{sub.titulo}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div className="flex gap-2 justify-end">
                  <button onClick={() => toggleEstado(t)} className="flex items-center justify-center gap-1 bg-indigo-600 hover:bg-indigo-700 px-2 py-1 rounded text-white text-sm">
                    {t.estado === 'pendiente' ? <FaCheckCircle /> : <FaRedo />}
                  </button>
                  <button onClick={() => {
                    setModoEdicion(t._id);
                    setEditData({ titulo: t.titulo, descripcion: t.descripcion, fecha: t.fecha, categoria: t.categoria || '' });
                  }} className="flex items-center justify-center gap-1 bg-yellow-600 hover:bg-yellow-700 px-2 py-1 rounded text-white text-sm">
                    <FaEdit />
                  </button>
                  <button onClick={() => eliminarTarea(t._id)} className="flex items-center justify-center gap-1 bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-white text-sm">
                    <FaTrashAlt />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default Tareas;
