/**
 * Mapa Corporal Humano Interativo & Visualizador de Lesões
 * Sistema de Gestão de Acidentes de Trabalho - HMA
 */
(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';

  /* ── Definições das Regiões Anatômicas ── */
  var BODY_PARTS = [
    { id: 'cabeca', label: 'Cabeça', category: 'Cabeça e Pescoço' },
    { id: 'olhos', label: 'Olhos / Face', category: 'Cabeça e Pescoço' },
    { id: 'pescoco', label: 'Pescoço', category: 'Cabeça e Pescoço' },
    { id: 'ombro_esq', label: 'Ombro Esquerdo', category: 'Membros Superiores' },
    { id: 'ombro_dir', label: 'Ombro Direito', category: 'Membros Superiores' },
    { id: 'braco_esq', label: 'Braço Esquerdo', category: 'Membros Superiores' },
    { id: 'braco_dir', label: 'Braço Direito', category: 'Membros Superiores' },
    { id: 'antbraco_esq', label: 'Antebraço Esquerdo', category: 'Membros Superiores' },
    { id: 'antbraco_dir', label: 'Antebraço Direito', category: 'Membros Superiores' },
    { id: 'mao_esq', label: 'Mão Esquerda', category: 'Membros Superiores' },
    { id: 'mao_dir', label: 'Mão Direita', category: 'Membros Superiores' },
    { id: 'dedos', label: 'Dedos', category: 'Membros Superiores' },
    { id: 'torax', label: 'Tórax / Peito', category: 'Tronco' },
    { id: 'abdomen', label: 'Abdômen', category: 'Tronco' },
    { id: 'costas', label: 'Costas (Dorsal)', category: 'Tronco' },
    { id: 'coluna', label: 'Coluna / Lombar', category: 'Tronco' },
    { id: 'quadril', label: 'Quadril / Pélvis', category: 'Tronco' },
    { id: 'coxa_esq', label: 'Coxa Esquerda', category: 'Membros Inferiores' },
    { id: 'coxa_dir', label: 'Coxa Direita', category: 'Membros Inferiores' },
    { id: 'joelho_esq', label: 'Joelho Esquerdo', category: 'Membros Inferiores' },
    { id: 'joelho_dir', label: 'Joelho Direito', category: 'Membros Inferiores' },
    { id: 'perna_esq', label: 'Perna Esquerda', category: 'Membros Inferiores' },
    { id: 'perna_dir', label: 'Perna Direita', category: 'Membros Inferiores' },
    { id: 'pe_esq', label: 'Pé Esquerdo', category: 'Membros Inferiores' },
    { id: 'pe_dir', label: 'Pé Direito', category: 'Membros Inferiores' }
  ];

  /* ── Elementos do SVG (Frente e Costas) ── */
  var SVG_SHAPES = [
    /* === FRENTE (Anterior) - Centro X = 115 === */
    { tag: 'ellipse', id: 'cabeca', view: 'frente', label: 'Cabeça', cx: 115, cy: 46, rx: 20, ry: 24 },
    { tag: 'ellipse', id: 'olhos', view: 'frente', label: 'Olhos / Face', cx: 115, cy: 46, rx: 12, ry: 7 },
    { tag: 'rect', id: 'pescoco', view: 'frente', label: 'Pescoço', x: 107, y: 70, width: 16, height: 15, rx: 3 },
    { tag: 'path', id: 'ombro_esq', view: 'frente', label: 'Ombro Esquerdo', d: 'M106,75 C94,76 80,82 66,93 L73,110 C83,103 95,98 106,96 Z' },
    { tag: 'path', id: 'ombro_dir', view: 'frente', label: 'Ombro Direito', d: 'M124,75 C136,76 150,82 164,93 L157,110 C147,103 135,98 124,96 Z' },
    { tag: 'path', id: 'torax', view: 'frente', label: 'Tórax / Peito', d: 'M85,86 L145,86 C143,110 141,130 138,136 L92,136 C89,130 87,110 85,86 Z' },
    { tag: 'path', id: 'abdomen', view: 'frente', label: 'Abdômen', d: 'M92,138 L138,138 L134,186 L96,186 Z' },
    { tag: 'rect', id: 'braco_esq', view: 'frente', label: 'Braço Esquerdo', x: 52, y: 99, width: 19, height: 66, rx: 9, transform: 'rotate(7 61 132)' },
    { tag: 'rect', id: 'braco_dir', view: 'frente', label: 'Braço Direito', x: 159, y: 99, width: 19, height: 66, rx: 9, transform: 'rotate(-7 169 132)' },
    { tag: 'rect', id: 'antbraco_esq', view: 'frente', label: 'Antebraço Esquerdo', x: 42, y: 170, width: 18, height: 64, rx: 8, transform: 'rotate(6 51 202)' },
    { tag: 'rect', id: 'antbraco_dir', view: 'frente', label: 'Antebraço Direito', x: 170, y: 170, width: 18, height: 64, rx: 8, transform: 'rotate(-6 179 202)' },
    { tag: 'ellipse', id: 'mao_esq', view: 'frente', label: 'Mão Esquerda', cx: 44, cy: 248, rx: 12, ry: 16 },
    { tag: 'ellipse', id: 'mao_dir', view: 'frente', label: 'Mão Direita', cx: 186, cy: 248, rx: 12, ry: 16 },
    { tag: 'path', id: 'quadril', view: 'frente', label: 'Quadril / Pélvis', d: 'M95,188 L135,188 L142,216 C140,226 128,232 115,232 C102,232 90,226 88,216 Z' },
    { tag: 'path', id: 'coxa_esq', view: 'frente', label: 'Coxa Esquerda', d: 'M89,222 C92,250 92,275 90,295 L111,295 C113,275 113,250 114,230 Z' },
    { tag: 'path', id: 'coxa_dir', view: 'frente', label: 'Coxa Direita', d: 'M116,230 C117,250 117,275 119,295 L140,295 C138,275 138,250 141,222 Z' },
    { tag: 'ellipse', id: 'joelho_esq', view: 'frente', label: 'Joelho Esquerdo', cx: 101, cy: 306, rx: 12, ry: 9 },
    { tag: 'ellipse', id: 'joelho_dir', view: 'frente', label: 'Joelho Direito', cx: 129, cy: 306, rx: 12, ry: 9 },
    { tag: 'path', id: 'perna_esq', view: 'frente', label: 'Perna Esquerda', d: 'M91,316 L111,316 L108,374 L94,374 Z' },
    { tag: 'path', id: 'perna_dir', view: 'frente', label: 'Perna Direita', d: 'M119,316 L139,316 L136,374 L122,374 Z' },
    { tag: 'ellipse', id: 'pe_esq', view: 'frente', label: 'Pé Esquerdo', cx: 99, cy: 388, rx: 14, ry: 9 },
    { tag: 'ellipse', id: 'pe_dir', view: 'frente', label: 'Pé Direito', cx: 131, cy: 388, rx: 14, ry: 9 },

    /* === COSTAS (Posterior) - Centro X = 345 === */
    { tag: 'ellipse', id: 'cabeca', view: 'costas', label: 'Cabeça (Posterior)', cx: 345, cy: 46, rx: 20, ry: 24 },
    { tag: 'rect', id: 'pescoco', view: 'costas', label: 'Pescoço / Cervical', x: 337, y: 70, width: 16, height: 15, rx: 3 },
    { tag: 'path', id: 'ombro_dir', view: 'costas', label: 'Ombro Direito (Costas)', d: 'M336,75 C324,76 310,82 296,93 L303,110 C313,103 325,98 336,96 Z' },
    { tag: 'path', id: 'ombro_esq', view: 'costas', label: 'Ombro Esquerdo (Costas)', d: 'M354,75 C366,76 380,82 394,93 L387,110 C377,103 365,98 354,96 Z' },
    { tag: 'path', id: 'costas', view: 'costas', label: 'Costas (Dorsal)', d: 'M315,86 L375,86 C373,110 371,130 368,136 L322,136 C319,130 317,110 315,86 Z' },
    { tag: 'path', id: 'coluna', view: 'costas', label: 'Coluna / Lombar', d: 'M322,138 L368,138 L364,186 L326,186 Z' },
    { tag: 'rect', id: 'braco_dir', view: 'costas', label: 'Braço Direito (Costas)', x: 282, y: 99, width: 19, height: 66, rx: 9, transform: 'rotate(7 291 132)' },
    { tag: 'rect', id: 'braco_esq', view: 'costas', label: 'Braço Esquerdo (Costas)', x: 389, y: 99, width: 19, height: 66, rx: 9, transform: 'rotate(-7 399 132)' },
    { tag: 'rect', id: 'antbraco_dir', view: 'costas', label: 'Antebraço Direito (Costas)', x: 272, y: 170, width: 18, height: 64, rx: 8, transform: 'rotate(6 281 202)' },
    { tag: 'rect', id: 'antbraco_esq', view: 'costas', label: 'Antebraço Esquerdo (Costas)', x: 400, y: 170, width: 18, height: 64, rx: 8, transform: 'rotate(-6 409 202)' },
    { tag: 'ellipse', id: 'mao_dir', view: 'costas', label: 'Mão Direita (Costas)', cx: 274, cy: 248, rx: 12, ry: 16 },
    { tag: 'ellipse', id: 'mao_esq', view: 'costas', label: 'Mão Esquerda (Costas)', cx: 416, cy: 248, rx: 12, ry: 16 },
    { tag: 'path', id: 'quadril', view: 'costas', label: 'Glúteos / Quadril (Costas)', d: 'M325,188 L365,188 L372,216 C370,226 358,232 345,232 C332,232 320,226 318,216 Z' },
    { tag: 'path', id: 'coxa_dir', view: 'costas', label: 'Coxa Direita (Costas)', d: 'M319,222 C322,250 322,275 320,295 L341,295 C343,275 343,250 344,230 Z' },
    { tag: 'path', id: 'coxa_esq', view: 'costas', label: 'Coxa Esquerda (Costas)', d: 'M346,230 C347,250 347,275 349,295 L370,295 C368,275 368,250 371,222 Z' },
    { tag: 'ellipse', id: 'joelho_dir', view: 'costas', label: 'Fossa Poplítea Direita', cx: 331, cy: 306, rx: 12, ry: 9 },
    { tag: 'ellipse', id: 'joelho_esq', view: 'costas', label: 'Fossa Poplítea Esquerda', cx: 359, cy: 306, rx: 12, ry: 9 },
    { tag: 'path', id: 'perna_dir', view: 'costas', label: 'Panturrilha Direita', d: 'M321,316 L341,316 L338,374 L324,374 Z' },
    { tag: 'path', id: 'perna_esq', view: 'costas', label: 'Panturrilha Esquerda', d: 'M349,316 L369,316 L366,374 L352,374 Z' },
    { tag: 'ellipse', id: 'pe_dir', view: 'costas', label: 'Calcanhar / Pé Direito', cx: 329, cy: 388, rx: 14, ry: 9 },
    { tag: 'ellipse', id: 'pe_esq', view: 'costas', label: 'Calcanhar / Pé Esquerdo', cx: 361, cy: 388, rx: 14, ry: 9 }
  ];

  /* ── Normalização de strings para busca e correspondência ── */
  function normalizeStr(str) {
    if (!str) return '';
    return str.toString()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();
  }

  /* ── Mapeamento Fuzzy de texto para IDs de partes ── */
  function matchTextToPartIds(text) {
    if (!text) return { ids: {}, unmatched: [] };
    var matchedIds = {};
    var rawTokens = text.split(/[,;\/\+]+/).map(function (s) { return s.trim(); }).filter(Boolean);
    var unmatchedTokens = [];

    rawTokens.forEach(function (token) {
      var norm = normalizeStr(token);
      var matched = false;

      // 1. Exact or startsWith label match
      BODY_PARTS.forEach(function (part) {
        var partNorm = normalizeStr(part.label);
        if (norm === partNorm || norm.indexOf(partNorm) !== -1 || partNorm.indexOf(norm) !== -1) {
          matchedIds[part.id] = true;
          matched = true;
        }
      });

      // 2. Specific medical/hospital keyword rules
      if (!matched) {
        if (norm.indexOf('dedo') !== -1) {
          matchedIds['dedos'] = true;
          if (norm.indexOf('dir') !== -1) matchedIds['mao_dir'] = true;
          else if (norm.indexOf('esq') !== -1) matchedIds['mao_esq'] = true;
          matched = true;
        }
        if (norm.indexOf('mao') !== -1) {
          if (norm.indexOf('dir') !== -1) matchedIds['mao_dir'] = true;
          else if (norm.indexOf('esq') !== -1) matchedIds['mao_esq'] = true;
          else { matchedIds['mao_dir'] = true; matchedIds['mao_esq'] = true; }
          matched = true;
        }
        if (norm.indexOf('olho') !== -1 || norm.indexOf('face') !== -1 || norm.indexOf('rosto') !== -1) {
          matchedIds['olhos'] = true;
          matched = true;
        }
        if (norm.indexOf('coluna') !== -1 || norm.indexOf('lombar') !== -1 || norm.indexOf('cervical') !== -1) {
          matchedIds['coluna'] = true;
          matched = true;
        }
        if (norm.indexOf('costa') !== -1 || norm.indexOf('dorso') !== -1) {
          matchedIds['costas'] = true;
          matched = true;
        }
        if (norm.indexOf('torax') !== -1 || norm.indexOf('peito') !== -1) {
          matchedIds['torax'] = true;
          matched = true;
        }
        if (norm.indexOf('abdom') !== -1 || norm.indexOf('barriga') !== -1) {
          matchedIds['abdomen'] = true;
          matched = true;
        }
        if (norm.indexOf('cabeca') !== -1 || norm.indexOf('cranio') !== -1) {
          matchedIds['cabeca'] = true;
          matched = true;
        }
        if (norm.indexOf('pescoco') !== -1) {
          matchedIds['pescoco'] = true;
          matched = true;
        }
        if (norm.indexOf('ombro') !== -1) {
          if (norm.indexOf('dir') !== -1) matchedIds['ombro_dir'] = true;
          else if (norm.indexOf('esq') !== -1) matchedIds['ombro_esq'] = true;
          else { matchedIds['ombro_dir'] = true; matchedIds['ombro_esq'] = true; }
          matched = true;
        }
        if (norm.indexOf('braco') !== -1 && norm.indexOf('ante') === -1) {
          if (norm.indexOf('dir') !== -1) matchedIds['braco_dir'] = true;
          else if (norm.indexOf('esq') !== -1) matchedIds['braco_esq'] = true;
          else { matchedIds['braco_dir'] = true; matchedIds['braco_esq'] = true; }
          matched = true;
        }
        if (norm.indexOf('antabraco') !== -1 || norm.indexOf('antebraco') !== -1) {
          if (norm.indexOf('dir') !== -1) matchedIds['antbraco_dir'] = true;
          else if (norm.indexOf('esq') !== -1) matchedIds['antbraco_esq'] = true;
          else { matchedIds['antbraco_dir'] = true; matchedIds['antbraco_esq'] = true; }
          matched = true;
        }
        if (norm.indexOf('joelho') !== -1) {
          if (norm.indexOf('dir') !== -1) matchedIds['joelho_dir'] = true;
          else if (norm.indexOf('esq') !== -1) matchedIds['joelho_esq'] = true;
          else { matchedIds['joelho_dir'] = true; matchedIds['joelho_esq'] = true; }
          matched = true;
        }
        if (norm.indexOf('perna') !== -1 || norm.indexOf('canela') !== -1 || norm.indexOf('panturrilha') !== -1) {
          if (norm.indexOf('dir') !== -1) matchedIds['perna_dir'] = true;
          else if (norm.indexOf('esq') !== -1) matchedIds['perna_esq'] = true;
          else { matchedIds['perna_dir'] = true; matchedIds['perna_esq'] = true; }
          matched = true;
        }
        if (norm.indexOf('pe') !== -1 || norm.indexOf('calcanhar') !== -1 || norm.indexOf('tornozelo') !== -1) {
          if (norm.indexOf('dir') !== -1) matchedIds['pe_dir'] = true;
          else if (norm.indexOf('esq') !== -1) matchedIds['pe_esq'] = true;
          else { matchedIds['pe_dir'] = true; matchedIds['pe_esq'] = true; }
          matched = true;
        }
      }

      if (!matched) {
        unmatchedTokens.push(token);
      }
    });

    return { ids: matchedIds, unmatched: unmatchedTokens };
  }

  /* ── Inicializador Principal do Mapa Corporal ── */
  function initBodyMap(container, opts) {
    if (typeof container === 'string') container = document.querySelector(container);
    if (!container) return;

    opts = opts || {};
    var interactive = opts.interactive !== false;
    var targetInput = opts.inputTarget ? document.querySelector(opts.inputTarget) : null;
    var rawInitial = opts.selected || (targetInput ? targetInput.value : '') || '';

    var matchRes = matchTextToPartIds(rawInitial);
    var selected = Object.assign({}, matchRes.ids);
    var customTags = matchRes.unmatched.slice();

    // Se 'dedos' está selecionado, também destaca visualmente mãos se nenhuma estiver
    if (selected['dedos'] && !selected['mao_dir'] && !selected['mao_esq']) {
      selected['mao_dir'] = true;
    }

    container.innerHTML = ''; // Limpa conteúdo prévio

    /* ── Layout Principal ── */
    var layoutWrap = document.createElement('div');
    layoutWrap.className = 'body-map-layout' + (interactive ? ' body-map--interactive' : ' body-map--readonly');

    /* ── Box do SVG (Figura Humana) ── */
    var figureBox = document.createElement('div');
    figureBox.className = 'body-map-figure-box';

    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 460 410');
    svg.setAttribute('class', 'body-map__svg');
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'Mapa anatômico do corpo humano');

    // Títulos de Vista no SVG
    var textFrente = document.createElementNS(NS, 'text');
    textFrente.setAttribute('x', '115');
    textFrente.setAttribute('y', '16');
    textFrente.setAttribute('text-anchor', 'middle');
    textFrente.setAttribute('class', 'body-view-title');
    textFrente.textContent = 'FRENTE (ANTERIOR)';
    svg.appendChild(textFrente);

    var textCostas = document.createElementNS(NS, 'text');
    textCostas.setAttribute('x', '345');
    textCostas.setAttribute('y', '16');
    textCostas.setAttribute('text-anchor', 'middle');
    textCostas.setAttribute('class', 'body-view-title');
    textCostas.textContent = 'COSTAS (POSTERIOR)';
    svg.appendChild(textCostas);

    // Linha divisória suave
    var divider = document.createElementNS(NS, 'line');
    divider.setAttribute('x1', '230');
    divider.setAttribute('y1', '10');
    divider.setAttribute('x2', '230');
    divider.setAttribute('y2', '400');
    divider.setAttribute('stroke', '#e2e8f0');
    divider.setAttribute('stroke-dasharray', '4 4');
    divider.setAttribute('stroke-width', '1');
    svg.appendChild(divider);

    // Tooltip flutuante
    var tooltip = document.createElement('div');
    tooltip.className = 'body-map__tooltip';
    figureBox.appendChild(tooltip);

    // Renderizar partes anatômicas do SVG
    var svgElements = [];
    SVG_SHAPES.forEach(function (item) {
      var el = document.createElementNS(NS, item.tag);
      for (var attr in item) {
        if (['tag', 'id', 'view', 'label'].indexOf(attr) === -1) {
          el.setAttribute(attr, item[attr]);
        }
      }
      el.classList.add('body-map__part');
      el.dataset.id = item.id;
      el.dataset.label = item.label;

      if (selected[item.id]) {
        el.classList.add('body-map__part--active');
      }

      // Eventos interativos
      if (interactive) {
        el.addEventListener('click', function () {
          togglePart(item.id);
        });
      }

      el.addEventListener('mouseenter', function (e) {
        var partDef = BODY_PARTS.find(function (p) { return p.id === item.id; });
        var displayLabel = (partDef ? partDef.label : item.label) + ' (' + (item.view === 'frente' ? 'Frente' : 'Costas') + ')';
        tooltip.textContent = displayLabel;
        tooltip.style.display = 'block';
        updateTooltipPos(e);
      });

      el.addEventListener('mousemove', updateTooltipPos);

      el.addEventListener('mouseleave', function () {
        tooltip.style.display = 'none';
      });

      svg.appendChild(el);
      svgElements.push(el);
    });

    figureBox.appendChild(svg);
    layoutWrap.appendChild(figureBox);

    /* ── Painel Lateral (Chips, Tags, Controles) ── */
    var sidePanel = document.createElement('div');
    sidePanel.className = 'body-map-side-panel';

    // Seção de Tags das Partes Atingidas
    var tagsBox = document.createElement('div');
    tagsBox.className = 'body-map-tags-box';

    var tagsHeader = document.createElement('div');
    tagsHeader.style.display = 'flex';
    tagsHeader.style.justifyContent = 'space-between';
    tagsHeader.style.alignItems = 'center';

    var tagsTitle = document.createElement('div');
    tagsTitle.className = 'body-map-side-title';
    tagsTitle.innerHTML = '📍 <strong>Regiões Atingidas Registradas:</strong>';
    tagsHeader.appendChild(tagsTitle);

    if (interactive) {
      var clearBtn = document.createElement('button');
      clearBtn.type = 'button';
      clearBtn.className = 'btn secondary';
      clearBtn.style.padding = '4px 10px';
      clearBtn.style.fontSize = '11px';
      clearBtn.textContent = 'Limpar seleção';
      clearBtn.addEventListener('click', function () {
        for (var k in selected) delete selected[k];
        customTags = [];
        syncAll();
      });
      tagsHeader.appendChild(clearBtn);
    }
    tagsBox.appendChild(tagsHeader);

    var tagsList = document.createElement('div');
    tagsList.className = 'body-map-tags-list';
    tagsBox.appendChild(tagsList);
    sidePanel.appendChild(tagsBox);

    // Seção de Botões Rápidos (Chips)
    var chipsTitle = document.createElement('div');
    chipsTitle.className = 'body-map-side-title';
    chipsTitle.innerHTML = interactive
      ? '⚡ <strong>Seleção Rápida por Região:</strong> <small style="font-weight:normal;color:#64748b">(Clique para marcar/desmarcar)</small>'
      : '📋 <strong>Principais Regiões Anatômicas:</strong>';
    sidePanel.appendChild(chipsTitle);

    var chipsGrid = document.createElement('div');
    chipsGrid.className = 'body-map-chips-grid';

    var chipButtons = {};
    BODY_PARTS.forEach(function (part) {
      var chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'body-map__chip' + (selected[part.id] ? ' body-map__chip--active' : '');
      chip.textContent = part.label;
      chip.dataset.id = part.id;

      if (interactive) {
        chip.addEventListener('click', function () {
          togglePart(part.id);
        });
      } else {
        chip.style.pointerEvents = 'none';
      }

      chipsGrid.appendChild(chip);
      chipButtons[part.id] = chip;
    });
    sidePanel.appendChild(chipsGrid);

    layoutWrap.appendChild(sidePanel);
    container.appendChild(layoutWrap);

    /* ── Funções de Lógica e Sincronização ── */
    function togglePart(id) {
      if (selected[id]) {
        delete selected[id];
      } else {
        selected[id] = true;
      }
      syncAll();
    }

    function updateTooltipPos(e) {
      var boxRect = figureBox.getBoundingClientRect();
      var x = e.clientX - boxRect.left;
      var y = e.clientY - boxRect.top;
      tooltip.style.left = x + 'px';
      tooltip.style.top = y + 'px';
    }

    function syncAll() {
      // 1. Atualizar classes no SVG
      svgElements.forEach(function (el) {
        var pid = el.dataset.id;
        if (selected[pid]) {
          el.classList.add('body-map__part--active');
        } else {
          el.classList.remove('body-map__part--active');
        }
      });

      // 2. Atualizar classes nos chips
      for (var id in chipButtons) {
        if (selected[id]) {
          chipButtons[id].classList.add('body-map__chip--active');
        } else {
          chipButtons[id].classList.remove('body-map__chip--active');
        }
      }

      // 3. Montar lista de labels selecionados
      var activeLabels = [];
      BODY_PARTS.forEach(function (p) {
        if (selected[p.id]) {
          activeLabels.push(p.label);
        }
      });

      var fullList = activeLabels.concat(customTags);

      // 4. Renderizar tags
      tagsList.innerHTML = '';
      if (!fullList.length) {
        tagsList.innerHTML = '<span class="body-map-empty-hint">' +
          (interactive
            ? 'Nenhuma parte selecionada. Clique no corpo humano ou nos botões acima.'
            : 'Nenhuma parte do corpo registrada para esta ocorrência.') +
          '</span>';
      } else {
        fullList.forEach(function (label, idx) {
          var tag = document.createElement('span');
          tag.className = 'body-map__tag';
          tag.textContent = label;

          if (interactive) {
            var removeBtn = document.createElement('span');
            removeBtn.className = 'body-map__tag-remove';
            removeBtn.innerHTML = '&times;';
            removeBtn.title = 'Remover ' + label;
            removeBtn.addEventListener('click', function (ev) {
              ev.stopPropagation();
              var p = BODY_PARTS.find(function (pp) { return pp.label.toLowerCase() === label.toLowerCase(); });
              if (p) {
                delete selected[p.id];
              } else {
                var cIdx = customTags.indexOf(label);
                if (cIdx !== -1) customTags.splice(cIdx, 1);
              }
              syncAll();
            });
            tag.appendChild(removeBtn);
          }
          tagsList.appendChild(tag);
        });
      }

      // 5. Sincronizar input alvo (se interativo)
      if (interactive) {
        var strVal = fullList.join(', ');
        if (targetInput && targetInput.value !== strVal) {
          targetInput.value = strVal;
        }
      }
    }

    // Se o usuário digitar no input manualmente, sincronizar de volta com o mapa
    if (interactive && targetInput) {
      targetInput.addEventListener('input', function () {
        var res = matchTextToPartIds(targetInput.value);
        selected = Object.assign({}, res.ids);
        customTags = res.unmatched.slice();
        syncAll();
      });
    }

    // Renderização inicial
    syncAll();
  }

  /* ── Auto-inicialização de todos os [data-body-map] da página ── */
  function autoInit() {
    document.querySelectorAll('[data-body-map]').forEach(function (el) {
      if (el.__bodyMapLoaded) return;
      el.__bodyMapLoaded = true;

      var mode = el.dataset.bodyMap;
      var selectedVal = el.dataset.selected || '';
      var inputTarget = el.dataset.inputTarget || '';

      initBodyMap(el, {
        interactive: mode === 'interactive',
        selected: selectedVal,
        inputTarget: inputTarget
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }

  window.initBodyMap = initBodyMap;
})();
