# =============================================================================
# MOTOR DE INFERENCIA - SISTEMA EXPERTO CARDÍACO
# =============================================================================

ENFERMEDADES = {
    "infarto_agudo_miocardio": {
        "nombre": "Infarto Agudo de Miocardio",
        "descripcion": "Obstrucción del flujo sanguíneo al músculo cardíaco. Requiere atención de emergencia inmediata.",
        "sintomas_clave": ["dolor_pecho", "sudoracion_excesiva", "falta_aire", "dolor_brazo_izquierdo", "nauseas"],
        "sintomas_secundarios": ["mareos", "fatiga_extrema", "palpitaciones"],
        "peso_clave": 3, "peso_secundario": 1, "umbral_alto": 6, "umbral_medio": 3,
    },
    "insuficiencia_cardiaca": {
        "nombre": "Insuficiencia Cardíaca",
        "descripcion": "El corazón no bombea suficiente sangre para satisfacer las necesidades del cuerpo.",
        "sintomas_clave": ["falta_aire", "fatiga_extrema", "hinchazon_piernas", "tos_persistente"],
        "sintomas_secundarios": ["latidos_irregulares", "mareos", "falta_concentracion"],
        "peso_clave": 3, "peso_secundario": 1, "umbral_alto": 6, "umbral_medio": 3,
    },
    "angina_pecho": {
        "nombre": "Angina de Pecho",
        "descripcion": "Dolor o presión en el pecho causado por reducción temporal del flujo sanguíneo al corazón.",
        "sintomas_clave": ["dolor_pecho", "falta_aire", "fatiga_extrema"],
        "sintomas_secundarios": ["sudoracion_excesiva", "mareos", "nauseas"],
        "peso_clave": 3, "peso_secundario": 1, "umbral_alto": 6, "umbral_medio": 3,
    },
    "arritmia_cardiaca": {
        "nombre": "Arritmia Cardíaca",
        "descripcion": "Trastorno del ritmo eléctrico del corazón que puede causar latidos irregulares.",
        "sintomas_clave": ["palpitaciones", "latidos_irregulares", "mareos"],
        "sintomas_secundarios": ["falta_aire", "fatiga_extrema", "dolor_pecho"],
        "peso_clave": 3, "peso_secundario": 1, "umbral_alto": 6, "umbral_medio": 3,
    },
    "hipertension_arterial": {
        "nombre": "Hipertensión Arterial",
        "descripcion": "Presión arterial crónicamente elevada que puede dañar el corazón y los vasos sanguíneos.",
        "sintomas_clave": ["dolor_cabeza", "mareos", "vision_borrosa"],
        "sintomas_secundarios": ["fatiga_extrema", "palpitaciones", "falta_aire"],
        "peso_clave": 3, "peso_secundario": 1, "umbral_alto": 6, "umbral_medio": 3,
    },
}

SINTOMAS_CATALOGO = {
    "dolor_pecho":          {"label": "Dolor o presión en el pecho",           "icono": "🫀", "urgencia": "alta"},
    "falta_aire":           {"label": "Falta de aire / Dificultad respiratoria","icono": "🫁", "urgencia": "alta"},
    "sudoracion_excesiva":  {"label": "Sudoración fría o excesiva",             "icono": "💧", "urgencia": "alta"},
    "mareos":               {"label": "Mareos o sensación de desmayo",          "icono": "😵", "urgencia": "media"},
    "fatiga_extrema":       {"label": "Fatiga o cansancio extremo",             "icono": "😴", "urgencia": "media"},
    "dolor_brazo_izquierdo":{"label": "Dolor en brazo izquierdo o mandíbula",  "icono": "💪", "urgencia": "alta"},
    "nauseas":              {"label": "Náuseas o vómito",                       "icono": "🤢", "urgencia": "media"},
    "palpitaciones":        {"label": "Palpitaciones o latidos acelerados",     "icono": "❤️", "urgencia": "media"},
    "latidos_irregulares":  {"label": "Latidos irregulares",                    "icono": "📈", "urgencia": "media"},
    "hinchazon_piernas":    {"label": "Hinchazón en piernas o tobillos",        "icono": "🦵", "urgencia": "media"},
    "tos_persistente":      {"label": "Tos persistente o sibilancias",          "icono": "😮‍💨", "urgencia": "media"},
    "dolor_cabeza":         {"label": "Dolor de cabeza intenso",                "icono": "🤕", "urgencia": "media"},
    "vision_borrosa":       {"label": "Visión borrosa o alterada",              "icono": "👁️", "urgencia": "media"},
    "falta_concentracion":  {"label": "Dificultad para concentrarse",           "icono": "🧠", "urgencia": "baja"},
}

