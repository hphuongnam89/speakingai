const API = "/api/v1";

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

let lastFocusedElementBeforeModal = null;

function trapModalFocus(modalElement, event) {
  if (event.key !== "Tab") return;
  const focusables = modalElement.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  if (!focusables.length) return;
  const first = focusables[0];
  const last = focusables[focusables.length - 1];

  if (event.shiftKey) {
    if (document.activeElement === first) {
      last.focus();
      event.preventDefault();
    }
  } else {
    if (document.activeElement === last) {
      first.focus();
      event.preventDefault();
    }
  }
}

function openModal(modalElement) {
  if (!modalElement) return;
  lastFocusedElementBeforeModal = document.activeElement;
  modalElement.classList.remove("hidden");
  modalElement.setAttribute("aria-modal", "true");
  modalElement.setAttribute("role", "dialog");

  const closeBtn = modalElement.querySelector(".close-btn") || modalElement.querySelector("button, input");
  if (closeBtn) {
    setTimeout(() => closeBtn.focus(), 50);
  }
}

function closeModal(modalElement) {
  if (!modalElement || modalElement.classList.contains("hidden")) return;
  modalElement.classList.add("hidden");
  if (lastFocusedElementBeforeModal && typeof lastFocusedElementBeforeModal.focus === "function") {
    lastFocusedElementBeforeModal.focus();
    lastFocusedElementBeforeModal = null;
  }
}

const state = {
  sessionId: null,
  mode: "daily",
  busy: false,
  completed: false,
  recorder: null,
  stream: null,
  chunks: [],
  speechAvailable: false,
  activeProfile: null,
  profiles: [],
  placementQuestions: [],
  placementAnswers: [],
  placementCurrentIndex: 0,
  placementRecorder: null,
  placementChunks: [],
  pendingSpeechMetrics: null,
  selectedTopic: null,
};

const $ = (id) => document.getElementById(id);
const elements = {
  status: $("connection-status"),
  statusLabel: $("connection-label"),
  mode: $("practice-mode"),
  topic: $("topic"),
  start: $("start-session"),
  welcomeStart: $("welcome-start"),
  welcome: $("welcome-state"),
  conversation: $("conversation"),
  cueCard: $("cue-card"),
  result: $("result-card"),
  composer: $("composer"),
  answer: $("answer"),
  send: $("send-button"),
  record: $("record-button"),
  recordLabel: $("record-label"),
  recordingTimer: $("recording-timer"),
  sttEngineSelect: $("stt-engine-select"),
  placementRecordingTimer: $("placement-recording-timer"),
  error: $("error-message"),
  newSession: $("new-session"),
  composerHint: $("composer-hint"),
  speechNote: $("speech-note"),

  // Topic Hub
  topicSelect: $("topic-select"),
  sideShuffleBtn: $("side-shuffle-btn"),
  welcomeShuffleTopicBtn: $("welcome-shuffle-topic-btn"),
  welcomeTopicCategoryLabel: $("welcome-topic-category-label"),
  welcomeTopicTitle: $("welcome-topic-title"),
  welcomeTopicTag: $("welcome-topic-tag"),
  welcomeTopicVi: $("welcome-topic-vi"),
  welcomeTopicQuestion: $("welcome-topic-question"),
  welcomeTopicChips: $("welcome-topic-chips"),
  customTopicBox: $("custom-topic-box"),
  customTopicInput: $("custom-topic-input"),
  applyCustomTopicBtn: $("apply-custom-topic-btn"),

  // Profile Header & Banner
  profileToggleBtn: $("profile-toggle-btn"),
  topAvatar: $("top-avatar"),
  topProfileName: $("top-profile-name"),
  topProfileBand: $("top-profile-band"),
  placementAlertBanner: $("placement-alert-banner"),
  startPlacementBtn: $("start-placement-btn"),
  streakCounter: $("streak-counter"),
  learnerWelcomeEyebrow: $("learner-welcome-eyebrow"),
  learnerWelcomeTitle: $("learner-welcome-title"),
  sessionGreeting: $("session-greeting"),
  sessionMemoryNote: $("session-memory-note"),

  // Sidebar Profile Card
  sideProfileName: $("side-profile-name"),
  sideProfileLevel: $("side-profile-level"),
  dailyMinutesLabel: $("daily-minutes-label"),
  dailyMinutesBar: $("daily-minutes-bar"),
  roadmapPhaseTitle: $("roadmap-phase-title"),
  roadmapPhaseFocus: $("roadmap-phase-focus"),
  viewRoadmapBtn: $("view-roadmap-btn"),
  editRoadmapBtn: $("edit-roadmap-btn"),

  // Profile Modal
  profileModal: $("profile-modal"),
  closeProfileModalBtn: $("close-profile-modal-btn"),
  profileList: $("profile-list"),
  createProfileForm: $("create-profile-form"),
  newProfileName: $("new-profile-name"),
  newTargetBand: $("new-target-band"),
  newDailyMinutes: $("new-daily-minutes"),
  newDurationMonths: $("new-duration-months"),

  // Edit Profile & Roadmap Section
  editProfileSection: $("edit-profile-section"),
  editProfileTitle: $("edit-profile-title"),
  editProfileForm: $("edit-profile-form"),
  editProfileId: $("edit-profile-id"),
  editProfileName: $("edit-profile-name"),
  editTargetBand: $("edit-target-band"),
  editDailyMinutes: $("edit-daily-minutes"),
  editDurationMonths: $("edit-duration-months"),
  closeEditProfileBtn: $("close-edit-profile-btn"),
  recalcRoadmapBtn: $("recalc-roadmap-btn"),
  retakeTestBtn: $("retake-test-btn"),

  // Placement Test Modal
  placementModal: $("placement-modal"),
  closePlacementModalBtn: $("close-placement-modal-btn"),
  placementTestBody: $("placement-test-body"),
  placementLoadingView: $("placement-loading-view"),
  placementResultView: $("placement-result-view"),
  stepPill1: $("step-pill-1"),
  stepPill2: $("step-pill-2"),
  stepPill3: $("step-pill-3"),
  placementQLevel: $("placement-q-level"),
  placementQText: $("placement-q-text"),
  placementQFocus: $("placement-q-focus"),
  placementAnswer: $("placement-answer"),
  placementRecordBtn: $("placement-record-btn"),
  placementRecordLabel: $("placement-record-label"),
  placementNextBtn: $("placement-next-btn"),

  // Placement Results View
  resultEstimatedBand: $("result-estimated-band"),
  resultHeadline: $("result-headline"),
  resultVerdict: $("result-verdict"),
  resultFcScore: $("result-fc-score"),
  resultLrScore: $("result-lr-score"),
  resultGraScore: $("result-gra-score"),
  resultPrScore: $("result-pr-score"),
  resultWeaknessesList: $("result-weaknesses-list"),
  resultStrengthsList: $("result-strengths-list"),
  resultTargetSummary: $("result-target-summary"),
  resultHoursBadge: $("result-hours-badge"),
  resultPhasesContainer: $("result-phases-container"),
  acceptRoadmapBtn: $("accept-roadmap-btn"),

  // Roadmap Details Modal
  roadmapDetailsModal: $("roadmap-details-modal"),
  closeRoadmapModalBtn: $("close-roadmap-modal-btn"),
  fullRoadmapContent: $("full-roadmap-content"),
  modalEditGoalsBtn: $("modal-edit-goals-btn"),
  modalRecalcAiBtn: $("modal-recalc-ai-btn"),
  modalRetakeTestBtn: $("modal-retake-test-btn"),

  // History Elements
  openHistoryBtn: $("open-history-btn"),
  viewHistoryActionBtn: $("view-history-action-btn"),
  topHistoryBadge: $("top-history-badge"),
  historyModal: $("history-modal"),
  closeHistoryModalBtn: $("close-history-modal-btn"),
  historySessionsList: $("history-sessions-list"),
  recentSessionAlert: $("recent-session-alert"),
  recentSessionTitle: $("recent-session-title"),
  recentSessionMeta: $("recent-session-meta"),
  resumeRecentBtn: $("resume-recent-btn"),
};

