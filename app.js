/**
 * CompGraphRAG — Enterprise Compliance Intelligence Platform
 * Complete Interactive JavaScript Engine
 */

// ════════════════════════════════════════════
// DATA
// ════════════════════════════════════════════

// ─── Two-output scoring design (commit 08cfd81) ─────────────────────────────
// rankingScore: unbounded base × (1 + 0.4 × grounding_ratio) — used for argmax
//               path selection only. NOT a probability.
// retrievalConf: sigma(z) of top-path base_score within candidate distribution.
//               Always in (0,1). Fed to conformal predictor and ECE.
//               Old grounded_score (min-clamped) pushed 17/24 queries to 1.0;
//               retrievalConf values below reflect real sigma-z distribution.
// ─────────────────────────────────────────────────────────────────────────────
const SCENARIOS = {
  "Q2-HIPAA-2HOP": {
    id: "Q2-HIPAA-2HOP",
    question: "Can a Covered Entity disclose PHI to a cloud vendor without an executed Business Associate Agreement?",
    hopCount: 2,
    determination: "NON-COMPLIANT",
    nodes: [
      { id: "CoveredEntity_A", label: "CoveredEntity_A", type: "Role" },
      { id: "CloudVendor_B",   label: "CloudVendor_B",   type: "Role" },
      { id: "BAA_Document",    label: "BAA_Document",    type: "Obligation" }
    ],
    edges: [
      { source: "CoveredEntity_A", target: "CloudVendor_B", relation: "disclosesPHITo",  confidence: 1.0 },
      { source: "CloudVendor_B",   target: "BAA_Document",  relation: "lacksAgreement",  confidence: 1.0 }
    ],
    triggeredRules: [{ rule_id: "RULE-HIPAA-BAA-REQUIRED", recommendation: "NON-COMPLIANT", finding: "PHI disclosed to Business Associate without executed BAA document." }],
    nlWalk: "Step 1: [CoveredEntity_A] --(disclosesPHITo)--> [CloudVendor_B]\nStep 2: [CloudVendor_B] --(lacksAgreement)--> [BAA_Document]",
    conformalSet: ["NON-COMPLIANT"],
    requiresAudit: false,
    hybridScores: { dense: 0.82, graph: 0.95, auth: 1.0, rankingScore: 1.023 },
    retrievalConf: 0.8819   // sigma(z) — bounded (0,1), not trivially 1.0
  },
  "Q3-HIPAA-3HOP": {
    id: "Q3-HIPAA-3HOP",
    question: "If a research project accesses de-identified data via a workforce member under an IRB waiver, does it violate the minimum necessary standard?",
    hopCount: 3,
    determination: "COMPLIANT",
    nodes: [
      { id: "ResearchProject_X", label: "ResearchProject_X", type: "Role" },
      { id: "DeIdentifiedPHI",   label: "DeIdentifiedPHI",   type: "DataType" },
      { id: "IRB_Waiver",        label: "IRB_Waiver",        type: "Exception" },
      { id: "MinNecessary",      label: "MinNecessary",      type: "Obligation" }
    ],
    edges: [
      { source: "ResearchProject_X", target: "DeIdentifiedPHI", relation: "usesData",          confidence: 0.95 },
      { source: "DeIdentifiedPHI",   target: "IRB_Waiver",      relation: "governedBy",         confidence: 1.0 },
      { source: "IRB_Waiver",        target: "MinNecessary",    relation: "satisfiesStandard",  confidence: 1.0 }
    ],
    triggeredRules: [{ rule_id: "RULE-HIPAA-TPO-EXCEPTION", recommendation: "COMPLIANT", finding: "Disclosure satisfies statutory IRB research exception requirements." }],
    nlWalk: "Step 1: [ResearchProject_X] --(usesData)--> [DeIdentifiedPHI]\nStep 2: [DeIdentifiedPHI] --(governedBy)--> [IRB_Waiver]\nStep 3: [IRB_Waiver] --(satisfiesStandard)--> [MinNecessary]",
    conformalSet: ["COMPLIANT"],
    requiresAudit: false,
    hybridScores: { dense: 0.78, graph: 0.98, auth: 1.0, rankingScore: 1.092 },
    retrievalConf: 0.8636   // sigma(z)
  },
  "Q1-HIPAA-1HOP": {
    id: "Q1-HIPAA-1HOP",
    question: "Does disclosure of PHI for patient treatment require patient authorization under 45 CFR 164.506?",
    hopCount: 1,
    determination: "COMPLIANT",
    nodes: [
      { id: "PHI_Disclosure", label: "PHI_Disclosure", type: "DataType" },
      { id: "TPO_Exception",  label: "TPO_Exception",  type: "Exception" }
    ],
    edges: [
      { source: "PHI_Disclosure", target: "TPO_Exception", relation: "subjectToException", confidence: 1.0 }
    ],
    triggeredRules: [{ rule_id: "RULE-HIPAA-TPO-EXCEPTION", recommendation: "COMPLIANT", finding: "Disclosure permitted under §164.506 Treatment exception." }],
    nlWalk: "Step 1: [PHI_Disclosure] --(subjectToException)--> [TPO_Exception]",
    conformalSet: ["COMPLIANT"],
    requiresAudit: false,
    hybridScores: { dense: 0.91, graph: 1.0, auth: 1.0, rankingScore: 1.274 },
    retrievalConf: 0.9136   // sigma(z) — Q03 mapped; high confidence, decisive winner
  },
  "Q6-HIPAA-3HOP": {
    id: "Q6-HIPAA-3HOP",
    question: "Does transmitting unencrypted PHI over public Wi-Fi by a subcontractor without technical safeguards breach the Security Rule?",
    hopCount: 3,
    determination: "NON-COMPLIANT",
    nodes: [
      { id: "Subcontractor_C", label: "Subcontractor_C", type: "Role" },
      { id: "UnencryptedPHI",  label: "UnencryptedPHI",  type: "DataType" },
      { id: "PublicWiFi",      label: "PublicWiFi",      type: "Incident" },
      { id: "SecurityRule",    label: "SecurityRule",    type: "Rule" }
    ],
    edges: [
      { source: "Subcontractor_C", target: "UnencryptedPHI", relation: "transmitsData",     confidence: 1.0 },
      { source: "UnencryptedPHI",  target: "PublicWiFi",     relation: "traversesNetwork",  confidence: 1.0 },
      { source: "PublicWiFi",      target: "SecurityRule",   relation: "violatesSafeguard", confidence: 1.0 }
    ],
    triggeredRules: [{ rule_id: "RULE-HIPAA-MIN-NECESSARY", recommendation: "NON-COMPLIANT", finding: "Transmission violates §164.312 Technical Safeguards requirements." }],
    nlWalk: "Step 1: [Subcontractor_C] --(transmitsData)--> [UnencryptedPHI]\nStep 2: [UnencryptedPHI] --(traversesNetwork)--> [PublicWiFi]\nStep 3: [PublicWiFi] --(violatesSafeguard)--> [SecurityRule]",
    conformalSet: ["NON-COMPLIANT"],
    requiresAudit: false,
    hybridScores: { dense: 0.74, graph: 0.96, auth: 1.0, rankingScore: 1.035 },
    retrievalConf: 0.8438   // sigma(z)
  }
};