RECOMENDACIONES = {
    "alto": [
        "Llame al 911 o acuda a urgencias INMEDIATAMENTE.",
        "No conduzca usted mismo — solicite una ambulancia.",
        "Informe a alguien cercano de su situación ahora mismo.",
        "No realice esfuerzo físico de ningún tipo.",
        "Si tiene aspirina y no es alérgico, mastique una tableta de 325 mg.",
        "Permanezca sentado o acostado en posición cómoda.",
    ],
    "medio": [
        "Consulte a un médico o cardiólogo HOY, no lo posponga.",
        "Evite el esfuerzo físico intenso hasta ser evaluado.",
        "Monitoree sus síntomas y anote si empeoran.",
        "Si los síntomas se intensifican, acuda a urgencias de inmediato.",
        "Evite el consumo de cafeína, alcohol y tabaco.",
        "Informe a familiares sobre su estado de salud.",
    ],
    "bajo": [
        "Programe una cita con su médico en los próximos días.",
        "Adopte hábitos saludables: dieta baja en sodio y grasas.",
        "Realice actividad física moderada y regular.",
        "Monitoree su presión arterial con regularidad.",
        "Reduzca el estrés mediante técnicas de relajación.",
        "Evite el tabaco y limite el consumo de alcohol.",
    ],
}


def evaluar_sintomas(sintomas_presentes: list) -> dict:
    """Motor de inferencia basado en reglas if-then."""
    sintomas_set = set(sintomas_presentes)
    resultados = {}

    for eid, datos in ENFERMEDADES.items():
        puntaje = 0
        clave_det = []
        sec_det = []

        # IF síntoma_clave presente THEN sumar peso_clave
        for s in datos["sintomas_clave"]:
            if s in sintomas_set:
                puntaje += datos["peso_clave"]
                clave_det.append(s)

        # IF síntoma_secundario presente THEN sumar peso_secundario
        for s in datos["sintomas_secundarios"]:
            if s in sintomas_set:
                puntaje += datos["peso_secundario"]
                sec_det.append(s)

        # Determinar riesgo por umbrales
        if puntaje >= datos["umbral_alto"]:
            riesgo = "alto"
        elif puntaje >= datos["umbral_medio"]:
            riesgo = "medio"
        elif puntaje > 0:
            riesgo = "bajo"
        else:
            riesgo = None

        if riesgo:
            resultados[eid] = {
                "nombre": datos["nombre"],
                "descripcion": datos["descripcion"],
                "puntaje": puntaje,
                "nivel_riesgo": riesgo,
                "clave_det": clave_det,
                "sec_det": sec_det,
            }

    if not sintomas_set or not resultados:
        return {
            "condicion": "Sin indicadores de riesgo cardíaco detectados",
            "condicion_id": None,
            "descripcion": "No se detectaron síntomas asociados a enfermedades cardíacas. Continúe con sus controles médicos regulares.",
            "nivel_riesgo": "bajo",
            "puntaje_total": 0,
            "recomendaciones": RECOMENDACIONES["bajo"],
            "sintomas_clave_detectados": [],
            "sintomas_secundarios_detectados": [],
            "condiciones_evaluadas": [],
        }

    orden = {"alto": 3, "medio": 2, "bajo": 1}
    principal = max(resultados.values(), key=lambda x: (orden[x["nivel_riesgo"]], x["puntaje"]))

    # Regla crítica de emergencia absoluta
    emergencia = {"dolor_pecho", "dolor_brazo_izquierdo", "sudoracion_excesiva"}
    if len(sintomas_set & emergencia) >= 2:
        principal["nivel_riesgo"] = "alto"

    nf = principal["nivel_riesgo"]
    return {
        "condicion": principal["nombre"],
        "condicion_id": next(k for k, v in resultados.items() if v is principal),
        "descripcion": principal["descripcion"],
        "nivel_riesgo": nf,
        "puntaje_total": principal["puntaje"],
        "recomendaciones": RECOMENDACIONES[nf],
        "sintomas_clave_detectados": [SINTOMAS_CATALOGO.get(s, {}).get("label", s) for s in principal["clave_det"]],
        "sintomas_secundarios_detectados": [SINTOMAS_CATALOGO.get(s, {}).get("label", s) for s in principal["sec_det"]],
        "condiciones_evaluadas": sorted(
            [{"nombre": v["nombre"], "puntaje": v["puntaje"], "nivel_riesgo": v["nivel_riesgo"]} for v in resultados.values()],
            key=lambda x: x["puntaje"], reverse=True
        ),
    }


def obtener_catalogo_sintomas() -> list:
    return [{"id": sid, **datos} for sid, datos in SINTOMAS_CATALOGO.items()]
