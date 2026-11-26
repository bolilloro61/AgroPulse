export interface ParsedCsv {
  headers: string[]
  rows: string[][]
}

export interface CsvMeasurement {
  date: string
  humidity: number
  temperature: number
  situation: string
  notes: string
}

export const validateCsvMeasurement = (
  values: { date: string; humidity: string; temperature: string; situation: string; notes: string },
  line: number
): CsvMeasurement => {
  const date = values.date.trim()
  const dateMatch = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$/.exec(date)
  const parsedDate = new Date(date)
  const humidityValue = values.humidity.trim()
  const temperatureValue = values.temperature.trim()
  const humidity = Number(humidityValue)
  const temperature = Number(temperatureValue)

  if (
    !dateMatch ||
    Number.isNaN(parsedDate.getTime()) ||
    parsedDate.getFullYear() !== Number(dateMatch[1]) ||
    parsedDate.getMonth() + 1 !== Number(dateMatch[2]) ||
    parsedDate.getDate() !== Number(dateMatch[3]) ||
    parsedDate.getHours() !== Number(dateMatch[4]) ||
    parsedDate.getMinutes() !== Number(dateMatch[5]) ||
    parsedDate.getSeconds() !== Number(dateMatch[6])
  ) {
    throw new Error(`Fila ${line}: la fecha debe ser válida y tener el formato YYYY-MM-DDTHH:mm:ss.`)
  }
  if (!humidityValue || !Number.isFinite(humidity) || humidity < 0 || humidity > 100) {
    throw new Error(`Fila ${line}: la humedad debe ser un número entre 0 y 100.`)
  }
  if (!temperatureValue || !Number.isFinite(temperature) || temperature < -15 || temperature > 60) {
    throw new Error(`Fila ${line}: la temperatura debe ser un número entre -15 y 60 °C.`)
  }

  return {
    date,
    humidity,
    temperature,
    situation: values.situation.trim() || 'Condición estable',
    notes: values.notes.trim()
  }
}

export const parseCsv = (source: string): ParsedCsv => {
  const text = source.replace(/^\uFEFF/, '')
  const records: string[][] = []
  let record: string[] = []
  let field = ''
  let quoted = false
  let quoteClosed = false

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index]
    if (quoted) {
      if (character === '"' && text[index + 1] === '"') {
        field += '"'
        index += 1
      } else if (character === '"') {
        quoted = false
        quoteClosed = true
      } else {
        field += character
      }
      continue
    }

    if (quoteClosed && character !== ',' && character !== '\n' && character !== '\r') {
      throw new Error('El CSV contiene caracteres después de cerrar un campo entre comillas.')
    }

    if (character === '"' && field.length === 0) {
      quoted = true
    } else if (character === '"') {
      throw new Error('El CSV contiene comillas dentro de un campo sin escapar.')
    } else if (character === ',') {
      record.push(field)
      field = ''
      quoteClosed = false
    } else if (character === '\n' || character === '\r') {
      record.push(field)
      records.push(record)
      record = []
      field = ''
      quoteClosed = false
      if (character === '\r' && text[index + 1] === '\n') index += 1
    } else {
      field += character
    }
  }

  if (quoted) throw new Error('El CSV contiene un campo entre comillas sin cerrar.')
  if (field.length > 0 || record.length > 0) {
    record.push(field)
    records.push(record)
  }

  const nonEmptyRecords = records.filter(row => row.some(value => value.trim() !== ''))
  if (nonEmptyRecords.length < 2) throw new Error('El CSV debe incluir encabezados y al menos una fila de datos.')

  const headers = nonEmptyRecords[0].map(header => header.trim().toLowerCase())
  if (headers.some(header => !header)) throw new Error('Todos los encabezados del CSV deben tener nombre.')
  if (new Set(headers).size !== headers.length) throw new Error('El CSV contiene encabezados duplicados.')

  const rows = nonEmptyRecords.slice(1)
  if (rows.some(row => row.length !== headers.length)) {
    throw new Error('Todas las filas del CSV deben tener la misma cantidad de columnas que los encabezados.')
  }

  return {
    headers,
    rows
  }
}
