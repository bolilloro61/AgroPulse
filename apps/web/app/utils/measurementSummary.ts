import type { Measurement } from '~/composables/useRecommendation'

export interface MeasurementSummary {
  score: number
  status: 'safe' | 'warning' | 'risk'
  estado: string
  clase: string
  claseEstado: string
  claseTexto: string
  icono: string
  tendencia: string
  consejo: string
}

export const summarizeMeasurements = (measurements: Measurement[]): MeasurementSummary | null => {
  if (measurements.length === 0) return null

  const chronological = [...measurements].reverse()
  const scoresByType: Record<string, number> = {
    optimo: 100,
    precaucion: 65,
    advertencia: 40,
    critico: 15,
    helada: 0
  }
  const scores = chronological.map(item => scoresByType[item.recommendation?.tipo || ''] ?? 50)
  const score = scores.reduce((total, value) => total + value, 0) / scores.length

  let status: MeasurementSummary['status'] = 'safe'
  let estado = 'Segura'
  let clase = 'border-emerald-300 bg-emerald-50 text-emerald-900'
  let claseEstado = 'bg-emerald-600'
  let claseTexto = 'text-white'
  let icono = '🟢'
  if (score < 50) {
    status = 'risk'
    estado = 'En riesgo'
    clase = 'border-red-400 bg-red-50 text-red-900'
    claseEstado = 'bg-red-600'
    icono = '🔴'
  } else if (score < 80) {
    status = 'warning'
    estado = 'En alerta'
    clase = 'border-amber-400 bg-amber-50 text-amber-900'
    claseEstado = 'bg-amber-500'
    claseTexto = 'text-slate-950'
    icono = '🟡'
  }

  let tendencia = 'Sin cambios suficientes'
  let consejo = 'Continúa registrando mediciones para identificar una tendencia confiable.'
  if (chronological.length >= 2) {
    const difference = scores[scores.length - 1] - scores[0]
    if (difference >= 10) {
      tendencia = 'La parcela ha estado mejorando'
      consejo = 'Mantén el esquema actual y continúa observando los sensores para conservar las condiciones.'
    } else if (difference <= -10) {
      tendencia = 'La parcela ha estado empeorando'
      consejo = 'Revisa riego, drenaje y temperatura; corrige cualquier valor fuera de los rangos óptimos.'
    } else {
      tendencia = 'Las condiciones han permanecido relativamente estables'
      consejo = 'Mantén el monitoreo y realiza ajustes preventivos si una medición se sale del rango óptimo.'
    }

    const abruptChanges = chronological.some((item, index) => {
      if (index === 0) return false
      const previous = chronological[index - 1]
      const situation = String(item.situation || '').toLowerCase()
      return Math.abs(Number(item.humidity) - Number(previous.humidity)) >= 15 ||
        Math.abs(Number(item.temperature) - Number(previous.temperature)) >= 8 ||
        situation.includes('brusca') ||
        situation.includes('pronunciada')
    })
    if (abruptChanges) {
      tendencia = `Cambios bruscos detectados · ${tendencia}`
      consejo = 'Investiga las variaciones entre lecturas, revisa los sensores y protege la parcela ante cambios rápidos de riego o temperatura.'
    }
  }

  return { score, status, estado, clase, claseEstado, claseTexto, icono, tendencia, consejo }
}
