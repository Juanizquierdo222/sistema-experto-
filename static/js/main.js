
'use strict';

// ── Estado de la aplicación ─────────────────────────────────────────────────
const state = {
  sintomas_seleccionados: new Set(),
};

// ── Inicialización ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initSintomasCards();
  initRadioOptions();
});

/**
 * Inicializa los eventos de las tarjetas de síntomas.
 */
function initSintomasCards() {
  document.addEventListener('click', (e) => {
    if (e.target.tagName === 'INPUT') return; /**aqui habia un error no dejaba marcar las casillas agrege esto y se arreglo */
    const card = e.target.closest('.sintoma-card');
    if (!card) return;

    const checkbox = card.querySelector('input[type="checkbox"]');
    if (!checkbox) return;

    const id = checkbox.value;

    if (state.sintomas_seleccionados.has(id)) { 
      state.sintomas_seleccionados.delete(id);
      checkbox.checked = false;
      card.classList.remove('checked');
    } else {
      state.sintomas_seleccionados.add(id); //Aquí el sistema guarda los síntomas elegidos.
      checkbox.checked = true;
      card.classList.add('checked');
    }

    updateSelectionBar();
  });
}

/**
 * Inicializa estilos de opciones de radio (sexo).
 */
function initRadioOptions() {
  const radios = document.querySelectorAll('.radio-option input[type="radio"]');
  radios.forEach(radio => {
    radio.addEventListener('change', () => {
      document.querySelectorAll('.radio-option').forEach(el => el.classList.remove('selected'));
      radio.closest('.radio-option').classList.add('selected');
    });
  });
}

/**
 * Actualiza el contador de síntomas seleccionados.
 */
function updateSelectionBar() {
  const count = state.sintomas_seleccionados.size;
  const label = document.getElementById('count-label');
  const btnClear = document.getElementById('btn-clear');

  if (count === 0) {
    label.textContent = 'Ningún síntoma seleccionado';
    btnClear.style.display = 'none';
  } else if (count === 1) {
    label.textContent = '1 síntoma seleccionado';
    btnClear.style.display = 'flex';
  } else {
    label.textContent = `${count} síntomas seleccionados`;
    btnClear.style.display = 'flex';
  }
}

/**
 * Limpia todos los síntomas seleccionados.
 */
function clearAll() {
  state.sintomas_seleccionados.clear();
  document.querySelectorAll('.sintoma-card').forEach(c => c.classList.remove('checked'));
  document.querySelectorAll('.sintoma-check').forEach(cb => cb.checked = false);
  updateSelectionBar();
}

/**
 * Obtiene los datos del paciente del formulario.
 */
function getPacienteData() {
  const nombre = document.getElementById('nombre').value.trim();
  const edad   = parseInt(document.getElementById('edad').value) || null;
  const sexoEl = document.querySelector('input[name="sexo"]:checked');
  return {
    nombre: nombre || 'Anónimo',
    edad,
    sexo: sexoEl ? sexoEl.value : null,
  };
}

/**
 * Ejecuta la evaluación llamando al API backend.
 */
