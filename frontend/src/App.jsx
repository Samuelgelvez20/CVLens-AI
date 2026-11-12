import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import EvaluadorView from './components/EvaluadorView';
import HistorialView from './components/HistorialView';
import CriteriosModal from './components/CriteriosModal';
import { checkHealth } from './services/api';

export default function App() {
  const [tabActiva, setTabActiva] = useState('historial');
  const [modalCriteriosAbierto, setModalCriteriosAbierto] = useState(false);
  const [health, setHealth] = useState(null);
  const [vacanteReusar, setVacanteReusar] = useState(null);

  useEffect(() => {
    async function loadHealth() {
      try {
        const data = await checkHealth();
        setHealth(data);
      } catch (err) {
        console.error('Error al consultar health check:', err);
      }
    }
    loadHealth();
  }, []);

  const handleCargarEnEvaluador = (titulo, descripcion) => {
    setVacanteReusar({ titulo, descripcion });
    setTabActiva('evaluador');
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* Navbar Superior */}
      <Navbar
        tabActiva={tabActiva}
        onCambiarTab={setTabActiva}
        onAbrirCriterios={() => setModalCriteriosAbierto(true)}
        health={health}
      />

      {/* Contenido Principal */}
      <main className="flex-1">
        {tabActiva === 'evaluador' ? (
          <EvaluadorView
            tituloInicial={vacanteReusar?.titulo || ''}
            descripcionInicial={vacanteReusar?.descripcion || ''}
            onVacanteGuardada={() => {
              // Notificar o refrescar
            }}
          />
        ) : (
          <HistorialView onCargarEnEvaluador={handleCargarEnEvaluador} />
        )}
      </main>

      {/* Modal de Criterios */}
      <CriteriosModal
        abierto={modalCriteriosAbierto}
        onCerrar={() => setModalCriteriosAbierto(false)}
      />

      {/* Footer minimalista */}
      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500">
        CVLens-AI &copy; 2026 &bull; Motor de Procesamiento Inteligente de Currículums con LangChain LCEL & Gemini
      </footer>
    </div>
  );
}
