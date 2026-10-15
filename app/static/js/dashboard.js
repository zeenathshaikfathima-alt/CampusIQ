
const $ = (selector) => document.querySelector(selector);

let performanceChart, riskChart, allStudents = [];

const esc = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[ch]));

function toast(message) {
  const el = $("#toastMessage");
  if (!el) return;

  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2800);
}

async function getJSON(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }

  return response.json();
}

function scoreClass(score) {
  if (score === null || score === undefined || !Number.isFinite(Number(score))) {
    return "score-unknown";
  }

  const value = Number(score);
  return value >= 75 ? "score-good" : value >= 55 ? "score-mid" : "score-low";
}

function formatScore(score) {
  if (score === null || score === undefined || score === "") {
    return "N/A";
  }

  const value = Number(score);
  return Number.isFinite(value) ? value.toFixed(1) : "N/A";
}

function riskClass(risk) {
  const normalized = String(risk || "unknown")
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, "-");

  return `risk-${normalized}`;
}

function getCompleteness(student) {
  const value = Number(student.data_completeness);

  if (student.data_completeness === null ||
      student.data_completeness === undefined ||
      student.data_completeness === "" ||
      !Number.isFinite(value)) {
    return null;
  }

  return Math.max(0, Math.min(100, value));
}

function completenessLabel(value) {
  if (value === null) return "Not available";
  if (value >= 90) return "High";
  if (value >= 60) return "Moderate";
  return "Low";
}

async function loadDashboard() {
  const department =
    $("#departmentFilter")?.value || "All Departments";

  const query = new URLSearchParams();

  if (department !== "All Departments") {
    query.set("department", department);
  }

  try {
    const [summary, students, insights] = await Promise.all([
      getJSON(`/api/analytics/summary?${query}`),
      getJSON(`/api/students?${query}`),
      getJSON("/api/agents/insights")
    ]);

    allStudents = Array.isArray(students) ? students : [];

    renderSummary(summary);
    renderStudents(allStudents);
    renderInsights(insights);
    renderPerformance(summary.dimensions || {});
    renderRisks(summary.risk_counts || {});
    renderSegments(summary.segments || {});
    populateDepartments(summary.departments || []);
  } catch (error) {
    console.error("Dashboard loading error:", error);
    toast("Could not load dashboard data. Check the Flask server.");
  }
}

function renderSummary(data) {
  $("#totalStudents").textContent = data.total_students ?? 0;

  const average = data.average_success_score;
  $("#averageScore").textContent =
    average === null || average === undefined
      ? "N/A"
      : `${formatScore(average)}%`;

  $("#academicRisk").textContent = data.academic_high_risk ?? 0;
  $("#placementRisk").textContent = data.placement_high_risk ?? 0;
  $("#recordCount").textContent = `${data.total_students || 0} records`;
}