async function evaluar() {
  if (state.sintomas_seleccionados.size === 0) {
    showToast('⚠️ Seleccione al menos un síntoma para evaluar.');
    return;
  }

  const loading = document.getElementById('loading');
  const results = document.getElementById('results');
  const btnEval = document.getElementById('btn-evaluar');

  // Mostrar loading
  btnEval.disabled = true;
  loading.style.display = 'block';
  results.style.display = 'none';

  // Scroll suave al loading
  loading.scrollIntoView({ behavior: 'smooth', block: 'center' });

  const payload = {
    sintomas: Array.from(state.sintomas_seleccionados),
    paciente: getPacienteData(),
  };

  try {
    const response = await fetch('/api/evaluar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'Error desconocido');
    }

    // Esperar un momento para que se vea el loader
    await sleep(800);

    loading.style.display = 'none';
    renderResults(data.resultado);
    results.style.display = 'block';

    // Scroll al resultado
    setTimeout(() => {
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

  } catch (error) {
    loading.style.display = 'none';
    console.error('Error en evaluación:', error);
    showToast('❌ Error al conectar con el servidor. Verifique que Flask esté corriendo.');
  } finally {
    btnEval.disabled = false;
  }
}

/**
 * Renderiza los resultados en el DOM.
 * @param {Object} r - Resultado del motor de inferencia
 */
function renderResults(r) {
  const riesgo = r.nivel_riesgo;

  // Header de resultado
  const header = document.getElementById('result-header');
  header.className = `result-header riesgo-${riesgo}`;

  // Icono según nivel
  const iconMap = { alto: 'fa-triangle-exclamation', medio: 'fa-circle-exclamation', bajo: 'fa-circle-check' };
  document.getElementById('result-icon').className = `fa-solid ${iconMap[riesgo] || 'fa-circle-info'}`;

  // Textos
  const riesgoLabels = { alto: 'ALTO', medio: 'MEDIO', bajo: 'BAJO' };
  document.getElementById('result-riesgo-label').textContent = 'NIVEL DE RIESGO';
  document.getElementById('result-riesgo').textContent = riesgoLabels[riesgo] || riesgo;
  document.getElementById('result-condicion').textContent = r.condicion;
  document.getElementById('result-desc').textContent = r.descripcion;

  // Síntomas detectados
  const allSymptoms = [...(r.sintomas_clave_detectados || []), ...(r.sintomas_secundarios_detectados || [])];
  const secSintomas = document.getElementById('section-sintomas-detectados');
  const tagsSintomas = document.getElementById('tags-sintomas');
  if (allSymptoms.length > 0) {
    tagsSintomas.innerHTML = allSymptoms
      .map(s => `<span class="tag">${s}</span>`)
      .join('');
    secSintomas.style.display = 'block';
  } else {
    secSintomas.style.display = 'none';
  }

  // Recomendaciones
  const recoList = document.getElementById('reco-list');
  recoList.innerHTML = (r.recomendaciones || [])
    .map((rec, i) => `
      <li class="reco-item ${riesgo === 'alto' && i === 0 ? 'urgente' : ''}">
        <span class="reco-num">${i + 1}</span>
        <span>${rec}</span>
      </li>
    `)
    .join('');

  // Condiciones evaluadas
  const secOtras = document.getElementById('section-otras');
  const barsCont = document.getElementById('conditions-bars');
  if (r.condiciones_evaluadas && r.condiciones_evaluadas.length > 0) {
    const maxScore = Math.max(...r.condiciones_evaluadas.map(c => c.puntaje), 1);
    barsCont.innerHTML = r.condiciones_evaluadas
      .map(c => {
        const pct = Math.round((c.puntaje / maxScore) * 100);
        return `
          <div class="cond-row">
            <span class="cond-name">${c.nombre}</span>
            <div class="cond-bar-wrap">
              <div class="cond-bar ${c.nivel_riesgo}" style="width:0" data-width="${pct}%"></div>
            </div>
            <span class="cond-score">${c.puntaje}pts</span>
          </div>
        `;
      })
      .join('');
    secOtras.style.display = 'block';

    // Animar barras
    setTimeout(() => {
      barsCont.querySelectorAll('.cond-bar').forEach(bar => {
        bar.style.width = bar.dataset.width;
      });
    }, 200);
  } else {
    secOtras.style.display = 'none';
  }
}

/**
 * Imprime solo el resultado.
 */
function printResults() {
  window.print();
}

/**
 * Reinicia el formulario para una nueva evaluación.
 */
function resetForm() {
  clearAll();
  document.getElementById('results').style.display = 'none';
  document.getElementById('nombre').value = '';
  document.getElementById('edad').value = '';
  const checkedRadio = document.querySelector('input[name="sexo"]:checked');
  if (checkedRadio) checkedRadio.checked = false;
  document.querySelectorAll('.radio-option').forEach(el => el.classList.remove('selected'));

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Muestra un toast de notificación temporal.
 */
function showToast(msg) {
  const existing = document.querySelector('.toast-notification');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.textContent = msg;
  toast.style.cssText = `
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: #1e293b; border: 1px solid rgba(255,255,255,0.1);
    color: #e8edf5; padding: 12px 24px; border-radius: 12px;
    font-size: 14px; font-family: 'Sora', sans-serif;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    z-index: 9999; animation: slide-up 0.3s ease;
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

/**
 * Espera un tiempo determinado (ms).
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/* =============================================================================
   ACCESIBILIDAD
   ============================================================================= */

let currentFontSize = 16;

function toggleAccessibilityMenu() {
    const menu = document.getElementById('acc-menu');

    if (menu.style.display === 'flex') {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'flex';
    }
}

function changeFontSize(change) {

    currentFontSize += change;

    if (currentFontSize < 14) currentFontSize = 14;
    if (currentFontSize > 24) currentFontSize = 24;

    document.body.style.fontSize = currentFontSize + 'px';
}

function toggleContrast() {
    document.body.classList.toggle('high-contrast');
}