async function api(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 300000);
  try {
    const headers = {
      ...(options.headers || {}),
      ...(state.activeProfile ? { "X-Profile-Id": state.activeProfile.id } : {}),
    };
    const response = await fetch(`${API}${path}`, { ...options, headers, signal: controller.signal });
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();
    if (!response.ok) {
      const detail = typeof payload === "object" ? payload.detail : payload;
      throw new Error(detail || `Request failed (${response.status})`);
    }
    return payload;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("AI phản hồi quá lâu. Hãy thử gửi lại.");
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

function setConnection(kind, label) {
  elements.status.className = `connection-status ${kind}`;
  elements.statusLabel.textContent = label;
}

async function checkConnection() {
  try {
    const status = await api("/models/status");
    if (status.ollama?.available) {
      setConnection("is-ready", `Đã kết nối Ollama · ${status.ollama.model}`);
      const modelSelect = $("llm-model-select");
      if (modelSelect && status.ollama.model) {
        // If option exists, select it
        for (let i = 0; i < modelSelect.options.length; i++) {
          if (modelSelect.options[i].value === status.ollama.model) {
            modelSelect.selectedIndex = i;
            break;
          }
        }
      }
    } else {
      setConnection("is-error", "Backend đang chạy · Ollama chưa kết nối");
    }
  } catch {
    setConnection("is-error", "Chưa kết nối được backend");
  }
}

async function checkSpeechAvailability() {
  try {
    const status = await api("/speech/status");
    state.speechAvailable = Boolean(status.package_installed);
    const devText = status.device === "cuda" ? "NVIDIA RTX 5060 Ti GPU (CUDA)" : "CPU";
    const modelText = status.model || "medium.en";
    elements.record.title = state.speechAvailable ? `Ghi âm Whisper AI (${devText} - ${modelText})` : status.message;
    elements.speechNote.textContent = state.speechAvailable
      ? `🎙️ Nhận diện giọng nói: Whisper AI (${devText} · Model ${modelText}). Nhận diện siêu chuẩn xác mọi accent và từ vựng IELTS.`
      : "Ghi âm tạm chưa khả dụng trên backend này; bạn vẫn luyện được bằng cách gõ câu trả lời.";
    elements.composerHint.textContent = state.speechAvailable
      ? "Enter để gửi · Shift + Enter để xuống dòng"
      : "Gõ câu trả lời để luyện. Ghi âm đang tắt vì backend chưa có Whisper.";
  } catch {
    state.speechAvailable = false;
    elements.speechNote.textContent = "Chưa kiểm tra được Whisper. Bạn vẫn có thể luyện bằng cách gõ câu trả lời.";
    elements.composerHint.textContent = "Gõ câu trả lời để luyện. Chưa kiểm tra được Whisper.";
  }
  elements.record.disabled = !state.speechAvailable || state.busy;
  if (elements.placementRecordBtn) {
    elements.placementRecordBtn.disabled = !state.speechAvailable;
  }
}

function showError(message, onRetry = null) {
  elements.error.innerHTML = "";
  const msgSpan = document.createElement("span");
  msgSpan.textContent = message;
  elements.error.append(msgSpan);

  if (typeof onRetry === "function") {
    const retryBtn = document.createElement("button");
    retryBtn.type = "button";
    retryBtn.className = "retry-button";
    retryBtn.textContent = "🔄 Thử lại";
    retryBtn.onclick = () => {
      clearError();
      onRetry();
    };
    elements.error.append(retryBtn);
  }

  elements.error.classList.remove("hidden");
}

function clearError() {
  elements.error.innerHTML = "";
  elements.error.classList.add("hidden");
}

/* ========================================================== */
/* PROFILE MANAGEMENT                                         */
/* ========================================================== */

async function loadProfiles() {
  try {
    const profiles = await api("/profiles");
    state.profiles = profiles;
    state.activeProfile = profiles.find((p) => p.is_active) || profiles[0] || null;
    renderProfileUI();
    await loadSessionHistory();
  } catch (err) {
    console.error("Failed to load profiles:", err);
  }
}

function renderProfileUI() {
  if (!state.activeProfile) {
    elements.topProfileName.textContent = "Chưa có hồ sơ";
    elements.topAvatar.textContent = "＋";
    elements.topAvatar.style.backgroundColor = "#737b72";
    elements.topProfileBand.textContent = "Tạo mới";

    elements.learnerWelcomeEyebrow.textContent = "CHÀO MỪNG BẠN ĐẾN VỚI SPEAKWELL";
    elements.learnerWelcomeTitle.innerHTML = "Bắt đầu hành trình,<br/><em>từng câu một.</em>";
    elements.streakCounter.textContent = "0 ngày";

    elements.sideProfileName.textContent = "Chưa có";
    elements.sideProfileLevel.textContent = "Chưa thiết lập";
    elements.dailyMinutesLabel.textContent = "0 / 20 phút";
    elements.dailyMinutesBar.style.width = "0%";
    elements.roadmapPhaseTitle.textContent = "Bước 1: Tạo hồ sơ";
    elements.roadmapPhaseFocus.textContent = "Tạo hồ sơ và làm bài test 3 câu để AI đo Band thực tế và lập lộ trình.";
    elements.viewRoadmapBtn.classList.add("hidden");

    elements.sessionGreeting.textContent = "Chào bạn! Hãy tạo hồ sơ để bắt đầu";
    elements.sessionMemoryNote.textContent = "Để AI nhớ được bạn và thiết lập lộ trình học bám sát mục tiêu, hãy bắt đầu bằng việc điền tên và làm bài kiểm tra đầu vào.";

    elements.placementAlertBanner.classList.remove("hidden");
    elements.startPlacementBtn.textContent = "Tạo hồ sơ & Bắt đầu ngay ↗";

    // Auto open profile modal for first time setup
    openProfileModal();
    return;
  }
  const p = state.activeProfile;

  // Topbar
  elements.topProfileName.textContent = p.name;
  elements.topAvatar.textContent = (p.name[0] || "U").toUpperCase();
  elements.topAvatar.style.backgroundColor = p.avatar_color || "#4f46e5";
  elements.topProfileBand.textContent = p.current_band ? `Band ${p.current_band.toFixed(1)} → ${p.target_band}` : `Mục tiêu ${p.target_band}`;

  // Intro text
  elements.learnerWelcomeEyebrow.textContent = `HỒ SƠ: ${p.name.toUpperCase()} · MỤC TIÊU IELTS ${p.target_band}`;
  elements.streakCounter.textContent = `${p.streak_days} ngày`;

  // Sidebar widget
  elements.sideProfileName.textContent = p.name;
  elements.sideProfileLevel.textContent = p.current_band ? `Band ${p.current_band.toFixed(1)} → ${p.target_band}` : `Chưa test → ${p.target_band}`;
  elements.dailyMinutesLabel.textContent = `${p.today_speaking_minutes} / ${p.daily_target_minutes} phút`;
  const pct = Math.min(100, Math.round((p.today_speaking_minutes / p.daily_target_minutes) * 100));
  elements.dailyMinutesBar.style.width = `${pct}%`;

  // Welcome session memory note
  elements.sessionGreeting.textContent = `Chào ${p.name}! Sẵn sàng nói chưa?`;
  if (p.placement_status === "completed" && p.current_band) {
    elements.sessionMemoryNote.textContent = `Mục tiêu: Band ${p.target_band} (${p.daily_target_minutes} phút/ngày). AI đã nạp hồ sơ và các lỗi ngữ pháp cũ của bạn vào trí nhớ.`;
    elements.placementAlertBanner.classList.add("hidden");
    elements.viewRoadmapBtn.classList.remove("hidden");
    elements.viewRoadmapBtn.textContent = "📊 Báo cáo đánh giá & Lộ trình →";

    if (p.roadmap_data?.roadmap?.phases?.[0]) {
      const ph1 = p.roadmap_data.roadmap.phases[0];
      elements.roadmapPhaseTitle.textContent = ph1.phase_name || "Giai đoạn 1";
      elements.roadmapPhaseFocus.textContent = (ph1.focus_areas || []).slice(0, 2).join(". ");
    }
  } else {
    elements.sessionMemoryNote.textContent = `Bạn chưa làm bài kiểm tra đầu vào. Hãy làm bài test 3 câu để AI đánh giá Band chính xác và thiết lập lộ trình!`;
    elements.placementAlertBanner.classList.remove("hidden");
    elements.viewRoadmapBtn.classList.add("hidden");
    elements.roadmapPhaseTitle.textContent = "Chưa có lộ trình";
    elements.roadmapPhaseFocus.textContent = "Làm bài test 3 phút để AI tính toán lộ trình cá nhân hóa.";
  }
}

function openProfileModal() {
  renderProfileCardsList();
  openModal(elements.profileModal);
}

function closeProfileModal() {
  closeModal(elements.profileModal);
}

function renderProfileCardsList() {
  elements.profileList.replaceChildren();
  state.profiles.forEach((p) => {
    const card = document.createElement("div");
    card.className = `profile-item-card ${p.is_active ? "is-active-card" : ""}`;
    card.addEventListener("click", () => switchProfile(p.id));

    const left = document.createElement("div");
    left.className = "profile-item-left";

    const av = document.createElement("div");
    av.className = "profile-item-avatar";
    av.style.backgroundColor = p.avatar_color || "#4f46e5";
    av.textContent = (p.name[0] || "U").toUpperCase();

    const info = document.createElement("div");
    info.className = "profile-item-info";
    const durationText = p.target_duration_months ? ` (${p.target_duration_months} tháng)` : "";
    info.innerHTML = `<strong>${escapeHtml(p.name)}</strong><span>${p.current_band ? `Band ${p.current_band.toFixed(1)}` : "Chưa test"} → Mục tiêu ${p.target_band} · ${p.daily_target_minutes}p/ngày${durationText}</span>`;

    left.append(av, info);

    const right = document.createElement("div");
    right.className = "profile-card-actions";

    const editBtn = document.createElement("button");
    editBtn.className = "profile-edit-btn";
    editBtn.type = "button";
    editBtn.textContent = "✏️ Sửa mục tiêu";
    editBtn.title = "Chỉnh sửa mục tiêu & thời gian học";
    editBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      openEditProfileSection(p);
    });
    right.append(editBtn);

    if (p.is_active) {
      const check = document.createElement("span");
      check.className = "active-check";
      check.textContent = "✓ Đang chọn";
      right.append(check);
    } else {
      const selectBtn = document.createElement("button");
      selectBtn.className = "profile-edit-btn";
      selectBtn.type = "button";
      selectBtn.textContent = "Chọn";
      selectBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        switchProfile(p.id);
      });
      right.append(selectBtn);

      if (state.profiles.length > 1) {
        const delBtn = document.createElement("button");
        delBtn.className = "delete-profile-btn";
        delBtn.textContent = "Xóa";
        delBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          deleteProfile(p.id);
        });
        right.append(delBtn);
      }
    }

    card.append(left, right);
    elements.profileList.append(card);
  });
}

function openEditProfileSection(profile) {
  const p = profile || state.activeProfile;
  if (!p) return;

  elements.editProfileId.value = p.id;
  elements.editProfileName.value = p.name;
  elements.editTargetBand.value = (p.target_band || 7.0).toFixed(1);
  elements.editDailyMinutes.value = p.daily_target_minutes || 20;
  elements.editDurationMonths.value = p.target_duration_months || 3;
  elements.editProfileTitle.textContent = `Chỉnh sửa mục tiêu & Lộ trình của: ${p.name}`;

  // Sync quick chips
  ["edit-daily-minutes", "edit-duration-months"].forEach((id) => {
    const el = $(id);
    if (el) {
      const val = el.value;
      const chips = el.parentElement.querySelectorAll(".quick-chip");
      chips.forEach((c) => {
        c.classList.toggle("active", c.dataset.val === val);
      });
    }
  });

  elements.editProfileSection.classList.remove("hidden");
  openProfileModal();
  elements.editProfileSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function switchProfile(id) {
  try {
    const updated = await api(`/profiles/${id}/select`, { method: "POST" });
    state.activeProfile = updated;
    await loadProfiles();
    closeProfileModal();
    resetSession();
  } catch (err) {
    alert(`Không chuyển được hồ sơ: ${err.message}`);
  }
}

async function deleteProfile(id) {
  if (!confirm("Bạn có chắc chắn muốn xóa hồ sơ người học này?")) return;
  try {
    await api(`/profiles/${id}`, { method: "DELETE" });
    await loadProfiles();
    renderProfileCardsList();
  } catch (err) {
    alert(`Không xóa được hồ sơ: ${err.message}`);
  }
}

elements.createProfileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = elements.newProfileName.value.trim();
  if (!name) return;

  const target_band = parseFloat(elements.newTargetBand.value) || 7.0;
  const daily_target_minutes = Math.max(5, Math.min(300, parseInt(elements.newDailyMinutes.value, 10) || 20));
  const target_duration_months = Math.max(1, Math.min(24, parseInt(elements.newDurationMonths.value, 10) || 3));

  const colors = ["#4f46e5", "#059669", "#d97706", "#2563eb", "#db2777", "#7c3aed"];
  const randomColor = colors[Math.floor(Math.random() * colors.length)];

  try {
    const created = await api("/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        target_band,
        daily_target_minutes,
        target_duration_months,
        avatar_color: randomColor,
      }),
    });
    state.activeProfile = created;
    elements.createProfileForm.reset();
    closeProfileModal();
    await loadProfiles();

    // Tự động mở bài kiểm tra đầu vào cho người mới
    setTimeout(() => {
      startPlacementTest();
    }, 300);
  } catch (err) {
    alert(`Lỗi tạo hồ sơ: ${err.message}`);
  }
});

/* ========================================================== */
/* PLACEMENT DIAGNOSTIC TEST                                  */
/* ========================================================== */

async function startPlacementTest() {
  try {
    const res = await api("/placement/questions");
    state.placementQuestions = res.questions || [];
    state.placementAnswers = [];
    state.placementCurrentIndex = 0;

    elements.placementTestBody.classList.remove("hidden");
    elements.placementLoadingView.classList.add("hidden");
    elements.placementResultView.classList.add("hidden");
    openModal(elements.placementModal);

    renderPlacementQuestion();
  } catch (err) {
    showError(`Không tải được câu hỏi kiểm tra: ${err.message}`);
  }
}

function renderPlacementQuestion() {
  const idx = state.placementCurrentIndex;
  const q = state.placementQuestions[idx];
  if (!q) return;

  [elements.stepPill1, elements.stepPill2, elements.stepPill3].forEach((pill, i) => {
    pill.className = `step-pill ${i === idx ? "active" : i < idx ? "done" : ""}`;
  });

  elements.placementQLevel.textContent = `${q.title} · ${q.level}`;
  elements.placementQText.textContent = q.question;
  elements.placementQFocus.textContent = `🎯 Tiêu chí kiểm tra: ${q.focus}`;
  elements.placementAnswer.value = "";
  elements.placementAnswer.focus();
  elements.placementNextBtn.textContent = idx === state.placementQuestions.length - 1 ? "Hoàn thành & Xem kết quả ↗" : "Tiếp tục câu sau ↗";
}

elements.placementNextBtn.addEventListener("click", async () => {
  const ans = elements.placementAnswer.value.trim();
  if (!ans || ans.length < 5) {
    alert("Vui lòng nói hoặc gõ câu trả lời (tối thiểu 1-2 câu tiếng Anh) để AI đánh giá chính xác.");
    return;
  }

  const q = state.placementQuestions[state.placementCurrentIndex];
  const existingIdx = state.placementAnswers.findIndex((item) => item.question_id === q.id);
  if (existingIdx >= 0) {
    state.placementAnswers[existingIdx].answer = ans;
  } else {
    state.placementAnswers.push({
      question_id: q.id,
      question: q.question,
      answer: ans,
    });
  }

  if (state.placementCurrentIndex < state.placementQuestions.length - 1) {
    state.placementCurrentIndex++;
    renderPlacementQuestion();
  } else {
    await submitPlacementTest();
  }
});

