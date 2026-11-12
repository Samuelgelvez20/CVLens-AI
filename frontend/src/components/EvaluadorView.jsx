import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  Trash2,
  Sparkles,
  Zap,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  GraduationCap,
  Clock,
  Layers,
  Save,
  Check,
  TrendingUp,
} from 'lucide-react';
import { evaluarCVs, guardarLote } from '../services/api';

const PLANTILLAS_VACANTE = [
  {
    titulo: 'Desarrollador Backend Python / IA',
    texto: `Puesto: Desarrollador Backend Python / IA

Requisitos obligatorios:
- Mínimo 2-3 años de experiencia desarrollando servicios y APIs en Python.
- Experiencia sólida construyendo APIs REST con FastAPI o Django.
- Manejo de bases de datos relacionales (PostgreSQL) y consultas SQL optimizadas.
- Uso de Git y flujos de trabajo colaborativos (Git Flow / Pull Requests).
- Inglés técnico intermedio para lectura fluida de documentación.

Requisitos deseables:
- Experiencia con contenedores Docker y Docker Compose.
- Conocimientos en integración de modelos de lenguaje (LangChain, OpenAI o Gemini).
- Experiencia escribiendo pruebas automatizadas con pytest.
- Formación en Ingeniería de Sistemas, Computación o afines.

Responsabilidades principales:
- Diseñar, desarrollar y desplegar microservicios y APIs escalables en Python.
- Integrar pipelines de procesamiento inteligente y modelos de IA generativa.
- Documentar endpoints técnicos y optimizar el rendimiento de base de datos.`,
  },
  {
    titulo: 'Desarrollador Full Stack Junior (Java & React)',
    texto: `Puesto: Desarrollador Full Stack Junior (Java 21 + React)

Requisitos obligatorios:
- Formación técnica o universitaria en Ingeniería de Software, Sistemas o afines.
- Fundamentos sólidos en Java 21, Spring Boot y patrones de arquitectura limpia.
- Experiencia práctica en React con TypeScript o JavaScript moderno.
- Manejo de bases de datos relacionales (PostgreSQL, MySQL) con JPA/Hibernate.
- Dominio de Git, GitHub y metodologías ágiles (Scrum).

Requisitos deseables:
- Conocimientos de Arquitectura Hexagonal y Domain-Driven Design (DDD).
- Experiencia con contenedores Docker y scripts en Linux.
- Integración de autenticación con JWT y documentación OpenAPI/Swagger.

Responsabilidades:
- Construir APIs RESTful seguras y componentes frontend reactivos.
- Participar activamente en ceremonias ágiles y revisiones de código colaborativas.`,
  },
];

