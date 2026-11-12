import React from 'react';
import { X, CheckCircle2, ShieldCheck, Zap, Layers, AlertCircle } from 'lucide-react';

export default function CriteriosModal({ abierto, onCerrar }) {
  if (!abierto) return null;

  const criterios = [
    {
      categoria: 'Experiencia Relevante',
      peso: '40%',
      color: 'border-cyan-500 text-cyan-400',
      bg: 'bg-cyan-500/10',
      descripcion:
        'Alineación directa entre los roles previos del candidato, responsabilidades desempeñadas y los desafíos técnicos del puesto.',
    },
    {
      categoria: 'Habilidades Técnicas',
      peso: '35%',
      color: 'border-blue-500 text-blue-400',
      bg: 'bg-blue-500/10',
      descripcion:
        'Dominio de lenguajes, frameworks, librerías, bases de datos (SQL/NoSQL) y herramientas requeridas obligatorias y deseables.',
    },
    {
      categoria: 'Formación y Certificaciones',
      peso: '15%',
      color: 'border-indigo-500 text-indigo-400',
      bg: 'bg-indigo-500/10',
      descripcion:
        'Nivel educativo más alto alcanzado, especializaciones afines en informática/ingeniería y certificaciones vigentes.',
    },
    {
      categoria: 'Coherencia Profesional',
      peso: '10%',
      color: 'border-purple-500 text-purple-400',
      bg: 'bg-purple-500/10',
      descripcion:
        'Evolución temporal lógica, consistencia en trayectorias y claridad expositiva de proyectos y logros alcanzados.',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-[#0c1017] border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl relative">
        <button
          onClick={onCerrar}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5 mb-2">
          <div className="p-2 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Criterios de Evaluación y Ponderación</h3>
            <p className="text-xs text-slate-400">Parámetros heurísticos del Agente Evaluador de CVs</p>
          </div>
        </div>

        <p className="text-xs text-slate-300 mt-3 mb-4 leading-relaxed">
          El modelo LLM (<code className="text-cyan-300 font-mono">Gemini 3.1 Flash</code>) analiza el texto extraído del documento PDF y genera una salida estructurada validada con Pydantic aplicando la siguiente matriz orientativa:
        </p>

        <div className="space-y-2.5 mb-5">
          {criterios.map((c, i) => (
            <div
              key={i}
              className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 flex items-start justify-between gap-3"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold text-slate-100">{c.categoria}</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-normal">{c.descripcion}</p>
              </div>
              <div
                className={`px-2.5 py-1 rounded-lg font-mono text-xs font-extrabold border ${c.color} ${c.bg} shrink-0`}
              >
                {c.peso}
              </div>
            </div>
          ))}
        </div>

        <div className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-[11px] text-amber-200/90 leading-relaxed">
            <strong>Requisito Técnico:</strong> Sube archivos PDF con texto seleccionable nativo. El motor no aplica OCR sobre imágenes o fotos escaneadas sin capa de texto.
          </p>
        </div>

        <div className="mt-5 flex justify-end">
          <button
            onClick={onCerrar}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white rounded-lg transition-colors cursor-pointer"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}