// Node colors — muted ink palette, single amber accent
// Avoids the neon purple/cyan AI-design tell
const NODE_COLORS = {
  Role:       { fill: '#18181b', stroke: '#d4953a', text: '#e8b872' },
  DataType:   { fill: '#16161a', stroke: '#7b80c0', text: '#a5a8d8' },
  Exception:  { fill: '#141a16', stroke: '#4d9b6b', text: '#7dc49a' },
  Obligation: { fill: '#1c1810', stroke: '#92672b', text: '#d4953a' },
  Incident:   { fill: '#1a1212', stroke: '#b45454', text: '#d98282' },
  Rule:       { fill: '#1a1212', stroke: '#8c6060', text: '#c09090' }
};

// ════════════════════════════════════════════
// STATE
// ════════════════════════════════════════════

let currentKey = "Q2-HIPAA-2HOP";
let showLabels = true;
let currentAuditResult = null;
let heroAnimFrame = null;
let heroNodes = [];
let heroEdges = [];
let particles = [];
let graphNodes = [];
let graphAnimProgress = 0;
let graphAnimRunning = false;

// ════════════════════════════════════════════
// NAV & CLOCK
// ════════════════════════════════════════════

function navClick(el, sectionId) {
  event.preventDefault();
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
}

// ─── Mobile hamburger ───────────────────────────────────
function toggleMobileMenu() {
  const btn    = document.getElementById('hamburgerBtn');
  const drawer = document.getElementById('mobileNavDrawer');
  const isOpen = drawer.classList.toggle('open');
  btn.classList.toggle('open', isOpen);
  // Prevent body scroll when drawer is open
  document.body.style.overflow = isOpen ? 'hidden' : '';
}

function mobileNavClick(sectionId) {
  // Close drawer first
  const btn    = document.getElementById('hamburgerBtn');
  const drawer = document.getElementById('mobileNavDrawer');
  drawer.classList.remove('open');
  btn.classList.remove('open');
  document.body.style.overflow = '';
  // Then scroll (slight delay so animation feels smooth)
  setTimeout(() => {
    const target = document.getElementById(sectionId);
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  }, 260);
}

// Close drawer when tapping outside
document.addEventListener('click', (e) => {
  const drawer = document.getElementById('mobileNavDrawer');
  const btn    = document.getElementById('hamburgerBtn');
  if (!drawer || !btn) return;
  if (drawer.classList.contains('open') &&
      !drawer.contains(e.target) &&
      !btn.contains(e.target)) {
    drawer.classList.remove('open');
    btn.classList.remove('open');
    document.body.style.overflow = '';
  }
});
// ────────────────────────────────────────────────────────

function updateClock() {
  const el = document.getElementById('navClock');
  if (!el) return;
  const now = new Date();
  const hh = String(now.getHours()).padStart(2,'0');
  const mm = String(now.getMinutes()).padStart(2,'0');
  const ss = String(now.getSeconds()).padStart(2,'0');
  el.textContent = `${hh}:${mm}:${ss}`;
}

