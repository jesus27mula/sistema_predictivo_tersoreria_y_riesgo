# Entrega 2: Selección de Idea de Proyecto y Análisis de Datos Necesarios

---

## 1. Idea seleccionada

La propuesta elegida para el desarrollo del Trabajo Final de Máster es el **Sistema predictivo de tesorería y riesgo de impago**. 

### Problema que resuelve
En el entorno empresarial, especialmente en pymes, micropymes y departamentos financieros de corporaciones, la falta de visibilidad sobre los flujos de caja futuros representa una de las mayores amenazas para la supervivencia del negocio. Muchas organizaciones gestionan su tesorería de forma reactiva, lo que provoca tensiones de liquidez imprevistas, dificultades para cubrir costes fijos inmediatos y una incapacidad latente para identificar qué clientes presentan una mayor propensión a demorar o incumplir sus compromisos de pago. Resolver este problema mediante la analítica avanzada aporta un valor estratégico crítico: permite a las direcciones financieras anticiparse a los periodos de escasez de caja, optimizar la planificación de la financiación y priorizar de manera eficiente las acciones de recobro sobre las cuentas por cobrar de mayor riesgo[cite: 25, 26, 32].

### Solución planteada
El proyecto abordará este desafío desde una perspectiva de Data Science combinando dos metodologías analíticas complementarias. Por un lado, se implementarán **modelos de clasificación y *scoring* supervisados** para estimar la probabilidad de que una factura sufra un retraso y predecir los días exactos de demora basándose en el comportamiento histórico de pago del cliente. Por otro lado, se desarrollarán **modelos de series temporales** (o modelos basados en componentes temporales y reglas de negocio) que consolidarán la previsión de cobros futuros con las proyecciones de pagos operativos fijos y variables. Toda esta inteligencia se unificará en un motor analítico capaz de proyectar de forma dinámica el saldo de caja disponible a corto y medio plazo.

### MVP del proyecto final
El Producto Mínimo Viable (MVP) consistirá en un **cuadro de mando (Dashboard) interactivo** e integrado. En este MVP, el usuario financiero podrá visualizar de forma clara:
1. Una proyección temporal de la línea de tesorería (curva de caja prevista frente a la real) para los próximos 30, 60 y 90 días, alertando sobre posibles puntos de ruptura de stock de liquidez.
2. Un módulo de *scoring* de clientes que ordene la cartera según su perfil de riesgo y probabilidad de impago de facturas vivas.
3. Un sistema automatizado de alertas tempranas sobre facturas próximas a vencer con alta probabilidad de retraso, facilitando la toma de decisiones preventivas en la gestión de circulante.

---

## 2. Datos necesarios

Para garantizar la viabilidad y realismo del modelo de tesorería sin incurrir en la invención sesgada de la variable de comportamiento de los clientes, la metodología del proyecto se dividirá estrictamente bajo la siguiente regla:
* **Facturas y cobros de clientes = Datos reales**
* **Proveedores, gastos y saldo inicial = Datos sintéticos**

### Variables o campos requeridos
* **Bloque de ingresos (Reales):** Identificador de cliente, identificador de factura, fecha de emisión, fecha de vencimiento, fecha de liquidación, importe de la factura y días de retraso (variable objetivo a predecir).
* **Bloque de egresos y estructura (Sintéticos):** Para completar la proyección de flujo de caja se simularán las siguientes variables:
  * Pagos a proveedores (fechas estimadas, importes, condiciones de pago).
  * Nóminas (salidas recurrentes fijas mensuales).
  * Alquileres y suministros (gastos mensuales estables).
  * Impuestos simulados (liquidaciones trimestrales de IVA/Retenciones e Impuesto de Sociedades anual).
  * Financiación (cuotas de amortización de préstamos o pólizas de crédito).
  * Saldo bancario inicial (punto de partida para la acumulación matemática del flujo de caja).

### Granularidad
La granularidad adecuada para el entrenamiento de los modelos de riesgo será **a nivel de transacción (por factura)**, asociada a un identificador único de cliente. Para la visualización e integración en el módulo de series temporales y previsión de caja, los datos se agregarán con una frecuencia **diaria y mensual**.

### Profundidad histórica y volumen
Se dispone de un histórico cerrado que oscila entre los **2.400 y 2.500 registros** de facturas transaccionales. Aunque este volumen es modesto para modelos de aprendizaje profundo (*Deep Learning*), es perfectamente manejable y suficiente para algoritmos clásicos de Machine Learning supervisado (como *Random Forest*, *Gradient Boosting* o *Regresión Logística*) y para establecer las reglas de negocio del motor de tesorería. Esta dimensión analítica inicial servirá como un entorno controlado de desarrollo para el MVP.

