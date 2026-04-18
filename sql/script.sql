
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de enfermedades cardiacas
CREATE TABLE IF NOT EXISTS enfermedades (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(50)  UNIQUE NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    descripcion     TEXT,
    nivel_gravedad  VARCHAR(20)  CHECK (nivel_gravedad IN ('leve','moderada','grave','critica')),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Tabla de sintomas disponibles
CREATE TABLE IF NOT EXISTS sintomas (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(50)  UNIQUE NOT NULL,
    label       VARCHAR(200) NOT NULL,
    icono       VARCHAR(20),
    urgencia    VARCHAR(10)  CHECK (urgencia IN ('alta','media','baja')),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Relacion N:M entre enfermedades y sintomas
CREATE TABLE IF NOT EXISTS enfermedad_sintoma (
    enfermedad_id   INT REFERENCES enfermedades(id) ON DELETE CASCADE,
    sintoma_id      INT REFERENCES sintomas(id)     ON DELETE CASCADE,
    tipo            VARCHAR(20) CHECK (tipo IN ('clave','secundario')),
    peso            INT DEFAULT 1,
    PRIMARY KEY (enfermedad_id, sintoma_id)
);

-- Tabla principal de evaluaciones realizadas
CREATE TABLE IF NOT EXISTS evaluaciones (
    id                   SERIAL PRIMARY KEY,
    nombre_paciente      VARCHAR(150) DEFAULT 'Anonimo',
    edad                 INT          CHECK (edad BETWEEN 0 AND 120),
    sexo                 CHAR(1)      CHECK (sexo IN ('M','F','O')),
    sintomas_reportados  JSONB        NOT NULL DEFAULT '[]',
    condicion_detectada  VARCHAR(200),
    nivel_riesgo         VARCHAR(20)  CHECK (nivel_riesgo IN ('bajo','medio','alto')),
    puntaje              INT          DEFAULT 0,
    recomendaciones      JSONB        DEFAULT '[]',
    fecha_evaluacion     TIMESTAMP    DEFAULT NOW(),
    ip_origen            INET
);

CREATE INDEX IF NOT EXISTS idx_evaluaciones_riesgo    ON evaluaciones(nivel_riesgo);
CREATE INDEX IF NOT EXISTS idx_evaluaciones_fecha     ON evaluaciones(fecha_evaluacion DESC);
CREATE INDEX IF NOT EXISTS idx_evaluaciones_condicion ON evaluaciones(condicion_detectada);

-- Datos semilla: enfermedades
INSERT INTO enfermedades (codigo, nombre, descripcion, nivel_gravedad) VALUES
    ('infarto_agudo_miocardio', 'Infarto Agudo de Miocardio',
     'Obstruccion del flujo sanguineo al musculo cardiaco. Emergencia medica.', 'critica'),
    ('insuficiencia_cardiaca', 'Insuficiencia Cardiaca',
     'El corazon no bombea suficiente sangre para el cuerpo.', 'grave'),
    ('angina_pecho', 'Angina de Pecho',
     'Dolor por reduccion temporal del flujo sanguineo al corazon.', 'moderada'),
    ('arritmia_cardiaca', 'Arritmia Cardiaca',
     'Trastorno del ritmo electrico del corazon.', 'moderada'),
    ('hipertension_arterial', 'Hipertension Arterial',
     'Presion arterial cronicamente elevada.', 'moderada')
ON CONFLICT (codigo) DO NOTHING;

-- Datos semilla: sintomas
INSERT INTO sintomas (codigo, label, icono, urgencia) VALUES
    ('dolor_pecho',           'Dolor o presion en el pecho',            'fa-heart-crack',       'alta'),
    ('falta_aire',            'Falta de aire / Dificultad respiratoria', 'fa-lungs',             'alta'),
    ('sudoracion_excesiva',   'Sudoracion fria o excesiva',              'fa-droplet',           'alta'),
    ('mareos',                'Mareos o sensacion de desmayo',           'fa-person-falling',    'media'),
    ('fatiga_extrema',        'Fatiga o cansancio extremo',              'fa-bed',               'media'),
    ('dolor_brazo_izquierdo', 'Dolor en brazo izquierdo o mandibula',   'fa-hand',              'alta'),
    ('nauseas',               'Nauseas o vomito',                        'fa-face-dizzy',        'media'),
    ('palpitaciones',         'Palpitaciones o latidos acelerados',      'fa-heart-pulse',       'media'),
    ('latidos_irregulares',   'Latidos irregulares',                     'fa-wave-square',       'media'),
    ('hinchazon_piernas',     'Hinchazon en piernas o tobillos',         'fa-socks',             'media'),
    ('tos_persistente',       'Tos persistente o sibilancias',           'fa-head-side-cough',   'media'),
    ('dolor_cabeza',          'Dolor de cabeza intenso',                 'fa-head-side-virus',   'media'),
    ('vision_borrosa',        'Vision borrosa o alterada',               'fa-eye-slash',         'media'),
    ('falta_concentracion',   'Dificultad para concentrarse',            'fa-brain',             'baja')
ON CONFLICT (codigo) DO NOTHING;

-- Vista: resumen de evaluaciones por dia
CREATE OR REPLACE VIEW v_resumen_evaluaciones AS
SELECT
    DATE(fecha_evaluacion)      AS fecha,
    nivel_riesgo,
    COUNT(*)                    AS total,
    AVG(puntaje)::NUMERIC(5,2)  AS puntaje_promedio
FROM evaluaciones
GROUP BY DATE(fecha_evaluacion), nivel_riesgo
ORDER BY fecha DESC, nivel_riesgo;

SELECT 'Base de datos configurada correctamente.' AS estado;
