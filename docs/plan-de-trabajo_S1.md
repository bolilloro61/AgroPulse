# Tzaphquiel

## Descripción del problema y documentación base
- Redactar el cuerpo del archivo README.md detallando la problemática agrícola que resuelve AgroPulse, el objetivo general del proyecto, el alcance del Producto Mínimo Viable (MVP), la justificación de la arquitectura elegida y la definición formal de roles del equipo.

## Pantalla de login/register 
- Implementar el módulo de autenticación de usuarios (registro e inicio de sesión) utilizando Firebase Authentication. Debe incluir el manejo del estado de sesión en el frontend y la asignación/verificación del primer rol funcional (ej. Productor o Técnico supervisor).

## Pantalla de fincas y parcelas 
- Diseñar e implementar el catálogo de gestión donde se puedan dar de alta y consultar las fincas y parcelas registradas. Debe permitir la parametrización de los rangos ambientales esperados (umbrales mínimos y máximos de humedad/temperatura) y guardar la información en la colección farms y plots de Firestore.

# Rogelio

## Creación de las historias de usuario 
- Redactar al menos 5 historias de usuario completas bajo el formato estándar ("Como [rol], quiero [acción] para [beneficio]"). Deben cubrir los flujos clave del proyecto como el registro de parcelas, la captura manual de mediciones ambientales y la lectura de alertas.

## Pantalla de mediciones ambientales 
- Diseñar e implementar la vista y la lógica del formulario para la captura manual de registros ambientales (humedad del suelo, temperatura, etc.). Debe incluir la conexión directa con la API/Firebase para escribir los datos en la colección measurements y la consulta para desplegar el historial de registros en pantalla.

## Pantalla de bienvenida 
- Crear la interfaz inicial o dashboard principal de la aplicación para los usuarios. Esta vista funcionará como punto de acceso general, mostrando un resumen general del estado del sistema, accesos directos a los módulos, inicio de sesión y registro y la bienvenida al perfil.