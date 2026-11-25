<template>
  <div class="min-h-screen bg-slate-100 text-slate-800 antialiased font-sans">
    <!-- Header de Navegación -->
    <header class="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-emerald-100 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <NuxtLink to="/parcelas" class="p-2 rounded-xl text-slate-500 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </NuxtLink>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-lg font-black tracking-tight text-slate-900">AgroPulse</span>
                <span class="px-2 py-0.5 text-[11px] font-bold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                  Hoja de Mediciones
                </span>
              </div>
              <p class="text-xs text-slate-500 hidden sm:block">
                {{ farm?.name || 'Finca' }} &rsaquo; {{ plot?.name || 'Parcela' }}
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <button
              @click="mostrarModalNuevaMedicion = true; mensajeExito = ''"
              class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs sm:text-sm shadow-md shadow-emerald-600/30 flex items-center gap-1.5 transition-all"
            >
              <span>➕</span>
              <span>Nueva Medición</span>
            </button>
            <button
              type="button"
              :disabled="importandoMediciones"
              @click="csvMedicionesInput?.click()"
              class="px-3 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs sm:text-sm font-bold transition-all flex items-center gap-1 disabled:opacity-50"
            >
              <span>📄</span>
              <span>{{ importandoMediciones ? 'Importando...' : 'Importar CSV' }}</span>
            </button>
            <input
              ref="csvMedicionesInput"
              type="file"
              accept=".csv,text/csv"
              class="sr-only"
              @change="importarMedicionesCsv"
            />
            <button
              @click="abrirModalEditarParcela"
              class="px-3 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs sm:text-sm font-bold transition-all flex items-center gap-1"
              title="Editar Parcela"
            >
              <span>✏️</span>
              <span>Editar</span>
            </button>
            <button
              @click="confirmarEliminarParcela"
              class="px-3 py-2 rounded-xl bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 text-xs sm:text-sm font-bold transition-all flex items-center gap-1"
              title="Eliminar Parcela"
            >
              <span>🗑️</span>
              <span>Eliminar</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      <p v-if="errorMediciones" role="alert" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
        {{ errorMediciones }}
      </p>
      <p v-if="mensajeExito" role="status" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
        {{ mensajeExito }}
      </p>

      <!-- Breadcrumb y Resumen del Cultivo -->
      <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div class="flex flex-col lg:flex-row justify-between lg:items-center gap-4 pb-6 border-b border-slate-100">
          <div>
            <div class="flex items-center gap-2 text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">
              <span>🏡 {{ farm?.name || 'Cargando Finca...' }}</span>
              <span>&bull;</span>
              <span>📍 {{ farm?.location || 'Ubicación' }}</span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-black text-slate-900 flex items-center gap-3">
              <span>{{ plot?.name || 'Parcela' }}</span>
              <span class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                {{ cropIcon }} {{ plot?.cropType || 'Cultivo' }}
              </span>
            </h1>
            <p class="text-xs sm:text-sm text-slate-600 mt-1 max-w-3xl">
              Registro continuo de parámetros ambientales, bitácora de condiciones estables y motor de recomendaciones agronómicas explicables.
            </p>
          </div>

          <!-- Umbrales Ideales Asignados desde Firebase -->
          <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200/90 space-y-2 shrink-0">
            <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Condiciones Ideales Asignadas:
            </span>
            <div class="flex items-center gap-4 text-xs font-mono">
              <div class="flex items-center gap-1.5">
                <span class="text-base">💧</span>
                <div>
                  <span class="text-slate-500 block text-[10px]">Humedad Óptima:</span>
                  <span class="font-bold text-emerald-700">{{ thresholds.humidity.min }}% - {{ thresholds.humidity.max }}%</span>
                </div>
              </div>
              <div class="w-px h-8 bg-slate-200"></div>
              <div class="flex items-center gap-1.5">
                <span class="text-base">🌡️</span>
                <div>
                  <span class="text-slate-500 block text-[10px]">Temp. Óptima:</span>
                  <span class="font-bold text-amber-700">{{ thresholds.temperature.min }}°C - {{ thresholds.temperature.max }}°C</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Banner de Último Estado y Recomendación Activa -->
        <div v-if="ultimaMedicion" class="rounded-2xl p-5 border" :class="clasesRecomendacion(ultimaMedicion.recommendation).contenedor">
          <div class="flex flex-col md:flex-row justify-between md:items-center gap-4">
            <div class="space-y-1.5">
              <div class="flex items-center gap-2">
                <span class="text-xs font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full" :class="clasesRecomendacion(ultimaMedicion.recommendation).insignia">
                  {{ ultimaMedicion.recommendation?.nivel }}
                </span>
                <span class="text-xs text-slate-500">
                  Última medición: {{ formatearFecha(ultimaMedicion.date) }}
                </span>
              </div>
              <h3 class="text-base font-bold text-slate-900">
                Recomendación: {{ ultimaMedicion.recommendation?.accion }}
              </h3>
              <p class="text-xs text-slate-700 font-mono leading-relaxed">
                {{ ultimaMedicion.recommendation?.explicacion }}
              </p>
            </div>

            <div class="flex flex-col gap-3 shrink-0 w-full md:w-64">
              <div class="flex items-center justify-center gap-3 bg-white/80 p-3 rounded-xl border border-slate-200/60 min-w-44">
                <div class="text-center px-2">
                  <span class="text-[10px] text-slate-500 block">Humedad</span>
                  <span class="text-base font-black text-emerald-700 font-mono">{{ ultimaMedicion.humidity }}%</span>
                </div>
                <div class="w-px h-6 bg-slate-200"></div>
                <div class="text-center px-2">
                  <span class="text-[10px] text-slate-500 block">Temperatura</span>
                  <span class="text-base font-black text-amber-700 font-mono">{{ ultimaMedicion.temperature }}°C</span>
                </div>
              </div>
              <div v-if="estadoPromedio" class="p-3 rounded-xl border-2" :class="estadoPromedio.clase">
                <div class="flex items-center justify-between gap-2 mb-1">
                  <span class="text-[10px] font-bold uppercase tracking-wider opacity-70">Estado promedio</span>
                  <span class="px-2 py-0.5 rounded-full text-[11px] font-black" :class="[estadoPromedio.claseEstado, estadoPromedio.claseTexto]">
                    {{ estadoPromedio.icono }} {{ estadoPromedio.estado }}
                  </span>
                </div>
                <p class="text-xs font-bold mt-0.5">{{ estadoPromedio.tendencia }}</p>
                <p class="text-[11px] leading-snug mt-1">{{ estadoPromedio.consejo }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtros de mediciones -->
      <div class="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-sm space-y-3">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div class="flex items-center gap-2 text-xs font-bold text-slate-800 uppercase tracking-wider">
            <span>🔍</span>
            <span>Filtros de mediciones</span>
            <span class="text-slate-400 font-normal">({{ medicionesFiltradas.length }} de {{ mediciones.length }} filas)</span>
          </div>

          <button
            v-if="filtrosActivos"
            @click="limpiarFiltros"
            class="text-xs text-emerald-700 hover:text-emerald-800 font-bold flex items-center gap-1"
          >
            <span>✕</span> Limpiar Filtros
          </button>
        </div>

        <!-- Inputs de Filtro -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <!-- Filtro por Día -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">📅 Filtrar por Día:</label>
            <input
              type="date"
              v-model="filtroDia"
              class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <!-- Filtro por Humedad -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">💧 Filtrar por Humedad:</label>
            <select
              v-model="filtroHumedad"
              class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="todos">Todas las humedades</option>
              <option value="baja">Baja / Estrés Seco (&lt; {{ thresholds.humidity.min }}%)</option>
              <option value="optima">Óptima ({{ thresholds.humidity.min }}% - {{ thresholds.humidity.max }}%)</option>
              <option value="alta">Alta / Saturada (&gt; {{ thresholds.humidity.max }}%)</option>
            </select>
          </div>

          <!-- Filtro por Temperatura -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">🌡️ Filtrar por Temperatura:</label>
            <select
              v-model="filtroTemperatura"
              class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="todas">Todas las temperaturas</option>
              <option value="frio">Frío / Helada (&lt; {{ thresholds.temperature.min }}°C)</option>
              <option value="optima">Óptima ({{ thresholds.temperature.min }}°C - {{ thresholds.temperature.max }}°C)</option>
              <option value="calor">Calor Extremo (&gt; {{ thresholds.temperature.max }}°C)</option>
            </select>
          </div>

          <!-- Buscador de Situación / Notas -->
          <div>
            <label class="block font-semibold text-slate-700 mb-1">🔎 Búsqueda de Situación:</label>
            <input
              type="text"
              v-model="filtroTexto"
              placeholder="Ej. Riego, Estable, Caída..."
              class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>
        </div>
      </div>

      <!-- Tabla de mediciones -->
      <div class="bg-white rounded-2xl border border-slate-300 shadow-sm overflow-hidden">
        <!-- Resumen de registros -->
        <div class="bg-emerald-800 text-white px-4 py-2.5 flex items-center justify-between text-xs font-semibold">
          <div class="flex items-center gap-3">
            <span class="flex items-center gap-1.5">
              <svg class="w-4 h-4 text-emerald-300" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3 3h18v18H3V3zm16 16V5H5v14h14zM7 7h10v2H7V7zm0 4h10v2H7v-2zm0 4h7v2H7v-2z"/>
              </svg>
              <span>Mediciones &bull; {{ plot?.name || 'Parcela' }}</span>
            </span>
          </div>
          <span class="text-emerald-200 text-[11px] font-mono">
            {{ medicionesFiltradas.length }} registros cargados
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <!-- Encabezados de la tabla -->
            <thead class="bg-slate-100 text-slate-700 font-bold border-b-2 border-slate-300 uppercase tracking-wider text-[11px]">
              <tr>
                <th class="px-3 py-3 border-r border-slate-200 text-center w-12 bg-slate-200/70">#</th>
                <th class="px-4 py-3 border-r border-slate-200">Fecha y Hora</th>
                <th class="px-4 py-3 border-r border-slate-200 text-center">Humedad Suelo</th>
                <th class="px-4 py-3 border-r border-slate-200 text-center">Temperatura</th>
                <th class="px-4 py-3 border-r border-slate-200">Situación / Estado</th>
                <th class="px-4 py-3 border-r border-slate-200">Diagnóstico del Motor</th>
                <th class="px-4 py-3 border-r border-slate-200">Recomendación Explicable</th>
                <th class="px-3 py-3 text-center w-24">Acciones</th>
              </tr>
            </thead>

            <!-- Filas de Mediciones -->
            <tbody class="divide-y divide-slate-200 font-sans">
              <tr
                v-for="(med, idx) in medicionesFiltradas"
                :key="med.id"
                class="hover:bg-emerald-50/50 transition-colors"
                :class="idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'"
              >
                <!-- Celda #: Índice -->
                <td class="px-3 py-3 border-r border-slate-200 text-center font-mono text-slate-400 bg-slate-100/60 font-semibold">
                  {{ idx + 1 }}
                </td>

                <!-- Celda Fecha -->
                <td class="px-4 py-3 border-r border-slate-200 font-mono whitespace-nowrap">
                  <div class="font-bold text-slate-800">{{ formatearFecha(med.date) }}</div>
                  <div class="text-[10px] text-slate-400">{{ formatearHora(med.date) }}</div>
                </td>

                <!-- Celda Humedad -->
                <td class="px-4 py-3 border-r border-slate-200 text-center">
                  <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-mono font-bold" :class="claseHumedad(med.humidity)">
                    <span>💧</span>
                    <span>{{ med.humidity }}%</span>
                  </div>
                </td>

                <!-- Celda Temperatura -->
                <td class="px-4 py-3 border-r border-slate-200 text-center">
                  <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-mono font-bold" :class="claseTemperatura(med.temperature)">
                    <span>🌡️</span>
                    <span>{{ med.temperature }}°C</span>
                  </div>
                </td>

                <!-- Celda Situación -->
                <td class="px-4 py-3 border-r border-slate-200">
                  <span class="inline-block px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                    {{ med.situation || 'Condición estable' }}
                  </span>
                  <p v-if="med.notes" class="text-[11px] text-slate-500 italic mt-1 line-clamp-1">
                    "{{ med.notes }}"
                  </p>
                </td>

                <!-- Celda Diagnóstico -->
                <td class="px-4 py-3 border-r border-slate-200 whitespace-nowrap">
                  <span
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold border"
                    :class="clasesRecomendacion(med.recommendation).contenedor"
                  >
                    <span>{{ iconoSituacion(med.recommendation?.tipo) }}</span>
                    <span>{{ med.recommendation?.nivel || 'Analizado' }}</span>
                  </span>
                </td>

                <!-- Celda Recomendación Explicable -->
                <td class="px-4 py-3 border-r border-slate-200 max-w-xs sm:max-w-md">
                  <div class="font-bold text-slate-900 leading-snug">
                    {{ med.recommendation?.accion }}
                  </div>
                  <div class="text-[11px] text-slate-600 font-mono mt-1 line-clamp-2 leading-relaxed">
                    {{ med.recommendation?.explicacion }}
                  </div>
                </td>

                <!-- Celda Acciones -->
                <td class="px-3 py-3 text-center whitespace-nowrap">
                  <div class="flex items-center justify-center gap-1">
                    <button
                      @click="verDetalleMedicion(med)"
                      title="Ver Detalle Completo"
                      class="p-1.5 rounded-lg text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 transition-colors"
                    >
                      👁️
                    </button>
                    <button
                      @click="editarMedicion(med)"
                      title="Editar Medición"
                      class="p-1.5 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-100 transition-colors"
                    >
                      ✏️
                    </button>
                    <button
                      @click="eliminarMedicion(med.id)"
                      title="Eliminar Registro"
                      class="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>

              <!-- Estado Vacío -->
              <tr v-if="medicionesFiltradas.length === 0">
                <td colspan="8" class="text-center py-12 px-4 text-slate-500 bg-white">
                  <div class="max-w-sm mx-auto space-y-3">
                    <div class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-2xl mx-auto">
                      📋
                    </div>
                    <p class="font-bold text-slate-800 text-sm">No se encontraron mediciones registradas</p>
                    <p class="text-xs text-slate-500">
                      {{ filtrosActivos ? 'Intenta modificar o limpiar los filtros seleccionados.' : 'Comienza registrando la primera medición con el botón superior.' }}
                    </p>
                    <button
                      v-if="!filtrosActivos"
                      @click="mostrarModalNuevaMedicion = true; mensajeExito = ''"
                      class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl transition-all"
                    >
                      ➕ Registrar Primera Medición
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Modal Nueva Medición con Calculadora en Vivo -->
    <div v-if="mostrarModalNuevaMedicion" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200 my-8">
        <div class="flex justify-between items-center border-b border-slate-100 pb-3">
          <div>
            <div class="text-[11px] font-bold text-emerald-700 uppercase tracking-wider">
              {{ farm?.name }} &bull; {{ plot?.name }}
            </div>
            <h3 class="text-xl font-black text-slate-900">Registrar Medición del Cultivo</h3>
          </div>
          <button @click="mostrarModalNuevaMedicion = false" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>

        <form class="space-y-4" @submit.prevent="guardarMedicion">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Fecha y Hora -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Fecha y Hora de la Lectura</label>
              <input
                type="datetime-local"
                v-model="nuevaMedicion.date"
                required
                class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>

            <!-- Humedad -->
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="text-xs font-bold text-slate-700 uppercase">Humedad Suelo (%)</label>
                <span class="text-xs font-mono font-bold text-emerald-700">{{ nuevaMedicion.humidity }}%</span>
              </div>
              <input
                type="number"
                min="0"
                max="100"
                v-model.number="nuevaMedicion.humidity"
                required
                placeholder="65"
                class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none font-mono"
              />
              <div class="text-[10px] text-slate-400 mt-1">
                Óptimo: {{ thresholds.humidity.min }}% - {{ thresholds.humidity.max }}%
              </div>
            </div>

            <!-- Temperatura -->
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="text-xs font-bold text-slate-700 uppercase">Temperatura (°C)</label>
                <span class="text-xs font-mono font-bold text-amber-700">{{ nuevaMedicion.temperature }}°C</span>
              </div>
              <input
                type="number"
                step="0.5"
                min="-15"
                max="60"
                v-model.number="nuevaMedicion.temperature"
                required
                placeholder="24"
                class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none font-mono"
              />
              <div class="text-[10px] text-slate-400 mt-1">
                Óptimo: {{ thresholds.temperature.min }}°C - {{ thresholds.temperature.max }}°C
              </div>
            </div>

            <!-- Situación del Cultivo -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Situación / Dinámica de la Parcela</label>
              <select
                v-model="nuevaMedicion.situation"
                class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
              >
                <option value="Condición estable">Condición estable</option>
                <option value="Bajo riego activo">Bajo riego activo</option>
                <option value="Caída brusca de humedad (-15%)">Caída brusca de humedad (-15% en 6h)</option>
                <option value="Alza térmica pronunciada (+8°C)">Alza térmica pronunciada (+8°C)</option>
                <option value="Lluvia reciente">Lluvia reciente</option>
                <option value="Estrés visible en follaje">Estrés visible en follaje</option>
              </select>
            </div>

            <!-- Observaciones Adicionales -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Notas / Observaciones del Operador (Opcional)</label>
              <input
                type="text"
                v-model="nuevaMedicion.notes"
                placeholder="Ej. Sensor revisado, sector poniente sin goteras"
                class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>
          </div>

          <!-- Diagnóstico en Tiempo Real Calculado para este Cultivo -->
          <div class="bg-emerald-950 text-white rounded-2xl p-4 sm:p-5 border border-emerald-800 space-y-3">
            <div class="flex items-center justify-between border-b border-emerald-800 pb-2">
              <span class="text-[11px] font-mono text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Diagnóstico y Recomendación en Tiempo Real
              </span>
              <span class="text-xs font-bold px-2.5 py-0.5 rounded-full" :class="clasesRecomendacion(previewRecomendacion).insignia">
                {{ previewRecomendacion.nivel }}
              </span>
            </div>

            <div>
              <span class="text-[11px] text-emerald-300 uppercase font-bold block">Tratamiento Sugerido:</span>
              <p class="text-sm font-bold text-white mt-0.5">{{ previewRecomendacion.accion }}</p>
            </div>

            <div class="bg-emerald-900/60 p-3 rounded-xl border border-emerald-700/60">
              <span class="text-[10px] text-emerald-300 font-mono font-bold block">REGLA DISPARADORA (TRANSPARENTE):</span>
              <p class="text-xs text-emerald-100 font-mono mt-0.5 leading-relaxed">{{ previewRecomendacion.explicacion }}</p>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              @click="mostrarModalNuevaMedicion = false"
              class="px-4 py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="guardandoMedicion"
              class="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/30 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <span v-if="guardandoMedicion" class="animate-spin">⏳</span>
              <span>Guardar medición</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Editar Medición -->
    <div v-if="medicionEditando" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200 my-8">
        <div class="flex justify-between items-center border-b border-slate-100 pb-3">
          <div>
            <div class="text-[11px] font-bold text-emerald-700 uppercase tracking-wider">
              {{ farm?.name }} &bull; {{ plot?.name }}
            </div>
            <h3 class="text-xl font-black text-slate-900">Editar Medición del Cultivo</h3>
          </div>
          <button @click="medicionEditando = false" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>

        <form class="space-y-4" @submit.prevent="actualizarMedicion">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Fecha y Hora de la Lectura</label>
              <input v-model="medicionAEditar.date" type="datetime-local" required class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
            </div>
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="text-xs font-bold text-slate-700 uppercase">Humedad Suelo (%)</label>
                <span class="text-xs font-mono font-bold text-emerald-700">{{ medicionAEditar.humidity }}%</span>
              </div>
              <input v-model.number="medicionAEditar.humidity" type="number" min="0" max="100" required class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none font-mono" />
              <div class="text-[10px] text-slate-400 mt-1">Óptimo: {{ thresholds.humidity.min }}% - {{ thresholds.humidity.max }}%</div>
            </div>
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="text-xs font-bold text-slate-700 uppercase">Temperatura (°C)</label>
                <span class="text-xs font-mono font-bold text-amber-700">{{ medicionAEditar.temperature }}°C</span>
              </div>
              <input v-model.number="medicionAEditar.temperature" type="number" min="-15" max="60" step="0.5" required class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none font-mono" />
              <div class="text-[10px] text-slate-400 mt-1">Óptimo: {{ thresholds.temperature.min }}°C - {{ thresholds.temperature.max }}°C</div>
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Situación / Dinámica de la Parcela</label>
              <select v-model="medicionAEditar.situation" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white">
                <option value="Condición estable">Condición estable</option>
                <option value="Bajo riego activo">Bajo riego activo</option>
                <option value="Caída brusca de humedad (-15%)">Caída brusca de humedad (-15% en 6h)</option>
                <option value="Alza térmica pronunciada (+8°C)">Alza térmica pronunciada (+8°C)</option>
                <option value="Lluvia reciente">Lluvia reciente</option>
                <option value="Estrés visible en follaje">Estrés visible en follaje</option>
              </select>
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Notas / Observaciones del Operador (Opcional)</label>
              <input v-model="medicionAEditar.notes" type="text" placeholder="Ej. Sensor revisado, sector poniente sin goteras" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
            </div>
          </div>

          <div class="bg-emerald-950 text-white rounded-2xl p-4 sm:p-5 border border-emerald-800 space-y-3">
            <div class="flex items-center justify-between border-b border-emerald-800 pb-2">
              <span class="text-[11px] font-mono text-emerald-400 uppercase tracking-wider">Diagnóstico y Recomendación en Tiempo Real</span>
              <span class="text-xs font-bold px-2.5 py-0.5 rounded-full" :class="clasesRecomendacion(previewRecomendacion).insignia">{{ previewRecomendacion.nivel }}</span>
            </div>
            <p class="text-sm font-bold">{{ previewRecomendacion.accion }}</p>
            <p class="text-xs text-emerald-100 font-mono">{{ previewRecomendacion.explicacion }}</p>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="medicionEditando = false" class="px-4 py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100">Cancelar</button>
            <button type="submit" :disabled="guardandoActualizacion" class="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/30 transition-all flex items-center gap-2 disabled:opacity-50">
              <span v-if="guardandoActualizacion" class="animate-spin">⏳</span>
              <span>Actualizar medición</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Detalle Completo de Medición -->
    <div v-if="medicionSeleccionada" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200">
        <div class="flex justify-between items-center border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-2xl">{{ iconoSituacion(medicionSeleccionada.recommendation?.tipo) }}</span>
            <div>
              <h3 class="text-lg font-black text-slate-900">Detalle de Medición</h3>
              <p class="text-xs text-slate-500">{{ formatearFecha(medicionSeleccionada.date) }} a las {{ formatearHora(medicionSeleccionada.date) }}</p>
            </div>
          </div>
          <button @click="medicionSeleccionada = null" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>

        <div class="grid grid-cols-2 gap-3 text-xs">
          <div class="bg-slate-50 p-3 rounded-xl border border-slate-200">
            <span class="text-slate-500 block text-[11px]">Humedad Suelo:</span>
            <span class="font-mono font-black text-emerald-700 text-lg">{{ medicionSeleccionada.humidity }}%</span>
            <span class="text-[10px] text-slate-400 block mt-0.5">Óptimo: {{ thresholds.humidity.min }}% - {{ thresholds.humidity.max }}%</span>
          </div>

          <div class="bg-slate-50 p-3 rounded-xl border border-slate-200">
            <span class="text-slate-500 block text-[11px]">Temperatura:</span>
            <span class="font-mono font-black text-amber-700 text-lg">{{ medicionSeleccionada.temperature }}°C</span>
            <span class="text-[10px] text-slate-400 block mt-0.5">Óptimo: {{ thresholds.temperature.min }}°C - {{ thresholds.temperature.max }}°C</span>
          </div>
        </div>

        <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1 text-xs">
          <span class="text-slate-500 font-bold block text-[11px] uppercase">Situación Reportada:</span>
          <p class="font-semibold text-slate-800">{{ medicionSeleccionada.situation || 'Condición estable' }}</p>
          <p v-if="medicionSeleccionada.notes" class="text-slate-600 italic pt-1">
            Notas: "{{ medicionSeleccionada.notes }}"
          </p>
        </div>

        <div class="rounded-2xl p-4 border space-y-2" :class="clasesRecomendacion(medicionSeleccionada.recommendation).contenedor">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider">Recomendación Agronómica:</span>
            <span class="px-2 py-0.5 text-[11px] font-bold rounded" :class="clasesRecomendacion(medicionSeleccionada.recommendation).insignia">
              {{ medicionSeleccionada.recommendation?.nivel }}
            </span>
          </div>
          <p class="text-sm font-bold text-slate-900">{{ medicionSeleccionada.recommendation?.accion }}</p>
          <p class="text-xs text-slate-700 font-mono leading-relaxed pt-1 border-t border-slate-200/60">
            {{ medicionSeleccionada.recommendation?.explicacion }}
          </p>
        </div>

        <div class="flex justify-end pt-2">
          <button
            @click="medicionSeleccionada = null"
            class="px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-xs font-bold hover:bg-emerald-500"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Editar Parcela -->
    <div v-if="mostrarModalEditarParcela" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-black text-slate-900">Editar Parcela</h3>
          <button @click="mostrarModalEditarParcela = false" class="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
        </div>

        <form class="space-y-4" @submit.prevent="guardarEdicionParcela">
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Nombre / Identificador del Lote</label>
            <input
              v-model="parcelaEnEdicion.name"
              required
              placeholder="Ej. Lote A-3 Tomates"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Tipo de Cultivo</label>
            <select
              v-model="parcelaEnEdicion.cropId"
              required
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
            >
              <option v-for="crop in cultivos" :key="crop.id" :value="crop.id">
                {{ crop.icon }} {{ crop.name }}
              </option>
            </select>
          </div>

          <div class="flex justify-end gap-3 pt-3">
            <button
              type="button"
              @click="mostrarModalEditarParcela = false"
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '~/composables/useAuth'
import { summarizeMeasurements } from '~/utils/measurementSummary'
import { parseCsv, validateCsvMeasurement } from '~/utils/csv'
import {
  useRecommendation,
  type CropOption,
  type CropThresholds,
  type Farm,
  type Measurement,
  type Plot,
  type RecommendationResult
} from '~/composables/useRecommendation'

definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()
const farmId = computed(() => (route.params.farmId || route.query.farmId) as string)
const plotId = computed(() => (route.params.plotId || route.query.plotId) as string)

const { user, isAuthReady } = useAuth()
const {
  getPlot,
  getCrops,
  getMeasurements,
  evaluateMeasurement,
  createMeasurement: apiCreateMeasurement,
  deleteMeasurement: apiDeleteMeasurement,
  updateMeasurement: apiUpdateMeasurement,
  updatePlot: apiUpdatePlot,
  deletePlot: apiDeletePlot
} = useRecommendation()

const farm = ref<Farm | null>(null)
const plot = ref<Plot | null>(null)
const cultivos = ref<CropOption[]>([])
const mediciones = ref<Measurement[]>([])
const errorMediciones = ref('')
const mensajeExito = ref('')

const mostrarModalNuevaMedicion = ref(false)
const guardandoMedicion = ref(false)
const importandoMediciones = ref(false)
const csvMedicionesInput = ref<HTMLInputElement | null>(null)
const medicionSeleccionada = ref<Measurement | null>(null)
const medicionEditando = ref(false)
const guardandoActualizacion = ref(false)
const medicionAEditar = ref<{
  id: string
  date: string
  humidity: number
  temperature: number
  situation: string
  notes: string
}>({
  id: '',
  date: '',
  humidity: 0,
  temperature: 0,
  situation: 'Condición estable',
  notes: ''
})

const mostrarModalEditarParcela = ref(false)
const parcelaEnEdicion = ref({
  name: '',
  cropId: ''
})

const abrirModalEditarParcela = async () => {
  if (!plot.value) return
  if (cultivos.value.length === 0) {
    try {
      cultivos.value = await getCrops()
    } catch (e) {
      console.error('Error cargando cultivos:', e)
    }
  }
  parcelaEnEdicion.value = {
    name: plot.value.name,
    cropId: plot.value.cropId
  }
  mostrarModalEditarParcela.value = true
}

const guardarEdicionParcela = async () => {
  if (!parcelaEnEdicion.value.name || !parcelaEnEdicion.value.cropId || !farmId.value || !plotId.value) return
  try {
    const updated = await apiUpdatePlot(farmId.value, plotId.value, {
      name: parcelaEnEdicion.value.name,
      cropId: parcelaEnEdicion.value.cropId
    })
    if (updated?.plot) {
      plot.value = updated.plot
    }
    mostrarModalEditarParcela.value = false
    window.location.reload()
  } catch (err) {
    console.error('Error al editar parcela:', err)
    errorMediciones.value = 'No se pudo actualizar la parcela. Inténtalo de nuevo.'
  }
}

const confirmarEliminarParcela = async () => {
  if (!plot.value || !farmId.value || !plotId.value) return
  const confirmMsg = `¿Estás seguro de eliminar la parcela "${plot.value.name}"? Esta acción no se puede deshacer.`
  if (!window.confirm(confirmMsg)) return
  try {
    await apiDeletePlot(farmId.value, plotId.value)
    router.push('/parcelas')
  } catch (err) {
    console.error('Error al eliminar parcela:', err)
    errorMediciones.value = 'No se pudo eliminar la parcela. Inténtalo de nuevo.'
  }
}

// Valores iniciales de nueva medición
const fechaHoraLocalActual = () => {
  const date = new Date()
  const pad = (value: number) => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const fechaHoraParaInput = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (part: number) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const nuevaMedicion = ref({
  date: fechaHoraLocalActual(),
  humidity: 65,
  temperature: 24,
  situation: 'Condición estable',
  notes: ''
})

// Filtros
const filtroDia = ref('')
const filtroHumedad = ref('todos')
const filtroTemperatura = ref('todas')
const filtroTexto = ref('')

const filtrosActivos = computed(() => {
  return !!filtroDia.value || filtroHumedad.value !== 'todos' || filtroTemperatura.value !== 'todas' || !!filtroTexto.value.trim()
})

const limpiarFiltros = () => {
  filtroDia.value = ''
  filtroHumedad.value = 'todos'
  filtroTemperatura.value = 'todas'
  filtroTexto.value = ''
}

// Icono del cultivo
const cropIcon = computed(() => {
  return plot.value?.cropIcon || '🌾'
})

const thresholds = computed<CropThresholds>(() =>
  plot.value?.thresholds || {
    humidity: { min: 0, max: 0 },
    temperature: { min: 0, max: 0 }
  }
)

const previewRecomendacion = ref<RecommendationResult>({
  nivel: 'Calculando recomendación...',
  tipo: 'optimo',
  badgeColor: 'border-emerald-500 bg-emerald-50 text-emerald-800',
  badgeBg: 'bg-emerald-600',
  badgeText: 'text-white',
  accion: 'La API analizará las condiciones ingresadas.',
  explicacion: 'La recomendación se calcula en el backend.'
})

let previewRequestId = 0
let previewTimer: ReturnType<typeof setTimeout> | undefined

const marcarPreviewDatosInvalidos = () => {
  previewRecomendacion.value = {
    nivel: 'Datos por validar',
    tipo: 'precaucion',
    badgeColor: 'border-amber-500 bg-amber-50 text-amber-800',
    badgeBg: 'bg-amber-500',
    badgeText: 'text-slate-900',
    accion: 'Ingresa una humedad de 0–100% y una temperatura de -15–60 °C.',
    explicacion: 'La recomendación se calculará cuando los valores estén dentro de los límites permitidos.'
  }
}

const actualizarPreview = async (
  datos: Pick<Measurement, 'humidity' | 'temperature' | 'situation'> = nuevaMedicion.value
) => {
  if (!plot.value?.cropId) return
  const requestId = ++previewRequestId
  const humidity = Number(datos.humidity)
  const temperature = Number(datos.temperature)
  if (
    !Number.isFinite(humidity) ||
    humidity < 0 ||
    humidity > 100 ||
    !Number.isFinite(temperature) ||
    temperature < -15 ||
    temperature > 60
  ) {
    marcarPreviewDatosInvalidos()
    return
  }

  try {
    const result = await evaluateMeasurement(
      plot.value.cropId,
      humidity,
      temperature,
      datos.situation
    )
    if (requestId === previewRequestId) {
      previewRecomendacion.value = result
    }
  } catch (err) {
    console.error('Error al calcular recomendación en el backend:', err)
    if (requestId === previewRequestId) {
      errorMediciones.value = 'No se pudo calcular la recomendación. Verifica que la API esté encendida.'
    }
  }
}

watch(
  () => [
    plot.value?.cropId,
    nuevaMedicion.value.humidity,
    nuevaMedicion.value.temperature,
    nuevaMedicion.value.situation
  ],
  () => {
    if (previewTimer) clearTimeout(previewTimer)
    previewTimer = setTimeout(() => {
      void actualizarPreview()
    }, 250)
  }
)

watch(
  () => [
    medicionEditando.value,
    medicionAEditar.value.humidity,
    medicionAEditar.value.temperature,
    medicionAEditar.value.situation
  ],
  () => {
    if (!medicionEditando.value) return
    if (previewTimer) clearTimeout(previewTimer)
    previewTimer = setTimeout(() => {
      void actualizarPreview(medicionAEditar.value)
    }, 250)
  }
)

const cargarDatosFinca = async () => {
  if (!user.value || !farmId.value || !plotId.value) return
  try {
    const result = await getPlot(farmId.value, plotId.value)
    farm.value = result.farm
    plot.value = result.plot
    errorMediciones.value = ''
  } catch (err) {
    console.error('Error al cargar datos de finca:', err)
    errorMediciones.value = 'No se pudieron cargar los datos. Verifica que la API esté encendida y que tengas permiso.'
  }
}

const cargarMediciones = async () => {
  if (!user.value || !farmId.value || !plotId.value) return
  try {
    mediciones.value = await getMeasurements(farmId.value, plotId.value)
    errorMediciones.value = ''
  } catch (err) {
    console.error('Error al cargar mediciones:', err)
    errorMediciones.value = 'No se pudieron cargar las mediciones desde la API.'
  }
}

// Última Medición
const ultimaMedicion = computed(() => {
  return mediciones.value.length > 0 ? mediciones.value[0] : null
})

const estadoPromedio = computed(() => summarizeMeasurements(mediciones.value))

// Filtrado de Mediciones
const medicionesFiltradas = computed(() => {
  return mediciones.value.filter(med => {
    // 1. Filtro por Día
    if (filtroDia.value) {
      const medDateStr = String(med.date || '').slice(0, 10)
      if (medDateStr !== filtroDia.value) return false
    }

    // 2. Filtro por Humedad
    const h = Number(med.humidity)
    const hMin = thresholds.value.humidity.min
    const hMax = thresholds.value.humidity.max
    if (filtroHumedad.value === 'baja' && h >= hMin) return false
    if (filtroHumedad.value === 'optima' && (h < hMin || h > hMax)) return false
    if (filtroHumedad.value === 'alta' && h <= hMax) return false

    // 3. Filtro por Temperatura
    const t = Number(med.temperature)
    const tMin = thresholds.value.temperature.min
    const tMax = thresholds.value.temperature.max
    if (filtroTemperatura.value === 'frio' && t >= tMin) return false
    if (filtroTemperatura.value === 'optima' && (t < tMin || t > tMax)) return false
    if (filtroTemperatura.value === 'calor' && t <= tMax) return false

    // 4. Filtro por Texto (situación o notas)
    if (filtroTexto.value.trim()) {
      const q = filtroTexto.value.toLowerCase()
      const sit = (med.situation || '').toLowerCase()
      const not = (med.notes || '').toLowerCase()
      const dia = (med.recommendation?.nivel || '').toLowerCase()
      if (!sit.includes(q) && !not.includes(q) && !dia.includes(q)) return false
    }

    return true
  })
})

const guardarMedicion = async () => {
  if (!user.value || !farmId.value || !plotId.value) return
  mensajeExito.value = ''
  const humidity = Number(nuevaMedicion.value.humidity)
  const temperature = Number(nuevaMedicion.value.temperature)
  if (
    !Number.isFinite(humidity) ||
    humidity < 0 ||
    humidity > 100 ||
    !Number.isFinite(temperature) ||
    temperature < -15 ||
    temperature > 60 ||
    !nuevaMedicion.value.date ||
    Number.isNaN(new Date(nuevaMedicion.value.date).getTime())
  ) {
    errorMediciones.value = 'Verifica la fecha, la humedad (0–100%) y la temperatura (-15–60 °C).'
    return
  }

  guardandoMedicion.value = true

  try {
    await apiCreateMeasurement(farmId.value, plotId.value, {
      date: nuevaMedicion.value.date,
      humidity,
      temperature,
      situation: nuevaMedicion.value.situation,
      notes: nuevaMedicion.value.notes || ''
    })

    // Reset formulario
    nuevaMedicion.value = {
      date: fechaHoraLocalActual(),
      humidity: 65,
      temperature: 24,
      situation: 'Condición estable',
      notes: ''
    }
    mostrarModalNuevaMedicion.value = false
    await cargarMediciones()
    mensajeExito.value = 'Información guardada correctamente.'
  } catch (err) {
    console.error('Error al guardar medición:', err)
    errorMediciones.value = 'No se pudo guardar la medición desde la API. Inténtalo de nuevo.'
  } finally {
    guardandoMedicion.value = false
  }
}

const importarMedicionesCsv = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  importandoMediciones.value = true
  errorMediciones.value = ''
  mensajeExito.value = ''
  try {
    if (!user.value || !farmId.value || !plotId.value) {
      throw new Error('Debes iniciar sesión y seleccionar una parcela válida para importar mediciones.')
    }

    const { headers, rows } = parseCsv(await file.text())
    const dateIndex = headers.indexOf('date')
    const humidityIndex = headers.indexOf('humidity')
    const temperatureIndex = headers.indexOf('temperature')
    const situationIndex = headers.indexOf('situation')
    const notesIndex = headers.indexOf('notes')
    if ([dateIndex, humidityIndex, temperatureIndex].some(index => index < 0)) {
      throw new Error('El CSV de mediciones debe incluir las columnas date, humidity y temperature.')
    }

    const medicionesCsv = rows.map((row, index) => {
      const line = index + 2
      return {
        line,
        ...validateCsvMeasurement({
          date: row[dateIndex] ?? '',
          humidity: row[humidityIndex] ?? '',
          temperature: row[temperatureIndex] ?? '',
          situation: situationIndex < 0 ? '' : row[situationIndex] ?? '',
          notes: notesIndex < 0 ? '' : row[notesIndex] ?? ''
        }, line)
      }
    })

    let imported = 0
    const failedRows: number[] = []
    for (const medicion of medicionesCsv) {
      try {
        await apiCreateMeasurement(farmId.value, plotId.value, {
          date: medicion.date,
          humidity: medicion.humidity,
          temperature: medicion.temperature,
          situation: medicion.situation,
          notes: medicion.notes
        })
        imported += 1
      } catch (err) {
        console.error(`Error al importar medición en fila ${medicion.line}:`, err)
        failedRows.push(medicion.line)
      }
    }

    await cargarMediciones()
    if (imported > 0) mensajeExito.value = `Se importaron ${imported} mediciones correctamente.`
    if (failedRows.length) {
      errorMediciones.value = `No se pudieron importar las filas: ${failedRows.join(', ')}.`
    }
  } catch (err) {
    console.error('Error al importar mediciones desde CSV:', err)
    errorMediciones.value = err instanceof Error ? err.message : 'No se pudieron importar las mediciones desde el CSV.'
  } finally {
    importandoMediciones.value = false
    input.value = ''
  }
}

// Eliminar Medición
const eliminarMedicion = async (id: string) => {
  if (!confirm('¿Deseas eliminar este registro de medición?')) return
  try {
    await apiDeleteMeasurement(id)
    mediciones.value = mediciones.value.filter(m => m.id !== id)
  } catch (err) {
    console.error('Error al eliminar medición:', err)
    errorMediciones.value = 'No se pudo eliminar la medición desde la API.'
  }
}

const editarMedicion = (medicion: Measurement) => {
  mensajeExito.value = ''
  errorMediciones.value = ''
  medicionAEditar.value = {
    id: medicion.id,
    date: fechaHoraParaInput(medicion.date),
    humidity: medicion.humidity,
    temperature: medicion.temperature,
    situation: medicion.situation || 'Condición estable',
    notes: medicion.notes || ''
  }
  medicionEditando.value = true
}

const actualizarMedicion = async () => {
  if (!farmId.value || !plotId.value || !medicionAEditar.value.id) return
  mensajeExito.value = ''
  errorMediciones.value = ''
  const humidity = Number(medicionAEditar.value.humidity)
  const temperature = Number(medicionAEditar.value.temperature)
  if (
    !Number.isFinite(humidity) ||
    humidity < 0 ||
    humidity > 100 ||
    !Number.isFinite(temperature) ||
    temperature < -15 ||
    temperature > 60 ||
    !medicionAEditar.value.date ||
    Number.isNaN(new Date(medicionAEditar.value.date).getTime())
  ) {
    errorMediciones.value = 'Verifica la fecha, la humedad (0–100%) y la temperatura (-15–60 °C).'
    return
  }

  guardandoActualizacion.value = true
  try {
    const updated = await apiUpdateMeasurement(farmId.value, plotId.value, medicionAEditar.value.id, {
      date: medicionAEditar.value.date,
      humidity,
      temperature,
      situation: medicionAEditar.value.situation,
      notes: medicionAEditar.value.notes
    })
    mediciones.value = [...mediciones.value.filter(item => item.id !== updated.id), updated]
      .sort((a, b) => String(b.date).localeCompare(String(a.date)))
    medicionEditando.value = false
    mensajeExito.value = 'Medición actualizada correctamente.'
  } catch (err) {
    console.error('Error al actualizar medición:', err)
    errorMediciones.value = 'No se pudo actualizar la medición desde la API.'
  } finally {
    guardandoActualizacion.value = false
  }
}

const verDetalleMedicion = (med: Measurement) => {
  medicionSeleccionada.value = med
}

// Helpers de formato y color
const formatearFecha = (dateStr: string) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatearHora = (dateStr: string) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
}

