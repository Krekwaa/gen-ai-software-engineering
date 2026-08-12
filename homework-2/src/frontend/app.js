const API_BASE = "http://127.0.0.1:8000";

const OPTIONS = {
  categories: [
    "account_access",
    "technical_issue",
    "billing_question",
    "feature_request",
    "bug_report",
    "other",
  ],
  priorities: ["urgent", "high", "medium", "low"],
  statuses: ["new", "in_progress", "waiting_customer", "resolved", "closed"],
  sources: ["web_form", "email", "api", "chat", "phone"],
  devices: ["desktop", "mobile", "tablet"],
};

const state = {
  tickets: [],
  selectedTicketId: null,
};

const els = {
  apiStatus: document.querySelector("#api-status"),
  feedback: document.querySelector("#feedback"),
  ticketCount: document.querySelector("#ticket-count"),
  tickets: document.querySelector("#tickets"),
  formTitle: document.querySelector("#form-title"),
  ticketForm: document.querySelector("#ticket-form"),
  ticketId: document.querySelector("#ticket-id"),
  customerId: document.querySelector("#customer-id"),
  customerEmail: document.querySelector("#customer-email"),
  customerName: document.querySelector("#customer-name"),
  subject: document.querySelector("#subject"),
  description: document.querySelector("#description"),
  category: document.querySelector("#category"),
  priority: document.querySelector("#priority"),
  status: document.querySelector("#status"),
  assignedTo: document.querySelector("#assigned-to"),
  tags: document.querySelector("#tags"),
  metadataSource: document.querySelector("#metadata-source"),
  metadataBrowser: document.querySelector("#metadata-browser"),
  metadataDevice: document.querySelector("#metadata-device"),
  autoClassify: document.querySelector("#auto-classify"),
  saveButton: document.querySelector("#save-button"),
  deleteButton: document.querySelector("#delete-button"),
  resetFormButton: document.querySelector("#reset-form-button"),
  classifyButton: document.querySelector("#classify-button"),
  ticketDetail: document.querySelector("#ticket-detail"),
  importForm: document.querySelector("#import-form"),
  importFile: document.querySelector("#import-file"),
  importResult: document.querySelector("#import-result"),
  filterCategory: document.querySelector("#filter-category"),
  filterPriority: document.querySelector("#filter-priority"),
  filterStatus: document.querySelector("#filter-status"),
  refreshButton: document.querySelector("#refresh-button"),
};

function formatLabel(value) {
  if (!value) {
    return "None";
  }

  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function populateSelect(select, values, includeEmpty = false) {
  const emptyOption = includeEmpty ? '<option value="">Unknown</option>' : "";
  select.innerHTML =
    emptyOption +
    values.map((value) => `<option value="${value}">${formatLabel(value)}</option>`).join("");
}

function initializeOptions() {
  populateSelect(els.category, OPTIONS.categories);
  populateSelect(els.priority, OPTIONS.priorities);
  populateSelect(els.status, OPTIONS.statuses);
  populateSelect(els.metadataSource, OPTIONS.sources);
  populateSelect(els.metadataDevice, OPTIONS.devices, true);

  populateSelect(els.filterCategory, OPTIONS.categories, true);
  populateSelect(els.filterPriority, OPTIONS.priorities, true);
  populateSelect(els.filterStatus, OPTIONS.statuses, true);
  els.filterCategory.firstElementChild.textContent = "All";
  els.filterPriority.firstElementChild.textContent = "All";
  els.filterStatus.firstElementChild.textContent = "All";
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join("; ")
      : detail || `HTTP ${response.status}`;
    throw new Error(message);
  }

  return data;
}

async function checkApiStatus() {
  try {
    await api("/health");
    els.apiStatus.textContent = "API connected";
    els.apiStatus.classList.remove("error");
    els.apiStatus.classList.add("ok");
  } catch (error) {
    els.apiStatus.textContent = "API offline";
    els.apiStatus.classList.remove("ok");
    els.apiStatus.classList.add("error");
  }
}

function showFeedback(message, type = "success") {
  els.feedback.textContent = message;
  els.feedback.className = `feedback ${type}`;
  els.feedback.hidden = false;
}

function clearFeedback() {
  els.feedback.hidden = true;
  els.feedback.textContent = "";
  els.feedback.className = "feedback";
}

function currentFilters() {
  const params = new URLSearchParams();

  if (els.filterCategory.value) {
    params.set("category", els.filterCategory.value);
  }
  if (els.filterPriority.value) {
    params.set("priority", els.filterPriority.value);
  }
  if (els.filterStatus.value) {
    params.set("status", els.filterStatus.value);
  }

  const query = params.toString();
  return query ? `?${query}` : "";
}