// Scroll-based navbar
window.addEventListener('scroll', () => {
  const nav = document.getElementById('navbar');
  if (window.scrollY > 20) nav.classList.add('scrolled');
  else nav.classList.remove('scrolled');

  // Close mobile drawer on scroll
  const drawer = document.getElementById('mobileNavDrawer');
  const btn    = document.getElementById('hamburgerBtn');
  if (drawer && drawer.classList.contains('open') && window.scrollY > 80) {
    drawer.classList.remove('open');
    btn.classList.remove('open');
    document.body.style.overflow = '';
  }

  // Highlight active nav link
  const sections = ['section-hero','section-how','section-demo','section-metrics','section-architecture','section-research'];
  const links = document.querySelectorAll('.nav-link');
  let current = '';
  sections.forEach((id, i) => {
    const el = document.getElementById(id);
    if (el && el.getBoundingClientRect().top <= 100) current = i;
  });
  links.forEach((l, i) => {
    if (i === current) l.classList.add('active');
    else l.classList.remove('active');
  });
});

// ════════════════════════════════════════════
// PARTICLE BACKGROUND
// ════════════════════════════════════════════

function initParticles() {
  // Particle canvas is hidden via CSS — no-op
  // The hero knowledge graph provides sufficient visual interest
}

// ════════════════════════════════════════════
// HERO GRAPH ANIMATION
// ════════════════════════════════════════════

function initHeroGraph() {
  const canvas = document.getElementById('heroGraphCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.parentElement.clientWidth;
    const h = canvas.parentElement.clientHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.scale(dpr, dpr);
    return { w, h };
  }

  let { w, h } = resize();
  window.addEventListener('resize', () => { const r = resize(); w = r.w; h = r.h; });

  // Create animated hero nodes — amber/slate palette, no neon
  const typeColors = ['#d4953a','#7b80c0','#4d9b6b','#92672b','#8c6060','#d4953a','#7b80c0','#4d9b6b','#92672b'];
  const labels = ['CoveredEntity','PHI_Disclosure','BAA_Document','TPO_Exception','IRB_Waiver','MinNecessary','SecurityRule','CloudVendor','DeIdentifiedPHI'];

  heroNodes = labels.map((l, i) => ({
    label: l,
    color: typeColors[i % typeColors.length],
    x: (0.15 + (i % 3) * 0.35) * (w || 600),
    y: (0.2 + Math.floor(i / 3) * 0.3) * (h || 400),
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    r: 28 + Math.random() * 10,
    pulse: Math.random() * Math.PI * 2
  }));

  heroEdges = [];
  for (let i = 0; i < heroNodes.length - 1; i++) {
    if (Math.random() > 0.3) {
      heroEdges.push({ from: i, to: i + 1 });
    }
  }
  heroEdges.push({ from: 0, to: 3 }, { from: 2, to: 5 }, { from: 6, to: 1 });

  let t = 0;

  function draw() {
    ctx.clearRect(0, 0, w, h);
    t += 0.01;

    // Subtle grid
    ctx.strokeStyle = 'rgba(99,102,241,0.04)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
      ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke();
    }

    // Edges — simple amber lines, moving dash offset
    heroEdges.forEach(e => {
      const n1 = heroNodes[e.from], n2 = heroNodes[e.to];
      ctx.beginPath();
      ctx.moveTo(n1.x, n1.y);
      ctx.lineTo(n2.x, n2.y);
      ctx.strokeStyle = 'rgba(212,149,58,0.22)';
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 6]);
      ctx.lineDashOffset = -t * 10;
      ctx.stroke();
      ctx.setLineDash([]);
    });

    // Nodes — clean circles, amber accent stroke
    heroNodes.forEach(node => {
      const pulse = Math.sin(t * 1.2 + node.pulse) * 2;  // subtle, not dramatic

      // Node circle — dark fill, muted stroke
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.r + pulse, 0, Math.PI * 2);
      ctx.fillStyle = '#111113';
      ctx.fill();
      ctx.strokeStyle = node.color;
      ctx.lineWidth = 1;
      ctx.stroke();

      // Label
      ctx.fillStyle = node.color;
      ctx.font = '500 8px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      const shortLabel = node.label.length > 12 ? node.label.slice(0, 11) + '…' : node.label;
      ctx.fillText(shortLabel, node.x, node.y);

      // Float animation
      node.x += node.vx;
      node.y += node.vy;

      // Soft boundary bounce
      const margin = node.r + 10;
      if (node.x < margin || node.x > w - margin) node.vx *= -1;
      if (node.y < margin || node.y > h - margin) node.vy *= -1;

      node.x = Math.max(margin, Math.min(w - margin, node.x));
      node.y = Math.max(margin, Math.min(h - margin, node.y));
    });

    heroAnimFrame = requestAnimationFrame(draw);
  }

  draw();
}

// ════════════════════════════════════════════
// COUNTER ANIMATIONS
// ════════════════════════════════════════════