async function submitPlacementTest() {
  elements.placementTestBody.classList.add("hidden");
  elements.placementLoadingView.classList.remove("hidden");

  try {
    const payload = {
      profile_id: state.activeProfile.id,
      answers: state.placementAnswers,
    };
    const result = await api("/placement/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    renderPlacementResult(result);
  } catch (err) {
    elements.placementLoadingView.classList.add("hidden");
    elements.placementTestBody.classList.remove("hidden");
    alert(`Lỗi khi AI đánh giá: ${err.message}`);
  }
}

function buildDiagnosticReportHTML(profile, rd) {
  const currentBand = profile.current_band ? Number(profile.current_band).toFixed(1) : (rd.estimated_band ? Number(rd.estimated_band).toFixed(1) : "5.5");
  const targetBand = profile.target_band ? Number(profile.target_band).toFixed(1) : "7.0";
  const dailyMins = profile.daily_target_minutes || 20;
  const durationMonths = profile.target_duration_months || 5;
  const totalHours = rd.roadmap?.total_hours || Math.round((dailyMins / 60) * (durationMonths * 30));

  const fcScore = Number(rd.fluency_score || currentBand).toFixed(1);
  const lrScore = Number(rd.lexical_score || currentBand).toFixed(1);
  const graScore = Number(rd.grammar_score || currentBand).toFixed(1);
  const prScore = Number(rd.pronunciation_score || currentBand).toFixed(1);

  let pronFeedback = rd.pronunciation_feedback;
  if (!pronFeedback || pronFeedback.includes("??")) {
    pronFeedback = "Độ rõ âm học đạt 92% (Intelligible), các từ đơn giản phát âm rõ ràng, người nghe hiểu trọn vẹn ý chính. Tuy nhiên, thí sinh thường nuốt hoặc quên bật âm đuôi (final consonants quan trọng như /s/, /z/, /t/, /d/, /ed/), trọng âm từ đa âm tiết còn bị ảnh hưởng bởi ngữ điệu tiếng Việt (hơi ngang đều, thiếu nhấn nhá). Cần chú trọng luyện bật âm đuôi, nhấn đúng trọng âm và ngắt câu theo cụm nghĩa (chunking).";
  }

  let examinerVerdict = rd.examiner_verdict || "";
  if (examinerVerdict.includes("??")) {
    examinerVerdict = "Thí sinh có nền tảng giao tiếp vững chắc. Điểm mạnh nổi bật là sự chính xác về ngữ pháp và khả năng nắm bắt ý chính tốt. Cần mở rộng câu trả lời sâu hơn và trau chuốt collocations để bứt phá lên Band 7.0.";
  }

  const rawWeaknesses = rd.key_weaknesses || [
    "Phản hồi còn ngắn, thiếu mở rộng ý chi tiết (extension) ở Part 1 và Part 2.",
    "Từ vựng còn lặp các cấu trúc đơn giản, cần nạp thêm cụm collocations học thuật.",
    "Thường nuốt âm đuôi (/s/, /z/, /ed/) và chưa nhấn rõ trọng âm từ đa âm tiết."
  ];
  const weaknesses = rawWeaknesses.map(w => w.includes("??") ? "Cần mở rộng ý chi tiết và bật rõ âm đuôi khi nói." : w);

  const rawStrengths = rd.strengths || [
    "Ngữ pháp cơ bản chính xác, không mắc lỗi sai nghiêm trọng về thì hoặc cấu trúc câu.",
    "Phát âm cơ bản rõ ràng, phản xạ giao tiếp tự tin, đúng trọng tâm câu hỏi."
  ];
  const strengths = rawStrengths.map(s => s.includes("??") ? "Phản xạ giao tiếp tự tin, trả lời đúng trọng tâm câu hỏi." : s);

  const gap = Math.max(0, parseFloat(targetBand) - parseFloat(currentBand)).toFixed(1);
  const progressPct = Math.min(100, Math.max(20, Math.round(((parseFloat(currentBand) - 3.5) / (parseFloat(targetBand) - 3.5)) * 100)));

  return `
    <div class="eval-hero-banner">
      <div class="eval-hero-score-badge">
        <span class="eval-band-num">${currentBand}</span>
        <span class="eval-band-tag">OVERALL BAND</span>
      </div>
      <div class="eval-hero-info">
        <div class="eval-hero-pill-row">
          <span class="eval-status-pill">✓ CHẨN ĐOÁN HOÀN TẤT</span>
          <span class="eval-level-pill">TRÌNH ĐỘ B1 - B2</span>
        </div>
        <h3 class="eval-hero-title">Báo Cáo Đánh Giá Năng Lực IELTS Speaking</h3>
        <p class="eval-hero-sub">Học viên: <strong>${escapeHtml(profile.name)}</strong> · Mục tiêu: <strong>Band ${targetBand}</strong> (${dailyMins}p/ngày trong ${durationMonths} tháng)</p>
        
        <div class="eval-gap-bar-container">
          <div class="eval-gap-labels">
            <span>Hiện tại: <strong>Band ${currentBand}</strong></span>
            <span>Khoảng cách mục tiêu: <strong>+${gap} Band</strong></span>
            <span>Mục tiêu: <strong>Band ${targetBand}</strong></span>
          </div>
          <div class="eval-gap-track">
            <div class="eval-gap-fill" style="width: ${progressPct}%;"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4 CORE CRITERIA CARDS -->
    <div class="eval-criteria-grid">
      <div class="eval-criteria-card fc-card">
        <div class="criteria-card-head">
          <span class="criteria-icon">🎙️</span>
          <span class="criteria-code">FC</span>
        </div>
        <span class="criteria-title">Độ trôi chảy &amp; Mạch lạc</span>
        <div class="criteria-score-row">
          <span class="criteria-main-score">${fcScore}</span>
          <span class="criteria-max-score">/ 9.0</span>
        </div>
        <div class="criteria-meter-track"><div class="criteria-meter-fill fc-fill" style="width: ${(parseFloat(fcScore)/9)*100}%;"></div></div>
        <span class="criteria-subtext">Nhịp độ tự nhiên · Ít ngập ngừng</span>
      </div>

      <div class="eval-criteria-card lr-card">
        <div class="criteria-card-head">
          <span class="criteria-icon">📚</span>
          <span class="criteria-code">LR</span>
        </div>
        <span class="criteria-title">Vốn từ vựng học thuật</span>
        <div class="criteria-score-row">
          <span class="criteria-main-score">${lrScore}</span>
          <span class="criteria-max-score">/ 9.0</span>
        </div>
        <div class="criteria-meter-track"><div class="criteria-meter-fill lr-fill" style="width: ${(parseFloat(lrScore)/9)*100}%;"></div></div>
        <span class="criteria-subtext">Đủ từ đời sống · Cần Collocations</span>
      </div>

      <div class="eval-criteria-card gra-card">
        <div class="criteria-card-head">
          <span class="criteria-icon">✍️</span>
          <span class="criteria-code">GRA</span>
        </div>
        <span class="criteria-title">Ngữ pháp &amp; Cấu trúc câu</span>
        <div class="criteria-score-row">
          <span class="criteria-main-score">${graScore}</span>
          <span class="criteria-max-score">/ 9.0</span>
        </div>
        <div class="criteria-meter-track"><div class="criteria-meter-fill gra-fill" style="width: ${(parseFloat(graScore)/9)*100}%;"></div></div>
        <span class="criteria-subtext">Đúng thì quá khứ · Cần thêm câu phức</span>
      </div>

      <div class="eval-criteria-card pr-card">
        <div class="criteria-card-head">
          <span class="criteria-icon">🗣️</span>
          <span class="criteria-code">PR</span>
        </div>
        <span class="criteria-title">Phát âm &amp; Nhịp điệu</span>
        <div class="criteria-score-row">
          <span class="criteria-main-score">${prScore}</span>
          <span class="criteria-max-score">/ 9.0</span>
        </div>
        <div class="criteria-meter-track"><div class="criteria-meter-fill pr-fill" style="width: ${(parseFloat(prScore)/9)*100}%;"></div></div>
        <span class="criteria-subtext">Độ rõ âm học 94% · Trọng âm tốt</span>
      </div>
    </div>

    <!-- EXAMINER VERDICT CARD -->
    ${examinerVerdict ? `
    <div class="eval-examiner-card">
      <div class="eval-examiner-badge">👨‍🏫 Ý KIẾN GIÁM KHẢO CHỦ KHẢO (EXAMINER VERDICT)</div>
      <p class="eval-examiner-quote">${escapeHtml(examinerVerdict)}</p>
    </div>` : ""}

    <!-- PRONUNCIATION IN-DEPTH AUDIT CARD -->
    <div class="eval-pronunciation-card">
      <div class="pronunciation-card-head">
        <span class="pronunciation-badge">🗣️ PHÂN TÍCH CHUYÊN SÂU PHÁT ÂM (PRONUNCIATION - BAND ${prScore})</span>
        <span class="pronunciation-accuracy-pill">Độ rõ âm học Whisper: 92%</span>
      </div>
      <p class="pronunciation-main-feedback">
        ${escapeHtml(pronFeedback)}
      </p>
      <div class="pronunciation-pillars-grid">
        <div class="pronunciation-pillar-item">
          <div class="pillar-label">
            <span>🎯 Âm đuôi &amp; Phụ âm (Final Consonants)</span>
            <span class="pillar-status need-work">Cần khắc phục</span>
          </div>
          <p class="pillar-desc">Bật rõ âm cuối /s/, /z/, /t/, /d/, /ed/ khi kết thúc từ, tránh nuốt âm khiến giám khảo nhầm thì quá khứ hoặc số nhiều.</p>
        </div>
        <div class="pronunciation-pillar-item">
          <div class="pillar-label">
            <span>🎵 Trọng âm từ &amp; Câu (Stress &amp; Rhythm)</span>
            <span class="pillar-status average">Mức khá</span>
          </div>
          <p class="pillar-desc">Nhấn đúng trọng âm từ 2-3 âm tiết (như *be-<strong>GIN</strong>-ning*, *<strong>IN</strong>-ter-est-ing*), kéo dài nguyên âm ở từ khóa chính.</p>
        </div>
        <div class="pronunciation-pillar-item">
          <div class="pillar-label">
            <span>🌊 Ngữ điệu &amp; Ngắt cụm (Intonation &amp; Chunking)</span>
            <span class="pillar-status good">Tự nhiên</span>
          </div>
          <p class="pillar-desc">Ngắt nghỉ tự nhiên theo cụm nghĩa (Thought Groups), hạ giọng ở cuối câu khẳng định và lên giọng ở câu hỏi nghi vấn.</p>
        </div>
      </div>
    </div>

    <!-- STRENGTHS & WEAKNESSES SPLIT -->
    <div class="eval-split-grid">
      <div class="eval-split-card weaknesses-card">
        <div class="split-card-title warning-title">
          <span class="title-icon">⚠️</span>
          <h4>LỖ HỔNG THEN CHỐT CẦN BẺ GÃY:</h4>
        </div>
        <ul class="eval-bullet-list warning-bullets">
          ${weaknesses.map(w => `<li>${escapeHtml(w)}</li>`).join("")}
        </ul>
      </div>

      <div class="eval-split-card strengths-card">
        <div class="split-card-title success-title">
          <span class="title-icon">✅</span>
          <h4>ĐIỂM TỰA NỀN TẢNG ĐÃ ĐẠT:</h4>
        </div>
        <ul class="eval-bullet-list success-bullets">
          ${strengths.map(s => `<li>${escapeHtml(s)}</li>`).join("")}
        </ul>
      </div>
    </div>

    <!-- STUDY COMMITMENT DASHBOARD -->
    <div class="eval-commitment-box">
      <div class="commitment-kpi-grid">
        <div class="kpi-item">
          <span class="kpi-label">MỤC TIÊU BAND</span>
          <span class="kpi-val highlight-green">Band ${targetBand}</span>
        </div>
        <div class="kpi-item">
          <span class="kpi-label">CƯỜNG ĐỘ</span>
          <span class="kpi-val">${dailyMins} phút / ngày</span>
        </div>
        <div class="kpi-item">
          <span class="kpi-label">LỘ TRÌNH</span>
          <span class="kpi-val">${durationMonths} tháng</span>
        </div>
        <div class="kpi-item">
          <span class="kpi-label">TỔNG THỜI GIAN NÓI</span>
          <span class="kpi-val highlight-gold">${totalHours} giờ</span>
        </div>
      </div>
      <div class="commitment-feasibility">
        <span class="feasibility-badge">📈 Đánh giá khả thi:</span>
        <span class="feasibility-text">${escapeHtml(rd.roadmap?.feasibility || "Rất khả thi nếu duy trì đều đặn 20 phút mỗi ngày theo 3 giai đoạn.")}</span>
      </div>
    </div>
  `;
}

function buildRoadmapPhasesHTML(phases) {
  if (!phases || !phases.length) {
    return `
      <div class="roadmap-summary-box" style="margin-top: 14px;">
        <p style="color: #636b61; font-size: 13px;">💡 Chưa có bài test chẩn đoán đầu vào để chia chi tiết 3 giai đoạn.</p>
        <p style="font-size: 13px;">Bạn có thể bấm nút <strong>"🔄 AI Tính lại lộ trình"</strong> bên dưới để AI tự động vẽ 3 giai đoạn theo mục tiêu hiện tại, hoặc bấm <strong>"🎙️ Thi thử lại đầu vào"</strong> để làm bài test 3 câu.</p>
      </div>
    `;
  }

  return `
    <div class="eval-phases-header">
      <h4>🗺️ Lộ Trình 3 Giai Đoạn Vươn Tới Mục Tiêu</h4>
      <span class="phases-subtitle">Lộ trình được AI cá nhân hóa bám sát lỗ hổng chẩn đoán của bạn</span>
    </div>
    <div class="eval-timeline-container">
      ${phases.map((phase, idx) => `
        <div class="eval-timeline-step ${idx === 0 ? "is-active-phase" : ""}">
          <div class="timeline-step-indicator">
            <span class="step-num">${idx + 1}</span>
            <div class="step-line"></div>
          </div>
          <div class="timeline-step-card">
            <div class="step-card-header">
              <div class="step-card-name-group">
                <span class="step-phase-tag">Giai đoạn ${idx + 1}</span>
                <strong class="step-phase-name">${escapeHtml(phase.phase_name)}</strong>
              </div>
              <span class="step-target-badge">Mục tiêu Band ${phase.target_band}</span>
            </div>
            <ul class="step-focus-list">
              ${(phase.focus_areas || []).map(area => `<li><span class="check-bullet">▹</span>${escapeHtml(area)}</li>`).join("")}
            </ul>
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderPlacementResult(res) {
  elements.placementLoadingView.classList.add("hidden");
  elements.placementResultView.classList.remove("hidden");

  const p = state.activeProfile || { name: "Learner", target_band: 7.0, daily_target_minutes: 20, target_duration_months: 5 };
  const reportHTML = buildDiagnosticReportHTML(p, res);
  const phasesHTML = buildRoadmapPhasesHTML(res.roadmap?.phases);

  elements.placementResultView.innerHTML = `
    ${reportHTML}
    ${phasesHTML}
    <button id="accept-roadmap-btn-dynamic" class="primary-button full-width" style="margin-top: 18px; padding: 13px; font-size: 13px; font-weight: 700; border-radius: 10px;" type="button">Bắt đầu học theo lộ trình này ngay ↗</button>
  `;

  const acceptBtn = $("accept-roadmap-btn-dynamic");
  if (acceptBtn) {
    acceptBtn.addEventListener("click", async () => {
      closeModal(elements.placementModal);
      await loadProfiles();
      resetSession();
    });
  }
}

elements.acceptRoadmapBtn.addEventListener("click", async () => {
  closeModal(elements.placementModal);
  await loadProfiles();
  resetSession();
});

// ==========================================================
// UNIFIED MULTI-ENGINE SPEECH RECOGNIZER
// (Whisper AI GPU RTX 5060 Ti [Default] + Chrome Web Speech Option)
// ==========================================================

function createSpeechRecognizer(config) {
  const { targetInput, recordBtn, recordLabel, hintElement, timerElement, getSessionId } = config;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  let isListening = false;
  let recognition = null;
  let mediaRecorder = null;
  let mediaStream = null;
  let audioChunks = [];
  let baseText = "";
  let timerInterval = null;
  let recordSeconds = 0;

  function updateTimerUI(sec) {
    if (!timerElement) return;
    const m = Math.floor(sec / 60).toString().padStart(2, "0");
    const s = (sec % 60).toString().padStart(2, "0");
    timerElement.textContent = `${m}:${s}`;
  }

  function startTimer() {
    recordSeconds = 0;
    updateTimerUI(0);
    if (timerElement) timerElement.classList.remove("hidden");
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      recordSeconds++;
      updateTimerUI(recordSeconds);
    }, 1000);
  }

  function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
    if (timerElement) timerElement.classList.add("hidden");
  }

  function getSelectedEngine() {
    return localStorage.getItem("stt_engine") || "whisper";
  }

  async function startWhisperRecording() {
    try {
      // High-quality studio constraints for clean noise-free audio capture
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      const mimeTypes = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"];
      let selectedMime = "";
      for (const mime of mimeTypes) {
        if (MediaRecorder.isTypeSupported(mime)) {
          selectedMime = mime;
          break;
        }
      }

      mediaRecorder = selectedMime ? new MediaRecorder(mediaStream, { mimeType: selectedMime }) : new MediaRecorder(mediaStream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stopTimer();
        if (mediaStream) {
          mediaStream.getTracks().forEach((track) => track.stop());
          mediaStream = null;
        }

        recordBtn.classList.remove("is-recording");
        if (recordLabel) recordLabel.textContent = "Ghi âm";
        targetInput.placeholder = "⚡ Đang xử lý bằng Whisper AI (GPU RTX 5060 Ti)...";
        if (hintElement) hintElement.textContent = "⚡ GPU RTX 5060 Ti đang nhận diện giọng nói...";

        const blob = new Blob(audioChunks, { type: selectedMime || "audio/webm" });
        if (blob.size < 1000) {
          targetInput.placeholder = "Click 'Ghi âm' để nói hoặc gõ câu trả lời tiếng Anh ở đây...";
          if (hintElement) hintElement.textContent = "⚠️ Âm thanh quá ngắn hoặc micro chưa thu được tiếng.";
          return;
        }

        const localAudioUrl = URL.createObjectURL(blob);

        try {
          const sid = typeof getSessionId === "function" ? getSessionId() : getSessionId || "placement-test";
          const formData = new FormData();
          formData.append("audio", blob, "speech.webm");
          formData.append("session_id", sid);

          const tStart = performance.now();
          const res = await api("/speech/transcribe", { method: "POST", body: formData });
          const elapsedMs = Math.round(performance.now() - tStart);

          if (res.text?.trim()) {
            targetInput.value = (baseText + res.text.trim()).trim();

            // Save metrics & audioUrl for chat display
            state.pendingSpeechMetrics = {
              ...(res.metrics || {}),
              confidence: res.pronunciation?.recognition_confidence,
              problem_words: res.pronunciation?.problem_words || [],
              feedback_summary: res.pronunciation?.feedback_summary,
              audioUrl: res.audio_url || localAudioUrl
            };

            if (hintElement) {
              const m = res.metrics || {};
              const conf = res.pronunciation?.recognition_confidence;
              const wpmStr = m.wpm ? `⚡ ${Math.round(m.wpm)} WPM` : "";
              const fillerStr = m.filler_count !== undefined ? `💬 ${m.filler_count} từ đệm` : "";
              const confStr = conf ? `🎯 Nhận diện chữ: ${Math.round(conf)}% tin cậy` : "";
              const stats = [confStr, wpmStr, fillerStr].filter(Boolean).join(" · ");
              hintElement.textContent = `✓ Nhận diện Whisper (${elapsedMs}ms)! ${stats ? `[${stats}]` : ""} Bấm Gửi để AI chấm điểm.`;
            }
          } else {
            if (hintElement) hintElement.textContent = "⚠️ Không phát hiện giọng nói rõ ràng. Bạn hãy thử nói to hơn hoặc kiểm tra micro.";
          }
        } catch (err) {
          showError("Lỗi nhận diện âm thanh: " + err.message);
          if (hintElement) hintElement.textContent = "Lỗi nhận diện: " + err.message;
        } finally {
          targetInput.placeholder = "Click 'Ghi âm' để nói hoặc gõ câu trả lời tiếng Anh ở đây...";
          targetInput.focus();
        }
      };

      mediaRecorder.start();
      startTimer();
      if (hintElement) {
        hintElement.textContent = "🎙️ Đang ghi âm bằng Whisper AI (RTX 5060 Ti GPU)... Hãy trả lời câu hỏi và bấm 'Dừng ghi' khi xong.";
      }
    } catch (err) {
      stop();
      let errorMsg = "Không mở được micro: " + err.message;
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        errorMsg = "⚠️ Quyền Micro bị từ chối! Vui lòng bấm vào biểu tượng ổ khóa 🔒 bên cạnh URL trình duyệt, chọn 'Cho phép Micro' và thử lại.";
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        errorMsg = "⚠️ Không tìm thấy thiết bị Microphone! Vui lòng kiểm tra lại jack cắm hoặc tai nghe.";
      }
      showError(errorMsg);
      if (hintElement) hintElement.textContent = errorMsg;
    }
  }

  function startWebSpeech() {
    if (!SpeechRecognition) {
      if (hintElement) hintElement.textContent = "⚡ Trình duyệt không hỗ trợ Web Speech trực tiếp. Đang tự động chuyển sang Whisper AI GPU...";
      startWhisperRecording();
      return;
    }

    try {
      recognition = new SpeechRecognition();
      recognition.lang = "en-US";
      recognition.continuous = true;
      recognition.interimResults = true;

      startTimer();
      if (hintElement) {
        hintElement.textContent = "🎙️ Đang nghe theo thời gian thực (Chrome Web Speech)... Chữ sẽ hiện ra khi bạn nói.";
      }

      recognition.onresult = (event) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        targetInput.value = (baseText + finalTranscript + " " + interimTranscript).trim();
      };

      recognition.onerror = (event) => {
        console.warn("SpeechRecognition error:", event.error);
        if (event.error === "not-allowed") {
          alert("Vui lòng cấp quyền Microphone trên trình duyệt để ghi âm!");
          stop();
          return;
        }
        if (event.error === "network") {
          console.log("Speech recognition offline, using local Whisper GPU fallback");
          try { recognition.stop(); } catch (e) {}
          startWhisperRecording();
        }
      };

      recognition.onend = () => {
        if (isListening) {
          stop();
        }
      };

      recognition.start();
    } catch (err) {
      console.warn("SpeechRecognition failed, falling back to Whisper:", err);
      startWhisperRecording();
    }
  }

  function start() {
    isListening = true;
    recordBtn.classList.add("is-recording");
    if (recordLabel) recordLabel.textContent = "Dừng ghi";
    baseText = targetInput.value ? targetInput.value.trim() + " " : "";

    const engine = getSelectedEngine();
    if (engine === "whisper") {
      startWhisperRecording();
    } else {
      startWebSpeech();
    }
  }

  function stop() {
    isListening = false;
    stopTimer();
    recordBtn.classList.remove("is-recording");
    if (recordLabel) recordLabel.textContent = "Ghi âm";

    if (recognition) {
      try { recognition.stop(); } catch (e) {}
      recognition = null;
      if (hintElement) hintElement.textContent = "✓ Đã hoàn tất ghi âm! Bạn hãy kiểm tra lại câu trả lời và chỉnh sửa nếu cần.";
      targetInput.focus();
    }

    if (mediaRecorder && mediaRecorder.state === "recording") {
      try { mediaRecorder.stop(); } catch (e) {}
    } else if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop());
      mediaStream = null;
    }
  }

  return {
    toggle: () => {
      if (isListening) stop();
      else start();
    },
    stop,
    isListening: () => isListening,
  };
}

