import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Calendar,
  Users,
  Award,
  ChevronRight,
  Search,
  ExternalLink,
  GraduationCap,
  Briefcase,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Sparkles,
} from 'lucide-react';
import { listarVacantes, obtenerAnalisisVacante, obtenerUrlExportacionCSV } from '../services/api';

export default function HistorialView({ onCargarEnEvaluador }) {
  const [vacantes, setVacantes] = useState([]);
  const [vacanteSeleccionada, setVacanteSeleccionada] = useState(null);
  const [detalleRanking, setDetalleRanking] = useState(null);
  const [cargandoVacantes, setCargandoVacantes] = useState(true);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);
  const [filtroTexto, setFiltroTexto] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarHistorial();
  }, []);

  async function cargarHistorial() {
    setCargandoVacantes(true);
    setError(null);
    try {
      const data = await listarVacantes();
      setVacantes(data);
      if (data.length > 0) {
        seleccionarVacante(data[0].id);
      }
    } catch (err) {
      setError(err.message || 'No se pudo cargar el historial');
    } finally {
      setCargandoVacantes(false);
    }
  }

  async function seleccionarVacante(id) {
    setCargandoDetalle(true);
    setVacanteSeleccionada(id);
    try {
      const res = await obtenerAnalisisVacante(id);
      setDetalleRanking(res);
    } catch (err) {
      setError(err.message || 'Error al obtener detalle del ranking');
    } finally {
      setCargandoDetalle(false);
    }
  }

  const vacantesFiltradas = vacantes.filter((v) =>
    v.titulo.toLowerCase().includes(filtroTexto.toLowerCase()) ||
    v.descripcion.toLowerCase().includes(filtroTexto.toLowerCase())
  );

  function getBadgeAjuste(porcentaje) {
    if (porcentaje >= 80) {
      return {
        label: 'Excelente',
        color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
      };
    }
    if (porcentaje >= 60) {
      return {
        label: 'Bueno',
        color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
      };
    }
    if (porcentaje >= 40) {
      return {
        label: 'Regular',
        color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      };
    }
    return {
      label: 'Bajo',
      color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
    };
  }

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Sidebar izquierdo: Lista de Vacantes Guardadas */}
        <div className="lg:col-span-4 bg-[#0c1017] border border-slate-800 rounded-2xl p-4 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Users className="w-4 h-4 text-cyan-400" />
              <span>Vacantes Guardadas</span>
            </h2>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
              {vacantes.length}
            </span>
          </div>

          {/* Search bar */}
          <div className="relative mb-3">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={filtroTexto}
              onChange={(e) => setFiltroTexto(e.target.value)}
              placeholder="Buscar vacante por nombre..."
              className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Lista de vacantes */}
          <div className="space-y-2 max-h-[640px] overflow-y-auto pr-1">
            {cargandoVacantes ? (
              <div className="py-8 text-center text-xs text-slate-400 animate-pulse">
                Cargando historial de vacantes...
              </div>
            ) : vacantesFiltradas.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                No se encontraron vacantes registradas.
              </div>
            ) : (
              vacantesFiltradas.map((v) => {
                const seleccionada = vacanteSeleccionada === v.id;
                return (
                  <div
                    key={v.id}
                    onClick={() => seleccionarVacante(v.id)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer ${
                      seleccionada
                        ? 'bg-slate-900 border-cyan-500 shadow-md shadow-cyan-500/10'
                        : 'bg-slate-900/50 border-slate-800/80 hover:bg-slate-900 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h3
                        className={`text-xs font-bold leading-snug line-clamp-2 ${
                          seleccionada ? 'text-cyan-300' : 'text-white'
                        }`}
                      >
                        {v.titulo}
                      </h3>
                      <ChevronRight
                        className={`w-3.5 h-3.5 shrink-0 transition-transform ${
                          seleccionada ? 'text-cyan-400 translate-x-0.5' : 'text-slate-600'
                        }`}
                      />
                    </div>
                    <div className="flex items-center gap-3 mt-2 text-[11px] text-slate-400">
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3 text-cyan-400" />
                        <strong>{v.total_cvs}</strong> CV(s)
                      </span>
                      <span className="flex items-center gap-1 text-[10px] text-slate-500 font-mono">
                        <Calendar className="w-2.5 h-2.5" />
                        {new Date(v.fecha_creacion).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Panel derecho: Detalle de la Vacante y Ranking de Candidatos */}
        <div className="lg:col-span-8 space-y-4">
          {cargandoDetalle ? (
            <div className="p-12 text-center bg-[#0c1017] border border-slate-800 rounded-2xl animate-pulse text-xs text-slate-400">
              Cargando ranking y análisis de la vacante...
            </div>
          ) : !detalleRanking ? (
            <div className="p-12 text-center bg-[#0c1017] border border-slate-800 rounded-2xl text-xs text-slate-500">
              Selecciona una vacante en el panel lateral para consultar su ranking.
            </div>
          ) : (
            <>
              {/* Header de la Vacante Seleccionada */}
              <div className="bg-[#0c1017] border border-slate-800 rounded-2xl p-5 shadow-xl">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[10px] font-mono font-bold">
                        Vacante #{detalleRanking.vacante.id}
                      </span>
                      <span className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
                        <Calendar className="w-3 h-3" />
                        {new Date(detalleRanking.vacante.fecha_creacion).toLocaleString()}
                      </span>
                    </div>
                    <h1 className="text-base font-extrabold text-white">
                      {detalleRanking.vacante.titulo}
                    </h1>
                  </div>

                  {/* Botones de acción: Exportar CSV & Cargar en Formulario */}
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() =>
                        onCargarEnEvaluador(
                          detalleRanking.vacante.titulo,
                          detalleRanking.vacante.descripcion
                        )
                      }
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 hover:text-white rounded-lg border border-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Re-usar Vacante</span>
                    </button>

                    <a
                      href={obtenerUrlExportacionCSV(detalleRanking.vacante.id)}
                      download
                      className="px-3 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-xs font-bold text-slate-950 rounded-lg shadow-md shadow-cyan-500/20 transition-all flex items-center gap-1.5"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Exportar CSV</span>
                    </a>
                  </div>
                </div>

                {/* Resumen de Requisitos */}
                <div className="mt-4 p-3 bg-slate-900/80 border border-slate-800/80 rounded-xl">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                    Descripción & Perfil Requerido
                  </span>
                  <p className="text-xs text-slate-300 whitespace-pre-line leading-relaxed max-h-36 overflow-y-auto pr-1">
                    {detalleRanking.vacante.descripcion}
                  </p>
                </div>
              </div>

              {/* Ranking de Candidatos */}
              <div className="bg-[#0c1017] border border-slate-800 rounded-2xl p-5 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-bold text-white flex items-center gap-2">
                    <Award className="w-4 h-4 text-cyan-400" />
                    <span>Ranking de Candidatos ({detalleRanking.total_candidatos})</span>
                  </h2>
                  <span className="text-xs text-slate-400">
                    Ordenado por porcentaje de ajuste
                  </span>
                </div>

                {detalleRanking.ranking.length === 0 ? (
                  <p className="text-xs text-slate-500 py-6 text-center">
                    No hay candidatos asociados a esta vacante.
                  </p>
                ) : (
                  <div className="space-y-3">
                    {detalleRanking.ranking.map((item, idx) => {
                      const badge = getBadgeAjuste(item.porcentaje_ajuste);
                      return (
                        <div
                          key={item.id}
                          className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all"
                        >
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3 pb-3 border-b border-slate-800/80">
                            <div className="flex items-center gap-3">
                              <div
                                className={`w-8 h-8 rounded-lg flex items-center justify-center font-mono font-extrabold text-xs ${
                                  idx === 0
                                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                                    : 'bg-slate-800 text-slate-300'
                                }`}
                              >
                                #{idx + 1}
                              </div>
                              <div>
                                <h3 className="text-sm font-bold text-white leading-tight">
                                  {item.nombre_candidato}
                                </h3>
                                <span className="text-[11px] text-slate-400 font-mono">
                                  {item.nombre_archivo_pdf}
                                </span>
                              </div>
                            </div>

                            {/* Score & Badge */}
                            <div className="flex items-center gap-3">
                              <div className="text-right">
                                <span className="text-lg font-extrabold text-white font-mono">
                                  {item.porcentaje_ajuste}%
                                </span>
                                <span className="block text-[10px] text-slate-400">
                                  Ajuste al Puesto
                                </span>
                              </div>
                              <span
                                className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${badge.color}`}
                              >
                                {badge.label}
                              </span>
                            </div>
                          </div>

                          {/* Info rápida */}
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3 text-xs">
                            <div className="flex items-center gap-2 text-slate-300">
                              <Briefcase className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                              <span>
                                <strong>Experiencia:</strong> {item.experiencia_anos} años
                              </span>
                            </div>
                            <div className="flex items-center gap-2 text-slate-300">
                              <GraduationCap className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                              <span className="truncate">
                                <strong>Educación:</strong> {item.education}
                              </span>
                            </div>
                          </div>

                          {/* Resumen Experiencia */}
                          <div className="mb-3 p-2.5 bg-slate-950/60 rounded-lg text-xs text-slate-300 leading-relaxed border border-slate-800/50">
                            <strong>Experiencia Relevante:</strong> {item.experiencia_relevante}
                          </div>

                          {/* Habilidades Clave */}
                          <div className="mb-3">
                            <span className="text-[11px] font-bold text-slate-400 block mb-1.5">
                              Habilidades Clave
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {item.habilidades_clave.map((hab, hIdx) => (
                                <span
                                  key={hIdx}
                                  className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-200 text-[11px] border border-slate-700/60 font-medium"
                                >
                                  {hab}
                                </span>
                              ))}
                            </div>
                          </div>

                          {/* Fortalezas & Áreas de Mejora */}
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800/60 text-xs">
                            <div>
                              <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1 mb-1">
                                <CheckCircle2 className="w-3 h-3" />
                                Fortalezas Principales
                              </span>
                              <ul className="space-y-1 text-slate-300 text-[11px]">
                                {item.fortalezas.map((f, fIdx) => (
                                  <li key={fIdx} className="flex items-start gap-1.5">
                                    <span className="text-emerald-400 mt-0.5">•</span>
                                    <span>{f}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <span className="text-[11px] font-bold text-amber-400 flex items-center gap-1 mb-1">
                                <AlertTriangle className="w-3 h-3" />
                                Áreas de Mejora
                              </span>
                              <ul className="space-y-1 text-slate-300 text-[11px]">
                                {item.areas_mejora.map((m, mIdx) => (
                                  <li key={mIdx} className="flex items-start gap-1.5">
                                    <span className="text-amber-400 mt-0.5">•</span>
                                    <span>{m}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
