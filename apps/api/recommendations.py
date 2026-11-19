"""Agronomic recommendation rules and their request/response models."""

from pydantic import BaseModel, ConfigDict, Field


class ThresholdRange(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    min: float
    max: float
    min_letal: float | None = Field(default=None, alias="minLetal")
    max_crit: float | None = Field(default=None, alias="maxCrit")
    min_crit: float | None = Field(default=None, alias="minCrit")


class CropThresholds(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    temperature: ThresholdRange
    humidity: ThresholdRange


class Crop(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    name: str
    icon: str = "🌾"
    description: str = ""
    category: str = ""
    scientific_name: str = Field(default="", alias="scientificName")
    thresholds: CropThresholds


class MeasurementValues(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    humidity: float = Field(ge=0, le=100, allow_inf_nan=False)
    temperature: float = Field(ge=-15, le=60, allow_inf_nan=False)
    situation: str = Field(default="Condición estable", max_length=200)


class Recommendation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nivel: str
    tipo: str
    badgeColor: str
    badgeBg: str
    badgeText: str
    accion: str
    explicacion: str


def evaluate_measurement(
    crop_name: str,
    humidity: float,
    temperature: float,
    situation: str,
    thresholds: CropThresholds,
) -> Recommendation:
    temperature_range = thresholds.temperature
    humidity_range = thresholds.humidity
    minimum_lethal_temperature = (
        temperature_range.min_letal
        if temperature_range.min_letal is not None
        else 0
    )
    maximum_critical_temperature = (
        temperature_range.max_crit
        if temperature_range.max_crit is not None
        else temperature_range.max + 4
    )
    situation_text = situation.casefold()
    sudden_humidity_drop = (
        "caída brusca" in situation_text or "desecación" in situation_text
    )
    heat_spike = "alza térmica" in situation_text or "calor" in situation_text

    if temperature <= minimum_lethal_temperature:
        return Recommendation(
            nivel="Emergencia por Helada",
            tipo="helada",
            badgeColor="border-indigo-500 bg-indigo-50 text-indigo-800",
            badgeBg="bg-indigo-600",
            badgeText="text-white",
            accion=(
                "Activar de urgencia sistemas antiheladas (aspersión térmica, "
                "calefactores o cubiertas térmicas) e inspeccionar tejidos."
            ),
            explicacion=(
                f"DISPARADOR: Temperatura registrada ({temperature}°C) está en o "
                f"por debajo del umbral letal ({minimum_lethal_temperature}°C) "
                f"para {crop_name}. El cultivo sufre congelamiento celular y "
                "necrosis irreversible sin protección activa."
            ),
        )

    if temperature < temperature_range.min:
        return Recommendation(
            nivel="Alerta por Estrés de Frío",
            tipo="advertencia",
            badgeColor="border-sky-500 bg-sky-50 text-sky-800",
            badgeBg="bg-sky-500",
            badgeText="text-white",
            accion=(
                "Monitorear descenso térmico nocturno y evitar riegos fríos que "
                "reduzcan la temperatura en la zona radicular."
            ),
            explicacion=(
                f"DISPARADOR: Temperatura ({temperature}°C) por debajo del "
                f"mínimo vegetativo óptimo ({temperature_range.min}°C) para "
                f"{crop_name}. Puede detener el crecimiento y el cuajado."
            ),
        )

    if temperature >= maximum_critical_temperature or heat_spike:
        return Recommendation(
            nivel="Alerta por Golpe de Calor",
            tipo="advertencia",
            badgeColor="border-amber-500 bg-amber-50 text-amber-800",
            badgeBg="bg-amber-500",
            badgeText="text-white",
            accion=(
                "Programar micropulverización o riego de mitigación térmica en "
                "horario vespertino para disipar calor."
            ),
            explicacion=(
                f"DISPARADOR: Temperatura ({temperature}°C) alcanza o supera el "
                f"umbral crítico ({maximum_critical_temperature}°C) para "
                f"{crop_name}. Existe riesgo de quemaduras foliares y daño "
                "durante la floración."
            ),
        )

    if humidity < humidity_range.min - 15 or sudden_humidity_drop:
        return Recommendation(
            nivel="Crítico por Estrés Hídrico",
            tipo="critico",
            badgeColor="border-red-500 bg-red-50 text-red-800",
            badgeBg="bg-red-600",
            badgeText="text-white",
            accion=(
                "Activar ciclo de riego por goteo urgente (45-60 min) e "
                "inspeccionar sensor de humedad en parcela."
            ),
            explicacion=(
                f"DISPARADOR: Humedad registrada ({humidity}%) está severamente "
                f"por debajo del rango óptimo ({humidity_range.min}% - "
                f"{humidity_range.max}%) para {crop_name}, con riesgo de "
                "desecación del bulbo radicular."
            ),
        )

    if humidity < humidity_range.min:
        return Recommendation(
            nivel="Precaución de Riego",
            tipo="precaucion",
            badgeColor="border-yellow-500 bg-yellow-50 text-yellow-800",
            badgeBg="bg-yellow-500",
            badgeText="text-slate-900",
            accion=(
                "Programar próximo turno de riego para reponer humedad en el "
                "bulbo radicular antes de entrar en déficit."
            ),
            explicacion=(
                f"DISPARADOR: Humedad del suelo ({humidity}%) está por debajo "
                f"del rango óptimo recomendado ({humidity_range.min}% - "
                f"{humidity_range.max}%) para {crop_name}."
            ),
        )

    if humidity > humidity_range.max:
        return Recommendation(
            nivel="Precaución por Sobresaturación",
            tipo="precaucion",
            badgeColor="border-blue-500 bg-blue-50 text-blue-800",
            badgeBg="bg-blue-600",
            badgeText="text-white",
            accion=(
                "Suspender ciclos de riego programados y verificar drenaje para "
                "prevenir asfixia radicular y hongos patógenos."
            ),
            explicacion=(
                f"DISPARADOR: Humedad del suelo ({humidity}%) supera el límite "
                f"superior óptimo ({humidity_range.max}%) para {crop_name}. "
                "Existe riesgo de asfixia radicular y patógenos fúngicos."
            ),
        )

    return Recommendation(
        nivel="Condición Óptima",
        tipo="optimo",
        badgeColor="border-emerald-500 bg-emerald-50 text-emerald-800",
        badgeBg="bg-emerald-600",
        badgeText="text-white",
        accion="Mantener esquema de monitoreo estándar. Parcela en condiciones biológicas ideales.",
        explicacion=(
            f"DISPARADOR: Humedad ({humidity}%) y temperatura ({temperature}°C) "
            f"están dentro del rango óptimo ({humidity_range.min}% - "
            f"{humidity_range.max}% de humedad, {temperature_range.min}°C - "
            f"{temperature_range.max}°C) para {crop_name}."
        ),
    )