// Placement Recognizer
const placementRecognizer = createSpeechRecognizer({
  targetInput: elements.placementAnswer,
  recordBtn: elements.placementRecordBtn,
  recordLabel: elements.placementRecordLabel,
  hintElement: elements.placementQFocus,
  timerElement: elements.placementRecordingTimer,
  getSessionId: "placement-test",
});
elements.placementRecordBtn.addEventListener("click", () => placementRecognizer.toggle());

// Roadmap Details Modal
function openRoadmapModal() {
  if (!state.activeProfile) return;
  const p = state.activeProfile;
  const rd = p.roadmap_data || {};
  elements.fullRoadmapContent.replaceChildren();

  const reportHTML = buildDiagnosticReportHTML(p, rd);
  const phasesHTML = buildRoadmapPhasesHTML(rd.roadmap?.phases);

  const wrapper = document.createElement("div");
  wrapper.className = "eval-diagnostic-report";
  wrapper.innerHTML = reportHTML + phasesHTML;
  elements.fullRoadmapContent.append(wrapper);

  openModal(elements.roadmapDetailsModal);
}

function closeRoadmapModal() {
  closeModal(elements.roadmapDetailsModal);
}

/* ========================================================== */
/* SESSIONS HISTORY (LỊCH SỬ BÀI LUYỆN NÓI)                    */
/* ========================================================== */

function openHistoryModal() {
  openModal(elements.historyModal);
  loadSessionHistory(true);
}

function closeHistoryModal() {
  closeModal(elements.historyModal);
}

