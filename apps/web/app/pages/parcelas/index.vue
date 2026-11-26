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
          v-if="role === 'Gerente'"
          @click="mostrarModalFinca = true"
          class="px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm transition-all shadow-lg shadow-emerald-600/30 hover:scale-[1.02] flex items-center gap-2 shrink-0"
        >
          <span>➕</span>
          <span>Nueva Finca</span>
        </button>
      </div>

      <p v-if="errorParcelas" role="alert" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
        {{ errorParcelas }}
      </p>
      <p v-if="mensajeCsv" role="status" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
        {{ mensajeCsv }}
      </p>
      <input
        ref="csvParcelasInput"
        type="file"
        accept=".csv,text/csv"
        class="sr-only"
        @change="importarParcelasCsv"
      />

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

            <div v-if="role === 'Gerente'" class="relative">
              <button
                type="button"
                :aria-expanded="menuFincaAbierto === farm.id"
                aria-label="Acciones de la finca"
                @click="menuFincaAbierto = menuFincaAbierto === farm.id ? '' : farm.id"
                class="w-10 h-10 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xl font-black"
              >
                ⋮
              </button>
              <div v-if="menuFincaAbierto === farm.id" class="absolute right-0 top-12 z-30 w-56 p-2 rounded-xl bg-white border border-slate-200 shadow-xl space-y-1">
                <button @click="menuFincaAbierto = ''; abrirModalParcela(farm.id)" class="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-emerald-50 text-slate-700">🌱 Añadir parcela</button>
                <button @click="menuFincaAbierto = ''; abrirImportadorParcelas(farm.id)" class="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-emerald-50 text-slate-700">📄 Importar CSV</button>
                <button @click="menuFincaAbierto = ''; abrirModalTrabajadores(farm)" class="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-emerald-50 text-slate-700">👥 Administrar trabajadores</button>
                <button @click="menuFincaAbierto = ''; abrirModalEditarFinca(farm)" class="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-emerald-50 text-slate-700">✏️ Editar finca</button>
                <button @click="menuFincaAbierto = ''; confirmarEliminarFinca(farm)" class="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-red-50 text-red-700">🗑️ Eliminar finca</button>
              </div>
            </div>
          </div>

          <!-- Grid de Parcelas de esta Finca -->
          <div v-if="farm.plots && farm.plots.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <div
              v-for="plot in farm.plots"
              :key="plot.id"
              class="bg-slate-50 rounded-2xl p-5 border border-slate-200/90 transition-all space-y-4"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="text-base font-bold text-slate-900">{{ plot.name }}</h3>
                  <span class="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                    {{ plot.cropIcon || '🌾' }} {{ plot.cropType }}
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
              <NuxtLink
                v-if="role === 'Gerente' || plot.assigned"
                :to="`/parcelas/${farm.id}/${plot.id}`"
                class="inline-flex items-center gap-1 px-3 py-2 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-bold"
              >
                Abrir mediciones →
              </NuxtLink>
              <p v-else class="text-xs text-slate-500">Mediciones sin asignar. Solicita acceso al gerente.</p>
            </div>
            </div>

          <div v-else class="text-center py-8 bg-slate-50 rounded-2xl border border-dashed border-slate-300 text-xs text-slate-500">
            {{ role === 'Gerente'
              ? 'No hay parcelas registradas. Usa el menú de la finca para añadir una.'
              : 'Esta finca todavía no tiene parcelas registradas.' }}
          </div>
        </div>
      </div>
      <div v-if="role === 'Trabajador'" class="flex justify-center">
        <button
          @click="mostrarModalUnirFinca = true"
          class="px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm transition-all shadow-lg shadow-emerald-600/30 flex items-center gap-2"
        >
          <span>🔗</span>
          <span>Vincular finca existente</span>
        </button>
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
              v-model="nuevaParcela.cropId"
              required
              :disabled="cultivos.length === 0"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
            >
              <option v-for="crop in cultivos" :key="crop.id" :value="crop.id">
                {{ crop.icon }} {{ crop.name }}
              </option>
            </select>
            <p v-if="errorCatalogo" role="status" class="mt-1 text-[11px] text-amber-700">
              {{ errorCatalogo }} Se utilizará el catálogo local disponible.
            </p>
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
    <!-- Modal Editar Finca -->
    <div v-if="mostrarModalEditarFinca" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-black text-slate-900">Editar Finca</h3>
          <button @click="mostrarModalEditarFinca = false" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>

        <form class="space-y-4" @submit.prevent="guardarEdicionFinca">
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Nombre de la Finca</label>
            <input
              v-model="fincaEnEdicion.name"
              required
              placeholder="Ej. Finca Santa Lucía"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Ubicación / Sector</label>
            <input
              v-model="fincaEnEdicion.location"
              required
              placeholder="Ej. Valle del Fuerte, Km 12"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <div class="flex justify-end gap-3 pt-3">
            <button
              type="button"
              @click="mostrarModalEditarFinca = false"
              class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/30"
            >
              Guardar Cambios
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="mostrarModalUnirFinca" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-black text-slate-900">Vincular una finca</h3>
          <button @click="mostrarModalUnirFinca = false" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>
        <p class="text-sm text-slate-600">Ingresa el código de seis dígitos que te proporcionó el gerente. Las parcelas aparecerán; sus mediciones requieren asignación.</p>
        <p v-if="errorUnirFinca" role="alert" class="text-sm text-red-700">{{ errorUnirFinca }}</p>
        <form class="space-y-4" @submit.prevent="unirFinca">
          <input
            v-model="codigoFinca"
            type="text"
            inputmode="numeric"
            pattern="[0-9]{6}"
            maxlength="6"
            required
            aria-label="Código de finca"
            placeholder="000000"
            class="w-full px-4 py-3 rounded-xl border border-slate-300 text-center text-lg tracking-[0.4em] focus:ring-2 focus:ring-emerald-500 focus:outline-none"
          />
          <div class="flex justify-end gap-3">
            <button type="button" @click="mostrarModalUnirFinca = false" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Cancelar</button>
            <button type="submit" :disabled="uniendoFinca" class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs disabled:opacity-50">
              {{ uniendoFinca ? 'Vinculando...' : 'Vincular finca' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="mostrarModalTrabajadores && fincaTrabajadores" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200">
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-lg font-black text-slate-900">Administrar trabajadores</h3>
            <p class="text-xs text-slate-500">{{ fincaTrabajadores.name }}</p>
          </div>
          <button @click="mostrarModalTrabajadores = false" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>

        <div class="p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
          <p class="text-xs font-bold text-emerald-900 mb-2">Código para vincular esta finca</p>
          <p v-if="cargandoCodigoFinca" class="text-sm text-slate-500">Cargando código...</p>
          <p v-else class="font-mono text-2xl font-black tracking-[0.3em] text-emerald-800">{{ codigoFincaGerente || 'No disponible' }}</p>
          <p class="text-[11px] text-emerald-800 mt-2">Al vincularse, el trabajador podrá ver las parcelas. Asigna aquí cuáles pueden abrir y registrar mediciones.</p>
        </div>

        <p v-if="errorTrabajadores" role="alert" class="text-sm text-red-700">{{ errorTrabajadores }}</p>
        <p v-if="cargandoTrabajadores" class="text-sm text-slate-500">Cargando trabajadores...</p>
        <div v-else-if="trabajadores.length === 0" class="p-4 rounded-xl bg-slate-50 text-sm text-slate-600">
          Todavía no hay trabajadores vinculados. Comparte el código de la finca para que puedan registrarse.
        </div>
        <div v-else class="space-y-4">
          <div v-for="worker in trabajadores" :key="worker.uid" class="p-4 rounded-2xl border border-slate-200 space-y-3">
            <div>
              <p class="font-bold text-slate-900">{{ worker.displayName || worker.email }}</p>
              <p class="text-xs text-slate-500">{{ worker.email }}</p>
            </div>
            <fieldset class="space-y-2">
              <legend class="text-xs font-bold text-slate-700">Parcelas con acceso a mediciones</legend>
              <label v-for="plot in fincaTrabajadores.plots" :key="plot.id" class="flex items-center gap-2 text-sm text-slate-700">
                <input v-model="worker.plotIds" type="checkbox" :value="plot.id" class="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
                {{ plot.name }}
              </label>
              <p v-if="fincaTrabajadores.plots.length === 0" class="text-xs text-slate-500">Primero crea parcelas en esta finca.</p>
            </fieldset>
            <button
              type="button"
              :disabled="guardandoAsignacion === worker.uid"
              @click="guardarAsignacion(worker)"
              class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs disabled:opacity-50"
            >
              {{ guardandoAsignacion === worker.uid ? 'Guardando...' : 'Guardar asignación' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useRecommendation, type CropOption, type Farm, type FarmWorker } from '~/composables/useRecommendation'
import { parseCsv, validateCsvMeasurement } from '~/utils/csv'

definePageMeta({
  middleware: 'auth'
})

const { user, role, logout, isAuthReady } = useAuth()
const {
  getCrops,
  getFarms,
  createFarm: apiCreateFarm,
  createPlot: apiCreatePlot,
  createMeasurement: apiCreateMeasurement,
  joinFarm: apiJoinFarm,
  getFarmWorkerCode,
  getFarmWorkers,
  updateWorkerAssignments,
  updateFarm: apiUpdateFarm,
  deleteFarm: apiDeleteFarm
} = useRecommendation()

const handleLogout = async () => {
  await logout()
  await navigateTo('/login')
}

const farms = ref<Farm[]>([])
const cultivos = ref<CropOption[]>([])
const errorParcelas = ref('')
const errorCatalogo = ref('')
const mensajeCsv = ref('')
const csvParcelasInput = ref<HTMLInputElement | null>(null)
const fincaImportacionId = ref('')
const importandoParcelas = ref(false)
const mostrarModalUnirFinca = ref(false)
const codigoFinca = ref('')
const uniendoFinca = ref(false)
const errorUnirFinca = ref('')
const menuFincaAbierto = ref('')
const mostrarModalTrabajadores = ref(false)
const fincaTrabajadores = ref<Farm | null>(null)
const trabajadores = ref<FarmWorker[]>([])
const codigoFincaGerente = ref('')
const cargandoCodigoFinca = ref(false)
const cargandoTrabajadores = ref(false)
const guardandoAsignacion = ref('')
const errorTrabajadores = ref('')

const fetchFarms = async () => {
  if (!user.value) return
  try {
    farms.value = await getFarms()
    errorParcelas.value = ''
  } catch (err) {
    console.error('Error al cargar fincas:', err)
    errorParcelas.value = 'No se pudieron cargar las fincas. Verifica tu conexión e inténtalo de nuevo.'
  }
}

const fetchCultivos = async () => {
  try {
    cultivos.value = await getCrops()
    if (cultivos.value.length > 0 && !cultivos.value.some(crop => crop.id === nuevaParcela.value.cropId)) {
      nuevaParcela.value.cropId = cultivos.value[0].id
    }
    errorCatalogo.value = ''
  } catch (err) {
    console.error('Error al cargar el catálogo de cultivos:', err)
    errorCatalogo.value = 'No se pudo cargar el catálogo de Firebase.'
  }
}

onMounted(() => {
  fetchCultivos()
  if (isAuthReady.value && user.value) {
    fetchFarms()
  } else {
    watch(isAuthReady, (ready) => {
      if (ready && user.value) {
        fetchFarms()
      }
    })
  }
})

const mostrarModalFinca = ref(false)
const nuevaFinca = ref({
  name: '',
  location: ''
})

const mostrarModalEditarFinca = ref(false)
const fincaEnEdicion = ref({
  id: '',
  name: '',
  location: ''
})

const abrirModalEditarFinca = (farm: Farm) => {
  fincaEnEdicion.value = {
    id: farm.id,
    name: farm.name,
    location: farm.location
  }
  mostrarModalEditarFinca.value = true
}

const guardarEdicionFinca = async () => {
  if (!fincaEnEdicion.value.id || !fincaEnEdicion.value.name || !fincaEnEdicion.value.location) return
  try {
    await apiUpdateFarm(fincaEnEdicion.value.id, {
      name: fincaEnEdicion.value.name,
      location: fincaEnEdicion.value.location
    })
    mostrarModalEditarFinca.value = false
    errorParcelas.value = ''
    await fetchFarms()
  } catch (err) {
    console.error('Error al editar finca:', err)
    errorParcelas.value = 'No se pudo actualizar la finca. Inténtalo de nuevo.'
  }
}

const confirmarEliminarFinca = async (farm: Farm) => {
  const plotsCount = farm.plots?.length || 0
  const confirmMsg = plotsCount > 0
    ? `¿Estás seguro de eliminar la finca "${farm.name}"? Se eliminarán también sus ${plotsCount} parcelas asociadas.`
    : `¿Estás seguro de eliminar la finca "${farm.name}"?`

  if (!window.confirm(confirmMsg)) return

  try {
    await apiDeleteFarm(farm.id)
    errorParcelas.value = ''
    await fetchFarms()
  } catch (err) {
    console.error('Error al eliminar finca:', err)
    errorParcelas.value = 'No se pudo eliminar la finca. Inténtalo de nuevo.'
  }
}

const guardarFinca = async () => {
  if (!nuevaFinca.value.name || !nuevaFinca.value.location || !user.value) return
  try {
    await apiCreateFarm({
      name: nuevaFinca.value.name,
      location: nuevaFinca.value.location
    })
    nuevaFinca.value = { name: '', location: '' }
    mostrarModalFinca.value = false
    errorParcelas.value = ''
    await fetchFarms()
  } catch (err) {
    console.error('Error al guardar finca:', err)
    errorParcelas.value = 'No se pudo guardar la finca. Inténtalo de nuevo.'
  }
}

const mostrarModalParcela = ref(false)
const fincaSeleccionadaId = ref('')
const nuevaParcela = ref({
  name: '',
  cropId: 'tomate-saladette'
})

const abrirModalParcela = (farmId: string) => {
  if (role.value !== 'Gerente') return
  fincaSeleccionadaId.value = farmId
  mostrarModalParcela.value = true
}

const guardarParcela = async () => {
  if (!nuevaParcela.value.name || !nuevaParcela.value.cropId || !fincaSeleccionadaId.value) {
    console.warn('Faltan datos:', { name: nuevaParcela.value.name, fincaId: fincaSeleccionadaId.value })
    return
  }
  try {
    await apiCreatePlot(fincaSeleccionadaId.value, {
      name: nuevaParcela.value.name,
      cropId: nuevaParcela.value.cropId
    })
    nuevaParcela.value = {
      name: '',
      cropId: cultivos.value[0]?.id || ''
    }
    mostrarModalParcela.value = false
    errorParcelas.value = ''
    await fetchFarms()
  } catch (err) {
    console.error('Error al guardar parcela:', err)
    errorParcelas.value = 'No se pudo guardar la parcela. Verifica que la finca exista e inténtalo de nuevo.'
  }
}

const abrirImportadorParcelas = (farmId: string) => {
  if (role.value !== 'Gerente' || importandoParcelas.value) return
  fincaImportacionId.value = farmId
  csvParcelasInput.value?.click()
}

const unirFinca = async () => {
  if (role.value !== 'Trabajador' || !/^[0-9]{6}$/.test(codigoFinca.value)) return
  uniendoFinca.value = true
  errorUnirFinca.value = ''
  errorParcelas.value = ''
  try {
    const result = await apiJoinFarm(codigoFinca.value)
    mostrarModalUnirFinca.value = false
    codigoFinca.value = ''
    mensajeCsv.value = `Finca "${result.farmName}" vinculada. Solicita al gerente acceso a las parcelas que necesitas.`
    await fetchFarms()
  } catch (err) {
    console.error('Error al vincular finca:', err)
    errorUnirFinca.value = 'No se pudo vincular la finca. Verifica el código e inténtalo de nuevo.'
  } finally {
    uniendoFinca.value = false
  }
}

const abrirModalTrabajadores = async (farm: Farm) => {
  if (role.value !== 'Gerente') return
  fincaTrabajadores.value = farm
  mostrarModalTrabajadores.value = true
  trabajadores.value = []
  errorTrabajadores.value = ''
  cargandoCodigoFinca.value = true
  cargandoTrabajadores.value = true
  try {
    const [code, workers] = await Promise.all([
      getFarmWorkerCode(farm.id),
      getFarmWorkers(farm.id)
    ])
    codigoFincaGerente.value = code.code
    trabajadores.value = workers
  } catch (err) {
    console.error('Error al cargar trabajadores de la finca:', err)
    errorTrabajadores.value = 'No se pudieron cargar el código o los trabajadores.'
  } finally {
    cargandoCodigoFinca.value = false
    cargandoTrabajadores.value = false
  }
}

const guardarAsignacion = async (worker: FarmWorker) => {
  if (!fincaTrabajadores.value || role.value !== 'Gerente') return
  guardandoAsignacion.value = worker.uid
  errorTrabajadores.value = ''
  try {
    await updateWorkerAssignments(fincaTrabajadores.value.id, worker.uid, worker.plotIds)
    errorTrabajadores.value = ''
  } catch (err) {
    console.error('Error al actualizar parcelas asignadas:', err)
    errorTrabajadores.value = 'No se pudo guardar la asignación de parcelas.'
  } finally {
    guardandoAsignacion.value = ''
  }
}

const importarParcelasCsv = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  importandoParcelas.value = true
  errorParcelas.value = ''
  mensajeCsv.value = ''
  try {
    if (cultivos.value.length === 0) await fetchCultivos()
    if (cultivos.value.length === 0) throw new Error('No se pudo cargar el catálogo de cultivos.')
    if (!fincaImportacionId.value) throw new Error('Selecciona la finca donde se crearán las parcelas.')

    const { headers, rows } = parseCsv(await file.text())
    const nameIndex = headers.indexOf('name')
    const cropIndex = headers.indexOf('crop')
    if (nameIndex < 0 || cropIndex < 0) {
      throw new Error('El CSV de parcelas debe incluir las columnas name y crop.')
    }
    const dateIndex = headers.indexOf('date')
    const humidityIndex = headers.indexOf('humidity')
    const temperatureIndex = headers.indexOf('temperature')
    const situationIndex = headers.indexOf('situation')
    const notesIndex = headers.indexOf('notes')
    const measurementHeaderCount = [dateIndex, humidityIndex, temperatureIndex].filter(index => index >= 0).length
    if (measurementHeaderCount !== 0 && measurementHeaderCount !== 3) {
      throw new Error('Para incluir mediciones, el CSV debe tener date, humidity y temperature.')
    }
    if (measurementHeaderCount === 0 && (situationIndex >= 0 || notesIndex >= 0)) {
      throw new Error('Las columnas situation y notes solo se usan junto con date, humidity y temperature.')
    }

    const registros = rows.map((row, index) => {
      const line = index + 2
      const name = row[nameIndex]?.trim()
      const cropValue = row[cropIndex]?.trim().toLowerCase()
      const crop = cultivos.value.find(item =>
        item.id.toLowerCase() === cropValue || item.name.trim().toLowerCase() === cropValue
      )
      if (!name) throw new Error(`Fila ${line}: falta el nombre de la parcela.`)
      if (!crop) throw new Error(`Fila ${line}: el cultivo "${row[cropIndex]?.trim()}" no existe en el catálogo.`)

      const plotKey = name.toLowerCase()
      const measurementValues = {
        date: dateIndex < 0 ? '' : row[dateIndex] ?? '',
        humidity: humidityIndex < 0 ? '' : row[humidityIndex] ?? '',
        temperature: temperatureIndex < 0 ? '' : row[temperatureIndex] ?? '',
        situation: situationIndex < 0 ? '' : row[situationIndex] ?? '',
        notes: notesIndex < 0 ? '' : row[notesIndex] ?? ''
      }
      const hasMeasurementData = Object.values(measurementValues).some(value => value.trim() !== '')
      const measurement = hasMeasurementData
        ? validateCsvMeasurement(measurementValues, line)
        : null
      return { line, name, cropId: crop.id, plotKey, measurement }
    })

    const parcelas = new Map<string, { name: string; cropId: string; lines: number[] }>()
    for (const registro of registros) {
      const parcela = parcelas.get(registro.plotKey)
      if (parcela && parcela.cropId !== registro.cropId) {
        throw new Error(`Fila ${registro.line}: la parcela "${registro.name}" aparece con cultivos distintos.`)
      }
      if (parcela) {
        parcela.lines.push(registro.line)
      } else {
        parcelas.set(registro.plotKey, {
          name: registro.name,
          cropId: registro.cropId,
          lines: [registro.line]
        })
      }
    }

    const farmId = fincaImportacionId.value
    const failedRows = new Set<number>()
    const plotIds = new Map<string, string>()
    let importedPlots = 0
    let importedMeasurements = 0
    for (const [plotKey, parcela] of parcelas) {
      try {
        const farm = await apiCreatePlot(farmId, { name: parcela.name, cropId: parcela.cropId })
        const createdPlot = farm.plots[farm.plots.length - 1]
        if (!createdPlot?.id) throw new Error('La API no devolvió la parcela creada.')
        plotIds.set(plotKey, createdPlot.id)
        importedPlots += 1
      } catch (err) {
        console.error(`Error al importar parcela de las filas ${parcela.lines.join(', ')}:`, err)
        parcela.lines.forEach(line => failedRows.add(line))
      }
    }

    for (const registro of registros) {
      if (!registro.measurement) continue
      const plotId = plotIds.get(registro.plotKey)
      if (!plotId) continue
      try {
        await apiCreateMeasurement(farmId, plotId, registro.measurement)
        importedMeasurements += 1
      } catch (err) {
        console.error(`Error al importar medición en fila ${registro.line}:`, err)
        failedRows.add(registro.line)
      }
    }

    await fetchFarms()
    mensajeCsv.value = `Se importaron ${importedPlots} parcelas y ${importedMeasurements} mediciones.`
    if (failedRows.size) errorParcelas.value = `Fallaron las filas: ${[...failedRows].sort((a, b) => a - b).join(', ')}.`
  } catch (err) {
    console.error('Error al importar parcelas desde CSV:', err)
    errorParcelas.value = err instanceof Error ? err.message : 'No se pudieron importar las parcelas desde el CSV.'
  } finally {
    importandoParcelas.value = false
    fincaImportacionId.value = ''
    input.value = ''
  }
}
</script>