### Datos imprescindibles vs. deseables
### Datos imprescindibles vs. deseables
* **Imprescindibles (Datos Reales):** El histórico real de facturación y comportamiento de cobros de clientes extraído del dataset de IBM (ID de factura, ID de cliente, importes, fechas de vencimiento y fecha efectiva de liquidación). Sin estos datos reales es imposible entrenar los modelos de clasificación y *scoring* de riesgo de impago, que constituyen el núcleo analítico del proyecto.
* **Imprescindibles (Datos Sintéticos Operativos):** El saldo bancario inicial y la estructura simulada de egresos (nóminas, alquileres, suministros e impuestos). Aunque son sintéticos, son **estrictamente obligatorios** para poder realizar la agregación matemática y proyectar la curva final de tesorería en el tiempo.
* **Deseables (No obligatorios):** Datos sectoriales de coyuntura económica, histórico de reclamaciones manuales del departamento de recobros, o detalles sobre el método de pago empleado (pagaré, transferencia, etc.). Su ausencia no frena el desarrollo del MVP, pero su inclusión futura enriquecería las variables del modelo de Machine Learning.

---

## 3. Fuentes de datos previstas

* **Fuente concreta:** Se utilizará el dataset público **"IBM Late Payment Histories"** disponible en plataformas de ciencia de datos.
* **Accesibilidad:** Es una fuente abierta, de carácter público y accesible sin restricciones de uso académico o de investigación.
* **Enlace a la fuente:** Kaggle / IBM Community Data Repositories (https://www.kaggle.com/datasets/hhenry/finance-factoring-ibm-late-payment-histories?resource=download).
* **Formato de los datos:** Archivo plano estructurado en formato **CSV**.
* **Disponibilidad histórica:** Sí, incluye un registro histórico completo y cerrado de transacciones con sus respectivas fechas de inicio a fin del ciclo de cobro.
* **Estabilidad de la fuente:** Al tratarse de un dataset estático de referencia ("benchmark") publicado por IBM para retos analíticos, la fuente es 100% estable; no depende de un mantenimiento activo ni de actualizaciones en tiempo real.
* **Riesgos detectados:** El principal riesgo es el sesgo contextual (datos provenientes de un entorno corporativo específico que podrían requerir adaptación al ecosistema de pyme estándar). Asimismo, al ser datos estáticos, no se evaluará la degradación del modelo en producción (*data drift*) en tiempo real, aspecto que se suplirá simulando ventanas temporales de evaluación de forma interna.

---

## 4. Consideraciones de privacidad y protección de datos

* **Información Personal Identificable (PII):** El dataset de IBM viene pre-anonimizado de origen. Los identificadores de clientes y facturas son códigos alfanuméricos enmascarados, por lo que **no se incluye información personal identificable** (nombres de empresas reales, direcciones, CIFs o datos de personas físicas).
* **Anonimización y agregación:** Al generar los datos sintéticos de proveedores y gastos, se utilizarán nombres genéricos ficticios ("Proveedor A", "Suministros Tipo B"), evitando explícitamente cualquier vinculación con entidades reales del mercado actual.
* **Seguridad académica:** Dado que los datos de entrada son públicos/sintéticos y carecen de implicaciones comerciales confidenciales, el proyecto puede desarrollarse, almacenarse en repositorios públicos (como GitHub) y exponerse ante el tribunal académico de forma **completamente segura y legal**.
* **Riesgos éticos o legales:** No se identifican riesgos de infracción del RGPD. A nivel ético, el sistema se plantea como una herramienta de soporte a la decisión humana (*human-in-the-loop*); el modelo sugiere la probabilidad de riesgo, pero la priorización final de acciones comerciales o de recobro recae sobre el criterio del analista financiero, mitigando sesgos de exclusión automatizada de clientes.

---

## 5. Viabilidad inicial del proyecto

* **¿Es viable obtener los datos?** Sí, es plenamente viable dado que la base de datos principal de facturación ya está localizada y disponible para su descarga inmediata, y la estructura de gastos es de naturaleza lógica/sintética controlada por el propio desarrollador.
* **¿Calidad, granularidad y profundidad adecuadas?** Sí, el dataset cumple rigurosamente con la granularidad transaccional necesaria y la profundidad histórica requerida para calcular retrasos exactos y entrenar modelos predictivos estables.
* **¿Desarrollo realista durante el curso?** El alcance es ambicioso pero perfectamente realista. Al acotar los egresos a un modelo de simulación paramétrico, se evita la complejidad técnica de limpiar múltiples fuentes de datos dispares de proveedores, permitiendo concentrar el esfuerzo del curso en la ingeniería de variables del riesgo de clientes y en el diseño del dashboard interactivo.
* **Parte más arriesgada en este momento:** El mayor reto técnico reside en la **alineación temporal** entre los desfases de cobros previstos de forma probabilística (Machine Learning) y la agregación determinista de los gastos fijos para construir la curva de caja final de forma coherente y sin descuadres matemáticos.
* **Alternativa en caso de fallo de la fuente principal:** Si el dataset de IBM presentase problemas de consistencia ocultos, la alternativa directa sería recurrir a repositorios públicos equivalentes enfocados en contabilidad/facturación (como datasets de ERPs de código abierto tipo Odoo en entornos de prueba) o, en última instancia, expandir el motor sintético mediante generadores de datos probabilísticos basados en librerías especializadas de Python (como *Faker* combinada con distribuciones estadísticas de retrasos).