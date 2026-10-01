/**
 * Painel Analítico de Gráficos - Sistema HMA
 * Renderização dinâmica com Chart.js
 */
(function () {
  'use strict';

  var classifSelect = document.getElementById('filtroClassificacao');
  var cargoSelect = document.getElementById('filtroCargo');
  var setorSelect = document.getElementById('filtroSetor');
  var mesSelect = document.getElementById('filtroMes');
  var btnLimpar = document.getElementById('limparFiltrosGraficos');

  var loadedFilters = false;
  var charts = {};

  if (window.Chart) {
    Chart.defaults.font.family = 'Inter, Segoe UI, -apple-system, sans-serif';
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#475569';
    Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a';
    Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
    Chart.defaults.plugins.tooltip.bodyColor = '#f8fafc';
    Chart.defaults.plugins.tooltip.titleFont = { size: 11, weight: '700' };
    Chart.defaults.plugins.tooltip.bodyFont = { size: 11 };
    Chart.defaults.plugins.tooltip.padding = 8;
    Chart.defaults.plugins.tooltip.cornerRadius = 6;
  }

  /* ── 1. Gráfico de Cargos / Funções ── */
  function updateChartCargos(rows) {
    var canvas = document.getElementById('chartGeralCargos');
    var empty = document.getElementById('emptyGeralCargos');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.cargos) { charts.cargos.destroy(); delete charts.cargos; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });

    if (charts.cargos) charts.cargos.destroy();

    var ctx = canvas.getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
    gradient.addColorStop(0, '#818cf8');
    gradient.addColorStop(1, '#4f46e5');

    charts.cargos = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Ocorrências',
          data: values,
          backgroundColor: gradient,
          borderRadius: 4,
          barPercentage: 0.6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                var total = values.reduce(function (a, b) { return a + b; }, 0);
                var pct = total > 0 ? Math.round((ctx.raw / total) * 100) : 0;
                return ' ' + ctx.raw + ' ocorrência' + (ctx.raw > 1 ? 's' : '') + ' (' + pct + '%)';
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 10 } },
            grid: { color: '#f1f5f9' }
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 11, weight: '600' } }
          }
        }
      }
    });
  }

  /* ── 2. Gráfico de Setores ── */
  function updateChartSetores(rows) {
    var canvas = document.getElementById('chartGeralSetores');
    var empty = document.getElementById('emptyGeralSetores');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.setores) { charts.setores.destroy(); delete charts.setores; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });
    var colors = ['#0284c7', '#0ea5e9', '#38bdf8', '#06b6d4', '#14b8a6', '#10b981', '#6366f1', '#8b5cf6'];

    if (charts.setores) charts.setores.destroy();

    var ctx = canvas.getContext('2d');
    charts.setores = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Ocorrências',
          data: values,
          backgroundColor: colors.slice(0, values.length),
          borderRadius: 4,
          barPercentage: 0.6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 10 } },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false },
            ticks: { maxRotation: 25, minRotation: 0, font: { size: 10 } }
          }
        }
      }
    });
  }

  /* ── 3. Gráfico de Local onde ocorreu o acidente ── */
  function updateChartLocais(rows) {
    var canvas = document.getElementById('chartGeralLocais');
    var empty = document.getElementById('emptyGeralLocais');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.locais) { charts.locais.destroy(); delete charts.locais; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });

    if (charts.locais) charts.locais.destroy();

    var ctx = canvas.getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
    gradient.addColorStop(0, '#64748b');
    gradient.addColorStop(1, '#334155');

    charts.locais = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Ocorrências',
          data: values,
          backgroundColor: gradient,
          borderRadius: 4,
          barPercentage: 0.6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                var total = values.reduce(function (a, b) { return a + b; }, 0);
                var pct = total > 0 ? Math.round((ctx.raw / total) * 100) : 0;
                return ' ' + ctx.raw + ' ocorrência' + (ctx.raw > 1 ? 's' : '') + ' (' + pct + '%)';
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 10 } },
            grid: { color: '#f1f5f9' }
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 11, weight: '600' } }
          }
        }
      }
    });
  }

  /* ── 4. Gráfico de Tipo de Exposição (Biológico) ── */
  function updateChartExposicoes(rows) {
    var canvas = document.getElementById('chartGeralExposicoes');
    var empty = document.getElementById('emptyGeralExposicoes');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.exposicoes) { charts.exposicoes.destroy(); delete charts.exposicoes; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });
    var palette = ['#ef4444', '#f97316', '#eab308', '#dc2626'];

    if (charts.exposicoes) charts.exposicoes.destroy();

    var ctx = canvas.getContext('2d');
    charts.exposicoes = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: palette.slice(0, values.length),
          borderColor: '#ffffff',
          borderWidth: 2,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '55%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 10,
              boxHeight: 10,
              padding: 8,
              font: { size: 11, weight: '500' }
            }
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                var total = values.reduce(function (a, b) { return a + b; }, 0);
                var pct = total > 0 ? Math.round((ctx.raw / total) * 100) : 0;
                return ' ' + ctx.label + ': ' + ctx.raw + ' (' + pct + '%)';
              }
            }
          }
        }
      }
    });
  }

  /* ── 5. Gráfico de Período do Dia (Turno) ── */
  function updateChartPeriodos(rows) {
    var canvas = document.getElementById('chartGeralPeriodos');
    var empty = document.getElementById('emptyGeralPeriodos');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.periodos) { charts.periodos.destroy(); delete charts.periodos; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });
    var colors = ['#f59e0b', '#3b82f6', '#1e293b', '#6366f1', '#64748b'];

    if (charts.periodos) charts.periodos.destroy();

    var ctx = canvas.getContext('2d');
    charts.periodos = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Ocorrências por turno',
          data: values,
          backgroundColor: colors.slice(0, values.length),
          borderRadius: 4,
          barPercentage: 0.55
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 10 } },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 11, weight: '600' } }
          }
        }
      }
    });
  }

  /* ── 6. Gráfico de Partes do Corpo Atingidas ── */
  function updateChartPartes(rows) {
    var canvas = document.getElementById('chartGeralPartes');
    var empty = document.getElementById('emptyGeralPartes');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.partes) { charts.partes.destroy(); delete charts.partes; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });

    if (charts.partes) charts.partes.destroy();

    var ctx = canvas.getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
    gradient.addColorStop(0, '#34d399');
    gradient.addColorStop(1, '#059669');

    charts.partes = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Lesões',
          data: values,
          backgroundColor: gradient,
          borderRadius: 4,
          barPercentage: 0.6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                var total = values.reduce(function (a, b) { return a + b; }, 0);
                var pct = total > 0 ? Math.round((ctx.raw / total) * 100) : 0;
                return ' ' + ctx.raw + ' ocorrência' + (ctx.raw > 1 ? 's' : '') + ' (' + pct + '%)';
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 10 } },
            grid: { color: '#f1f5f9' }
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 11, weight: '600' } }
          }
        }
      }
    });
  }

  /* ── Carregamento Assíncrono dos Dados de Gráficos ── */
  async function loadGraficos() {
    try {
      var q = new URLSearchParams();
      if (classifSelect && classifSelect.value) q.set('classificacao', classifSelect.value);
      if (cargoSelect && cargoSelect.value) q.set('cargo', cargoSelect.value);
      if (setorSelect && setorSelect.value) q.set('setor', setorSelect.value);
      if (mesSelect && mesSelect.value) q.set('mes', mesSelect.value);

      var resp = await fetch('/api/graficos?' + q.toString());
      if (!resp.ok) throw new Error('Erro ao carregar dados analíticos');
      var data = await resp.json();

      // Preencher opções dos filtros apenas na primeira carga
      if (!loadedFilters && data.filtros) {
        if (data.filtros.cargos && cargoSelect) {
          data.filtros.cargos.forEach(function (v) {
            cargoSelect.add(new Option(v, v));
          });
        }
        if (data.filtros.setores && setorSelect) {
          data.filtros.setores.forEach(function (v) {
            setorSelect.add(new Option(v, v));
          });
        }
        loadedFilters = true;
      }

      // Atualizar os 6 gráficos
      updateChartCargos(data.cargos);
      updateChartSetores(data.setores);
      updateChartLocais(data.locais);
      updateChartExposicoes(data.exposicoes);
      updateChartPeriodos(data.periodos);
      updateChartPartes(data.partes);

    } catch (err) {
      console.error('Erro ao atualizar painel de gráficos:', err);
    }
  }

  // Event Listeners
  if (classifSelect) classifSelect.addEventListener('change', loadGraficos);
  if (cargoSelect) cargoSelect.addEventListener('change', loadGraficos);
  if (setorSelect) setorSelect.addEventListener('change', loadGraficos);
  if (mesSelect) mesSelect.addEventListener('change', loadGraficos);

  if (btnLimpar) {
    btnLimpar.addEventListener('click', function () {
      if (classifSelect) classifSelect.value = 'Acidente';
      if (cargoSelect) cargoSelect.value = '';
      if (setorSelect) setorSelect.value = '';
      if (mesSelect) mesSelect.value = '';
      loadGraficos();
    });
  }

  // Inicialização
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadGraficos);
  } else {
    loadGraficos();
  }
})();
