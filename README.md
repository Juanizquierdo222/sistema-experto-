## En Mexico las enfermedades del corazón se consolidaron como la principal causa de muerte en México en 2024, de acuerdo con las cifras del Instituto Nacional de Estadística y Geografía (Inegi). La magnitud del problema es enorme: los padecimientos cardiacos no solo lideran las estadísticas nacionales, sino que causaron 97,187 fallecimientos solo entre enero y junio de 2023. Excélsior. Todos los derechos reservados. El contenido de este sitio y de la edición impresa está protegido por la Ley Federal del Derecho de Autor. Prohibida la reproducción total o parcial sin autorización previa y por escrito. El material de terceros conserva sus propios derechos.

> Sistema experto basado en reglas if-then para la detección temprana de enfermedades
> cardiovasculares en México. Desarrollado con Flask, PostgreSQL y una interfaz
> web moderna y accesible.

---

## Descripción del sistema

**CardioScan MX** es un sistema experto médico que evalúa síntomas cardiovasculares
reportados por el usuario y genera un prediagnóstico orientativo usando un motor
de inferencia basado en reglas (if-then). El sistema:

- Evalúa **14 síntomas** cardíacos de diferente nivel de urgencia.
- Detecta **5 condiciones**: Infarto Agudo de Miocardio, Insuficiencia Cardíaca,
  Angina de Pecho, Arritmia Cardíaca e Hipertensión Arterial.
- Asigna un **nivel de riesgo**: Bajo / Medio / Alto.
- Genera **recomendaciones** personalizadas según el nivel de riesgo.
- Persiste los resultados en **PostgreSQL** para análisis estadístico.

> ⚠️ **AVISO**: Este sistema es orientativo y no reemplaza la evaluación médica profesional.
> En caso de emergencia, llame al **911**.

---

## Estructura del proyecto

```
sistema_experto/
├── app.py            # Aplicación Flask principal + rutas API
├── rules.py          # Motor de inferencia + base de conocimiento
├── database.py       # Conexión PostgreSQL + operaciones CRUD
├── requirements.txt  # Dependencias Python
├── .env.example      # Variables de entorno de ejemplo
│
├── templates/
│   └── index.html    # Interfaz principal (HTML + Jinja2)
│
├── static/
│   ├── css/
│   │   └── main.css  # Estilos premium (dark theme)
│   └── js/
│       └── main.js   # Lógica de UI y llamadas API
│
├── sql/
│   └── script.sql    # Schema + datos semilla PostgreSQL
│
└── README.md         # Este archivo
```

---

## Requisitos previos

| Herramienta | Versión mínima |
|-------------|---------------|
| Python      | 3.10+         |
| pip         | 22+           |
| PostgreSQL  | 14+           |

---

## Instrucciones de instalación paso a paso

### Paso 1 — Clonar / descomprimir el proyecto

```bash
unzip sistema_experto.zip
cd sistema_experto
```

### Paso 2 — Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Paso 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4 — Configurar PostgreSQL

#### 4.1 Crear la base de datos

```sql
-- Conectarse a PostgreSQL como superusuario
psql -U postgres

-- En la consola de psql:
CREATE DATABASE sistema_cardiaco WITH ENCODING 'UTF8';
\q
```

#### 4.2 Ejecutar el script SQL

```bash
psql -U postgres -d sistema_cardiaco -f sql/script.sql
```

Deberá ver al final:
```
     estado
--------------------------
 Base de datos configurada correctamente.
```

#### 4.3 Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con sus credenciales reales:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=sistema_cardiaco
# DB_USER=postgres
# DB_PASSWORD=su_password
```

### Paso 5 — Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

---

## Uso de la interfaz

1. **Abra** http://localhost:5000 en su navegador.
2. **(Opcional)** Ingrese nombre, edad y sexo del paciente.
3. **Seleccione** todos los síntomas que el paciente está experimentando.
4. **Presione** el botón "Evaluar Síntomas".
5. **Revise** el resultado: nivel de riesgo, condición probable y recomendaciones.

---

## API REST — Documentación

### `GET /api/sintomas`

Retorna el catálogo completo de síntomas disponibles.

**Respuesta:**
```json
{
  "success": true,
  "sintomas": [
    { "id": "dolor_pecho", "label": "Dolor o presión en el pecho", "icono": "🫀", "urgencia": "alta" },
    ...
  ]
}
```

---

### `POST /api/evaluar`

Evalúa síntomas y retorna el prediagnóstico.

**Request body:**
```json
{
  "sintomas": ["dolor_pecho", "falta_aire", "sudoracion_excesiva"],
  "paciente": {
    "nombre": "Juan García",
    "edad": 52,
    "sexo": "M"
  }
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "resultado": {
    "condicion": "Infarto Agudo de Miocardio",
    "condicion_id": "infarto_agudo_miocardio",
    "descripcion": "Obstrucción del flujo sanguíneo al músculo cardíaco...",
    "nivel_riesgo": "alto",
    "puntaje_total": 9,
    "recomendaciones": [
      "Llame al 911 o acuda a urgencias INMEDIATAMENTE.",
      "No conduzca usted mismo — solicite una ambulancia.",
      ...
    ],
    "sintomas_clave_detectados": [
      "Dolor o presión en el pecho",
      "Falta de aire / Dificultad respiratoria",
      "Sudoración fría o excesiva"
    ],
    "condiciones_evaluadas": [
      { "nombre": "Infarto Agudo de Miocardio", "puntaje": 9, "nivel_riesgo": "alto" },
      { "nombre": "Angina de Pecho", "puntaje": 6, "nivel_riesgo": "alto" }
    ]
  }
}
```

---

### `GET /api/estadisticas`

Retorna estadísticas de evaluaciones guardadas en la DB.

**Respuesta:**
```json
{
  "success": true,
  "estadisticas": {
    "total": 42,
    "alto": 12,
    "medio": 18,
    "bajo": 12
  }
}
```

---

## Lógica del motor de inferencia

El motor de inferencia (`rules.py`) implementa un sistema basado en reglas **if-then**:

```python
# Para cada enfermedad en la base de conocimiento:
FOR cada enfermedad:
    puntaje = 0
    FOR cada síntoma_clave en enfermedad.sintomas_clave:
        IF síntoma_clave IN síntomas_reportados:
            puntaje += peso_clave  # +3 puntos
    FOR cada síntoma_secundario en enfermedad.sintomas_secundarios:
        IF síntoma_secundario IN síntomas_reportados:
            puntaje += peso_secundario  # +1 punto

    IF puntaje >= umbral_alto:  riesgo = "alto"
    ELIF puntaje >= umbral_medio: riesgo = "medio"
    ELIF puntaje > 0:            riesgo = "bajo"