const claseHumedad = (h: number) => {
  const min = thresholds.value.humidity.min
  const max = thresholds.value.humidity.max
  if (h < min - 15) return 'bg-red-100 text-red-800 border border-red-200'
  if (h < min) return 'bg-yellow-100 text-yellow-800 border border-yellow-200'
  if (h > max) return 'bg-blue-100 text-blue-800 border border-blue-200'
  return 'bg-emerald-100 text-emerald-800 border border-emerald-200'
}

const claseTemperatura = (t: number) => {
  const minLetal = thresholds.value.temperature.minLetal ?? 0
  const min = thresholds.value.temperature.min
  const max = thresholds.value.temperature.max
  if (t <= minLetal) return 'bg-indigo-100 text-indigo-800 border border-indigo-300'
  if (t < min) return 'bg-sky-100 text-sky-800 border border-sky-200'
  if (t > max) return 'bg-amber-100 text-amber-800 border border-amber-200'
  return 'bg-emerald-100 text-emerald-800 border border-emerald-200'
}

const clasesRecomendacion = (recomendacion?: RecommendationResult) => {
  const nivel = recomendacion?.nivel.toLowerCase() || ''
  if (recomendacion?.tipo === 'helada') {
    return { contenedor: 'border-indigo-500 bg-indigo-50 text-indigo-900', insignia: 'bg-indigo-600 text-white' }
  }
  if (recomendacion?.tipo === 'critico') {
    return { contenedor: 'border-red-500 bg-red-50 text-red-900', insignia: 'bg-red-600 text-white' }
  }
  if (recomendacion?.tipo === 'advertencia' && nivel.includes('frío')) {
    return { contenedor: 'border-sky-500 bg-sky-50 text-sky-900', insignia: 'bg-sky-600 text-white' }
  }
  if (recomendacion?.tipo === 'advertencia') {
    return { contenedor: 'border-amber-500 bg-amber-50 text-amber-900', insignia: 'bg-amber-500 text-slate-950' }
  }
  if (recomendacion?.tipo === 'precaucion' && nivel.includes('sobresaturación')) {
    return { contenedor: 'border-blue-500 bg-blue-50 text-blue-900', insignia: 'bg-blue-600 text-white' }
  }
  if (recomendacion?.tipo === 'precaucion') {
    return { contenedor: 'border-yellow-500 bg-yellow-50 text-yellow-950', insignia: 'bg-yellow-400 text-slate-950' }
  }
  if (recomendacion?.tipo === 'optimo') {
    return { contenedor: 'border-emerald-500 bg-emerald-50 text-emerald-900', insignia: 'bg-emerald-600 text-white' }
  }
  return { contenedor: 'border-slate-300 bg-slate-50 text-slate-800', insignia: 'bg-slate-600 text-white' }
}

const iconoSituacion = (tipo?: string) => {
  if (tipo === 'helada') return '❄️'
  if (tipo === 'advertencia') return '⚠️'
  if (tipo === 'critico') return '🚨'
  if (tipo === 'precaucion') return '⚡'
  return '🌱'
}

onMounted(() => {
  const cargarParcelaYMediciones = async () => {
    await cargarDatosFinca()
    if (farm.value && plot.value) {
      await cargarMediciones()
      await actualizarPreview()
    }
  }

  if (isAuthReady.value && user.value) {
    void cargarParcelaYMediciones()
  } else {
    watch(isAuthReady, (ready) => {
      if (ready && user.value) {
        void cargarParcelaYMediciones()
      }
    })
  }
})

onUnmounted(() => {
  if (previewTimer) clearTimeout(previewTimer)
})
</script>