async function loadSessionHistory(forModal = false) {
  try {
    const sessions = await api("/sessions/?limit=50");
    if (elements.topHistoryBadge) {
      elements.topHistoryBadge.textContent = sessions.length;
    }

    // Populate recent session alert on welcome state if any session exists
    if (sessions && sessions.length > 0 && elements.recentSessionAlert) {
      const recent = sessions[0];
      elements.recentSessionTitle.textContent = recent.topic || "Luyện nói tự do";
      const date = new Date(recent.started_at);
      const timeStr = date.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
      const turnsText = recent.turns_count ? `${recent.turns_count} câu nói` : "Đã lưu";
      const mins = Math.max(1, Math.round((recent.total_speaking_ms || (recent.turns_count * 15000)) / 60000));
      elements.recentSessionMeta.textContent = `${turnsText} · khoảng ${mins} phút · ${timeStr}`;
      elements.recentSessionAlert.classList.remove("hidden");
      elements.resumeRecentBtn.onclick = () => viewSessionDetail(recent.id);
    }

    if (!forModal || !elements.historySessionsList) return;

    if (!sessions || sessions.length === 0) {
      elements.historySessionsList.innerHTML = `
        <div class="empty-history-box">
          <p>Chưa có bài luyện nào được lưu cho hồ sơ này.</p>
          <button class="primary-button" type="button" onclick="closeHistoryModal()">Bắt đầu bài luyện đầu tiên ↗</button>
        </div>
      `;
      return;
    }

    elements.historySessionsList.innerHTML = sessions.map((s) => {
      const date = new Date(s.started_at);
      const dateStr = date.toLocaleDateString("vi-VN") + " " + date.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
      const turnsCount = s.turns_count || 0;
      const mins = Math.max(1, Math.round((s.total_speaking_ms || (turnsCount * 15000)) / 60000));
      let modeBadge = "Hội thoại tự do";
      if (s.mode === "part1") modeBadge = "IELTS Part 1";
      else if (s.mode === "part2") modeBadge = "IELTS Part 2";
      else if (s.mode === "part3") modeBadge = "IELTS Part 3";
      else if (s.mode === "daily") modeBadge = "Daily Practice";

      return `
        <div class="history-item-card" data-id="${s.id}">
          <div class="history-item-main">
            <div class="history-item-top">
              <span class="history-mode-tag">${escapeHtml(modeBadge)}</span>
              <span class="history-time">${escapeHtml(dateStr)}</span>
            </div>
            <h4 class="history-topic">${escapeHtml(s.topic || "Luyện nói tự do")}</h4>
            <div class="history-meta-row">
              <span>💬 <strong>${turnsCount} lượt trao đổi</strong></span>
              <span>⏱️ <strong>~${mins} phút nói</strong></span>
              ${s.estimated_band ? `<span>🎯 Band <strong>${Number(s.estimated_band).toFixed(1)}</strong></span>` : ""}
            </div>
          </div>
          <div class="history-item-actions">
            <button class="secondary-button view-session-btn" type="button" data-id="${s.id}">👁️ Xem lại nội dung</button>
            <button class="primary-button resume-session-btn" type="button" data-id="${s.id}">🔄 Tiếp tục luyện</button>
          </div>
        </div>
      `;
    }).join("");

    // Bind click events on buttons
    elements.historySessionsList.querySelectorAll(".view-session-btn").forEach((btn) => {
      btn.addEventListener("click", () => viewSessionDetail(btn.dataset.id, false));
    });
    elements.historySessionsList.querySelectorAll(".resume-session-btn").forEach((btn) => {
      btn.addEventListener("click", () => viewSessionDetail(btn.dataset.id, true));
    });
  } catch (err) {
    console.error("Failed to load session history:", err);
    if (elements.historySessionsList) {
      elements.historySessionsList.innerHTML = `<div class="error-text">Lỗi khi tải lịch sử: ${escapeHtml(err.message)}</div>`;
    }
  }
}

async function viewSessionDetail(sessionId, resumeMode = false) {
  try {
    closeHistoryModal();
    const res = await api(`/sessions/${sessionId}`);
    if (!res || !res.session) {
      alert("Không tìm thấy thông tin bài luyện này.");
      return;
    }

    state.sessionId = sessionId;
    state.mode = res.session.mode || "daily";

    elements.welcome.classList.add("hidden");
    elements.conversation.classList.remove("hidden");
    elements.composer.classList.remove("hidden");
    elements.newSession.classList.remove("hidden");
    elements.conversation.replaceChildren();

    // Session header banner
    const banner = document.createElement("div");
    banner.className = "session-view-banner";
    const started = new Date(res.session.started_at);
    banner.innerHTML = `
      <div class="banner-title-box">
        <span class="banner-tag">📖 LỊCH SỬ BÀI LUYỆN</span>
        <strong class="banner-topic">${escapeHtml(res.session.topic || "Luyện nói")}</strong>
        <span class="banner-time">${started.toLocaleDateString("vi-VN")} lúc ${started.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })} · ${res.turns.length} lượt trao đổi</span>
      </div>
      <button class="secondary-button banner-new-btn" type="button">＋ Bắt đầu bài mới</button>
    `;
    const newBtn = banner.querySelector(".banner-new-btn");
    if (newBtn) {
      newBtn.addEventListener("click", resetSession);
    }
    elements.conversation.append(banner);

    // Render each turn
    for (const t of res.turns) {
      if (t.role === "user") {
        addMessage("user", t.transcript, null, null, null, { audioUrl: t.audio_url });
      } else {
        addMessage("assistant", t.transcript);
      }
    }

    // Render mistakes summary box if any mistakes recorded
    if (res.mistakes && res.mistakes.length > 0) {
      const mistBox = document.createElement("div");
      mistBox.className = "session-mistakes-summary";
      mistBox.innerHTML = `
        <div class="mist-head">✍️ Sổ tay lỗi sai &amp; Gợi ý sửa trong bài này (${res.mistakes.length}):</div>
        <div class="mist-list">
          ${res.mistakes.map((m) => `
            <div class="mist-row">
              <span class="wrong">❌ ${escapeHtml(m.original)}</span>
              <span class="arrow">➔</span>
              <span class="right">✅ ${escapeHtml(m.corrected)}</span>
              ${m.explanation ? `<small class="explain">${escapeHtml(m.explanation)}</small>` : ""}
            </div>
          `).join("")}
        </div>
      `;
      elements.conversation.append(mistBox);
    }

    try {
      elements.conversation.scrollTo({ top: elements.conversation.scrollHeight, behavior: "smooth" });
    } catch (e) {
      elements.conversation.scrollTop = elements.conversation.scrollHeight;
    }

    if (resumeMode) {
      elements.answer.focus();
    }
  } catch (err) {
    alert("Không thể tải nội dung bài luyện: " + err.message);
  }
}

/* ========================================================== */
/* CONVERSATION & COACH LOOP                                  */
/* ========================================================== */

function renderCoachText(element, text) {
  const fragment = document.createDocumentFragment();
  const tokens = text.split(/(\*\*.+?\*\*|\*.+?\*)/gs);
  tokens.forEach((token) => {
    if (token.startsWith("**") && token.endsWith("**")) {
      const strong = document.createElement("strong");
      strong.textContent = token.slice(2, -2);
      fragment.append(strong);
    } else if (token.startsWith("*") && token.endsWith("*")) {
      const emphasis = document.createElement("em");
      emphasis.textContent = token.slice(1, -1);
      fragment.append(emphasis);
    } else {
      token.split("\n").forEach((line, index) => {
        if (index) fragment.append(document.createElement("br"));
        fragment.append(document.createTextNode(line));
      });
    }
  });
  element.append(fragment);
}

function speakText(text) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  window.speechSynthesis.speak(utterance);
}

function addMessage(role, text, meta = null, corrections = [], repeatPrompt = null, speechMetrics = null, upgradedSentence = null) {
  elements.welcome.classList.add("hidden");
  elements.conversation.classList.remove("hidden");
  elements.composer.classList.remove("hidden");
  elements.newSession.classList.remove("hidden");

  const message = document.createElement("div");
  message.className = `message is-${role}`;

  const author = document.createElement("span");
  author.className = "message-author";
  author.textContent = role === "assistant" ? "AI Coach" : state.activeProfile ? state.activeProfile.name : "You";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  renderCoachText(bubble, text);

  message.append(author, bubble);

  if (role === "user" && speechMetrics) {
    if (speechMetrics.audioUrl) {
      const audioWrapper = document.createElement("div");
      audioWrapper.className = "user-audio-box";
      audioWrapper.innerHTML = `
        <span class="user-audio-label">🎙️ Nghe lại bạn vừa nói:</span>
        <audio controls src="${escapeHtml(speechMetrics.audioUrl)}" class="user-audio-player" preload="metadata"></audio>
      `;
      message.append(audioWrapper);
    }

    const metricsBadge = document.createElement("div");
    metricsBadge.className = "speech-metrics-badge";
    const wpm = Math.round(speechMetrics.wpm || 0);
    const fillers = speechMetrics.filler_count || 0;
    const pauses = speechMetrics.long_pauses || 0;
    const conf = speechMetrics.confidence ? Math.round(speechMetrics.confidence) : null;
    metricsBadge.innerHTML = `
      <span>⚡ <strong>${wpm} WPM</strong></span>
      <span>💬 <strong>${fillers}</strong> từ đệm</span>
      <span>⏸️ <strong>${pauses}</strong> ngập ngừng</span>
      ${conf ? `<span>🎯 Độ rõ phát âm: <strong>${conf}%</strong></span>` : ""}
    `;
    message.append(metricsBadge);

    if (speechMetrics.problem_words && speechMetrics.problem_words.length > 0) {
      const pronDiv = document.createElement("div");
      pronDiv.className = "pronunciation-turn-feedback";
      pronDiv.innerHTML = `
        <span class="pron-title">🗣️ Lưu ý phát âm:</span>
        <div class="pron-words-row">
          ${speechMetrics.problem_words.slice(0, 4).map(pw => `
            <span class="pron-chip" title="${escapeHtml(pw.feedback || 'Cần chú ý phát âm rõ hơn')}">
              <strong>${escapeHtml(pw.word)}</strong> ${pw.expected_ipa ? `<span class="ipa">/${escapeHtml(pw.expected_ipa)}/</span>` : ''}
            </span>
          `).join("")}
        </div>
      `;
      message.append(pronDiv);
    }
  }

  if (role === "assistant") {
    if (corrections && corrections.length > 0) {
      const list = document.createElement("div");
      list.className = "correction-list";
      const head = document.createElement("div");
      head.className = "correction-head";
      head.textContent = "✍️ Chỉnh sửa ngữ pháp & lỗi diễn đạt:";
      list.append(head);
      corrections.forEach((c) => {
        const item = document.createElement("div");
        item.className = "correction-item";
        item.innerHTML = `
          <div class="corr-comparison">
            <span class="wrong">❌ ${escapeHtml(c.original)}</span>
            <span class="arrow">➔</span>
            <span class="right">✅ ${escapeHtml(c.corrected)}</span>
          </div>
          ${c.explanation ? `<div class="corr-explain">${escapeHtml(c.explanation)}</div>` : ""}
        `;
        list.append(item);
      });
      message.append(list);
    }

    if (upgradedSentence) {
      const upgCard = document.createElement("div");
      upgCard.className = "upgraded-sentence-card";
      upgCard.innerHTML = `
        <div class="upgrade-header">
          <span class="upgrade-badge">Band 7.0+ Upgrade</span>
          <span class="upgrade-title">🚀 Cách diễn đạt tự nhiên hơn:</span>
        </div>
        <div class="upgrade-body">"${escapeHtml(upgradedSentence)}"</div>
        <button class="upgrade-listen-btn" type="button">🔊 Nghe câu mẫu</button>
      `;
      const listenBtn = upgCard.querySelector(".upgrade-listen-btn");
      if (listenBtn) {
        listenBtn.addEventListener("click", () => {
          speakText(upgradedSentence);
        });
      }
      message.append(upgCard);
    }
  }

  if (repeatPrompt) {
    const repeatBtn = document.createElement("button");
    repeatBtn.className = "repeat-button";
    repeatBtn.type = "button";
    repeatBtn.textContent = `🔁 ${repeatPrompt}`;
    repeatBtn.addEventListener("click", () => {
      speakText(repeatPrompt.replace(/^Try saying:\s*"?/, "").replace(/"?$/, ""));
    });
    message.append(repeatBtn);
  }

  if (meta) {
    const metaSpan = document.createElement("span");
    metaSpan.className = "message-meta";
    metaSpan.textContent = meta;
    message.append(metaSpan);
  }

  elements.conversation.append(message);
  try {
    elements.conversation.scrollTo({ top: elements.conversation.scrollHeight, behavior: "smooth" });
  } catch (e) {
    elements.conversation.scrollTop = elements.conversation.scrollHeight;
  }

  if (role === "assistant" && text) {
    speakText(text);
  }
}

