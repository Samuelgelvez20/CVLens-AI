const API_BASE = '/api';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Error al conectar con el motor backend');
  return res.json();
}

export async function listarVacantes() {
  const res = await fetch(`${API_BASE}/vacantes`);
  if (!res.ok) throw new Error('Error al consultar historial de vacantes');
  return res.json();
}

export async function obtenerVacante(vacanteId) {
  const res = await fetch(`${API_BASE}/vacantes/${vacanteId}`);
  if (!res.ok) throw new Error('Error al obtener datos de la vacante');
  return res.json();
}

export async function obtenerAnalisisVacante(vacanteId) {
  const res = await fetch(`${API_BASE}/vacantes/${vacanteId}/analisis`);
  if (!res.ok) throw new Error('Error al consultar ranking de candidatos');
  return res.json();
}

export async function evaluarCVs(archivos, descripcionPuesto, tituloVacante) {
  const formData = new FormData();
  archivos.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('descripcion_puesto', descripcionPuesto);
  if (tituloVacante) {
    formData.append('titulo_vacante', tituloVacante);
  }

  const res = await fetch(`${API_BASE}/evaluar`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Fallo durante la evaluación de los currículums');
  }

  return res.json();
}

export async function guardarLote(titulo, descripcion, items) {
  const res = await fetch(`${API_BASE}/vacantes/guardar`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      titulo,
      descripcion,
      items,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Error al persistir análisis en base de datos');
  }

  return res.json();
}

export function obtenerUrlExportacionCSV(vacanteId) {
  return `${API_BASE}/vacantes/${vacanteId}/export-csv`;
}
