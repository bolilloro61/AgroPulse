import { useAuth } from '~/composables/useAuth'

export interface CropThresholdRange {
  min: number
  max: number
  minLetal?: number
  maxCrit?: number
  minCrit?: number
}

export interface CropThresholds {
  temperature: CropThresholdRange
  humidity: CropThresholdRange
}

export interface CropOption {
  id: string
  name: string
  icon: string
  description: string
  thresholds: CropThresholds
}

export interface RecommendationResult {
  nivel: string
  tipo: 'optimo' | 'precaucion' | 'advertencia' | 'critico' | 'helada'
  badgeColor: string
  badgeBg: string
  badgeText: string
  accion: string
  explicacion: string
}

export interface Plot {
  id: string
  name: string
  cropId: string
  cropType: string
  cropIcon: string
  thresholds: CropThresholds
  createdAt: string
}

export interface FarmInput {
  name: string
  location: string
}

export interface Farm {
  id: string
  name: string
  location: string
  plots: Plot[]
  createdAt: string
}

export interface UpdatePlot {
  name: string
  cropId: string
}

export interface Measurement {
  id: string
  date: string
  humidity: number
  temperature: number
  situation: string
  notes: string
  recommendation: RecommendationResult
  createdAt: string
}

interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: Record<string, unknown>
  authenticated?: boolean
}

export const useRecommendation = () => {
  const config = useRuntimeConfig()
  const { user } = useAuth()
  const apiBaseUrl = String(config.public.apiBaseUrl || 'http://localhost:8000').replace(/\/$/, '')

  const request = async <T>(path: string, options: ApiRequestOptions = {}): Promise<T> => {
    const headers: Record<string, string> = {}
    if (options.authenticated) {
      const token = await user.value?.getIdToken()
      if (!token) throw new Error('Debes iniciar sesión para realizar esta operación.')
      headers.Authorization = `Bearer ${token}`
    }

    return await $fetch<T>(`${apiBaseUrl}/api${path}`, {
      method: options.method || 'GET',
      body: options.body,
      headers
    })
  }

  return {
    getCrops: () => request<CropOption[]>('/crops'),
    evaluateMeasurement: (
      cropId: string,
      humidity: number,
      temperature: number,
      situation = 'Condición estable'
    ) => request<RecommendationResult>('/recommendations/evaluate', {
      method: 'POST',
      body: { cropId, humidity, temperature, situation }
    }),
    getFarms: () => request<Farm[]>('/farms', { authenticated: true }),
    createFarm: (farm: { name: string; location: string }) =>
      request<Farm>('/farms', { method: 'POST', body: farm, authenticated: true }),
    createPlot: (farmId: string, plot: { name: string; cropId: string }) =>
      request<Farm>(`/farms/${encodeURIComponent(farmId)}/plots`, {
        method: 'POST',
        body: plot,
        authenticated: true
      }),
    getPlot: (farmId: string, plotId: string) =>
      request<{ farm: Farm; plot: Plot }>(
        `/farms/${encodeURIComponent(farmId)}/plots/${encodeURIComponent(plotId)}`,
        { authenticated: true }
      ),
    getMeasurements: (farmId: string, plotId: string) =>
      request<Measurement[]>(
        `/farms/${encodeURIComponent(farmId)}/plots/${encodeURIComponent(plotId)}/measurements`,
        { authenticated: true }
      ),
    createMeasurement: (
      farmId: string,
      plotId: string,
      measurement: {
        date: string
        humidity: number
        temperature: number
        situation: string
        notes: string
      }
    ) =>
      request<Measurement>(
        `/farms/${encodeURIComponent(farmId)}/plots/${encodeURIComponent(plotId)}/measurements`,
        { method: 'POST', body: measurement, authenticated: true }
      ),
    deleteMeasurement: (measurementId: string) =>
      request<{ deleted: boolean }>(
        `/measurements/${encodeURIComponent(measurementId)}`,
        { method: 'DELETE', authenticated: true }
      ),
    updateMeasurement: (
      farmId: string,
      plotId: string,
      measurementId: string,
      measurement: {
        date: string
        humidity: number
        temperature: number
        situation: string
        notes: string
      }
    ) =>
      request<Measurement>(
        `/farms/${encodeURIComponent(farmId)}/plots/${encodeURIComponent(plotId)}/measurements/${encodeURIComponent(measurementId)}`,
        { method: 'PUT', body: measurement, authenticated: true }
      ),
    updatePlot: (farmId: string, plotId: string, plot: UpdatePlot) =>
      request<{ farm: Farm; plot: Plot }>(
        `/farms/${encodeURIComponent(farmId)}/plots/${encodeURIComponent(plotId)}`,
        { method: 'PUT', body: plot, authenticated: true }
      ),
    deletePlot: (farmId: string, plotId: string) =>
      request<{ deleted: boolean }>(
        `/farms/${encodeURIComponent(farmId)}/plots/${encodeURIComponent(plotId)}`,
        { method: 'DELETE', authenticated: true }
      ),
    updateFarm: (farmId: string, farm: FarmInput) =>
      request<Farm>(
        `/farms/${encodeURIComponent(farmId)}`,
        { method: 'PUT', body: farm, authenticated: true }
      ),
    deleteFarm: (farmId: string) =>
      request<{ deleted: boolean }>(
        `/farms/${encodeURIComponent(farmId)}`,
        { method: 'DELETE', authenticated: true }
      )
  }
}