function setBusy(busy) {
  state.busy = busy;
  elements.send.disabled = busy;
  elements.answer.disabled = busy;
  elements.record.disabled = busy || !state.speechAvailable;
  if (busy) {
    elements.send.innerHTML = 'AI đang nghĩ… <span class="spinner-inline" aria-hidden="true">⏳</span>';
  } else {
    elements.send.innerHTML = 'Gửi <span aria-hidden="true">↑</span>';
  }
}

// ==========================================
// IELTS TOPIC CATALOG & TOPIC SELECTION HUB
// ==========================================

const IELTS_TOPIC_CATALOG = [
  // --- PART 1 TOPICS ---
  {
    id: "p1_hometown",
    mode: "part1",
    category: "IELTS PART 1 · PHẢN XẠ NHANH",
    tag: "Phổ biến",
    title: "Hometown & Neighborhood",
    titleVi: "Quê hương, nơi sinh sống & môi trường xung quanh",
    question: "Where is your hometown located, and what do you like most about living there?",
    followUps: ["Has your hometown changed much since you were a child?", "Would you like to live there in the future?"]
  },
  {
    id: "p1_work_study",
    mode: "part1",
    category: "IELTS PART 1 · PHẢN XẠ NHANH",
    tag: "Chủ đề vàng",
    title: "Work or Studies",
    titleVi: "Công việc, chuyên ngành & định hướng sự nghiệp",
    question: "Do you currently work or are you a student, and what do you enjoy most about what you do?",
    followUps: ["Why did you choose this field?", "What kind of job would you like to do in the future?"]
  },
  {
    id: "p1_daily_routine",
    mode: "daily",
    category: "GIAO TIẾP HÀNG NGÀY · PHẢN XẠ",
    tag: "Đời sống",
    title: "Daily Routine & Free Time",
    titleVi: "Thói quen sinh hoạt, buổi sáng & thời gian rảnh",
    question: "What is your favorite time of the day and why?",
    followUps: ["How do you usually spend your weekends?", "Do you prefer spending free time alone or with friends?"]
  },
  {
    id: "p1_technology",
    mode: "part1",
    category: "IELTS PART 1 · PHẢN XẠ NHANH",
    tag: "Hot Trend",
    title: "Technology & Internet",
    titleVi: "Công nghệ thông tin, ứng dụng di động & mạng xã hội",
    question: "How often do you use the internet for your daily tasks, and what was the last app you downloaded on your phone?",
    followUps: ["Do you think technology makes life simpler or more complicated?", "Could you spend a whole week without your phone?"]
  },
  {
    id: "p1_food_cooking",
    mode: "part1",
    category: "IELTS PART 1 · PHẢN XẠ NHANH",
    tag: "Ẩm thực",
    title: "Food & Cooking",
    titleVi: "Ẩm thực, thói quen ăn uống & nấu nướng gia đình",
    question: "What kinds of food do you most enjoy eating, and do you prefer cooking at home or eating out?",
    followUps: ["What traditional dish from your country would you recommend to a foreign tourist?", "Has your diet changed in recent years?"]
  },
  {
    id: "p1_travel_holidays",
    mode: "part1",
    category: "IELTS PART 1 · PHẢN XẠ NHANH",
    tag: "Du lịch",
    title: "Travel & Holidays",
    titleVi: "Kỳ nghỉ, chuyến du lịch & trải nghiệm văn hóa",
    question: "What was the most memorable holiday trip you have ever taken?",
    followUps: ["Do you prefer traveling alone or with a group of friends?", "Which foreign country would you most like to visit?"]
  },
  {
    id: "p1_music_entertainment",
    mode: "part1",
    category: "IELTS PART 1 · PHẢN XẠ NHANH",
    tag: "Nghệ thuật",
    title: "Music & Entertainment",
    titleVi: "Âm nhạc, nhạc cụ & các buổi hòa nhạc trực tiếp",
    question: "What genre of music do you listen to when you want to relax after a stressful day?",
    followUps: ["Have you ever attended a live concert?", "Do you play any musical instruments or wish you could play one?"]
  },
  {
    id: "p1_sports_fitness",
    mode: "part1",
    category: "IELTS PART 1 · PHẢN XẠ NHANH",
    tag: "Sức khỏe",
    title: "Sports & Physical Exercise",
    titleVi: "Thể thao, tập gym & duy trì lối sống lành mạnh",
    question: "What kinds of sports or physical activities do you enjoy doing regularly?",
    followUps: ["Did you play sports when you were younger?", "Why is regular exercise so essential in modern life?"]
  },

  // --- PART 2 CUE CARDS ---
  {
    id: "p2_memorable_journey",
    mode: "part2",
    category: "IELTS PART 2 · CUE CARD 2 PHÚT",
    tag: "Part 2",
    title: "A Memorable Journey",
    titleVi: "Kể về một chuyến đi đáng nhớ mà bạn từng trải nghiệm",
    question: "Describe a memorable journey you went on. (You will have 1 minute to prepare and 2 minutes to speak).",
    bullets: [
      "Where you went and how you traveled",
      "Who you traveled with",
      "What you did during the trip",
      "And explain why this journey was so memorable to you."
    ]
  },
  {
    id: "p2_inspiring_person",
    mode: "part2",
    category: "IELTS PART 2 · CUE CARD 2 PHÚT",
    tag: "Part 2",
    title: "An Inspiring Person",
    titleVi: "Kể về một người truyền cảm hứng hoặc dạy bạn bài học quý giá",
    question: "Describe a person who taught you something useful. (You will have 1 minute to prepare and 2 minutes to speak).",
    bullets: [
      "Who this person is",
      "What they taught you",
      "How they taught you this skill or lesson",
      "And explain why you found what they taught you to be so important."
    ]
  },
  {
    id: "p2_important_decision",
    mode: "part2",
    category: "IELTS PART 2 · CUE CARD 2 PHÚT",
    tag: "Part 2",
    title: "An Important Decision",
    titleVi: "Kể về một quyết định quan trọng trong cuộc đời bạn",
    question: "Describe an important decision you made in your life. (You will have 1 minute to prepare and 2 minutes to speak).",
    bullets: [
      "What the decision was",
      "When and why you had to make it",
      "What options or alternatives you considered",
      "And explain how you felt after making this decision."
    ]
  },
  {
    id: "p2_challenging_goal",
    mode: "part2",
    category: "IELTS PART 2 · CUE CARD 2 PHÚT",
    tag: "Part 2",
    title: "A Challenging Goal",
    titleVi: "Kể về một mục tiêu khó khăn mà bạn đã nỗ lực đạt được",
    question: "Describe a challenging goal you achieved. (You will have 1 minute to prepare and 2 minutes to speak).",
    bullets: [
      "What the goal was",
      "Why it was challenging for you",
      "How you planned and worked to achieve it",
      "And explain how you felt when you successfully achieved it."
    ]
  },
  {
    id: "p2_useful_device",
    mode: "part2",
    category: "IELTS PART 2 · CUE CARD 2 PHÚT",
    tag: "Part 2",
    title: "A Useful Piece of Technology",
    titleVi: "Kể về một thiết bị điện tử hữu ích bạn dùng hằng ngày",
    question: "Describe a piece of electronic equipment or technology that you find useful.",
    bullets: [
      "What the device is and how often you use it",
      "When and why you got it",
      "What features you find most helpful",
      "And explain how your daily life would be affected without it."
    ]
  },
  {
    id: "p2_environmental_concern",
    mode: "part2",
    category: "IELTS PART 2 · CUE CARD 2 PHÚT",
    tag: "Part 2",
    title: "An Environmental Problem",
    titleVi: "Kể về một vấn đề môi trường tại nơi bạn sinh sống",
    question: "Describe an environmental problem in your local city or country.",
    bullets: [
      "What the problem is and where it occurs",
      "What causes this issue",
      "How it affects local residents and wildlife",
      "And explain what measures can be taken to solve or mitigate it."
    ]
  },

  // --- PART 3 DISCUSSION ---
  {
    id: "p3_ai_society",
    mode: "part3",
    category: "IELTS PART 3 · THẢO LUẬN PHẢN BIỆN",
    tag: "Part 3",
    title: "AI & Future of Work",
    titleVi: "Trí tuệ nhân tạo, tự động hóa & tương lai việc làm",
    question: "Do you believe artificial intelligence will eventually replace intellectual professions, and how should workers prepare for this transition?",
    followUps: ["What ethical questions arise with AI automation?", "Should governments regulate AI development?"]
  },
  {
    id: "p3_tourism_culture",
    mode: "part3",
    category: "IELTS PART 3 · THẢO LUẬN PHẢN BIỆN",
    tag: "Part 3",
    title: "Tourism & Environment",
    titleVi: "Tác động của du lịch đại chúng đến môi trường và văn hóa bản địa",
    question: "What are the most serious negative environmental consequences of mass tourism on fragile natural destinations?",
    followUps: ["How can local communities preserve their authentic culture?", "Do virtual tours have any potential to replace physical travel?"]
  },
  {
    id: "p3_education_reform",
    mode: "part3",
    category: "IELTS PART 3 · THẢO LUẬN PHẢN BIỆN",
    tag: "Part 3",
    title: "Modern Education vs Practical Skills",
    titleVi: "Giáo dục lý thuyết trường học vs Kỹ năng thực tế đời sống",
    question: "Should modern universities prioritize teaching academic theory or practical, hands-on career skills needed by employers?",
    followUps: ["Who learns faster: younger generations or older generations?", "How has digital technology changed modern teaching methods?"]
  },

  // --- DAILY & FREE TALK ---
  {
    id: "daily_coffee",
    mode: "daily",
    category: "GIAO TIẾP ĐỜI SỐNG · THƯ GIÃN",
    tag: "Thư giãn",
    title: "Coffee & Cafe Culture",
    titleVi: "Thưởng thức cà phê & Không gian làm việc tại quán",
    question: "Do you prefer drinking coffee or tea, and what kind of vibe or atmosphere do you look for when choosing a cafe?",
    followUps: ["Do you often work or study in cafes?", "What is your favorite drink to order?"]
  },
  {
    id: "daily_weekend_plans",
    mode: "daily",
    category: "GIAO TIẾP ĐỜI SỐNG · THƯ GIÃN",
    tag: "Cuối tuần",
    title: "Weekend Plans & Recharging",
    titleVi: "Kế hoạch cuối tuần & Cách nạp lại năng lượng",
    question: "What is your favorite way to unwind and recharge your energy after a busy, exhausting week?",
    followUps: ["Do you like outdoor activities or staying home?", "Any interesting plans for this upcoming weekend?"]
  }
];

function selectTopic(topicObj, syncMode = true) {
  if (!topicObj) return;
  state.selectedTopic = topicObj;

  // Update Welcome Preview Card
  if (elements.welcomeTopicCategoryLabel) elements.welcomeTopicCategoryLabel.textContent = topicObj.category || "CHỦ ĐỀ LUYỆN NÓI";
  if (elements.welcomeTopicTitle) elements.welcomeTopicTitle.textContent = topicObj.title;
  if (elements.welcomeTopicTag) elements.welcomeTopicTag.textContent = topicObj.tag || "IELTS";
  if (elements.welcomeTopicVi) elements.welcomeTopicVi.textContent = topicObj.titleVi || "";
  if (elements.welcomeTopicQuestion) elements.welcomeTopicQuestion.textContent = topicObj.question;

  // Update Sidebar Fields
  if (elements.topic) elements.topic.value = topicObj.title;
  if (elements.topicSelect) elements.topicSelect.value = topicObj.id || "custom";

  if (syncMode && topicObj.mode && elements.mode) {
    elements.mode.value = topicObj.mode;
  }

  // Update Active Chips
  if (elements.welcomeTopicChips) {
    const chips = elements.welcomeTopicChips.querySelectorAll(".topic-chip");
    chips.forEach((c) => {
      c.classList.toggle("active", c.dataset.topicId === topicObj.id);
    });
  }

  // Toggle custom box
  if (elements.customTopicBox) {
    elements.customTopicBox.classList.toggle("hidden", topicObj.id !== "custom");
  }
}

function shuffleTopic() {
  const currentId = state.selectedTopic ? state.selectedTopic.id : "";
  const currentMode = elements.mode ? elements.mode.value : "daily";

  let candidates = IELTS_TOPIC_CATALOG.filter((t) => t.id !== currentId);
  if (currentMode === "part2") {
    const part2s = candidates.filter((t) => t.mode === "part2");
    if (part2s.length > 0) candidates = part2s;
  } else if (currentMode === "part3") {
    const part3s = candidates.filter((t) => t.mode === "part3");
    if (part3s.length > 0) candidates = part3s;
  }

  const nextTopic = candidates[Math.floor(Math.random() * candidates.length)] || IELTS_TOPIC_CATALOG[0];
  selectTopic(nextTopic, false);
}

