// src/components/Estadisticas.jsx
import React, { useEffect, useState } from 'react';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import { useNavigate } from 'react-router-dom';
Chart.register(...registerables);

const Estadisticas = () => {
  const [tareas, setTareas] = useState([]);
  const [error, setError] = useState('');
  const API = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTareas = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/api/tasks`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (res.ok) setTareas(data);
        else setError(data.error || 'No se pudieron obtener estadísticas.');
      } catch (err) {
        setError('Error de red.');
      }
    };
    fetchTareas();
  }, []);

  const completadas = tareas.filter(t => t.estado === 'completada').length;
  const pendientes = tareas.filter(t => t.estado === 'pendiente').length;
  const categorias = [...new Set(tareas.map(t => t.categoria).filter(Boolean))];
  const tareasPorCategoria = categorias.map(cat => tareas.filter(t => t.categoria === cat).length);
  const fechas = [...new Set(tareas.map(t => t.fecha).sort())];
  const tareasPorFecha = fechas.map(f => tareas.filter(t => t.fecha === f).length);

  return (
    <div className="bg-gray-900 text-white p-6 min-h-screen">
      <button onClick={() => navigate('/dashboard')} className="text-blue-400 mb-4">← Volver</button>
      <h2 className="text-2xl font-bold mb-6">📊 Estadísticas de Tareas</h2>

      {error && <p className="text-red-400">{error}</p>}

      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-gray-800 p-4 rounded">
          <h3 className="text-lg mb-2">Tareas por Estado</h3>
          <Doughnut
            data={{
              labels: ['Pendientes', 'Completadas'],
              datasets: [{
                data: [pendientes, completadas],
                backgroundColor: ['#facc15', '#4ade80'],
              }]
            }}
          />
        </div>

        <div className="bg-gray-800 p-4 rounded">
          <h3 className="text-lg mb-2">Tareas por Categoría</h3>
          <Bar
            data={{
              labels: categorias,
              datasets: [{
                label: 'Cantidad',
                data: tareasPorCategoria,
                backgroundColor: '#60a5fa'
              }]
            }}
          />
        </div>

        <div className="bg-gray-800 p-4 rounded md:col-span-2">
          <h3 className="text-lg mb-2">Tareas por Fecha</h3>
          <Line
            data={{
              labels: fechas,
              datasets: [{
                label: 'Tareas creadas',
                data: tareasPorFecha,
                fill: false,
                borderColor: '#c084fc',
                tension: 0.3
              }]
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default Estadisticas;

