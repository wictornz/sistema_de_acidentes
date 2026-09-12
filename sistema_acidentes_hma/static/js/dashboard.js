/**
 * Dashboard Epidemiológico & Indicadores de Segurança - HMA
 * Renderização de gráficos modernos e compactos com Chart.js
 */
(function () {
  'use strict';

  var anoSelect = document.getElementById('filtroAno');
  var setorSelect = document.getElementById('filtroSetor');
  var btnLimpar = document.getElementById('limparFiltros');
  var loadedFilters = false;

  // Instâncias ativas dos gráficos
  var charts = {};

  // Configuração global do Chart.js
  if (window.Chart) {
    Chart.defaults.font.family = 'Inter, Segoe UI, -apple-system, sans-serif';
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#475569';
    Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a';
    Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
    Chart.defaults.plugins.tooltip.bodyColor = '#f8fafc';
    Chart.defaults.plugins.tooltip.titleFont = { size: 11, weight: '700' };
    Chart.defaults.plugins.tooltip.bodyFont = { size: 11 };
    Chart.defaults.plugins.tooltip.padding = 7;
    Chart.defaults.plugins.tooltip.cornerRadius = 6;
    Chart.defaults.plugins.tooltip.boxPadding = 4;
  }

  /* ── Gráfico: Partes do Corpo Mais Atingidas (Horizontal Bar Compacto) ── */
  function updateChartPartes(rows) {
    var canvas = document.getElementById('chartPartes');
    var empty = document.getElementById('emptyPartes');
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
    gradient.addColorStop(0, '#fb7185');
    gradient.addColorStop(1, '#f43f5e');

    charts.partes = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Lesões',
          data: values,
          backgroundColor: gradient,
          borderColor: '#e11d48',
          borderWidth: 1.2,
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

  /* ── Gráfico: Tipos de Acidente (Doughnut / Rosca Moderna) ── */
  function updateChartTipo(rows) {
    var canvas = document.getElementById('chartTipo');
    var empty = document.getElementById('emptyTipo');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.tipo) { charts.tipo.destroy(); delete charts.tipo; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });
    var palette = ['#0284c7', '#f59e0b', '#ef4444', '#8b5cf6', '#10b981', '#6366f1', '#ec4899', '#14b8a6'];

    if (charts.tipo) charts.tipo.destroy();

    var ctx = canvas.getContext('2d');
    charts.tipo = new Chart(ctx, {
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
        cutout: '60%',
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

  /* ── Gráfico: Evolução Mensal (Curved Area Line) ── */
  function updateChartMes(rows) {
    var canvas = document.getElementById('chartMes');
    var empty = document.getElementById('emptyMes');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.mes) { charts.mes.destroy(); delete charts.mes; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });

    if (charts.mes) charts.mes.destroy();

    var ctx = canvas.getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, 0, canvas.height || 185);
    gradient.addColorStop(0, 'rgba(37, 99, 235, 0.28)');
    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.01)');

    charts.mes = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Acidentes no mês',
          data: values,
          borderColor: '#2563eb',
          borderWidth: 2,
          backgroundColor: gradient,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#ffffff',
          pointBorderColor: '#2563eb',
          pointBorderWidth: 1.5,
          pointRadius: 3.5,
          pointHoverRadius: 5.5
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
            ticks: { font: { size: 10 } }
          }
        }
      }
    });
  }

  /* ── Gráfico: Acidentes por Setor (Colored Bars) ── */
  function updateChartSetor(rows) {
    var canvas = document.getElementById('chartSetor');
    var empty = document.getElementById('emptySetor');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.setor) { charts.setor.destroy(); delete charts.setor; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });
    var colors = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#64748b', '#f97316'];

    if (charts.setor) charts.setor.destroy();

    var ctx = canvas.getContext('2d');
    charts.setor = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Acidentes',
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
            ticks: {
              maxRotation: 20,
              minRotation: 0,
              font: { size: 10 }
            }
          }
        }
      }
    });
  }

  /* ── Gráfico: Acidentes por Função / Cargo (Horizontal Bars) ── */
  function updateChartFuncao(rows) {
    var canvas = document.getElementById('chartFuncao');
    var empty = document.getElementById('emptyFuncao');
    if (!canvas) return;

    if (!rows || !rows.length) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = 'flex';
      if (charts.funcao) { charts.funcao.destroy(); delete charts.funcao; }
      return;
    }
    canvas.style.display = 'block';
    if (empty) empty.style.display = 'none';

    var labels = rows.map(function (r) { return r.nome; });
    var values = rows.map(function (r) { return r.qtd; });

    if (charts.funcao) charts.funcao.destroy();

    var ctx = canvas.getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
    gradient.addColorStop(0, '#818cf8');
    gradient.addColorStop(1, '#6366f1');

    charts.funcao = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Acidentes',
          data: values,
          backgroundColor: gradient,
          borderRadius: 4,
          barPercentage: 0.55
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0, font: { size: 10 } },
            grid: { color: '#f1f5f9' }
          },
          y: {
            grid: { display: false },
            ticks: {
              font: { size: 11, weight: '600' }
            }
          }
        }
      }
    });
  }

  /* ── Carregamento Assíncrono do Dashboard ── */
  async function loadDashboard() {
    try {
      var q = new URLSearchParams();
      if (anoSelect && anoSelect.value) q.set('ano', anoSelect.value);
      if (setorSelect && setorSelect.value) q.set('setor', setorSelect.value);

      var resp = await fetch('/api/dashboard?' + q.toString());
      if (!resp.ok) throw new Error('Erro ao carregar dados');
      var data = await resp.json();

      // Atualizar KPIs
      var totalEl = document.getElementById('kpiTotal');
      var diasEl = document.getElementById('kpiDias');
      var catEl = document.getElementById('kpiCat');
      var afastEl = document.getElementById('kpiAfast');

      if (totalEl) totalEl.textContent = data.kpis.total;
      if (diasEl) diasEl.textContent = data.kpis.dias;
      if (catEl) catEl.textContent = data.kpis.cat;
      if (afastEl) afastEl.textContent = data.kpis.afastamentos;

      // Preencher opções dos filtros apenas na primeira carga
      if (!loadedFilters && data.filtros) {
        if (data.filtros.anos && anoSelect) {
          data.filtros.anos.forEach(function (v) {
            anoSelect.add(new Option(v, v));
          });
        }
        if (data.filtros.setores && setorSelect) {
          data.filtros.setores.forEach(function (v) {
            setorSelect.add(new Option(v, v));
          });
        }
        loadedFilters = true;
      }

      // Renderizar gráficos compactos
      updateChartPartes(data.partes);
      updateChartTipo(data.tipos);
      updateChartMes(data.mensal);
      updateChartSetor(data.setores);
      updateChartFuncao(data.funcoes);

    } catch (err) {
      console.error('Erro ao atualizar dashboard:', err);
    }
  }

  // Event Listeners
  if (anoSelect) anoSelect.addEventListener('change', loadDashboard);
  if (setorSelect) setorSelect.addEventListener('change', loadDashboard);
  if (btnLimpar) {
    btnLimpar.addEventListener('click', function () {
      if (anoSelect) anoSelect.value = '';
      if (setorSelect) setorSelect.value = '';
      loadDashboard();
    });
  }

  // Inicialização
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadDashboard);
  } else {
    loadDashboard();
  }
})();