# Regla de emergencia crítica:
IF dolor_pecho AND (dolor_brazo_izquierdo OR sudoracion_excesiva):
    riesgo = "alto"  # Sin importar el puntaje

# Seleccionar la condición con mayor puntaje y riesgo más alto
condicion_principal = MAX(condiciones, key=(riesgo, puntaje))
```

---

## Esquema de base de datos

```
enfermedades          sintomas
─────────────────     ─────────────────
id (PK)               id (PK)
codigo (UNIQUE)       codigo (UNIQUE)
nombre                label
descripcion           icono
nivel_gravedad        urgencia
created_at            created_at
      │                     │
      └───── enfermedad_sintoma ─────┘
             (enfermedad_id FK)
             (sintoma_id FK)
             tipo: 'clave'|'secundario'
             peso

evaluaciones
─────────────────────────────────
id (PK)
nombre_paciente
edad, sexo
sintomas_reportados (JSONB)
condicion_detectada
nivel_riesgo
puntaje
recomendaciones (JSONB)
fecha_evaluacion
ip_origen
```

---

## Descripción de la interfaz

La interfaz está diseñada con un tema oscuro médico profesional:

- **Header fijo** con logo animado y badge de estado.
- **Sección hero** con onda ECG animada en SVG.
- **Formulario de dos pasos**: datos del paciente (opcional) + selección de síntomas.
- **Tarjetas de síntomas** con indicador visual de urgencia (rojo/amarillo/verde).
- **Botón de evaluación** con animación de pulso.
- **Panel de resultados** con:
  - Nivel de riesgo destacado en color (🔴 alto / 🟡 medio / 🟢 bajo).
  - Condición detectada y descripción.
  - Lista de recomendaciones numeradas.
  - Gráficas de barras con condiciones evaluadas.
- **Diseño responsive** para móvil, tablet y escritorio.

---

## Arquitectura del sistema

El sistema sigue una arquitectura cliente-servidor:

- **Frontend (Cliente):** Interfaz web interactiva que permite al usuario seleccionar síntomas.
- **Backend (Servidor):** API REST desarrollada en Flask que procesa las solicitudes.
- **Motor de inferencia:** Módulo en Python que evalúa reglas if-then.
- **Base de datos:** PostgreSQL para persistencia de evaluaciones.

Flujo:

Usuario → Interfaz → API Flask → Motor de inferencia → PostgreSQL → Respuesta → Interfaz

## Tecnologías utilizadas

| Capa       | Tecnología               |
|------------|--------------------------|
| Backend    | Python 3.10 + Flask 3.0  |
| Base datos | PostgreSQL 14 + psycopg2 |
| Frontend   | HTML5 + CSS3 + JavaScript|
| Fuentes    | Sora + DM Mono (Google)  |
| Iconos     | Font Awesome 6           |

---

## Equipo de desarrollo

Sistema Experto Cardíaco MX — Proyecto Académico  
Inteligencia Artificial | Sistemas Expertos

---

*Este sistema es únicamente orientativo y no reemplaza la evaluación médica profesional.*

## Tipo de Inteligencia Artificial

Este sistema implementa **IA simbólica basada en reglas**, no aprendizaje automático.

- No utiliza modelos de machine learning
- No requiere entrenamiento con datos
- Se basa en conocimiento experto codificado mediante reglas if-then

## Limitaciones del sistema

- Depende de la veracidad de los síntomas ingresados por el usuario.
- No considera historial clínico completo ni estudios médicos.
- No sustituye diagnóstico profesional.
- No utiliza aprendizaje automático ni mejora automática.

Este sistema debe considerarse únicamente como una herramienta de apoyo.

## Ejemplo de uso

Entrada:
- dolor_pecho
- falta_aire
- sudoracion_excesiva

Salida:
- Riesgo: ALTO
- Condición: Infarto Agudo de Miocardio