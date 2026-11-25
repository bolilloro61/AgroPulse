import { ref, computed } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useRecommendation, type Farm, type Plot, type RecommendationResult } from '~/composables/useRecommendation'

export type AlertWithParcel = {
  farmId: string
  farmName: string
  plot: Plot
  recommendation: RecommendationResult
}

const ALERT_TYPES = ['helada', 'advertencia', 'critico', 'precaucion'] as const
type AlertType = typeof ALERT_TYPES[number]

const isAlertType = (tipo: RecommendationResult['tipo']): tipo is AlertType => {
  return ALERT_TYPES.includes(tipo as AlertType)
}

export const useAlerts = () => {
  const { user } = useAuth()
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
          if (!plot.thresholds) continue

          const measurements = await getMeasurements(farm.id, plot.id).catch(() => [])
          if (!measurements.length) continue

          const latest = measurements[measurements.length - 1]
          const result = await evaluateMeasurement(
            plot.cropId,
            latest.humidity,
            latest.temperature,
            latest.situation
          ).catch(() => null)

          if (result && isAlertType(result.tipo)) {
            alertResults.push({
              farmId: farm.id,
              farmName: farm.name,
              plot,
              recommendation: result
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