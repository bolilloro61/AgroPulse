<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 antialiased font-sans">
    <!-- Header de la sección de Parcelas -->
    <header class="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-emerald-100 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <NuxtLink to="/" class="flex items-center space-x-3 group">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-green-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20 group-hover:scale-105 transition-transform">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div>
              <span class="text-xl font-extrabold tracking-tight text-slate-900">AgroPulse</span>
              <p class="text-xs text-slate-500 hidden sm:block">Gestión de Fincas y Parcelas</p>
            </div>
          </NuxtLink>

          <nav class="flex items-center space-x-3">
            <NuxtLink
              to="/"
              class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-emerald-700 hover:bg-emerald-50 border border-slate-200 transition-all flex items-center gap-1.5"
            >
              <span>🏠</span>
              <span>Inicio</span>
            </NuxtLink>

            <div class="hidden sm:flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-xl">
              <span class="text-xs text-emerald-800 font-bold uppercase tracking-wider">{{ role || 'Usuario' }}</span>
              <span class="text-xs text-slate-500">({{ user?.email?.split('@')[0] }})</span>
            </div>

            <button
              @click="handleLogout"
              class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-red-600 hover:bg-red-50 border border-slate-200 transition-all"
            >
              Cerrar Sesión
            </button>
          </nav>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-10">
      <!-- Banner Principal -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider mb-2">
            🌱 Módulo de Catálogo Agrícola
          </div>
          <h1 class="text-2xl sm:text-4xl font-black text-slate-900">
            Fincas y Parcelas Registradas
          </h1>
          <p class="text-sm text-slate-600 mt-1 max-w-2xl">
            Parametriza y supervisa los umbrales ambientales mínimos y máximos esperados para cada lote de cultivo.
          </p>
        </div>

        <button
          @click="mostrarModalFinca = true"
          class="px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm transition-all shadow-lg shadow-emerald-600/30 hover:scale-[1.02] flex items-center gap-2 shrink-0"
        >
          <span>➕</span>
          <span>Nueva Finca</span>
        </button>
      </div>

      <!-- Lista de Fincas y Parcelas -->
      <div class="space-y-8">
        <div
          v-for="farm in farms"
          :key="farm.id"
          class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6"
        >
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-100">
            <div>
              <div class="flex items-center gap-3">
                <span class="text-2xl">🏡</span>
                <h2 class="text-xl sm:text-2xl font-black text-slate-900">{{ farm.name }}</h2>
              </div>
              <p class="text-xs sm:text-sm text-slate-500 mt-1">📍 {{ farm.location }}</p>
            </div>

            <button
              @click="abrirModalParcela(farm.id)"
              class="px-4 py-2 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 text-xs font-bold transition-all flex items-center gap-1.5"
            >
              <span>🌱</span>
              <span>Añadir Parcela</span>
            </button>
          </div>

          <!-- Grid de Parcelas de esta Finca -->
          <div v-if="farm.plots && farm.plots.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <div
              v-for="plot in farm.plots"
              :key="plot.id"
              class="bg-slate-50 rounded-2xl p-5 border border-slate-200/90 hover:border-emerald-300 transition-all space-y-4"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="text-base font-bold text-slate-900">{{ plot.name }}</h3>
                  <span class="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                    🌾 {{ plot.cropType }}
                  </span>
                </div>
              </div>

              <!-- Umbrales Ambientales Parametrizados -->
              <div class="space-y-2.5 pt-2 border-t border-slate-200">
                <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  Umbrales Biológicos Parametrizados:
                </div>

                <div class="bg-white rounded-xl p-3 border border-slate-200 space-y-1.5">
                  <div class="flex justify-between items-center text-xs">
                    <span class="text-slate-600 font-medium flex items-center gap-1">
                      <span>💧</span> Humedad Óptima:
                    </span>
                    <span class="font-mono font-bold text-emerald-700">
                      {{ plot.thresholds?.humidity?.min }}% - {{ plot.thresholds?.humidity?.max }}%
                    </span>
                  </div>
                  <div class="flex justify-between items-center text-xs">
                    <span class="text-slate-600 font-medium flex items-center gap-1">
                      <span>🌡️</span> Temperatura Óptima:
                    </span>
                    <span class="font-mono font-bold text-amber-700">
                      {{ plot.thresholds?.temperature?.min }}°C - {{ plot.thresholds?.temperature?.max }}°C
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 bg-slate-50 rounded-2xl border border-dashed border-slate-300 text-xs text-slate-500">
            No hay parcelas registradas en esta finca aún. Haz clic en "Añadir Parcela" para comenzar.
          </div>
        </div>
      </div>
    </main>

    <!-- Modal Nueva Finca -->
    <div v-if="mostrarModalFinca" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-black text-slate-900">Registrar Nueva Finca</h3>
          <button @click="mostrarModalFinca = false" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>

        <form class="space-y-4" @submit.prevent="guardarFinca">
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Nombre de la Finca</label>
            <input
              v-model="nuevaFinca.name"
              required
              placeholder="Ej. Finca Santa Lucía"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Ubicación / Sector</label>
            <input
              v-model="nuevaFinca.location"
              required
              placeholder="Ej. Valle del Fuerte, Km 12"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <div class="flex justify-end gap-3 pt-3">
            <button
              type="button"
              @click="mostrarModalFinca = false"
              class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/30"
            >
              Guardar Finca
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Nueva Parcela -->
    <div v-if="mostrarModalParcela" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-black text-slate-900">Registrar Parcela y Umbrales</h3>
          <button @click="mostrarModalParcela = false" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>

        <form class="space-y-4" @submit.prevent="guardarParcela">
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Nombre / Identificador del Lote</label>
            <input
              v-model="nuevaParcela.name"
              required
              placeholder="Ej. Lote A-3 Tomates"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Tipo de Cultivo</label>
            <select
              v-model="nuevaParcela.cropType"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
            >
              <option value="Tomate Saladette">Tomate Saladette</option>
              <option value="Maíz Grano">Maíz Grano</option>
              <option value="Aguacate Hass">Aguacate Hass</option>
              <option value="Vid / Uva">Vid / Uva</option>
              <option value="Chile Jalapeño">Chile Jalapeño</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3 pt-2">
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Humedad Mínima (%)</label>
              <input
                v-model.number="nuevaParcela.thresholds.humidity.min"
                type="number"
                min="0"
                max="100"
                required
                class="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Humedad Máxima (%)</label>
              <input
                v-model.number="nuevaParcela.thresholds.humidity.max"
                type="number"
                min="0"
                max="100"
                required
                class="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Temp. Mínima (°C)</label>
              <input
                v-model.number="nuevaParcela.thresholds.temperature.min"
                type="number"
                min="-10"
                max="50"
                required
                class="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Temp. Máxima (°C)</label>
              <input
                v-model.number="nuevaParcela.thresholds.temperature.max"
                type="number"
                min="-10"
                max="50"
                required
                class="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
              />
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-3">
            <button
              type="button"
              @click="mostrarModalParcela = false"
              class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/30"
            >
              Guardar Parcela
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