function animateCounters(selector) {
  const els = document.querySelectorAll(selector);
  els.forEach(el => {
    const target = parseFloat(el.dataset.target);
    const suffix = el.dataset.suffix || '';
    const duration = 1800;
    const start = performance.now();

    function step(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = target * ease;
      el.textContent = (current % 1 === 0 || current > 99) ? current.toFixed(1) + suffix : current.toFixed(2) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  });
}

function setupIntersectionObserver() {
  const heroStats = document.querySelectorAll('.hero-stat-val');
  const kpiVals = document.querySelectorAll('.animate-counter');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        entry.target.dataset.animated = 'true';
        const targetStr = entry.target.dataset.target || '0';
        const target = parseFloat(targetStr);
        const dec = targetStr.includes('.') ? targetStr.split('.')[1].length : 0;
        const suffix = entry.target.dataset.suffix || '';
        const duration = 1600;
        const start = performance.now();

        function step(now) {
          const elapsed = now - start;
          const progress = Math.min(elapsed / duration, 1);
          const ease = 1 - Math.pow(1 - progress, 3);
          const current = target * ease;
          const valFormatted = current.toFixed(dec);
          if (entry.target.classList.contains('hero-stat-val')) {
            entry.target.textContent = valFormatted;
          } else {
            entry.target.textContent = valFormatted + suffix;
          }
          if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      }
    });
  }, { threshold: 0.3 });

  heroStats.forEach(el => observer.observe(el));
  kpiVals.forEach(el => observer.observe(el));

  // Entity linker bars
  const elBars = document.querySelectorAll('.el-bar-fill');
  const barObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        entry.target.dataset.animated = 'true';
        const w = parseFloat(entry.target.dataset.w);
        setTimeout(() => {
          entry.target.style.width = w + '%';
        }, 200);
      }
    });
  }, { threshold: 0.3 });

  elBars.forEach(el => barObserver.observe(el));
}

// ════════════════════════════════════════════
// SCENARIO SELECTION & DEMO
// ════════════════════════════════════════════

function selectScenario(el, key) {
  document.querySelectorAll('.scenario-item').forEach(s => s.classList.remove('active'));
  el.classList.add('active');
  currentKey = key;
  const sc = SCENARIOS[key];
  document.getElementById('queryText').textContent = sc.question;
  document.getElementById('hopBadgeDisplay').textContent = sc.hopCount + '-HOP';
  document.getElementById('graphFooterText').textContent =
    `REF: HIPAA 45 CFR · NODES: ${sc.nodes.length} · EDGES: ${sc.edges.length} · DECAY λ=0.85`;

  // Reset pipeline
  resetPipelineUI();
  // Render graph for new scenario
  renderMainGraph(sc);
}

function resetPipelineUI() {
  ['pt-1','pt-2','pt-3','pt-4'].forEach((id, i) => {
    const el = document.getElementById(id);
    el.classList.remove('active','done');
    const state = document.getElementById('pts-' + (i+1));
    if (state) state.textContent = 'IDLE';
  });

  const pStatus = document.getElementById('pipelineStatus');
  pStatus.textContent = 'READY';
  pStatus.className = 'pipeline-status';

  // Reset outputs
  document.getElementById('detLabel').textContent = 'AWAITING PIPELINE';
  document.getElementById('detState').className = 'det-state';
  document.getElementById('detState').style.textAlign = 'center';
  document.getElementById('detState').style.padding = '1rem 0';
  document.getElementById('detState').innerHTML = '<div style="font-size:2rem;margin-bottom:0.3rem;">◉</div><div id="detLabel" style="font-size:0.85rem;color:#64748b;font-family:Inter,sans-serif;">AWAITING PIPELINE</div>';
  document.getElementById('detScores').style.display = 'none';

  document.getElementById('conformalSet').textContent = 'Pending…';
  document.getElementById('conformalAudit').textContent = '—';

  document.getElementById('nlWalkDisplay').innerHTML = '<div class="nlwalk-placeholder">Execute the pipeline to view the natural language reasoning path walk…</div>';
  document.getElementById('auditJson').textContent = '{ "status": "IDLE", "system": "COMPGRAPHRAG_V1" }';
  document.getElementById('exportBtn').disabled = true;
  currentAuditResult = null;
}

function runAuditPipeline() {
  const sc = SCENARIOS[currentKey];
  const btn = document.getElementById('executeBtn');
  btn.disabled = true;
  btn.classList.add('running');

  const pStatus = document.getElementById('pipelineStatus');
  pStatus.textContent = 'RUNNING';
  pStatus.className = 'pipeline-status running';

  // Reset all stages
  ['pt-1','pt-2','pt-3','pt-4'].forEach((id, i) => {
    const el = document.getElementById(id);
    el.classList.remove('active','done');
    const state = document.getElementById('pts-' + (i+1));
    if (state) state.textContent = 'IDLE';
  });

  const stages = ['pt-1','pt-2','pt-3','pt-4'];
  const stageLabels = ['RUNNING…','CHECKING…','CALIBRATING…','GENERATING…'];
  const doneLbls = ['✓ DONE','✓ DONE','✓ DONE','✓ DONE'];
  let step = 0;

  function runStep() {
    if (step > 0) {
      // Mark previous done
      const prev = document.getElementById(stages[step-1]);
      prev.classList.remove('active');
      prev.classList.add('done');
      const prevState = document.getElementById('pts-' + step);
      if (prevState) prevState.textContent = '✓ DONE';
    }

    if (step >= stages.length) {
      // Done
      pStatus.textContent = 'COMPLETE';
      pStatus.className = 'pipeline-status done';
      btn.disabled = false;
      btn.classList.remove('running');
      displayAuditResult(sc);
      return;
    }

    const stageEl = document.getElementById(stages[step]);
    stageEl.classList.add('active');
    const stateEl = document.getElementById('pts-' + (step+1));
    if (stateEl) stateEl.textContent = stageLabels[step];

    step++;
    setTimeout(runStep, 500 + Math.random() * 300);
  }

  runStep();
}

