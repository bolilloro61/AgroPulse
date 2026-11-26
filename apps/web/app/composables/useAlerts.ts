import { ref, computed } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useRecommendation, type Farm, type Plot, type RecommendationResult } from '~/composables/useRecommendation'
import { summarizeMeasurements, type MeasurementSummary } from '~/utils/measurementSummary'

export type AlertWithParcel = {
  farmId: string
  farmName: string
  plot: Plot
  recommendation: RecommendationResult
  averageStatus: MeasurementSummary
}

const ALERT_TYPES = ['helada', 'advertencia', 'critico', 'precaucion'] as const
type AlertType = typeof ALERT_TYPES[number]

const isAlertType = (tipo: RecommendationResult['tipo']): tipo is AlertType => {
  return ALERT_TYPES.includes(tipo as AlertType)
}

export const useAlerts = () => {
  const { user, role } = useAuth()
  const { getFarms, evaluateMeasurement, getMeasurements } = useRecommendation()

  const farms = ref<Farm[]>([])
  const alerts = ref<AlertWithParcel[]>([])
  const loading = ref(false)
  const error = ref('')

  const hasActiveAlerts = computed(() => alerts.value.length > 0)

  const fetchFarmsAndCheckAlerts = async () => {
    if (!user.value) return

    loading.value = true
    error.value = ''

    try {
      farms.value = await getFarms()

      const alertResults: AlertWithParcel[] = []

      for (const farm of farms.value) {
        for (const plot of farm.plots || []) {
          if (role.value === 'Trabajador' && !plot.assigned) continue
          if (!plot.thresholds) continue

          const measurements = await getMeasurements(farm.id, plot.id).catch(() => [])
          if (!measurements.length) continue

          const latest = measurements[0]
          const averageStatus = summarizeMeasurements(measurements)
          const result = await evaluateMeasurement(
            plot.cropId,
            latest.humidity,
            latest.temperature,
            latest.situation
          ).catch(() => null)

          const latestRecommendationIsAlert = result !== null && isAlertType(result.tipo)
          const averageRisk = averageStatus?.status === 'risk'
          if (averageStatus && (latestRecommendationIsAlert || averageRisk)) {
            const recommendation = latestRecommendationIsAlert
              ? result
              : {
                  nivel: 'Riesgo alto según el estado promedio',
                  tipo: 'critico' as const,
                  badgeColor: 'border-red-500 bg-red-50 text-red-800',
                  badgeBg: 'bg-red-600',
                  badgeText: 'text-white',
                  accion: averageStatus.consejo,
                  explicacion: `Promedio de estado: ${Math.round(averageStatus.score)}/100. ${averageStatus.tendencia}.`
                }
            alertResults.push({
              farmId: farm.id,
              farmName: farm.name,
              plot,
              recommendation,
              averageStatus
            })
          }
        }
      }

      alerts.value = alertResults
    } catch (e) {
      console.error('Error al cargar alertas:', e)
      error.value = 'No se pudieron cargar las alertas.'
    } finally {
      loading.value = false
    }
  }

  const clearAlerts = () => {
    alerts.value = []
  }

  return {
    farms,
    alerts,
    loading,
    error,
    hasActiveAlerts,
    fetchFarmsAndCheckAlerts,
    clearAlerts
  }
}