export default function EvaluadorView({
  tituloInicial = '',
  descripcionInicial = '',
  onVacanteGuardada,
}) {
  const [archivos, setArchivos] = useState([]);
  const [tituloVacante, setTituloVacante] = useState(tituloInicial);
  const [descripcionPuesto, setDescripcionPuesto] = useState(descripcionInicial);
  const [evaluando, setEvaluando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [guardadoExitoso, setGuardadoExitoso] = useState(false);
  const [resultadoLote, setResultadoLote] = useState(null);
  const [error, setError] = useState(null);

  const handleSeleccionarArchivos = (e) => {
    if (e.target.files) {
      const seleccionados = Array.from(e.target.files).filter(
        (f) => f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf')
      );
      setArchivos((prev) => [...prev, ...seleccionados]);
      setError(null);
    }
  };

  const handleEliminarArchivo = (indice) => {
    setArchivos((prev) => prev.filter((_, i) => i !== indice));
  };

  const handleLimpiarTodo = () => {
    setArchivos([]);
    setTituloVacante('');
    setDescripcionPuesto('');
    setResultadoLote(null);
    setError(null);
    setGuardadoExitoso(false);
  };

  const handleEjecutarEvaluacion = async () => {
    if (archivos.length === 0) {
      setError('Carga al menos un archivo PDF de currículum para evaluar.');
      return;
    }
    if (!descripcionPuesto.trim()) {
      setError('Escribe los requisitos y descripción del puesto a evaluar.');
      return;
    }

    setEvaluando(true);
    setError(null);
    setGuardadoExitoso(false);

    try {
      const data = await evaluarCVs(archivos, descripcionPuesto, tituloVacante);
      setResultadoLote(data);
    } catch (err) {
      setError(err.message || 'Ocurrió un error al evaluar los currículums');
    } finally {
      setEvaluando(false);
    }
  };

  const handleGuardarResultados = async () => {
    if (!resultadoLote) return;

    const itemsValidos = resultadoLote.resultados
      .filter((r) => r.ok && r.analisis)
      .map((r) => ({
        nombre_archivo: r.nombre_archivo,
        analisis: r.analisis,
      }));

    if (itemsValidos.length === 0) {
      setError('No hay análisis válidos para guardar.');
      return;
    }

    setGuardando(true);
    setError(null);

    try {
      await guardarLote(
        resultadoLote.titulo,
        resultadoLote.descripcion,
        itemsValidos
      );
      setGuardadoExitoso(true);
      if (onVacanteGuardada) {
        onVacanteGuardada();
      }
    } catch (err) {
      setError(err.message || 'Error al persistir en la base de datos');
    } finally {
      setGuardando(false);
    }
  };

  function getBadgeAjuste(porcentaje) {
    if (porcentaje >= 80) {
      return {
        label: 'Excelente',
        color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
        bar: 'bg-emerald-500',
      };
    }
    if (porcentaje >= 60) {
      return {
        label: 'Bueno',
        color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
        bar: 'bg-cyan-500',
      };
    }
    if (porcentaje >= 40) {
      return {
        label: 'Regular',
        color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
        bar: 'bg-amber-500',
      };
    }
    return {
      label: 'Bajo',
      color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
      bar: 'bg-rose-500',
    };
  }

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Columna Izquierda: Entradas (Archivos + Puesto) */}
        <div className="lg:col-span-5 space-y-5">
          {/* 1. Carga de Archivos PDF */}
          <div className="bg-[#0c1017] border border-slate-800 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                <span>1. Currículums en PDF ({archivos.length})</span>
              </h2>
              {archivos.length > 0 && (
                <button
                  onClick={() => setArchivos([])}
                  className="text-[11px] text-rose-400 hover:text-rose-300 transition-colors"
                >
                  Quitar todos
                </button>
              )}
            </div>

            {/* Drag & Drop Area */}
            <label className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-xl p-5 flex flex-col items-center justify-center text-center cursor-pointer transition-all bg-slate-900/40 hover:bg-slate-900/80 group">
              <input
                type="file"
                multiple
                accept=".pdf,application/pdf"
                onChange={handleSeleccionarArchivos}
                className="hidden"
              />
              <div className="w-10 h-10 rounded-xl bg-slate-800 group-hover:bg-cyan-500/10 group-hover:text-cyan-400 flex items-center justify-center text-slate-400 transition-colors mb-2">
                <UploadCloud className="w-5 h-5" />
              </div>
              <span className="text-xs font-semibold text-slate-200 block">
                Selecciona o arrastra CVs en PDF
              </span>
              <span className="text-[11px] text-slate-500 mt-0.5">
                Archivos con texto seleccionable (evaluación paralela)
              </span>
            </label>

            {/* Lista de archivos seleccionados */}
            {archivos.length > 0 && (
              <div className="mt-3 space-y-1.5 max-h-40 overflow-y-auto pr-1">
                {archivos.map((file, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between px-3 py-1.5 bg-slate-900 border border-slate-800/80 rounded-lg text-xs"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                      <span className="text-slate-200 truncate">{file.name}</span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        ({(file.size / 1024).toFixed(0)} KB)
                      </span>
                    </div>
                    <button
                      onClick={() => handleEliminarArchivo(i)}
                      className="text-slate-500 hover:text-rose-400 p-1 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 2. Definición del Puesto / Vacante */}
          <div className="bg-[#0c1017] border border-slate-800 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-cyan-400" />
                <span>2. Requisitos de la Vacante</span>
              </h2>
            </div>

            {/* Quick Templates */}
            <div className="flex flex-wrap gap-1.5 mb-3">
              <span className="text-[10px] font-bold text-slate-500 uppercase self-center mr-1">
                Plantillas:
              </span>
              {PLANTILLAS_VACANTE.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setTituloVacante(p.titulo);
                    setDescripcionPuesto(p.texto);
                  }}
                  className="px-2 py-0.5 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 text-[10px] font-medium transition-colors cursor-pointer"
                >
                  {p.titulo.split('(')[0].trim()}
                </button>
              ))}
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-semibold text-slate-400 block mb-1">
                  Título de la Vacante (Opcional)
                </label>
                <input
                  type="text"
                  value={tituloVacante}
                  onChange={(e) => setTituloVacante(e.target.value)}
                  placeholder="Ej. Desarrollador Backend Python Junior"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-400 block mb-1">
                  Descripción & Requisitos del Puesto
                </label>
                <textarea
                  rows={9}
                  value={descripcionPuesto}
                  onChange={(e) => setDescripcionPuesto(e.target.value)}
                  placeholder="Escribe o pega aquí los requisitos, responsabilidades, tecnologías y experiencia requerida..."
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 leading-relaxed font-mono text-[11px]"
                ></textarea>
              </div>
            </div>

            {/* Actions */}
            {error && (
              <div className="mt-3 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            <div className="mt-4 flex items-center gap-3">
              <button
                disabled={evaluando}
                onClick={handleEjecutarEvaluacion}
                className="flex-1 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-extrabold text-xs rounded-xl shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {evaluando ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                    <span>Evaluando con Gemini LLM...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Analizar {archivos.length > 0 ? `${archivos.length} CV(s)` : 'Candidatos'}</span>
                  </>
                )}
              </button>

              <button
                onClick={handleLimpiarTodo}
                className="px-3.5 py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 rounded-xl text-xs font-semibold transition-colors cursor-pointer"
              >
                Limpiar
              </button>
            </div>
          </div>
        </div>

        {/* Columna Derecha: Resultados del Análisis en Tiempo Real */}
        <div className="lg:col-span-7 space-y-4">
          {evaluando ? (
            <div className="bg-[#0c1017] border border-slate-800 rounded-2xl p-12 text-center shadow-xl">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center justify-center mb-4 animate-bounce">
                <Sparkles className="w-7 h-7" />
              </div>
              <h3 className="text-base font-bold text-white mb-2">
                Agente Evaluador en Ejecución
              </h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                Extrayendo texto de {archivos.length} PDF(s), invocando cadena LCEL estructurada con Gemini 3.1 Flash y ponderando criterios en paralelo...
              </p>
              <div className="mt-6 max-w-xs mx-auto bg-slate-900 rounded-full h-1.5 overflow-hidden">
                <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full w-2/3 animate-pulse"></div>
              </div>
            </div>
          ) : !resultadoLote ? (
            /* Estado Inicial Informativo */
            <div className="bg-[#0c1017] border border-slate-800 rounded-2xl p-8 shadow-xl text-center">
              <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto mb-3 text-cyan-400">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-base font-extrabold text-white mb-2">
                Panel de Evaluación y Ranking
              </h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed mb-6">
                Carga uno o varios currículums en PDF a la izquierda, define los requisitos del puesto y presiona <strong>Analizar Candidatos</strong>. El modelo estructurado evaluará cada perfil devolviendo porcentajes de ajuste, fortalezas y áreas de mejora.
              </p>

              {/* Arquitectura de 3 pasos */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left max-w-xl mx-auto">
                <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl">
                  <span className="text-[10px] font-mono font-bold text-cyan-400 block mb-1">
                    01. EXTRACCIÓN
                  </span>
                  <p className="text-[11px] text-slate-300">
                    Procesamiento de texto con PyPDF2 y sanitización segura.
                  </p>
                </div>
                <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl">
                  <span className="text-[10px] font-mono font-bold text-blue-400 block mb-1">
                    02. AGENTE LLM
                  </span>
                  <p className="text-[11px] text-slate-300">
                    LangChain LCEL estructurado con Pydantic y reintentos ante cuellos de botella.
                  </p>
                </div>
                <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl">
                  <span className="text-[10px] font-mono font-bold text-emerald-400 block mb-1">
                    03. PERSISTENCIA
                  </span>
                  <p className="text-[11px] text-slate-300">
                    Almacenamiento ACID en PostgreSQL y exportación a CSV.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            /* Resultados Listos */
            <div className="space-y-4">
              {/* Resumen Superior del Lote */}
              <div className="bg-[#0c1017] border border-slate-800 rounded-2xl p-5 shadow-xl">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
                  <div>
                    <span className="text-[10px] font-mono font-bold text-cyan-400 uppercase tracking-wider block mb-0.5">
                      Evaluación Completada
                    </span>
                    <h2 className="text-base font-bold text-white leading-tight">
                      {resultadoLote.titulo}
                    </h2>
                  </div>

                  {/* Botón Guardar en BD */}
                  <div className="flex items-center gap-2">
                    {guardadoExitoso ? (
                      <div className="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl text-xs font-bold flex items-center gap-1.5">
                        <Check className="w-3.5 h-3.5" />
                        <span>Guardado en Historial</span>
                      </div>
                    ) : (
                      <button
                        disabled={guardando}
                        onClick={handleGuardarResultados}
                        className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                      >
                        <Save className="w-3.5 h-3.5" />
                        <span>{guardando ? 'Guardando...' : 'Guardar Análisis'}</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Métricas KPI del Lote */}
                <div className="grid grid-cols-3 gap-3 mt-4 text-center">
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-slate-800">
                    <span className="text-base font-mono font-extrabold text-white block">
                      {resultadoLote.total_exitosos} / {resultadoLote.total}
                    </span>
                    <span className="text-[10px] text-slate-400 uppercase">Candidatos Evaluados</span>
                  </div>
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-slate-800">
                    <span className="text-base font-mono font-extrabold text-cyan-400 block">
                      {resultadoLote.duracion_segundos}s
                    </span>
                    <span className="text-[10px] text-slate-400 uppercase">Tiempo de Respuesta</span>
                  </div>
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-slate-800">
                    <span className="text-base font-mono font-extrabold text-emerald-400 block">
                      {
                        resultadoLote.resultados.filter(
                          (r) => r.ok && r.analisis?.porcentaje_ajuste >= 70
                        ).length
                      }
                    </span>
                    <span className="text-[10px] text-slate-400 uppercase">Recomendados (&gt;70%)</span>
                  </div>
                </div>
              </div>

              {/* Lista de Candidatos Evaluados */}
              <div className="space-y-3">
                {resultadoLote.resultados.map((item, idx) => {
                  if (!item.ok) {
                    return (
                      <div
                        key={idx}
                        className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2.5"
                      >
                        <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                        <div>
                          <strong>{item.nombre_archivo}:</strong> {item.error}
                        </div>
                      </div>
                    );
                  }

                  const an = item.analisis;
                  const badge = getBadgeAjuste(an.porcentaje_ajuste);

                  return (
                    <div
                      key={idx}
                      className="p-5 rounded-2xl bg-[#0c1017] border border-slate-800 hover:border-slate-700 shadow-xl transition-all"
                    >
                      {/* Cabecera del Candidato */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-9 h-9 rounded-xl flex items-center justify-center font-mono font-extrabold text-sm ${
                              idx === 0
                                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                                : 'bg-slate-800 text-slate-300'
                            }`}
                          >
                            #{idx + 1}
                          </div>
                          <div>
                            <h3 className="text-sm font-extrabold text-white leading-tight">
                              {an.nombre_candidato}
                            </h3>
                            <span className="text-[11px] text-slate-400 font-mono">
                              {item.nombre_archivo}
                            </span>
                          </div>
                        </div>

                        {/* Match Score & Badge */}
                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <span className="text-2xl font-mono font-black text-white">
                              {an.porcentaje_ajuste}%
                            </span>
                            <span className="block text-[10px] text-slate-400">
                              Ajuste Calculado
                            </span>
                          </div>
                          <span
                            className={`px-3 py-1 rounded-lg text-xs font-extrabold border ${badge.color}`}
                          >
                            {badge.label}
                          </span>
                        </div>
                      </div>

                      {/* Barra de Progreso */}
                      <div className="w-full bg-slate-900 rounded-full h-2 mb-4 overflow-hidden border border-slate-800">
                        <div
                          className={`h-full rounded-full ${badge.bar} transition-all duration-500`}
                          style={{ width: `${an.porcentaje_ajuste}%` }}
                        ></div>
                      </div>

                      {/* Detalles: Experiencia & Educación */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3 text-xs">
                        <div className="flex items-center gap-2 text-slate-300">
                          <Briefcase className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                          <span>
                            <strong>Experiencia:</strong> {an.experiencia_años} años relevantes
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-slate-300">
                          <GraduationCap className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                          <span className="truncate">
                            <strong>Educación:</strong> {an.education}
                          </span>
                        </div>
                      </div>

                      {/* Resumen Experiencia */}
                      <div className="mb-3.5 p-3 bg-slate-900/70 rounded-xl text-xs text-slate-300 leading-relaxed border border-slate-800/60">
                        <span className="font-semibold text-slate-200 block mb-1">
                          Experiencia Relevante para el Puesto:
                        </span>
                        {an.experiencia_relevante}
                      </div>

                      {/* Habilidades Clave */}
                      <div className="mb-3.5">
                        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
                          Habilidades Clave Identificadas
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {an.habilidades_clave.map((hab, hIdx) => (
                            <span
                              key={hIdx}
                              className="px-2.5 py-0.5 rounded-lg bg-slate-800 text-slate-200 text-xs border border-slate-700/70 font-medium"
                            >
                              {hab}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Fortalezas & Áreas de Mejora */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-slate-800/80 text-xs">
                        <div className="p-3 bg-emerald-500/5 rounded-xl border border-emerald-500/20">
                          <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1.5 mb-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Fortalezas Principales
                          </span>
                          <ul className="space-y-1 text-slate-300 text-[11px]">
                            {an.fortalezas.map((f, fIdx) => (
                              <li key={fIdx} className="flex items-start gap-1.5">
                                <span className="text-emerald-400 mt-0.5">•</span>
                                <span>{f}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="p-3 bg-amber-500/5 rounded-xl border border-amber-500/20">
                          <span className="text-[11px] font-bold text-amber-400 flex items-center gap-1.5 mb-1.5">
                            <AlertCircle className="w-3.5 h-3.5" />
                            Áreas de Mejora & Brechas
                          </span>
                          <ul className="space-y-1 text-slate-300 text-[11px]">
                            {an.areas_mejora.map((m, mIdx) => (
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
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
