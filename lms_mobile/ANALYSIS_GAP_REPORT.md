# Análisis de Brechas y Hoja de Ruta - LMS Mobile App

Este documento detalla las diferencias funcionales identificadas entre la plataforma web (Django) y la aplicación móvil (Flutter), así como una hoja de ruta sugerida para lograr la paridad de funciones y mejorar la experiencia de usuario.

## 1. Análisis de Brechas (Gap Analysis)

### A. Evaluaciones y Exámenes (Prioridad Alta)
*   **Estado Web:** Soporte completo para exámenes con múltiples tipos de preguntas (Opción única, Múltiple, V/F, Respuesta corta, Ordenamiento, Relacionar). Lógica de calificación automática y manual.
*   **Estado Móvil:** **Inexistente.** No hay pantallas para visualizar preguntas ni enviar respuestas.
*   **Impacto:** Los estudiantes no pueden completar cursos que requieran aprobación de exámenes desde el móvil.

### B. Reproducción de Contenido (Prioridad Alta)
*   **Estado Web:** Reproducción de video (YouTube/Vimeo), visualización de HTML enriquecido.
*   **Estado Móvil:** Básico.
    *   **Video:** Muestra solo la URL en texto. No hay reproductor integrado.
    *   **Recursos:** No hay soporte para visualizar archivos PDF o descargar adjuntos (ZIP, Excel).
    *   **HTML:** Renderizado básico de texto, pero sin soporte avanzado para imágenes incrustadas o formatos complejos.

### C. Pagos e Inscripciones (Prioridad Media)
*   **Estado Web:** Flujo completo de inscripción. Soporte para pagos mensuales (cuotas) con subida de comprobantes (vouchers).
*   **Estado Móvil:**
    *   Permite ver la lista de cuotas (`InstallmentsScreen`).
    *   **Falta:** No permite **subir la foto del comprobante** de pago para una cuota específica.

### D. Interactividad en Eventos (Prioridad Media)
*   **Estado Web:** Registro a eventos, visualización de agenda detallada, sesiones y speakers.
*   **Estado Móvil:** Lista básica de eventos. Faltan detalles de la agenda (sesiones) y la gestión de tickets (QR).

### E. Tareas (Assignments)
*   **Estado Web:** Los estudiantes pueden subir archivos o escribir texto para completar una tarea.
*   **Estado Móvil:** La pantalla de lección no ofrece interfaz para subir archivos o textos de tarea.

## 2. Recomendaciones Técnicas

*   **Manejo de Errores:** Implementar interceptores HTTP globales para manejar tokens expirados (401) y errores de servidor (500) de manera uniforme.
*   **Cache:** Mejorar el uso de `cached_network_image` para todas las miniaturas y avatares.
*   **Estado Global:** Evaluar si `Provider` es suficiente a medida que la app crezca; considerar Riverpod o Bloc para lógica más compleja (como la máquina de estados de un examen).
*   **Seguridad:** Asegurar que no se guarden datos sensibles en `SharedPreferences` sin cifrar (aunque el token es estándar).

## 3. Hoja de Ruta de Implementación (Roadmap)

### Fase 1: Consumo de Contenido (Inmediato)
1.  **Reproductor de Video:** Integrar `youtube_player_flutter` en `LessonScreen` para reproducción nativa.
2.  **Soporte PDF/Enlaces:** Agregar botones para abrir recursos externos o visualizar PDFs básicos.

### Fase 2: Evaluación (Corto Plazo)
1.  **Pantalla de Quiz:** Crear `QuizScreen` que soporte al menos preguntas de "Opción Única" y "Múltiple".
2.  **Lógica de Envío:** Integrar con el endpoint `POST /api/progress/quiz/{id}/submit`.

### Fase 3: Gestión Administrativa (Mediano Plazo)
1.  **Subida de Vouchers:** Permitir seleccionar imagen de galería/cámara en `InstallmentsScreen` y subirla.
2.  **Perfil Completo:** Edición de todos los campos del perfil (Bio, Redes).

### Fase 4: Experiencia Offline (Largo Plazo)
1.  **Descarga de Contenido:** Permitir guardar videos (si la licencia lo permite) o textos para lectura sin conexión.
2.  **Base de datos local:** Sincronizar progreso con SQLite/Drift.