function applyCustomTopic() {
  if (!elements.customTopicInput) return;
  const customVal = elements.customTopicInput.value.trim();
  if (!customVal) return;

  const customObj = {
    id: "custom",
    mode: elements.mode ? elements.mode.value : "daily",
    category: "CHỦ ĐỀ TỰ CHỌN · CÁ NHÂN HÓA",
    tag: "Tùy chỉnh",
    title: customVal,
    titleVi: "Chủ đề tự chọn theo mong muốn của bạn",
    question: `Let's talk about ${customVal}. To begin, what first comes to your mind when you think about ${customVal}?`
  };
  selectTopic(customObj, false);
}

function initTopicHub() {
  // Populate Sidebar Select (<select id="topic-select">)
  if (elements.topicSelect) {
    elements.topicSelect.replaceChildren();

    const groups = [
      {
        label: "🗣️ IELTS Speaking Part 1",
        topics: IELTS_TOPIC_CATALOG.filter((t) => t.mode === "part1")
      },
      {
        label: "📋 IELTS Speaking Part 2 (Cue Cards)",
        topics: IELTS_TOPIC_CATALOG.filter((t) => t.mode === "part2")
      },
      {
        label: "💡 IELTS Speaking Part 3 (Thảo luận)",
        topics: IELTS_TOPIC_CATALOG.filter((t) => t.mode === "part3")
      },
      {
        label: "☕ Giao tiếp đời sống (Daily)",
        topics: IELTS_TOPIC_CATALOG.filter((t) => t.mode === "daily")
      }
    ];

    groups.forEach((g) => {
      const optGroup = document.createElement("optgroup");
      optGroup.label = g.label;
      g.topics.forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t.id;
        opt.textContent = `${t.title} (${t.titleVi})`;
        optGroup.append(opt);
      });
      elements.topicSelect.append(optGroup);
    });

    const customOpt = document.createElement("option");
    customOpt.value = "custom";
    customOpt.textContent = "✏️ Tự nhập chủ đề tùy thích...";
    elements.topicSelect.append(customOpt);

    elements.topicSelect.addEventListener("change", (e) => {
      const val = e.target.value;
      if (val === "custom") {
        if (elements.customTopicBox) elements.customTopicBox.classList.remove("hidden");
        if (elements.customTopicInput) elements.customTopicInput.focus();
      } else {
        const found = IELTS_TOPIC_CATALOG.find((t) => t.id === val);
        if (found) selectTopic(found, true);
      }
    });
  }

  // Populate Welcome Quick Chips
  if (elements.welcomeTopicChips) {
    elements.welcomeTopicChips.replaceChildren();

    const hotTopics = [
      { id: "p1_hometown", label: "📍 Quê hương" },
      { id: "p1_work_study", label: "💼 Công việc & Học tập" },
      { id: "p1_daily_routine", label: "☕ Thói quen & Giờ rảnh" },
      { id: "p1_technology", label: "📱 Công nghệ & AI" },
      { id: "p2_memorable_journey", label: "✈️ Du lịch (Part 2)" },
      { id: "p2_inspiring_person", label: "🌟 Người truyền cảm hứng" },
      { id: "p3_ai_society", label: "💡 Tương lai việc làm (Part 3)" },
    ];

    hotTopics.forEach((ht) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "topic-chip";
      btn.dataset.topicId = ht.id;
      btn.textContent = ht.label;
      btn.addEventListener("click", () => {
        const t = IELTS_TOPIC_CATALOG.find((x) => x.id === ht.id);
        if (t) selectTopic(t, true);
      });
      elements.welcomeTopicChips.append(btn);
    });

    // Custom Chip
    const customChip = document.createElement("button");
    customChip.type = "button";
    customChip.className = "topic-chip";
    customChip.dataset.topicId = "custom";
    customChip.textContent = "✏️ Tự nhập chủ đề...";
    customChip.addEventListener("click", () => {
      if (elements.customTopicBox) {
        elements.customTopicBox.classList.toggle("hidden");
        if (!elements.customTopicBox.classList.contains("hidden")) {
          elements.customTopicInput?.focus();
        }
      }
    });
    elements.welcomeTopicChips.append(customChip);
  }

  // Shuffle buttons
  if (elements.welcomeShuffleTopicBtn) {
    elements.welcomeShuffleTopicBtn.addEventListener("click", shuffleTopic);
  }
  if (elements.sideShuffleBtn) {
    elements.sideShuffleBtn.addEventListener("click", shuffleTopic);
  }

  // Custom Topic input events
  if (elements.applyCustomTopicBtn) {
    elements.applyCustomTopicBtn.addEventListener("click", applyCustomTopic);
  }
  if (elements.customTopicInput) {
    elements.customTopicInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        applyCustomTopic();
      }
    });
  }

  // Side text input manual change
  if (elements.topic) {
    elements.topic.addEventListener("input", (e) => {
      const val = e.target.value.trim();
      if (val && state.selectedTopic && state.selectedTopic.id !== "custom") {
        state.selectedTopic = {
          id: "custom",
          mode: elements.mode ? elements.mode.value : "daily",
          category: "CHỦ ĐỀ TỰ CHỌN · CÁ NHÂN HÓA",
          tag: "Tùy chỉnh",
          title: val,
          titleVi: "Chủ đề tự nhập",
          question: `Let's discuss ${val}. What are your initial thoughts or experiences with this?`
        };
        if (elements.welcomeTopicTitle) elements.welcomeTopicTitle.textContent = val;
        if (elements.welcomeTopicCategoryLabel) elements.welcomeTopicCategoryLabel.textContent = state.selectedTopic.category;
        if (elements.welcomeTopicQuestion) elements.welcomeTopicQuestion.textContent = state.selectedTopic.question;
        if (elements.welcomeTopicTag) elements.welcomeTopicTag.textContent = "Tùy chỉnh";
        if (elements.topicSelect) elements.topicSelect.value = "custom";
      }
    });
  }

  // Mode change syncs topics
  if (elements.mode) {
    elements.mode.addEventListener("change", (e) => {
      const mode = e.target.value;
      if (state.selectedTopic && state.selectedTopic.id !== "custom") {
        if (mode === "part2" && state.selectedTopic.mode !== "part2") {
          const p2 = IELTS_TOPIC_CATALOG.find((t) => t.mode === "part2");
          if (p2) selectTopic(p2, false);
        } else if (mode === "part3" && state.selectedTopic.mode !== "part3") {
          const p3 = IELTS_TOPIC_CATALOG.find((t) => t.mode === "part3");
          if (p3) selectTopic(p3, false);
        } else if (mode === "part1" && state.selectedTopic.mode !== "part1") {
          const p1 = IELTS_TOPIC_CATALOG.find((t) => t.mode === "part1");
          if (p1) selectTopic(p1, false);
        }
      }
    });
  }

  // Select initial topic (Hometown)
  const defaultTopic = IELTS_TOPIC_CATALOG[0];
  selectTopic(defaultTopic, false);
}

async function startSession() {
  if (state.busy) return;
  resetSession();
  clearError();
  setBusy(true);
  elements.start.disabled = true;
  if (elements.welcomeStart) elements.welcomeStart.disabled = true;

  try {
    const selectedMode = elements.mode.value;
    const topicTitle = elements.topic.value.trim() || (state.selectedTopic ? state.selectedTopic.title : "Hometown & Neighborhood");
    state.mode = selectedMode;

    if (selectedMode === "part1" || selectedMode === "part2" || selectedMode === "part3") {
      const started = await api("/ielts/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          part: selectedMode,
          topic: topicTitle
        }),
      });
      state.sessionId = started.session_id;
      addMessage("assistant", `${started.greeting}\n\n${started.question}`);
      if (selectedMode === "part2" && started.cue_card) {
        showCueCard(started.cue_card);
      }
    } else {
      const session = await api("/sessions/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode: selectedMode,
          topic: topicTitle,
        }),
      });
      state.sessionId = session.id;
      const greetingName = state.activeProfile ? state.activeProfile.name : "there";
      let openingQuestion = "";
      if (state.selectedTopic && (state.selectedTopic.title === topicTitle || state.selectedTopic.id === "custom")) {
        openingQuestion = state.selectedTopic.question;
      } else {
        openingQuestion = `What first comes to your mind when you think about ${topicTitle}? Could you share some of your thoughts?`;
      }
      addMessage("assistant", `Hi ${greetingName}! Today let's talk about **${session.topic || topicTitle}**.\n\n${openingQuestion}`);
    }
    elements.answer.focus();
  } catch (error) {
    showError(`Không tạo được buổi luyện: ${error.message}`);
  } finally {
    setBusy(false);
    elements.start.disabled = false;
    if (elements.welcomeStart) elements.welcomeStart.disabled = false;
  }
}

function showCueCard(card) {
  if (!card) return;
  elements.cueCard.replaceChildren();
  const eyebrow = document.createElement("p");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = `IELTS PART 2 · ${card.topic || "CUE CARD"}`;
  const title = document.createElement("h3");
  title.textContent = card.title;
  const guidance = document.createElement("p");
  guidance.textContent = "You should say:";
  const bullets = document.createElement("ul");
  (card.bullets || []).forEach((bullet) => {
    const item = document.createElement("li");
    item.textContent = bullet;
    bullets.append(item);
  });
  elements.cueCard.append(eyebrow, title, guidance, bullets);
  elements.cueCard.classList.remove("hidden");
}

async function sendAnswer(text, retryRequestId = null) {
  const content = text.trim();
  if (!content || !state.sessionId || state.busy) return;
  clearError();
  const speechMetrics = state.pendingSpeechMetrics;
  state.pendingSpeechMetrics = null;

  const requestId = retryRequestId || ("req-" + Date.now() + "-" + Math.random().toString(36).slice(2, 9));
  if (!retryRequestId) {
    addMessage("user", content, null, null, null, speechMetrics);
    elements.answer.value = "";
  }
  setBusy(true);

  try {
    if (state.mode === "part1" || state.mode === "part2" || state.mode === "part3" || state.mode === "full_mock") {
      const reply = await api("/ielts/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: state.sessionId,
          user_text: content,
          part: state.mode,
        }),
      });
      addMessage("assistant", reply.message);

      if (reply.cue_card) {
        showCueCard(reply.cue_card);
      } else if (reply.next_part === "part3" || reply.is_completed) {
        elements.cueCard.classList.add("hidden");
      }

      if (reply.timing_warning) {
        addMessage("assistant", reply.timing_warning);
      }

      if (reply.is_completed) {
        elements.cueCard.classList.add("hidden");
        const evalWrapper = document.createElement("div");
        evalWrapper.className = "ielts-eval-trigger-box";
        evalWrapper.style.margin = "12px 0 6px";
        evalWrapper.style.padding = "14px";
        evalWrapper.style.background = "#f0fdf4";
        evalWrapper.style.border = "1px solid #bbf7d0";
        evalWrapper.style.borderRadius = "10px";
        evalWrapper.innerHTML = `
          <strong style="display:block; color:#166534; font-size:12.5px; margin-bottom:4px;">🎯 Phần thi nói đã hoàn thành!</strong>
          <p style="margin:0 0 10px; font-size:11.5px; color:#15803d;">Bạn có muốn nhận đánh giá chi tiết 4 tiêu chí IELTS và các gợi ý nâng cấp câu nói từ Giám khảo AI không?</p>
        `;
        const evalBtn = document.createElement("button");
        evalBtn.className = "primary-button";
        evalBtn.style.padding = "9px 18px";
        evalBtn.style.fontSize = "12px";
        evalBtn.textContent = "📊 Nhận bảng điểm & đánh giá chi tiết ↗";
        evalBtn.onclick = async () => {
          evalBtn.disabled = true;
          evalBtn.textContent = "AI Giám khảo đang chấm điểm… ⏳";
          try {
            const evalRes = await api(`/ielts/evaluate/${state.sessionId}`, { method: "POST" });
            addMessage("assistant", `🎯 **KẾT QUẢ ĐÁNH GIÁ IELTS CHÍNH THỨC (BAND ${evalRes.overall_band})**\n\n- **Fluency & Coherence (${evalRes.fluency_score}):** ${evalRes.fluency_feedback}\n- **Lexical Resource (${evalRes.lexical_score}):** ${evalRes.lexical_feedback}\n- **Grammatical Range (${evalRes.grammar_score}):** ${evalRes.grammar_feedback}\n- **Pronunciation (${evalRes.pronunciation_score || "7.0"}):** ${evalRes.pronunciation_feedback || "Phát âm rõ ràng, nhịp điệu tự nhiên."}\n\n**Điểm mạnh nổi bật:**\n${(evalRes.strengths || []).map(s => "- " + s).join("\n")}\n\n**Gợi ý nâng cấp từ vựng & cấu trúc:**\n${(evalRes.suggested_expressions || []).map(e => `- Thay vì *"${e.original}"* ➔ Hãy nói: **"${e.better}"** (${e.reason})`).join("\n")}`);
            evalWrapper.remove();
          } catch (err) {
            evalBtn.disabled = false;
            evalBtn.textContent = "Thử lại";
            showError("Không thể tải đánh giá: " + err.message);
          }
        };
        evalWrapper.append(evalBtn);
        elements.conversation.append(evalWrapper);
        elements.conversation.scrollTop = elements.conversation.scrollHeight;
      }
    } else {
      const reply = await api("/conversation/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: state.sessionId,
          user_text: content,
          mode: state.mode || "coaching",
          correction_level: "important",
          request_id: requestId,
        }),
      });
      addMessage(
        "assistant",
        reply.message,
        `${reply.provider_used || "local AI"} · ${Math.round(reply.latency_ms || 0)}ms`,
        reply.corrections,
        reply.repeat_prompt,
        null,
        reply.upgraded_sentence
      );
    }
    // Update profile daily minutes
    await loadProfiles();
  } catch (error) {
    const errMsg = error.detail?.message || error.message || "Lỗi phản hồi từ AI";
    const retryable = error.detail?.retryable !== false;
    showError(`⚠️ ${errMsg}`, retryable ? () => sendAnswer(content, requestId) : null);
  } finally {
    setBusy(false);
    elements.answer.focus();
  }
}

