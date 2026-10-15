# Vibe Report – EcoTrack

## 1. Cómo configuré las reglas de mi agente
Mi `.cursorrules` define tres cosas: **rol** (la IA es copiloto técnico y yo pongo la visión), **stack** (Python + Streamlit, lógica separada de la interfaz) y **forma de trabajo** (plan corto antes de cambios grandes, cambios pequeños, un test por cada regla nueva y ejecutar `pytest` al terminar). También fijé reglas de dominio: los factores de emisión viven en un solo archivo y la app debe decir que son aproximaciones, nunca cifras oficiales. Esa última regla evitó que la IA presentara estimados como datos exactos.

El ecosistema funciona así: Cursor es mi taller (el agente escribe, ejecuta tests y corrige), GitHub guarda el código y Replit lo despliega con una URL pública. El `.replit` y el `config.toml` dejan el despliegue reproducible sin configurar nada a mano.

## 2. Dificultades al delegar el código
- **Ambigüedad del lenguaje natural.** "Carne de pollo" se contaba como carne de res. Un test lo detectó y la corrección fue una regla de prioridad entre categorías, no un parche suelto.
- **Texto partido por comas.** "Viajé en bus, 20 km" separaba el medio de transporte de la distancia; hubo que recordar el transporte pendiente hasta encontrar el dato. Además, la coma decimal ("1,5 km") no debía cortar la frase.
- **Confiar sin verificar.** La IA escribe con seguridad aunque se equivoque. Aprendí a exigir pruebas ejecutadas en lugar de aceptar un "ya funciona".
- **Datos de dominio.** Los factores de emisión son aproximaciones; tuve que decidir cuánta precisión prometer en la interfaz.

## 3. De escribir código a orquestar una visión
Al principio se siente raro no teclear cada línea: da una mezcla de velocidad y pérdida de control. Lo que cambió fue dónde pongo la atención. Ahora mi trabajo es decidir **qué** problema resuelve el producto, **cómo se ve un buen resultado** (el ejemplo "comí carne y viajé 20 km en bus" como criterio de aceptación) y **cómo comprobarlo** (tests, prueba de la app). Escribir prompts claros se parece más a dirigir que a programar: cuanto mejor defino la intención y los límites, mejor responde el agente.

Mi conclusión es que delegar el código no elimina la responsabilidad: la mueve hacia el criterio, la verificación y el diseño del producto. Entender lo que la IA genera sigue siendo indispensable, porque yo respondo por el resultado.
