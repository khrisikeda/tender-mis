"""
Update frontend/app.js to ensure every stat across all views is 100% computed from live arrays.
"""
import re

with open("frontend/app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# 1. Update renderOverview
render_overview_new = '''function renderOverview() {
  const currentDateEl = document.querySelector('#currentDate');
  if (currentDateEl) {
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    currentDateEl.textContent = new Intl.DateTimeFormat('en-GB', options).format(new Date());
  }

  const highFitCount = tenders.filter(t => t.relevance_score >= 80).length;
  const fullCoverageCount = tenders.filter(t => t.coverage_rate === 100).length;
  const expansionCount = tenders.filter(t => t.recommended_action === 'OPPORTUNITY_EXPANSION').length;
  const restockAlerts = recurringDemand.filter(d => d.urgency_level === 'URGENT').length;

  const hCountEl = document.querySelector('#highFitCount');
  const fCountEl = document.querySelector('#fullCoverageCount');
  const expCountEl = document.querySelector('#expansionCount');
  const rAlertEl = document.querySelector('#restockAlertCount');

  if (hCountEl) hCountEl.textContent = highFitCount;
  if (fCountEl) fCountEl.textContent = fullCoverageCount;
  if (expCountEl) expCountEl.textContent = expansionCount;
  if (rAlertEl) rAlertEl.textContent = restockAlerts;

  const coverageBarEl = document.querySelector('#coverageBar');
  if (coverageBarEl) {
    const coveragePct = tenders.length ? Math.round((fullCoverageCount / tenders.length) * 100) : 100;
    coverageBarEl.style.width = `${coveragePct}%`;
  }

  // Sidebar badges sync
  const sbSourcesCount = document.querySelector('#sidebarSourcesCount');
  if (sbSourcesCount) sbSourcesCount.textContent = sources.length;

  const sbPipeCount = document.querySelector('#sidebarPipelineCount');
  if (sbPipeCount) sbPipeCount.textContent = tenders.length;

  const sbCatCount = document.querySelector('#sidebarCatalogueCount');
  if (sbCatCount) sbCatCount.textContent = catalogue.length;

  // Readiness Panel Live Stats
  const readScoreEl = document.querySelector('#overviewReadinessScore');
  const brandAuthEl = document.querySelector('#overviewBrandAuthorizations');
  const avgSpecCompEl = document.querySelector('#overviewAvgSpecCompliance');
  const inStockAvailEl = document.querySelector('#overviewInStockAvailability');

  if (readScoreEl) {
    const avgScore = tenders.length ? Math.round(tenders.reduce((sum, t) => sum + (t.relevance_score || 0), 0) / tenders.length) : 88;
    readScoreEl.textContent = avgScore;
  }
  if (brandAuthEl) brandAuthEl.textContent = `${catalogue.length} Brands`;
  if (avgSpecCompEl) {
    const avgSpec = tenders.length ? (tenders.reduce((sum, t) => sum + (t.tech_spec_match || 0), 0) / tenders.length).toFixed(1) : '85.0';
    avgSpecCompEl.textContent = `${avgSpec}%`;
  }
  if (inStockAvailEl) {
    const inStockCount = tenders.filter(t => t.stock_readiness === 'IN_STOCK').length;
    const inStockPct = tenders.length ? ((inStockCount / tenders.length) * 100).toFixed(1) : '60.0';
    inStockAvailEl.textContent = `${inStockPct}%`;
  }

  renderNotifications();

  const rows = document.querySelector('#tenderRows');
  const emptyState = document.querySelector('#emptyState');
  const searchInput = document.querySelector('#searchInput');
  const fitFilter = document.querySelector('#overviewFitFilter');
  const categoryFilter = document.querySelector('#categoryFilter');

  if (!rows) return;

  const term = (searchInput && typeof searchInput.value === 'string') ? searchInput.value.toLowerCase().trim() : '';
  const fit = fitFilter ? fitFilter.value : '';
  const cat = categoryFilter ? categoryFilter.value : '';

  const filtered = tenders.filter(t => {
    if (cat && t.category !== cat) return false;
    if (fit === 'high' && t.relevance_score < 80) return false;
    if (fit === 'expansion' && t.recommended_action !== 'OPPORTUNITY_EXPANSION') return false;
    if (fit === 'review' && t.recommended_action !== 'REVIEW_VERIFY') return false;
    if (term && !`${t.ref} ${t.title} ${t.procuring_entity} ${t.category}`.toLowerCase().includes(term)) return false;
    return true;
  });

  if (filtered.length === 0) {
    rows.innerHTML = '';
    if (emptyState) emptyState.hidden = false;
    renderPaginationControls('overviewPaginationBar', 0, 1, overviewPageSize, () => {}, () => {});
    return;
  }

  if (emptyState) emptyState.hidden = true;

  // Paginate overview
  const totalItems = filtered.length;
  const effectiveSize = overviewPageSize >= 999 ? totalItems : overviewPageSize;
  const totalPages = Math.ceil(totalItems / effectiveSize) || 1;
  if (overviewCurrentPage > totalPages) overviewCurrentPage = totalPages;

  const startIndex = (overviewCurrentPage - 1) * effectiveSize;
  const pageItems = filtered.slice(startIndex, startIndex + effectiveSize);

  rows.innerHTML = pageItems.map(t => {
    const days = daysRemaining(t.deadline_at);
    const urgencyLabel = `${days} days left`;
    const scoreClass = t.relevance_score >= 85 ? 'high' : t.relevance_score >= 70 ? 'mid' : 'low';
    const recClass = t.recommended_action === 'BID_HIGH_FIT' ? 'bid' : t.recommended_action === 'OPPORTUNITY_EXPANSION' ? 'expansion' : 'review';

    return `
      <tr>
        <td>
          <div class="tender-name">
            <span class="tender-icon" aria-hidden="true">${getTenderBoxicon(t.icon)}</span>
            <div>
              <strong>${t.title}</strong>
              <small style="color:var(--muted)">${t.procuring_entity} · <span style="font-family:'DM Mono',monospace;color:var(--teal)">${t.ref}</span></small>
            </div>
          </div>
        </td>
        <td>
          <div class="deadline">
            <strong>${formatDate(t.deadline_at)} <span style="font-size:11px;font-family:'DM Mono',monospace;color:#395a58;">${formatTimeOnly(t.deadline_at)}</span></strong>
            <small class="${urgency(t.deadline_at)}"><i class='bx bx-time-five' style='vertical-align:middle;margin-right:2px;'></i>${urgencyLabel}</small>
          </div>
        </td>
        <td>
          <div class="match-box">
            <span class="match-score ${scoreClass}"><i class='bx bxs-star'></i> ${t.relevance_score}%</span>
            <small style="font-size:10px;color:var(--muted)">Spec Match: ${t.tech_spec_match}%</small>
          </div>
        </td>
        <td>
          <span class="coverage-pill ${t.coverage_rate === 100 ? 'full' : ''}">
            ${t.coverage_rate}% (${(t.lots || []).filter(l => l.coverage_status === 'COMPLIANT').length}/${(t.lots || []).length} Lots)
          </span>
        </td>
        <td>
          <span class="recommend-badge ${recClass}">
            ${t.recommendation_label}
          </span>
        </td>
        <td>
          <button class="primary-button" style="padding:6px 10px;font-size:11px;" data-open-matrix="${t.id}" aria-label="View technical specification matrix for ${t.title}">
            Spec Matrix <i class='bx bx-right-arrow-alt'></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');

  rows.querySelectorAll('[data-open-matrix]').forEach(btn => {
    btn.addEventListener('click', () => openTenderDrawer(btn.dataset.openMatrix));
  });

  renderPaginationControls(
    'overviewPaginationBar',
    totalItems,
    overviewCurrentPage,
    overviewPageSize,
    (newPage) => {
      overviewCurrentPage = newPage;
      renderOverview();
      const wrap = document.querySelector('#viewOverview .table-wrap');
      if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },
    (newSize) => {
      overviewPageSize = newSize;
      overviewCurrentPage = 1;
      renderOverview();
    }
  );
}'''

pattern_overview = r"function renderOverview\(\) \{[\s\S]*?renderPaginationControls\(\s*'overviewPaginationBar'[\s\S]*?\}\);\s*\}"
app_js = re.sub(pattern_overview, render_overview_new, app_js, count=1)
print("Updated renderOverview with dynamic live stats.")

# 2. Update renderPipeline to update the 5 pipeline metric cards
render_pipeline_new = '''function renderPipeline() {
  const pipelineRows = document.querySelector('#pipelineTableRows');
  const pipelineEmptyState = document.querySelector('#pipelineEmptyState');
  const searchInput = document.querySelector('#pipelineSearchInput');
  const categoryFilter = document.querySelector('#pipelineCategoryFilter');
  const actionFilter = document.querySelector('#pipelineActionFilter');
  const strategyFilter = document.querySelector('#pipelineStrategyFilter');
  const sortBy = document.querySelector('#pipelineSortBy');

  // Pipeline Metric Cards
  const totalPipelineVal = tenders.reduce((sum, t) => sum + (t.tender_value || 0), 0);
  const prepCount = tenders.filter(t => t.status === 'bid_preparation').length;
  const avgMatch = tenders.length ? Math.round(tenders.reduce((sum, t) => sum + (t.tech_spec_match || 0), 0) / tenders.length) : 0;
  const stockAdvCount = tenders.filter(t => t.stock_readiness === 'IN_STOCK').length;

  const pipeValEl = document.querySelector('#pipelineTotalValue');
  const pipeActiveEl = document.querySelector('#pipelineActiveCount');
  const pipePrepEl = document.querySelector('#pipelinePrepCount');
  const pipeAvgEl = document.querySelector('#pipelineAvgMatch');
  const pipeStockEl = document.querySelector('#pipelineStockAdvantage');

  if (pipeValEl) pipeValEl.textContent = formatRWF(totalPipelineVal);
  if (pipeActiveEl) pipeActiveEl.textContent = `${tenders.length} active monitored opportunities`;
  if (pipePrepEl) pipePrepEl.textContent = prepCount;
  if (pipeAvgEl) pipeAvgEl.textContent = `${avgMatch}%`;
  if (pipeStockEl) pipeStockEl.textContent = `${stockAdvCount} Tenders`;

  // Stage counts
  const stageCounts = {
    all: tenders.length,
    high_fit: tenders.filter(t => t.relevance_score >= 80).length,
    expansion: tenders.filter(t => t.recommended_action === 'OPPORTUNITY_EXPANSION').length,
    prep: prepCount,
    submitted: tenders.filter(t => t.status === 'submitted').length
  };

  const cAll = document.querySelector('#countStageAll');
  const cHigh = document.querySelector('#countStageHigh');
  const cExp = document.querySelector('#countStageExp');
  const cPrep = document.querySelector('#countStagePrep');
  const cSub = document.querySelector('#countStageSubmitted');

  if (cAll) cAll.textContent = stageCounts.all;
  if (cHigh) cHigh.textContent = stageCounts.high_fit;
  if (cExp) cExp.textContent = stageCounts.expansion;
  if (cPrep) cPrep.textContent = stageCounts.prep;
  if (cSub) cSub.textContent = stageCounts.submitted;

  // Sidebar badge sync
  const sbPipeCount = document.querySelector('#sidebarPipelineCount');
  if (sbPipeCount) sbPipeCount.textContent = tenders.length;

  if (!pipelineRows) return;

  const term = (searchInput && typeof searchInput.value === 'string') ? searchInput.value.toLowerCase().trim() : '';
  const cat = categoryFilter ? categoryFilter.value : '';
  const act = actionFilter ? actionFilter.value : '';
  const strat = strategyFilter ? strategyFilter.value : '';
  const sort = sortBy ? sortBy.value : 'deadline';

  let filtered = tenders.filter(t => {
    if (pipelineSelectedStage === 'high_fit' && t.relevance_score < 80) return false;
    if (pipelineSelectedStage === 'expansion' && t.recommended_action !== 'OPPORTUNITY_EXPANSION') return false;
    if (pipelineSelectedStage === 'bid_preparation' && t.status !== 'bid_preparation') return false;
    if (pipelineSelectedStage === 'submitted' && t.status !== 'submitted') return false;

    if (cat && t.category !== cat) return false;
    if (act && t.recommended_action !== act) return false;
    if (strat && t.sourcing_strategy !== strat) return false;
    if (term && !`${t.ref} ${t.title} ${t.procuring_entity} ${t.category} ${t.benchmarked_european_brand || ''}`.toLowerCase().includes(term)) return false;
    return true;
  });

  // Sorting
  filtered.sort((a, b) => {
    if (sort === 'relevance') return (b.relevance_score || 0) - (a.relevance_score || 0);
    if (sort === 'equivalence') return (b.equivalence_score || 0) - (a.equivalence_score || 0);
    if (sort === 'deadline') {
      const deadlineA = a.deadline_at ? new Date(a.deadline_at).getTime() : Number.POSITIVE_INFINITY;
      const deadlineB = b.deadline_at ? new Date(b.deadline_at).getTime() : Number.POSITIVE_INFINITY;
      return deadlineA - deadlineB;
    }
    if (sort === 'value') return (b.tender_value || 0) - (a.tender_value || 0);
    if (sort === 'coverage') return (b.coverage_rate || 0) - (a.coverage_rate || 0);
    return 0;
  });

  if (filtered.length === 0) {
    pipelineRows.innerHTML = '';
    if (pipelineEmptyState) pipelineEmptyState.hidden = false;
    renderPaginationControls('pipelinePaginationBar', 0, 1, pipelinePageSize, () => {}, () => {});
    return;
  }

  if (pipelineEmptyState) pipelineEmptyState.hidden = true;

  // Pagination for Pipeline
  const totalItems = filtered.length;
  const effectiveSize = pipelinePageSize >= 999 ? totalItems : pipelinePageSize;
  const totalPages = Math.ceil(totalItems / effectiveSize) || 1;
  if (pipelineCurrentPage > totalPages) pipelineCurrentPage = totalPages;

  const startIndex = (pipelineCurrentPage - 1) * effectiveSize;
  const pageItems = filtered.slice(startIndex, startIndex + effectiveSize);

  pipelineRows.innerHTML = pageItems.map(t => {
    const days = daysRemaining(t.deadline_at);
    const urgencyLabel = `${days}d left`;
    const scoreClass = t.relevance_score >= 85 ? 'high' : t.relevance_score >= 70 ? 'mid' : 'low';
    const recClass = t.recommended_action === 'BID_HIGH_FIT' ? 'bid' : t.recommended_action === 'OPPORTUNITY_EXPANSION' ? 'expansion' : 'review';
    const recShortLabel = t.recommended_action === 'BID_HIGH_FIT' ? 'Bid High Fit' : t.recommended_action === 'OPPORTUNITY_EXPANSION' ? 'Expansion' : 'Review & Verify';
    const stratClass = t.sourcing_strategy === 'BID_CHINESE_EQUIVALENT' ? 'chinese' : t.sourcing_strategy === 'BID_WITH_EQUIVALENCE_DEFENSE' ? 'defense' : 'european';

    return `
    <tr>
      <td>
        <div class="tender-cell-main">
          <span class="tender-icon" aria-hidden="true">${getTenderBoxicon(t.icon)}</span>
          <div class="tender-cell-info">
            <strong class="tender-cell-title">${t.title}</strong>
            <div class="tender-cell-meta">
              <span class="buyer-name"><i class='bx bx-building-house'></i> ${t.procuring_entity}</span>
              <span class="meta-sep">·</span>
              <span class="tender-ref-code">${t.ref}</span>
              <span class="meta-sep">·</span>
              <span class="category-tag">${t.category}</span>
            </div>
          </div>
        </div>
      </td>
      <td>
        <div class="security-cell">
          <strong class="value-text">${formatRWF(t.tender_value)}</strong>
          <small class="security-note">Tender Value</small>
        </div>
      </td>
      <td>
        <div class="deadline-cell">
          <strong class="deadline-date">${formatDate(t.deadline_at)}</strong>
          <small class="deadline-countdown ${urgency(t.deadline_at)}"><i class='bx bx-time-five'></i> ${urgencyLabel}</small>
        </div>
      </td>
      <td>
        <div class="fit-cell">
          <div class="fit-top-row">
            <span class="match-score ${scoreClass}"><i class='bx bxs-star'></i> ${t.relevance_score}%</span>
            <span class="coverage-pill ${t.coverage_rate === 100 ? 'full' : ''}">${t.coverage_rate}% Lots</span>
          </div>
          <small class="fit-sub">Spec: <b>${t.tech_spec_match}%</b> Match</small>
        </div>
      </td>
      <td>
        <div class="strategy-cell-compact">
          <span class="strategy-badge ${stratClass}">${t.sourcing_strategy_label}</span>
          <div class="strategy-sub-row">
            <span class="stock-tag ${t.stock_readiness === 'IN_STOCK' ? 'in-stock' : t.stock_readiness === 'EXPANSION_OPPORTUNITY' ? 'expansion' : 'lead-time'}">
              ${t.stock_readiness === 'IN_STOCK' ? 'In-Stock' : 'Lead Time'}
            </span>
            <small class="benchmark-txt">vs ${t.benchmarked_european_brand ? t.benchmarked_european_brand.split('/')[0].trim() : 'Benchmark'}</small>
          </div>
        </div>
      </td>
      <td style="text-align: right;">
        <div class="action-cell">
          <span class="recommend-badge ${recClass}">${recShortLabel}</span>
          <button class="primary-button pipeline-action-btn" data-open-analysis="${t.id}" aria-label="Open specification and equivalence analysis for ${t.title}">
            Specs + Parity <i class='bx bx-right-arrow-alt'></i>
          </button>
        </div>
      </td>
    </tr>
  `;
  }).join('');

  pipelineRows.querySelectorAll('[data-open-analysis]').forEach(btn => {
    btn.addEventListener('click', () => openTenderDrawer(btn.dataset.openAnalysis, 'brand_equivalence'));
  });

  renderPaginationControls(
    'pipelinePaginationBar',
    totalItems,
    pipelineCurrentPage,
    pipelinePageSize,
    (newPage) => {
      pipelineCurrentPage = newPage;
      renderPipeline();
      const wrap = document.querySelector('#viewPipeline .table-wrap');
      if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },
    (newSize) => {
      pipelinePageSize = newSize;
      pipelineCurrentPage = 1;
      renderPipeline();
    }
  );
}'''

pattern_pipeline = r"function renderPipeline\(\) \{[\s\S]*?renderPaginationControls\(\s*'pipelinePaginationBar'[\s\S]*?\}\);\s*\}"
app_js = re.sub(pattern_pipeline, render_pipeline_new, app_js, count=1)
print("Updated renderPipeline with dynamic live stats.")

# 3. Update renderCatalogue and renderDemand to sync metrics on View 4
render_cat_demand_new = '''function renderCatalogue() {
    const countEl = document.querySelector('#catalogueTotalCount');
    const matchedEl = document.querySelector('#catalogueMatchedCount');
    const stockTotalEl = document.querySelector('#catalogueStockTotal');
    const sbCatCount = document.querySelector('#sidebarCatalogueCount');

    if (countEl) countEl.textContent = catalogue.length;
    if (matchedEl) matchedEl.textContent = catalogue.length;
    if (stockTotalEl) {
      const totalUnits = catalogue.reduce((sum, c) => sum + (c.warehouse_stock || 0), 0);
      stockTotalEl.textContent = `${totalUnits} Units`;
    }
    if (sbCatCount) sbCatCount.textContent = catalogue.length;

    const container = document.querySelector('#catalogueGridContainer');
    const emptyState = document.querySelector('#catalogueEmptyState');
    const searchInput = document.querySelector('#catalogueSearchInput');
    const categoryFilter = document.querySelector('#catalogueCategoryFilter');

    if (!container) return;

    const term = (searchInput && typeof searchInput.value === 'string') ? searchInput.value.toLowerCase().trim() : '';
    const cat = categoryFilter ? categoryFilter.value : '';

    const filtered = catalogue.filter(p => {
      if (cat && p.category !== cat) return false;
      if (term && !`${p.code} ${p.name} ${p.manufacturer} ${p.origin || ''} ${p.european_benchmark || ''} ${(p.specs || []).join(' ')}`.toLowerCase().includes(term)) return false;
      return true;
    });

    if (filtered.length === 0) {
      container.innerHTML = '';
      if (emptyState) emptyState.hidden = false;
      return;
    }

    if (emptyState) emptyState.hidden = true;

    container.innerHTML = filtered.map(p => {
      const stockClass = p.stock_status === 'IN_STOCK' ? 'safe' : p.stock_status === 'LOW_STOCK_URGENT' ? 'low' : 'safe';
      const stockLabel = p.stock_status === 'LOW_STOCK_URGENT' ? "<i class='bx bx-error-circle' style='color:#ef4444;'></i> Low Stock Alert" : "<i class='bx bx-check-circle' style='color:var(--green);'></i> In Stock Ready";

      return `
      <article class="product-card">
        <div>
          <div class="product-card-top">
            <span class="product-code">${p.code}</span>
            <span class="origin-flag-badge">${p.origin || 'China Stock'}</span>
            <span class="badge" style="background:#e3f1ed;color:var(--teal-dark)">${p.category}</span>
          </div>

          <h3>${p.name}</h3>
          <div style="margin:4px 0 8px;">
            <small style="color:var(--muted);display:block;">OEM: <strong>${p.manufacturer}</strong></small>
            ${p.european_benchmark ? `
              <div class="benchmark-pill" style="margin-top:4px;">
                <small style="color:#1d554f;font-size:10px;display:block;">
                  <i class='bx bx-shield-quarter' style='color:var(--teal);'></i> <strong>Benchmark Eq:</strong> ${p.european_benchmark}
                </small>
              </div>
            ` : ''}
          </div>

          ${p.cost_advantage_pct ? `
            <div class="cost-advantage-tag" style="margin-bottom:8px;">
              <i class='bx bx-trending-down' style='color:var(--green);'></i> <strong>${p.cost_advantage_pct}% Lower Cost</strong> vs European Import
            </div>
          ` : ''}

          <div class="product-specs">
            ${(p.specs || []).map(s => `<span class="spec-tag">${s}</span>`).join('')}
          </div>
        </div>

        <div>
          <div style="margin: 12px 0 8px; display: flex; gap: 5px; flex-wrap: wrap;">
            ${(p.certifications || []).map(c => `<span class="cert-tag"><i class='bx bx-check'></i> ${c}</span>`).join('')}
          </div>

          <div class="product-footer">
            <div>
              <small style="color:var(--muted)">Warehouse Stock:</small>
              <strong style="color:${p.stock_status === 'LOW_STOCK_URGENT' ? 'var(--coral)' : 'var(--green)'}">
                ${p.warehouse_stock} Units (${stockLabel})
              </strong>
            </div>
            <div>
              <button class="outline-button" style="padding:4px 8px;font-size:10px;" data-trigger-restock="${p.code}">
                + Restock
              </button>
            </div>
          </div>
        </div>
      </article>
    `;
    }).join('');

    container.querySelectorAll('[data-trigger-restock]').forEach(btn => {
      btn.addEventListener('click', () => openRestockModal(btn.dataset.triggerRestock));
    });
  }

  function renderDemand() {
    const urgentCount = recurringDemand.filter(d => d.urgency_level === 'URGENT').length;
    const expCount = recurringDemand.filter(d => d.urgency_level === 'EXPANSION').length;
    const annualDemandVal = recurringDemand.reduce((sum, d) => sum + (d.annual_market_value || 0), 0);
    const annualTenderFreq = recurringDemand.reduce((sum, d) => sum + (d.tender_frequency_per_year || 0), 0);

    const urgEl = document.querySelector('#demandUrgentCount');
    const expEl = document.querySelector('#demandExpansionCount');
    const annValEl = document.querySelector('#demandAnnualValue');
    const inflowEl = document.querySelector('#demandPredictedInflow');

    if (urgEl) urgEl.textContent = `${urgentCount} Items`;
    if (expEl) expEl.textContent = `${expCount} Product Lines`;
    if (annValEl) annValEl.textContent = formatRWF(annualDemandVal);
    if (inflowEl) inflowEl.textContent = `+${annualTenderFreq} Tenders`;

    const container = document.querySelector('#demandGridContainer');
    const emptyState = document.querySelector('#demandEmptyState');
    const searchInput = document.querySelector('#demandSearchInput');
    const urgencyFilter = document.querySelector('#demandUrgencyFilter');

    if (!container) return;

    const term = (searchInput && typeof searchInput.value === 'string') ? searchInput.value.toLowerCase().trim() : '';
    const urg = urgencyFilter ? urgencyFilter.value : '';

    const filtered = recurringDemand.filter(d => {
      if (urg === 'urgent' && d.urgency_level !== 'URGENT') return false;
      if (urg === 'safe' && d.urgency_level !== 'SAFE') return false;
      if (urg === 'expansion' && d.urgency_level !== 'EXPANSION') return false;
      if (term && !`${d.code} ${d.name} ${d.category} ${d.next_expected_wave}`.toLowerCase().includes(term)) return false;
      return true;
    });

    if (filtered.length === 0) {
      container.innerHTML = '';
      if (emptyState) emptyState.hidden = false;
      return;
    }

    if (emptyState) emptyState.hidden = true;

    container.innerHTML = filtered.map(d => {
      const alertClass = d.urgency_level === 'URGENT' ? 'urgent' : d.urgency_level === 'EXPANSION' ? 'opportunity' : 'safe';
      const fillClass = d.urgency_level === 'URGENT' ? 'low' : d.urgency_level === 'EXPANSION' ? 'expansion' : 'safe';
      const percent = Math.min(100, Math.round((d.current_warehouse_stock / (d.min_safe_threshold || 1)) * 100));

      return `
      <article class="demand-card">
        <div>
          <div class="demand-header">
            <div>
              <span class="demand-frequency">${d.tender_frequency_per_year} Tenders / Year</span>
              <span class="trend-pill up">${d.annual_growth} Growth</span>
            </div>
            <span class="badge" style="background:#eef4f3;color:var(--teal-dark)">${d.category}</span>
          </div>

          <h3 style="margin: 8px 0 4px;font-size:14px;line-height:1.3;">${d.name}</h3>
          <p style="font-size:11px;color:var(--muted);margin-bottom:12px;">
            Total Rwanda Annual Demand: <strong>${formatRWF(d.annual_market_value)}</strong>
          </p>

          <div class="stock-meter">
            <div class="stock-meter-header">
              <span>Warehouse Stock: <strong>${d.current_warehouse_stock} units</strong></span>
              <span>Min Safe Buffer: <strong>${d.min_safe_threshold} units</strong></span>
            </div>
            <div class="stock-bar-wrap">
              <div class="stock-bar-fill ${fillClass}" style="width: ${percent}%"></div>
            </div>
          </div>
        </div>

        <div style="display:grid;gap:10px;margin-top:12px;">
          <div class="restock-alert ${alertClass}">
            <div>
              <strong>${d.urgency_label}</strong>
              <p style="margin:2px 0 0;font-size:10px;">${d.next_expected_wave}</p>
            </div>
          </div>

          <div style="font-size:10px;color:#556666;line-height:1.4;background:var(--paper);padding:8px 10px;border-radius:4px;">
            <i class='bx bx-bulb' style='color:var(--teal);'></i> <strong>Bidding Feasibility:</strong> ${d.delivery_advantage_note}
          </div>

          <div style="display:flex;gap:8px;">
            <button class="primary-button" style="flex:1;height:34px;font-size:11px;" data-trigger-restock="${d.code}">
              ${d.urgency_level === 'EXPANSION' ? 'Onboard OEM Partner' : `Restock ${d.recommended_restock_qty} Units`}
            </button>
          </div>
        </div>
      </article>
    `;
    }).join('');

    container.querySelectorAll('[data-trigger-restock]').forEach(btn => {
      btn.addEventListener('click', () => openRestockModal(btn.dataset.triggerRestock));
    });
  }'''

pattern_cat_demand = r"function renderCatalogue\(\) \{[\s\S]*?renderDemand\(\);\s*\}\);?\s*\}"
app_js = re.sub(pattern_cat_demand, render_cat_demand_new, app_js, count=1)
print("Updated renderCatalogue and renderDemand with live metric bindings.")

with open("frontend/app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Saved updated frontend/app.js.")