definePageMeta({
  middleware: 'auth'
})

const { user, role, logout } = useAuth()

const handleLogout = async () => {
  await logout()
  await navigateTo('/login')
}

const farms = ref([
  {
    id: 'f1',
    name: 'Finca Los Olivos',
    location: 'Valle Central, Sector A',
    plots: [
      {
        id: 'p1',
        name: 'Lote Tomates Norte',
        cropType: 'Tomate Saladette',
        thresholds: {
          humidity: { min: 60, max: 80 },
          temperature: { min: 18, max: 27 }
        }
      },
      {
        id: 'p2',
        name: 'Lote Maíz Sur',
        cropType: 'Maíz Grano',
        thresholds: {
          humidity: { min: 50, max: 70 },
          temperature: { min: 20, max: 30 }
        }
      }
    ]
  },
  {
    id: 'f2',
    name: 'Finca El Nogal',
    location: 'Sierra Norte, Km 45',
    plots: [
      {
        id: 'p3',
        name: 'Parcela Aguacates',
        cropType: 'Aguacate Hass',
        thresholds: {
          humidity: { min: 55, max: 75 },
          temperature: { min: 15, max: 26 }
        }
      }
    ]
  }
])

const mostrarModalFinca = ref(false)
const nuevaFinca = ref({
  name: '',
  location: ''
})

const guardarFinca = () => {
  if (!nuevaFinca.value.name || !nuevaFinca.value.location) return
  farms.value.push({
    id: 'f_' + Date.now(),
    name: nuevaFinca.value.name,
    location: nuevaFinca.value.location,
    plots: []
  })
  nuevaFinca.value = { name: '', location: '' }
  mostrarModalFinca.value = false
}

const mostrarModalParcela = ref(false)
const fincaSeleccionadaId = ref('')
const nuevaParcela = ref({
  name: '',
  cropType: 'Tomate Saladette',
  thresholds: {
    humidity: { min: 60, max: 80 },
    temperature: { min: 18, max: 27 }
  }
})

const abrirModalParcela = (farmId: string) => {
  fincaSeleccionadaId.value = farmId
  mostrarModalParcela.value = true
}

const guardarParcela = () => {
  const farm = farms.value.find(f => f.id === fincaSeleccionadaId.value)
  if (!farm) return
  farm.plots.push({
    id: 'p_' + Date.now(),
    name: nuevaParcela.value.name,
    cropType: nuevaParcela.value.cropType,
    thresholds: {
      humidity: { ...nuevaParcela.value.thresholds.humidity },
      temperature: { ...nuevaParcela.value.thresholds.temperature }
    }
  })
  nuevaParcela.value = {
    name: '',
    cropType: 'Tomate Saladette',
    thresholds: {
      humidity: { min: 60, max: 80 },
      temperature: { min: 18, max: 27 }
    }
  }
  mostrarModalParcela.value = false
}
</script>