async function loadTickets() {
  try {
    await checkApiStatus();
    state.tickets = await api(`/tickets${currentFilters()}`);
    renderTickets();
    renderSelectedTicket();
  } catch (error) {
    state.tickets = [];
    renderTickets();
    showFeedback(error.message, "error");
  }
}

function renderTickets() {
  els.ticketCount.textContent = `${state.tickets.length} total`;

  if (state.tickets.length === 0) {
    els.tickets.innerHTML = '<div class="empty">No tickets found</div>';
    return;
  }

  els.tickets.innerHTML = `
    <div class="ticket-items">
      ${state.tickets.map(renderTicketItem).join("")}
    </div>
  `;

  document.querySelectorAll(".ticket-item").forEach((button) => {
    button.addEventListener("click", () => selectTicket(button.dataset.ticketId));
  });
}

function renderTicketItem(ticket) {
  const active = ticket.id === state.selectedTicketId ? " active" : "";
  return `
    <button class="ticket-item${active}" type="button" data-ticket-id="${ticket.id}">
      <span class="ticket-subject">${escapeHtml(ticket.subject)}</span>
      <span class="muted">${escapeHtml(ticket.customer_name)} - ${escapeHtml(ticket.customer_email)}</span>
      <span class="pill-row">
        <span class="pill ${ticket.priority}">${formatLabel(ticket.priority)}</span>
        <span class="pill ${ticket.status}">${formatLabel(ticket.status)}</span>
        <span class="pill">${formatLabel(ticket.category)}</span>
      </span>
    </button>
  `;
}

function selectTicket(ticketId) {
  state.selectedTicketId = ticketId;
  const ticket = getSelectedTicket();
  if (ticket) {
    fillForm(ticket);
  }
  renderTickets();
  renderSelectedTicket();
}

function getSelectedTicket() {
  return state.tickets.find((ticket) => ticket.id === state.selectedTicketId) || null;
}

function renderSelectedTicket() {
  const ticket = getSelectedTicket();
  els.classifyButton.disabled = !ticket;

  if (!ticket) {
    els.ticketDetail.className = "detail-empty";
    els.ticketDetail.textContent = "No ticket selected";
    return;
  }

  els.ticketDetail.className = "detail-grid";
  els.ticketDetail.innerHTML = `
    <div>
      <h3>${escapeHtml(ticket.subject)}</h3>
      <p>${escapeHtml(ticket.description)}</p>
    </div>
    <div class="pill-row">
      <span class="pill ${ticket.category}">${formatLabel(ticket.category)}</span>
      <span class="pill ${ticket.priority}">${formatLabel(ticket.priority)}</span>
      <span class="pill ${ticket.status}">${formatLabel(ticket.status)}</span>
    </div>
    <div class="detail-block">
      <strong>Customer</strong>
      <p>${escapeHtml(ticket.customer_name)}<br>${escapeHtml(ticket.customer_email)}</p>
    </div>
    <div class="detail-block">
      <strong>Classification</strong>
      <p>${renderClassification(ticket)}</p>
    </div>
    <div class="detail-block">
      <strong>Metadata</strong>
      <p>${formatLabel(ticket.metadata?.source)} / ${formatLabel(ticket.metadata?.device_type)} / ${escapeHtml(ticket.metadata?.browser || "No browser")}</p>
    </div>
  `;
}

function renderClassification(ticket) {
  if (ticket.classification_confidence === null) {
    return "Not classified";
  }

  const confidence = Math.round(ticket.classification_confidence * 100);
  const keywords = ticket.classification_keywords?.length
    ? ` Keywords: ${ticket.classification_keywords.join(", ")}.`
    : "";
  const override = ticket.classification_overridden ? " Manual override applied." : "";
  return `${confidence}% confidence. ${escapeHtml(ticket.classification_reasoning || "")}${escapeHtml(keywords)}${override}`;
}

function fillForm(ticket) {
  els.formTitle.textContent = "Edit Ticket";
  els.saveButton.textContent = "Save Changes";
  els.deleteButton.hidden = false;
  els.ticketId.value = ticket.id;
  els.customerId.value = ticket.customer_id;
  els.customerEmail.value = ticket.customer_email;
  els.customerName.value = ticket.customer_name;
  els.subject.value = ticket.subject;
  els.description.value = ticket.description;
  els.category.value = ticket.category;
  els.priority.value = ticket.priority;
  els.status.value = ticket.status;
  els.assignedTo.value = ticket.assigned_to || "";
  els.tags.value = (ticket.tags || []).join(", ");
  els.metadataSource.value = ticket.metadata?.source || "api";
  els.metadataBrowser.value = ticket.metadata?.browser || "";
  els.metadataDevice.value = ticket.metadata?.device_type || "";
  els.autoClassify.checked = false;
}