function renderStudents(students) {
  const tbody = $("#studentRows");
  if (!tbody) return;

  if (!students.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="empty-cell">
          No student records match these filters.
        </td>
      </tr>`;
    return;
  }

  tbody.innerHTML = students.slice(0, 12).map((student) => {
    const score = formatScore(student.success_score);
    const completeness = getCompleteness(student);

    const completenessText = completeness === null
      ? "Not available"
      : `${completeness.toFixed(1)}% (${completenessLabel(completeness)})`;

    const drivers = Array.isArray(student.risk_drivers)
      ? student.risk_drivers
      : [];

    const explanation = drivers.length
      ? drivers.join("; ")
      : "No risk drivers supplied by the API.";

    const scoreDescription = student.success_score === null ||
      student.success_score === undefined
      ? "A score cannot be calculated from the available data."
      : `Success score: ${score}/100. Data completeness: ${completenessText}.`;

    return `
      <tr>
        <td>
          <span class="student-id">${esc(student.student_id)}</span>
        </td>
        <td>${esc(student.name)}</td>
        <td>${esc(student.department)}</td>
        <td>
          <span
            class="score-chip ${scoreClass(student.success_score)}"
            title="${esc(scoreDescription)}"
          >${esc(score)}</span>
          <div class="student-data-quality">
            <small>Data: ${esc(completenessText)}</small>
          </div>
        </td>
        <td>
          <span
            class="segment-tag"
            title="${esc(student.segment)}"
          >${esc(student.segment)}</span>
        </td>
        <td>
          <span
            class="risk-badge ${riskClass(student.academic_risk)}"
            title="${esc(explanation)}"
          >${esc(student.academic_risk)}</span>
          <div class="student-data-quality">
            <small>${esc(explanation)}</small>
          </div>
        </td>
      </tr>`;
  }).join("");
}

function renderInsights(payload) {
  const root = $("#aiInsights");
  if (!root) return;

  if (!payload.insights?.length) {
    root.innerHTML = `
      <div class="empty-state">
        ${esc(payload.message || "No insights available yet.")}
      </div>`;
    return;
  }

  const iconMap = {
    academic_risk: ["red", "bi-exclamation-triangle"],
    placement_risk: ["purple", "bi-briefcase"],
    attendance: ["teal", "bi-calendar2-check"],
    data_quality: ["blue", "bi-database-check"]
  };

  root.innerHTML = payload.insights.map((item) => {
    const [color, icon] = iconMap[item.type] || iconMap.data_quality;

    return `
      <div class="insight-item">
        <span class="insight-symbol ${color}">
          <i class="bi ${icon}"></i>
        </span>
        <div>
          <strong>${esc(item.title)}</strong>
          <p>${esc(item.detail)}</p>
        </div>
      </div>`;
  }).join("");
}

function chartDefaults() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#0b2140",
        titleColor: "#fff",
        bodyColor: "#c9dcf5",
        borderColor: "#24466f",
        borderWidth: 1
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: "#8fa9cc", font: { size: 10 } },
        border: { color: "#1c3557" }
      },
      y: {
        beginAtZero: true,
        max: 100,
        grid: { color: "#18304f", drawBorder: false },
        ticks: { color: "#8fa9cc", stepSize: 20, font: { size: 10 } },
        border: { display: false }
      }
    }
  };
}

function renderPerformance(dimensions) {
  const canvas = $("#performanceChart");
  if (!canvas || typeof Chart === "undefined") return;

  const entries = Object.entries(dimensions).filter(
    ([, value]) => value !== null &&
      value !== undefined &&
      Number.isFinite(Number(value))
  );

  const labels = entries.map(([label]) => label);
  const values = entries.map(([, value]) => Number(value));

  if (performanceChart) performanceChart.destroy();

  performanceChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: [
          "#269cff", "#25d6c0", "#8b7cff",
          "#f5b94e", "#e879f9", "#3c82f6"
        ],
        borderRadius: 6,
        borderSkipped: false,
        maxBarThickness: 38
      }]
    },
    options: {
      ...chartDefaults(),
      scales: {
        ...chartDefaults().scales,
        y: {
          ...chartDefaults().scales.y,
          suggestedMax: 100
        }
      },
      plugins: {
        ...chartDefaults().plugins,
        tooltip: {
          ...chartDefaults().plugins.tooltip,
          callbacks: {
            label: (context) => `${context.parsed.y.toFixed(1)} / 100`
          }
        }
      }
    }
  });
}

function renderRisks(counts) {
  const canvas = $("#riskChart");
  if (!canvas || typeof Chart === "undefined") return;

  const labels = ["Low", "Medium", "High", "Insufficient data"];
  const values = [
    counts.Low || 0,
    counts.Medium || 0,
    counts.High || 0,
    counts["Insufficient data"] || 0
  ];

  const colors = ["#24d6b0", "#f5bf4f", "#ff5f83", "#7890ad"];

  if (riskChart) riskChart.destroy();

  riskChart = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderColor: "#06152b",
        borderWidth: 4,
        hoverOffset: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "70%",
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0b2140",
          titleColor: "#fff",
          bodyColor: "#c9dcf5"
        }
      }
    }
  });

  $("#riskLegend").innerHTML = labels.map((label, index) => `
    <div class="legend-item">
      <span class="legend-dot" style="background:${colors[index]}"></span>
      ${esc(label)}
      <strong>${values[index]}</strong>
    </div>
  `).join("");
}

function renderSegments(segments) {
  const entries = Object.entries(segments)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  const total = entries.reduce((sum, entry) => sum + entry[1], 0) || 1;

  $("#segmentList").innerHTML = entries.length
    ? entries.map(([name, count]) => `
        <div class="segment-row">
          <span title="${esc(name)}">${esc(name)}</span>
          <div class="segment-bar">
            <span style="width:${Math.max(3, count / total * 100)}%"></span>
          </div>
          <strong>${count}</strong>
        </div>
      `).join("")
    : `
      <div class="empty-state compact">
        Segments appear when student data is available.
      </div>`;
}

function populateDepartments(departments) {
  const select = $("#departmentFilter");
  if (!select) return;

  const current = select.value;
  const options = [
    "All Departments",
    ...departments.filter((department) => department !== "All Departments")
  ];

  if (select.options.length !== options.length) {
    select.innerHTML = options
      .map((department) => `<option>${esc(department)}</option>`)
      .join("");
  }

  if (options.includes(current)) {
    select.value = current;
  }
}

function applySearch() {
  const search = $("#globalSearch");
  if (!search) return;

  const term = search.value.trim().toLowerCase();

  const filtered = allStudents.filter((student) =>
    [
      student.name,
      student.student_id,
      student.department,
      student.segment
    ].some((value) => String(value || "").toLowerCase().includes(term))
  );

  renderStudents(filtered);

  $("#recordCount").textContent = `${filtered.length} matching records`;
}

document.addEventListener("DOMContentLoaded", () => {
  $("#departmentFilter")?.addEventListener("change", loadDashboard);
  $("#globalSearch")?.addEventListener("input", applySearch);

  $("#refreshButton")?.addEventListener("click", () =>
    loadDashboard().then(() => toast("Dashboard refreshed."))
  );

  $("#mobileMenu")?.addEventListener("click", () =>
    document.querySelector(".sidebar")?.classList.toggle("open")
  );

  loadDashboard();
});
