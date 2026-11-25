# Importar parcelas y mediciones desde CSV

Los archivos deben estar codificados en UTF-8, usar coma (`,`) como separador y tener una fila de encabezados. Se aceptan finales de línea Windows o Unix y campos entre comillas dobles; las comillas dentro de un campo se escriben duplicadas (`""`). Los encabezados no distinguen mayúsculas de minúsculas.

## Parcelas y mediciones en una finca

La importación se inicia desde **Importar CSV** en una finca existente; el archivo no crea una finca ni lleva una columna de finca. Cada parcela se crea una sola vez por nombre. Si su nombre aparece en varias filas, todas deben tener el mismo cultivo y cada fila con datos de medición agrega una lectura a esa parcela.

Encabezados requeridos para crear parcelas:

```csv
name,crop
```

- `name`: nombre de la parcela; no puede estar vacío.
- `crop`: nombre del cultivo tal como aparece en el catálogo, o su identificador (`cropId`).

Para incluir mediciones en el mismo archivo, agregue `date`, `humidity` y `temperature`. `situation` y `notes` siguen siendo opcionales:

```csv
name,crop,date,humidity,temperature,situation,notes
Lote Norte,tomate-saladette,2026-11-24T08:30:00,68,23.5,Condición estable,Sensor revisado
Lote Norte,tomate-saladette,2026-11-24T14:30:00,42,31,"Humedad en descenso","Riego pendiente, sector norte"
Lote Sur,maiz-grano,2026-11-24T09:00:00,58,25,Condición estable,
```

Una fila puede dejar vacíos los cinco campos de medición para crear una parcela sin lecturas. Los cultivos deben existir en el catálogo de AgroPulse; no se crean cultivos desde el CSV. Si el mismo nombre de parcela aparece con cultivos distintos, se rechaza el archivo antes de guardar.

## Mediciones

La importación se hace desde la hoja de mediciones de una parcela; todas las filas se agregan a esa parcela.

Encabezados requeridos:

```csv
date,humidity,temperature
```

Encabezados opcionales:

- `situation`: situación observada. Si se omite o queda vacío, se usa `Condición estable`.
- `notes`: notas adicionales; puede omitirse o quedar vacío.

Ejemplo:

```csv
date,humidity,temperature,situation,notes
2026-11-24T08:30:00,68,23.5,Condición estable,Sensor revisado
2026-11-24T14:30:00,42,31,"Caída brusca de humedad (-15%)","Riego pendiente, sector norte"
```

- `date`: fecha y hora local en formato ISO `YYYY-MM-DDTHH:mm:ss`.
- `humidity`: número entre `0` y `100`, expresado en porcentaje.
- `temperature`: número entre `-15` y `60`, expresado en °C.
- Use punto (`.`) como separador decimal.
- La recomendación agronómica se calcula al importar cada medición.

Se validan todas las filas antes de enviar datos. Si una operación falla en el servidor, las demás filas válidas todavía pueden importarse; el resultado informa cuántas parcelas y mediciones se guardaron y cuáles filas fallaron. Hay ejemplos listos para subir en `evidencias/CSV/`.