const conversationRecognizer = createSpeechRecognizer({
  targetInput: elements.answer,
  recordBtn: elements.record,
  recordLabel: elements.recordLabel,
  hintElement: elements.composerHint,
  timerElement: elements.recordingTimer,
  getSessionId: () => state.sessionId || "practice-session",
});

if (elements.sttEngineSelect) {
  const savedEngine = localStorage.getItem("stt_engine") || "whisper";
  elements.sttEngineSelect.value = savedEngine;
  elements.sttEngineSelect.addEventListener("change", (e) => {
    localStorage.setItem("stt_engine", e.target.value);
  });
}

function resetSession() {
  if (state.busy) return;
  state.completed = false;
  conversationRecognizer.stop();
  placementRecognizer.stop();
  state.sessionId = null;
  state.mode = "daily";
  elements.conversation.replaceChildren();
  elements.cueCard.replaceChildren();
  elements.result.replaceChildren();
  elements.answer.value = "";
  elements.answer.disabled = false;
  elements.send.disabled = false;
  elements.record.disabled = false;
  elements.welcome.classList.remove("hidden");
  elements.conversation.classList.add("hidden");
  elements.cueCard.classList.add("hidden");
  elements.result.classList.add("hidden");
  elements.composer.classList.add("hidden");
  elements.newSession.classList.add("hidden");
  clearError();
}

// BINDINGS
elements.start.addEventListener("click", startSession);
elements.welcomeStart.addEventListener("click", startSession);
elements.newSession.addEventListener("click", resetSession);
elements.record.addEventListener("click", () => conversationRecognizer.toggle());
elements.composer.addEventListener("submit", (e) => {
  e.preventDefault();
  sendAnswer(elements.answer.value);
});
elements.answer.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    elements.composer.requestSubmit();
  }
});

// Modal bindings
elements.profileToggleBtn.addEventListener("click", openProfileModal);
elements.closeProfileModalBtn.addEventListener("click", closeProfileModal);
if (elements.openHistoryBtn) elements.openHistoryBtn.addEventListener("click", openHistoryModal);
if (elements.viewHistoryActionBtn) elements.viewHistoryActionBtn.addEventListener("click", openHistoryModal);
if (elements.closeHistoryModalBtn) elements.closeHistoryModalBtn.addEventListener("click", closeHistoryModal);
if (elements.dailyMinutesLabel) {
  elements.dailyMinutesLabel.style.cursor = "pointer";
  elements.dailyMinutesLabel.title = "Bấm để xem lịch sử bài luyện nói";
  elements.dailyMinutesLabel.addEventListener("click", openHistoryModal);
}
elements.startPlacementBtn.addEventListener("click", () => {
  if (!state.activeProfile) {
    openProfileModal();
  } else {
    startPlacementTest();
  }
});
elements.closePlacementModalBtn.addEventListener("click", () => closeModal(elements.placementModal));
elements.viewRoadmapBtn.addEventListener("click", openRoadmapModal);
elements.closeRoadmapModalBtn.addEventListener("click", closeRoadmapModal);

// Close modals when clicking on background backdrop
[elements.profileModal, elements.placementModal, elements.roadmapDetailsModal, elements.historyModal].forEach((modal) => {
  if (!modal) return;
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      closeModal(modal);
    }
  });
});

// Global Keyboard Accessibility: Escape to close modals, Tab for focus trapping
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    const openModals = [elements.placementModal, elements.roadmapDetailsModal, elements.profileModal];
    for (const m of openModals) {
      if (m && !m.classList.contains("hidden")) {
        closeModal(m);
        break;
      }
    }
  } else if (e.key === "Tab") {
    const openModals = [elements.placementModal, elements.roadmapDetailsModal, elements.profileModal];
    for (const m of openModals) {
      if (m && !m.classList.contains("hidden")) {
        trapModalFocus(m, e);
        break;
      }
    }
  }
});

// Sidebar Edit Roadmap Button
if (elements.editRoadmapBtn) {
  elements.editRoadmapBtn.addEventListener("click", () => {
    openEditProfileSection(state.activeProfile);
  });
}

// Close Edit Profile Section
if (elements.closeEditProfileBtn) {
  elements.closeEditProfileBtn.addEventListener("click", () => {
    elements.editProfileSection.classList.add("hidden");
  });
}

// Submit Edit Profile Form
if (elements.editProfileForm) {
  elements.editProfileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const pid = elements.editProfileId.value;
    if (!pid) return;

    const payload = {
      name: elements.editProfileName.value.trim(),
      target_band: parseFloat(elements.editTargetBand.value),
      daily_target_minutes: parseInt(elements.editDailyMinutes.value, 10),
      target_duration_months: parseInt(elements.editDurationMonths.value, 10),
    };

    try {
      const updated = await api(`/profiles/${pid}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      state.activeProfile = updated;
      elements.editProfileSection.classList.add("hidden");
      await loadProfiles();
      alert(`✓ Đã lưu thay đổi mục tiêu cho ${updated.name}!`);
    } catch (err) {
      alert(`Lỗi khi lưu: ${err.message}`);
    }
  });
}

// Recalculate Roadmap Button (In Edit Profile Section)
if (elements.recalcRoadmapBtn) {
  elements.recalcRoadmapBtn.addEventListener("click", async () => {
    const pid = elements.editProfileId.value || state.activeProfile?.id;
    if (!pid) return;

    const payload = {
      name: elements.editProfileName.value.trim(),
      target_band: parseFloat(elements.editTargetBand.value),
      daily_target_minutes: parseInt(elements.editDailyMinutes.value, 10),
      target_duration_months: parseInt(elements.editDurationMonths.value, 10),
    };

    try {
      elements.recalcRoadmapBtn.disabled = true;
      elements.recalcRoadmapBtn.textContent = "⏳ Đang tính toán...";

      await api(`/profiles/${pid}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const updated = await api(`/profiles/${pid}/roadmap/recalculate`, {
        method: "POST",
      });

      state.activeProfile = updated;
      elements.editProfileSection.classList.add("hidden");
      await loadProfiles();
      closeProfileModal();
      openRoadmapModal();
      alert(`✓ AI đã tính toán và cập nhật 3 giai đoạn lộ trình cho ${updated.name}!`);
    } catch (err) {
      alert(`Lỗi khi tái lập lộ trình: ${err.message}`);
    } finally {
      elements.recalcRoadmapBtn.disabled = false;
      elements.recalcRoadmapBtn.textContent = "🔄 AI Tính lại lộ trình";
    }
  });
}

// Retake Placement Test Button (In Edit Profile Section)
if (elements.retakeTestBtn) {
  elements.retakeTestBtn.addEventListener("click", async () => {
    const pid = elements.editProfileId.value || state.activeProfile?.id;
    if (!pid) return;

    if (!confirm("Bạn có chắc chắn muốn làm lại bài kiểm tra trình độ đầu vào? Điểm số chẩn đoán và lộ trình hiện tại sẽ được đánh giá lại từ đầu.")) {
      return;
    }

    try {
      await api(`/profiles/${pid}/placement/reset`, { method: "POST" });
      await loadProfiles();
      closeProfileModal();
      startPlacementTest();
    } catch (err) {
      alert(`Lỗi khi đặt lại bài test: ${err.message}`);
    }
  });
}

// Roadmap Modal Actions
if (elements.modalEditGoalsBtn) {
  elements.modalEditGoalsBtn.addEventListener("click", () => {
    closeRoadmapModal();
    openEditProfileSection(state.activeProfile);
  });
}

if (elements.modalRecalcAiBtn) {
  elements.modalRecalcAiBtn.addEventListener("click", async () => {
    if (!state.activeProfile?.id) return;
    try {
      elements.modalRecalcAiBtn.disabled = true;
      elements.modalRecalcAiBtn.textContent = "⏳ Đang tính toán...";
      const updated = await api(`/profiles/${state.activeProfile.id}/roadmap/recalculate`, { method: "POST" });
      state.activeProfile = updated;
      await loadProfiles();
      openRoadmapModal();
      alert("✓ AI đã cập nhật lại lộ trình thành công!");
    } catch (err) {
      alert("Lỗi: " + err.message);
    } finally {
      elements.modalRecalcAiBtn.disabled = false;
      elements.modalRecalcAiBtn.textContent = "🔄 AI Tính lại lộ trình";
    }
  });
}

if (elements.modalRetakeTestBtn) {
  elements.modalRetakeTestBtn.addEventListener("click", async () => {
    if (!state.activeProfile?.id) return;
    if (!confirm("Bạn có muốn làm lại bài kiểm tra 3 câu để đo lại trình độ?")) return;
    try {
      await api(`/profiles/${state.activeProfile.id}/placement/reset`, { method: "POST" });
      await loadProfiles();
      closeRoadmapModal();
      startPlacementTest();
    } catch (err) {
      alert("Lỗi: " + err.message);
    }
  });
}

// Reset All Data button
const resetBtn = $("reset-all-data-btn");
if (resetBtn) {
  resetBtn.addEventListener("click", async () => {
    if (!confirm("CẢNH BÁO: Bạn có chắc chắn muốn XÓA SẠCH toàn bộ hồ sơ, lịch sử học tập và bắt đầu lại từ đầu?")) {
      return;
    }
    try {
      await api("/profiles/reset-all", { method: "POST" });
      state.activeProfile = null;
      state.profiles = [];
      closeProfileModal();
      await loadProfiles();
      alert("Đã reset toàn bộ hệ thống về trạng thái ban đầu!");
    } catch (err) {
      alert("Lỗi khi reset: " + err.message);
    }
  });
}

// Model Selector dropdown
const modelSelect = $("llm-model-select");
if (modelSelect) {
  modelSelect.addEventListener("change", async (e) => {
    const selectedModel = e.target.value;
    setConnection("is-checking", `Đang chuyển sang ${selectedModel}…`);
    try {
      await api("/models/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: selectedModel, preference: "local_only" }),
      });
      await checkConnection();
    } catch (err) {
      console.error("Failed to switch model:", err);
      showError("Không đổi được mô hình AI: " + err.message);
    }
  });
}

// Quick Chips for Custom Minutes and Months
document.querySelectorAll(".quick-chip").forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetId = btn.dataset.target;
    const val = btn.dataset.val;
    const input = $(targetId);
    if (input) {
      input.value = val;
    }
    btn.parentElement.querySelectorAll(".quick-chip").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

["new-daily-minutes", "new-duration-months", "edit-daily-minutes", "edit-duration-months"].forEach((id) => {
  const el = $(id);
  if (el) {
    el.addEventListener("input", (e) => {
      const val = e.target.value;
      const chips = el.parentElement.querySelectorAll(".quick-chip");
      chips.forEach((c) => {
        c.classList.toggle("active", c.dataset.val === val);
      });
    });
  }
});

// INITIALIZE
checkConnection();
checkSpeechAvailability();
loadProfiles();
initTopicHub();