function resetForm() {
  state.selectedTicketId = null;
  els.ticketForm.reset();
  els.formTitle.textContent = "New Ticket";
  els.saveButton.textContent = "Create Ticket";
  els.deleteButton.hidden = true;
  els.ticketId.value = "";
  els.category.value = "other";
  els.priority.value = "medium";
  els.status.value = "new";
  els.metadataSource.value = "api";
  els.metadataDevice.value = "";
  renderTickets();
  renderSelectedTicket();
}

function formPayload(includeAutoClassify) {
  const metadata = {
    source: els.metadataSource.value || "api",
  };

  if (els.metadataBrowser.value.trim()) {
    metadata.browser = els.metadataBrowser.value.trim();
  }

  if (els.metadataDevice.value) {
    metadata.device_type = els.metadataDevice.value;
  }

  const payload = {
    customer_id: els.customerId.value.trim(),
    customer_email: els.customerEmail.value.trim(),
    customer_name: els.customerName.value.trim(),
    subject: els.subject.value.trim(),
    description: els.description.value.trim(),
    category: els.category.value,
    priority: els.priority.value,
    status: els.status.value,
    assigned_to: els.assignedTo.value.trim() || null,
    tags: parseTags(els.tags.value),
    metadata,
  };

  if (includeAutoClassify) {
    payload.auto_classify = els.autoClassify.checked;
  }

  return payload;
}

function validateForm() {
  if (!els.ticketForm.reportValidity()) {
    return false;
  }

  if (els.description.value.trim().length < 10) {
    showFeedback("Description must be at least 10 characters.", "error");
    return false;
  }

  return true;
}

async function saveTicket(event) {
  event.preventDefault();
  clearFeedback();

  if (!validateForm()) {
    return;
  }

  const ticketId = els.ticketId.value;
  const isEdit = Boolean(ticketId);
  const payload = formPayload(!isEdit);

  try {
    const saved = isEdit
      ? await api(`/tickets/${ticketId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        })
      : await api("/tickets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

    state.selectedTicketId = saved.id;
    await loadTickets();
    showFeedback(isEdit ? "Ticket updated." : "Ticket created.");
  } catch (error) {
    showFeedback(error.message, "error");
  }
}

async function deleteSelectedTicket() {
  const ticketId = els.ticketId.value;
  if (!ticketId) {
    return;
  }

  try {
    await api(`/tickets/${ticketId}`, { method: "DELETE" });
    resetForm();
    await loadTickets();
    showFeedback("Ticket deleted.");
  } catch (error) {
    showFeedback(error.message, "error");
  }
}

async function classifySelectedTicket() {
  const ticket = getSelectedTicket();
  if (!ticket) {
    return;
  }

  try {
    const result = await api(`/tickets/${ticket.id}/auto-classify`, { method: "POST" });
    await loadTickets();
    showFeedback(`Classified as ${formatLabel(result.category)} / ${formatLabel(result.priority)}.`);
  } catch (error) {
    showFeedback(error.message, "error");
  }
}

async function importTickets(event) {
  event.preventDefault();
  clearFeedback();

  const file = els.importFile.files[0];
  if (!file) {
    showFeedback("Select a CSV, JSON, or XML file.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const result = await api("/tickets/import", {
      method: "POST",
      body: formData,
    });
    els.importResult.hidden = false;
    els.importResult.textContent = JSON.stringify(result, null, 2);
    els.importForm.reset();
    await loadTickets();
    showFeedback(`Imported ${result.successful} of ${result.total_records} records.`);
  } catch (error) {
    showFeedback(error.message, "error");
  }
}

function parseTags(value) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bindEvents() {
  els.ticketForm.addEventListener("submit", saveTicket);
  els.deleteButton.addEventListener("click", deleteSelectedTicket);
  els.resetFormButton.addEventListener("click", resetForm);
  els.classifyButton.addEventListener("click", classifySelectedTicket);
  els.importForm.addEventListener("submit", importTickets);
  els.refreshButton.addEventListener("click", loadTickets);
  els.filterCategory.addEventListener("change", loadTickets);
  els.filterPriority.addEventListener("change", loadTickets);
  els.filterStatus.addEventListener("change", loadTickets);
}

initializeOptions();
bindEvents();
resetForm();
loadTickets();
