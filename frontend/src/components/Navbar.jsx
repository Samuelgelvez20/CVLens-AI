import React from 'react';
import { FileText, Cpu, Database, History, Sliders, Sparkles, RefreshCw } from 'lucide-react';

export default function Navbar({
  tabActiva,
  onCambiarTab,
  onAbrirCriterios,
  health,
  onRefrescar,
}) {
  return (
    <header className="sticky top-0 z-30 bg-[#07090e]/90 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand & Identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                CVLens-AI
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                v2.0
              </span>
              <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <Sparkles className="w-2.5 h-2.5" />
                LangChain & Gemini LLM
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Motor Inteligente de Evaluación, Ranking y Análisis Curricular Estructurado
            </p>
          </div>
        </div>

        {/* Center / Navigation Tabs */}
        <div className="flex items-center bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => onCambiarTab('evaluador')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              tabActiva === 'evaluador'
                ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/25'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Evaluador en Vivo</span>
          </button>

          <button
            onClick={() => onCambiarTab('historial')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              tabActiva === 'historial'
                ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/25'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Historial & Rankings</span>
          </button>
        </div>

        {/* Right / Telemetry & Criterios Modal Trigger */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={onAbrirCriterios}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg transition-colors cursor-pointer"
            title="Ver Criterios y Ponderaciones del Modelo"
          >
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden md:inline">Ponderación</span>
          </button>

          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-slate-900/80 border border-slate-800 rounded-lg text-[11px] text-slate-400 font-mono">
            <Database className="w-3 h-3 text-emerald-400" />
            <span>{health?.database_engine === 'postgres' ? 'PostgreSQL' : 'DB Engine'}</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          </div>
        </div>
      </div>
    </header>
  );
}