function displayAuditResult(sc) {
  // Determination badge
  const detState = document.getElementById('detState');
  const isPass = sc.determination === 'COMPLIANT';

  detState.className = 'det-state ' + (isPass ? 'pass' : 'fail');
  detState.style.textAlign = 'center';
  detState.style.padding = '1rem';

  const verdictColor = isPass ? '#34d399' : '#f87171';
  const verdictIcon = isPass ? '✓' : '✗';
  detState.innerHTML = `
    <div style="font-size:2.5rem;margin-bottom:0.5rem;">${verdictIcon}</div>
    <div class="det-verdict ${isPass?'pass-text':'fail-text'}">${sc.determination}</div>
    <div style="font-size:0.72rem;color:#64748b;margin-top:0.3rem;font-family:'JetBrains Mono',monospace;">
      ${sc.triggeredRules[0].rule_id}
    </div>
  `;

  // Scores — two-output design: ranking score (unbounded) + retrieval confidence (sigma-z)
  const detScores = document.getElementById('detScores');
  detScores.style.display = 'flex';
  document.getElementById('sc-dense').textContent = sc.hybridScores.dense.toFixed(3);
  document.getElementById('sc-graph').textContent = sc.hybridScores.graph.toFixed(3);
  document.getElementById('sc-auth').textContent  = sc.hybridScores.auth.toFixed(3);
  // rankingScore is unbounded (>1.0 possible) — used for argmax path selection only
  document.getElementById('sc-final').textContent = (sc.hybridScores.rankingScore !== undefined
    ? sc.hybridScores.rankingScore.toFixed(3)
    : (sc.hybridScores.final || 0).toFixed(3));
  // retrieval_confidence: sigma(z) — bounded (0,1), fed to conformal + ECE
  const confEl = document.getElementById('sc-conf');
  if (confEl) confEl.textContent = sc.retrievalConf !== undefined ? sc.retrievalConf.toFixed(4) : '—';

  // Conformal
  document.getElementById('conformalSet').textContent = '[' + sc.conformalSet.join(', ') + ']';
  const auditEl = document.getElementById('conformalAudit');
  auditEl.textContent = sc.requiresAudit ? '⚠ YES — Route to Human' : '✓ No — Unambiguous';
  auditEl.style.color = sc.requiresAudit ? '#f59e0b' : '#34d399';

  // NL Walk
  const nlEl = document.getElementById('nlWalkDisplay');
  const steps = sc.nlWalk.split('\n');
  nlEl.innerHTML = steps.map(s => {
    // amber for edge labels, not indigo
    const formatted = s.replace(/\[(.*?)\]/g, '<strong>[$1]</strong>').replace(/--(.*?)-->/g, '<span style="color:#d4953a;">--($1)--></span>');
    return `<div class="nlwalk-step" style="margin-bottom:0.4rem;">${formatted}</div>`;
  }).join('');

  // Build JSON certificate — two-output design (commit 08cfd81)
  currentAuditResult = {
    query_id: sc.id,
    timestamp: new Date().toISOString(),
    question: sc.question,
    hop_complexity: sc.hopCount,
    retrieval_scores: {
      dense_similarity:  sc.hybridScores.dense,
      graph_path_score:  sc.hybridScores.graph,
      authority_score:   sc.hybridScores.auth,
      // ranking_score: unbounded — used ONLY for argmax path selection, NOT a probability
      ranking_score:     sc.hybridScores.rankingScore !== undefined
                           ? sc.hybridScores.rankingScore
                           : sc.hybridScores.final
    },
    // retrieval_confidence: sigma(z) of top-path base_score within candidate distribution.
    // Always in (0,1). Fed to conformal predictor and ECE. Replaces the former
    // grounded_score which was min(1.0,...)-clamped and pushed 17/24 queries to exactly 1.0.
    retrieval_confidence: sc.retrievalConf !== undefined ? sc.retrievalConf : null,
    triggered_rules: sc.triggeredRules,
    subgraph_pi: {
      nodes: sc.nodes.map(n => n.id),
      edges: sc.edges
    },
    conformal_uncertainty: {
      alpha: 0.10,
      target_coverage: 0.90,
      q_hat: 0.2578,     // calibrated on 12-item split; sigma-z non-conformity scores
      confidence_set: sc.conformalSet,
      requires_human_audit: sc.requiresAudit
    },
    determination: sc.determination
  };

  document.getElementById('auditJson').textContent = JSON.stringify(currentAuditResult, null, 2);
  document.getElementById('exportBtn').disabled = false;

  // Re-render graph with animation
  renderMainGraph(sc, true);
}

function exportAuditJson() {
  if (!currentAuditResult) return;
  const blob = new Blob([JSON.stringify(currentAuditResult, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `compgraphrag_audit_${currentKey}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ════════════════════════════════════════════
// MAIN GRAPH CANVAS RENDERER
// ════════════════════════════════════════════

let mainAnimFrame = null;
let nodePositions = {};
let graphAnimTime = 0;

function renderMainGraph(sc, withAnimation) {
  const canvas = document.getElementById('mainGraphCanvas');
  if (!canvas) return;
  if (mainAnimFrame) cancelAnimationFrame(mainAnimFrame);

  const wrap = canvas.parentElement;
  const dpr = window.devicePixelRatio || 1;
  const W = Math.max(wrap.clientWidth, 200);   // guard against zero-width on mobile
  const H = Math.max(wrap.clientHeight || 380, 200);
  canvas.width  = W * dpr;
  canvas.height = H * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  // Responsive sizes — smaller nodes on narrow screens
  const isMobile   = W < 500;
  const nodeRadius  = isMobile ? 22 : 32;
  const layoutMargin = isMobile ? 40 : 80;
  const yWobble     = isMobile ? 18 : 30;

  // Layout nodes
  const n = sc.nodes.length;
  const cx = W / 2, cy = H / 2;
  const radius = Math.min(W, H) * 0.3;

  nodePositions = {};
  sc.nodes.forEach((node, i) => {
    if (n === 1) {
      nodePositions[node.id] = { x: cx, y: cy };
    } else if (n === 2) {
      nodePositions[node.id] = { x: cx + (i === 0 ? -radius*0.8 : radius*0.8), y: cy };
    } else if (n === 3) {
      const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
      nodePositions[node.id] = { x: cx + Math.cos(angle) * radius, y: cy + Math.sin(angle) * radius * 0.7 };
    } else {
      const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
      nodePositions[node.id] = { x: cx + Math.cos(angle) * radius, y: cy + Math.sin(angle) * radius };
    }
  });

  // Linear chain layout for ≤4 nodes (clearer on mobile)
  if (n <= 4) {
    sc.nodes.forEach((node, i) => {
      const spacing = (W - layoutMargin * 2) / Math.max(n - 1, 1);
      nodePositions[node.id] = {
        x: n === 1 ? cx : layoutMargin + i * spacing,
        y: cy + (i % 2 === 0 ? -yWobble : yWobble)
      };
    });
  }

  graphAnimTime = 0;
  const totalDuration = withAnimation ? 60 : 0; // frames

  function drawFrame() {
    graphAnimTime++;
    const progress = withAnimation ? Math.min(graphAnimTime / totalDuration, 1) : 1;
    const ease = 1 - Math.pow(1 - progress, 3);

    ctx.clearRect(0, 0, W, H);

    // Subtle grid — ink palette, not neon
    ctx.strokeStyle = 'rgba(255,255,255,0.035)';
    ctx.lineWidth = 1;
    for (let x = 0; x < W; x += 40) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
    for (let y = 0; y < H; y += 40) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }

    // Draw edges
    sc.edges.forEach(edge => {
      const src = nodePositions[edge.source];
      const tgt = nodePositions[edge.target];
      if (!src || !tgt) return;

      // Interpolate draw length
      const dx = (tgt.x - src.x) * ease;
      const dy = (tgt.y - src.y) * ease;

      // Edge gradient
      const grad = ctx.createLinearGradient(src.x, src.y, src.x + dx, src.y + dy);
      const srcColor = NODE_COLORS[SCENARIOS[currentKey].nodes.find(n => n.id === edge.source)?.type || 'Role'].stroke;
      const tgtColor = NODE_COLORS[SCENARIOS[currentKey].nodes.find(n => n.id === edge.target)?.type || 'Role'].stroke;
      grad.addColorStop(0, srcColor + 'aa');
      grad.addColorStop(1, tgtColor + 'aa');

      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(src.x + dx, src.y + dy);
      ctx.strokeStyle = grad;
      ctx.lineWidth = 2;
      ctx.shadowColor = srcColor;
      ctx.shadowBlur = 6;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Arrowhead at destination
      if (progress > 0.8) {
        const alpha = (progress - 0.8) / 0.2;
        const angle = Math.atan2(dy, dx);
        const ax = src.x + dx, ay = src.y + dy;
        const arLen = 10;
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(ax - arLen * Math.cos(angle - 0.4), ay - arLen * Math.sin(angle - 0.4));
        ctx.lineTo(ax - arLen * Math.cos(angle + 0.4), ay - arLen * Math.sin(angle + 0.4));
        ctx.closePath();
        ctx.fillStyle = tgtColor;
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      // Edge label
      if (showLabels && progress > 0.6) {
        const alpha = Math.min((progress - 0.6) / 0.4, 1);
        const midX = src.x + dx * 0.5;
        const midY = src.y + dy * 0.5 - 14;
        ctx.globalAlpha = alpha;

        const lblText = edge.relation;
        ctx.font = '600 10px "JetBrains Mono", monospace';
        const tw = ctx.measureText(lblText).width;

        // Label background
        ctx.fillStyle = 'rgba(3,7,18,0.85)';
        ctx.strokeStyle = srcColor + '60';
        ctx.lineWidth = 1;
        ctx.beginPath();
        const pad = 4;
        ctx.roundRect(midX - tw/2 - pad, midY - 8, tw + pad*2, 16, 3);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = srcColor;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(lblText, midX, midY);
        ctx.globalAlpha = 1;
      }
    });

    // Draw nodes
    sc.nodes.forEach((node, i) => {
      const pos = nodePositions[node.id];
      if (!pos) return;
      const colors = NODE_COLORS[node.type] || NODE_COLORS.Role;
      const nodeProgress = withAnimation ? Math.max(0, Math.min(1, (graphAnimTime - i * 8) / 20)) : 1;
      if (nodeProgress <= 0) return;

      // Use the responsive nodeRadius set at function scope
      const nodeR   = nodeRadius * nodeProgress;
      const pulse   = Math.sin(graphAnimTime * 0.06 + i) * (isMobile ? 1 : 2);

      // Draw enter opacity fade-in (no glowing halo)
      ctx.globalAlpha = nodeProgress;

      // Node body — dark fill, colored stroke, no glow shadow
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, nodeR + pulse, 0, Math.PI * 2);
      ctx.fillStyle = colors.fill;
      ctx.fill();
      ctx.strokeStyle = colors.stroke;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Type label (tiny, above node) — desktop only
      if (!isMobile) {
        ctx.font = '700 7px "JetBrains Mono", monospace';
        ctx.fillStyle = colors.stroke + '88';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText('[' + node.type.toUpperCase() + ']', pos.x, pos.y - nodeR - 4);
      }

      // Main label below node
      const labelFontSize = isMobile ? 8 : 10;
      ctx.font = `600 ${labelFontSize}px Inter, sans-serif`;
      ctx.fillStyle = colors.text;
      ctx.textBaseline = 'top';
      const maxChars = isMobile ? 9 : 14;
      const shortId  = node.id.length > maxChars ? node.id.slice(0, maxChars - 1) + '…' : node.id;
      ctx.fillText(shortId, pos.x, pos.y + nodeR + 5);

      // Confidence score inside node
      if (sc.edges.some(e => e.source === node.id || e.target === node.id)) {
        const edge = sc.edges.find(e => e.source === node.id || e.target === node.id);
        if (edge) {
          const confFontSize = isMobile ? 7 : 9;
          ctx.font = `500 ${confFontSize}px "JetBrains Mono", monospace`;
          ctx.fillStyle = colors.text + 'cc';
          ctx.textBaseline = 'middle';
          ctx.fillText(edge.confidence.toFixed(2), pos.x, pos.y);
        }
      }
    });

    ctx.globalAlpha = 1; // reset after node opacity animations

    mainAnimFrame = requestAnimationFrame(drawFrame);
  }

  drawFrame();
}

function resetGraph() {
  renderMainGraph(SCENARIOS[currentKey], true);
}

function toggleLabels() {
  showLabels = !showLabels;
  const btn = document.getElementById('labelToggle');
  btn.textContent = showLabels ? '⊞ Labels' : '⊟ Labels';
  renderMainGraph(SCENARIOS[currentKey], false);
}

function animateGraph() {
  renderMainGraph(SCENARIOS[currentKey], true);
}

// ════════════════════════════════════════════
// CHARTS
// ════════════════════════════════════════════

function drawHopChart() {
  const canvas = document.getElementById('hopChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.clientWidth || 400;
  canvas.width = W;
  canvas.height = 240;
  ctx.clearRect(0, 0, W, 240);

  const hops = ['1-HOP', '2-HOP', '3-HOP', '4-HOP'];
  const comp = [100.0, 100.0, 100.0, 100.0];
  const vect = [83.3, 66.7, 100.0, 100.0];

  const margin = { top: 20, right: 20, bottom: 40, left: 50 };
  const cW = W - margin.left - margin.right;
  const cH = 240 - margin.top - margin.bottom;

  ctx.save();
  ctx.translate(margin.left, margin.top);

  // Y grid lines & labels
  [0, 25, 50, 75, 100].forEach(v => {
    const y = cH - (v / 100) * cH;
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(cW, y); ctx.stroke();
    ctx.fillStyle = '#484f58';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(v + '%', -6, y + 4);
  });

  const barW = cW / hops.length;
  const bw = barW * 0.35;
  const gap = barW * 0.05;

  hops.forEach((h, i) => {
    const x = i * barW + barW * 0.1;

    // CompGraphRAG bar — amber, solid
    const ch = (comp[i] / 100) * cH;
    ctx.fillStyle = '#d4953a';
    ctx.beginPath();
    ctx.roundRect(x, cH - ch, bw, ch, [3, 3, 0, 0]);
    ctx.fill();

    // Vector RAG bar — muted slate
    const vh = (vect[i] / 100) * cH;
    ctx.fillStyle = '#2a2a30';
    ctx.beginPath();
    ctx.roundRect(x + bw + gap, cH - vh, bw, vh, [3, 3, 0, 0]);
    ctx.fill();

    // X label
    ctx.fillStyle = '#57534e';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(h, x + bw, cH + 15);

    // Value labels
    ctx.fillStyle = '#e8b872';
    ctx.font = '700 9px Inter, sans-serif';
    ctx.fillText(comp[i] === 100 ? '100%' : comp[i].toFixed(1) + '%', x + bw/2, cH - ch - 6);

    ctx.fillStyle = '#57534e';
    ctx.fillText(vect[i] === 100 ? '100%' : vect[i].toFixed(1) + '%', x + bw * 1.5 + gap, cH - vh - 6);
  });

  // Legend
  ctx.fillStyle = '#d4953a';
  ctx.fillRect(0, -15, 10, 8);
  ctx.fillStyle = '#a8a29e';
  ctx.font = '10px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('CompGraphRAG', 14, -8);

  ctx.fillStyle = '#2a2a30';
  ctx.fillRect(130, -15, 10, 8);
  ctx.fillStyle = '#57534e';
  ctx.fillText('Vector-RAG', 144, -8);

  ctx.restore();
}

function drawCalibChart() {
  const canvas = document.getElementById('calibChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.clientWidth || 400;
  canvas.width = W;
  canvas.height = 240;
  ctx.clearRect(0, 0, W, 240);

  const margin = { top: 20, right: 20, bottom: 40, left: 50 };
  const cW = W - margin.left - margin.right;
  const cH = 240 - margin.top - margin.bottom;

  ctx.save();
  ctx.translate(margin.left, margin.top);

  // Perfect calibration line
  ctx.strokeStyle = 'rgba(255,255,255,0.08)';
  ctx.lineWidth = 1;
  ctx.setLineDash([3, 4]);
  ctx.beginPath();
  ctx.moveTo(0, cH);
  ctx.lineTo(cW, 0);
  ctx.stroke();
  ctx.setLineDash([]);

  // Grid
  [0, 25, 50, 75, 100].forEach(v => {
    const y = cH - (v / 100) * cH;
    ctx.strokeStyle = 'rgba(255,255,255,0.04)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(cW, y); ctx.stroke();
    ctx.fillStyle = '#57534e';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(v + '%', -6, y + 4);
  });

  // Calibration curve updated for sigma(z) confidence signal (commit 08cfd81).
  // Old grounded_score clustered at ~99% confidence → near-perfect apparent calibration
  // that was artifactual (17/24 queries = exactly 1.0). New sigma(z) has genuine spread
  // [0.74, 0.95] while accuracy = 100%, producing real underconfidence: ECE = 0.1582.
  // Points: [confidence_bin_midpoint%, observed_accuracy%]
  const conformalPts = [[0,0],[74,100],[80,100],[85,100],[90,100],[95,100],[100,100]];
  const rawPts = [[0,0],[20,12],[40,38],[60,58],[80,78],[100,100]];

  function drawCurve(pts, color, isDashed) {
    ctx.beginPath();
    pts.forEach((p, i) => {
      const x = (p[0] / 100) * cW;
      const y = cH - (p[1] / 100) * cH;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = color;
    ctx.lineWidth = isDashed ? 1.5 : 2;
    if (isDashed) ctx.setLineDash([4, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    if (!isDashed) {
      pts.forEach(p => {
        const x = (p[0] / 100) * cW;
        const y = cH - (p[1] / 100) * cH;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
      });
    }
  }

  drawCurve(conformalPts, '#d4953a', false);
  drawCurve(rawPts, '#3b3935', true);

  // Labels
  ctx.fillStyle = '#57534e';
  ctx.font = '10px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('Predicted Confidence', cW / 2, cH + 25);

  // Legend
  ctx.fillStyle = '#d4953a';
  ctx.fillRect(0, -15, 14, 2);
  ctx.fillStyle = '#a8a29e';
  ctx.font = '10px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Conformal UQ', 18, -8);

  ctx.strokeStyle = '#3b3935';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([4,4]);
  ctx.beginPath(); ctx.moveTo(cW - 100, -13); ctx.lineTo(cW - 86, -13); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = '#57534e';
  ctx.textAlign = 'left';
  ctx.fillText('Raw Softmax', cW - 82, -8);

  ctx.restore();
}

// ════════════════════════════════════════════
// ARCHITECTURE TABS
// ════════════════════════════════════════════

function switchArchTab(btn, paneId) {
  document.querySelectorAll('.arch-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.arch-pane').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  const pane = document.getElementById(paneId);
  if (pane) pane.classList.add('active');
}

// ════════════════════════════════════════════
// INIT
// ════════════════════════════════════════════

window.addEventListener('DOMContentLoaded', () => {
  // Clock
  updateClock();
  setInterval(updateClock, 1000);

  // Particle background
  initParticles();

  // Hero graph
  initHeroGraph();

  // Animated counters (intersection observer)
  setupIntersectionObserver();

  // Initial scenario load
  renderMainGraph(SCENARIOS[currentKey], false);

  // Charts (wait a tick for layout)
  setTimeout(() => {
    drawHopChart();
    drawCalibChart();
  }, 300);

  window.addEventListener('resize', () => {
    drawHopChart();
    drawCalibChart();
    renderMainGraph(SCENARIOS[currentKey], false);
  });
});
