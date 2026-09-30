const API = "/api/v1";
const state = { sessionId: null, mode: "daily", busy: false, completed: false, recorder: null, stream: null, chunks: [], speechAvailable: false };

const $ = (id) => document.getElementById(id);
const elements = {
  status: $("connection-status"), statusLabel: $("connection-label"),
  mode: $("practice-mode"), topic: $("topic"), start: $("start-session"), welcomeStart: $("welcome-start"),
  welcome: $("welcome-state"), conversation: $("conversation"), cueCard: $("cue-card"), result: $("result-card"),
  composer: $("composer"), answer: $("answer"), send: $("send-button"), record: $("record-button"),
  recordLabel: $("record-label"), error: $("error-message"), newSession: $("new-session"),
  composerHint: $("composer-hint"),
  speechNote: $("speech-note"),
};

async function api(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 150000);
  try {
    const response = await fetch(`${API}${path}`, { ...options, signal: controller.signal });
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
    elements.record.title = state.speechAvailable ? "Ghi âm câu trả lời" : status.message;
    elements.speechNote.textContent = state.speechAvailable
      ? "Bản ghi âm được gửi tới backend local để nhận dạng bằng Whisper."
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
}

function showError(message) {
  elements.error.textContent = message;
  elements.error.classList.remove("hidden");
}

function clearError() {
  elements.error.textContent = "";
  elements.error.classList.add("hidden");
}

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

function setBusy(busy) {
  state.busy = busy;
  elements.answer.disabled = busy || state.completed;
  elements.start.disabled = busy;
  elements.newSession.disabled = busy;
  elements.mode.disabled = busy;
  elements.topic.disabled = busy;
  elements.send.disabled = busy || elements.answer.disabled;
  elements.record.disabled = busy || elements.answer.disabled || !state.speechAvailable;
  elements.welcomeStart.disabled = busy;
  elements.send.innerHTML = busy ? "Đang nghĩ <span aria-hidden=\"true\">…</span>" : 'Gửi <span aria-hidden="true">↑</span>';
}

function addMessage(role, text, metadata = null) {
  const article = document.createElement("article");
  article.className = `message ${role === "user" ? "is-user" : "is-assistant"}`;

  const author = document.createElement("span");
  author.className = "message-author";
  author.textContent = role === "user" ? "YOU" : (state.mode === "part2" ? "IELTS EXAMINER" : "AI COACH");

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  if (role === "assistant") renderCoachText(bubble, text);
  else bubble.textContent = text;
  article.append(author, bubble);

  if (metadata?.corrections?.length) {
    const list = document.createElement("div");
    list.className = "correction-list";
    metadata.corrections.forEach((correction) => {
      const item = document.createElement("div");
      item.className = "correction-item";
      const wrong = document.createElement("span");
      wrong.className = "wrong";
      wrong.textContent = correction.original;
      const right = document.createElement("span");
      right.className = "right";
      right.textContent = correction.corrected;
      const explanation = document.createElement("span");
      explanation.textContent = ` — ${correction.explanation || "Cách diễn đạt tự nhiên hơn."}`;
      item.append(wrong, document.createTextNode(" → "), right, explanation);
      list.append(item);
    });
    article.append(list);
  }

  if (metadata?.repeat_prompt) {
    const repeat = document.createElement("button");
    repeat.type = "button";
    repeat.className = "repeat-button";
    repeat.textContent = `${metadata.repeat_prompt} · Luyện lại`;
    repeat.addEventListener("click", () => {
      elements.answer.value = metadata.repeat_prompt.replace(/^Try saying:\s*[“\"]?|[”\"]$/g, "");
      elements.answer.focus();
    });
    article.append(repeat);
  }

  if (metadata?.provider_used) {
    const info = document.createElement("span");
    info.className = "message-meta";
    const latency = Number.isFinite(metadata.latency_ms) ? ` · ${(metadata.latency_ms / 1000).toFixed(1)}s` : "";
    info.textContent = `${metadata.provider_used}${latency}`;
    article.append(info);
  }

  elements.conversation.append(article);
  elements.conversation.scrollTop = elements.conversation.scrollHeight;
  elements.welcome.classList.add("hidden");
  elements.conversation.classList.remove("hidden");
  elements.composer.classList.remove("hidden");
  elements.newSession.classList.remove("hidden");
  return article;
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
  const timing = document.createElement("p");
  timing.textContent = "Take one minute to prepare, then speak for one to two minutes.";
  elements.cueCard.append(eyebrow, title, guidance, bullets, timing);
  elements.cueCard.classList.remove("hidden");
}

async function startSession() {
  if (state.busy) return;
  resetSession();
  clearError();
  setBusy(true);
  elements.start.disabled = true;
  try {
    const selectedMode = elements.mode.value;
    if (selectedMode === "part2") {
      const started = await api("/ielts/start", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ part: "part2" }),
      });
      state.sessionId = started.session_id;
      state.mode = "part2";
      addMessage("assistant", `${started.greeting}\n\n${started.question}`);
      showCueCard(started.cue_card);
    } else {
      const session = await api("/sessions/", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: "daily", topic: elements.topic.value.trim() || "Daily conversation" }),
      });
      state.sessionId = session.id;
      state.mode = "daily";
      addMessage("assistant", `Hi! Let's talk about ${session.topic || "your day"}. What has been the best part of your week so far?`);
    }
    elements.answer.focus();
  } catch (error) {
    showError(`Không tạo được buổi luyện: ${error.message}`);
  } finally {
    setBusy(false);
    elements.start.disabled = false;
  }
}

function renderEvaluation(report) {
  elements.result.replaceChildren();
  const head = document.createElement("div");
  head.className = "result-head";
  const title = document.createElement("div");
  title.innerHTML = '<p class="eyebrow">YOUR PRACTICE ESTIMATE</p><strong>Ước lượng IELTS Speaking</strong>';
  const band = document.createElement("span");
  band.className = "result-band";
  band.textContent = Number(report.overall_band).toFixed(1);
  head.append(title, band);
  const summary = document.createElement("p");
  summary.textContent = report.examiner_summary;
  const feedback = document.createElement("p");
  feedback.textContent = `Fluency ${report.fluency_score}: ${report.fluency_feedback} · Vocabulary ${report.lexical_score}: ${report.lexical_feedback} · Grammar ${report.grammar_score}: ${report.grammar_feedback}`;
  const disclaimer = document.createElement("small");
  disclaimer.textContent = report.disclaimer || "Estimated score — not an official IELTS result.";
  elements.result.append(head, summary, feedback, disclaimer);
  elements.result.classList.remove("hidden");
}

async function sendAnswer(text) {
  const answer = text.trim();
  if (!answer || !state.sessionId || state.busy) return;
  clearError();
  const userMessage = addMessage("user", answer);
  let accepted = false;
  elements.answer.value = "";
  setBusy(true);
  try {
    if (state.mode === "part2") {
      const reply = await api("/ielts/respond", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: state.sessionId, user_text: answer, part: "part2" }),
      });
      accepted = true;
      addMessage("assistant", reply.message);
      if (reply.is_completed) {
        const report = await api(`/ielts/evaluate/${encodeURIComponent(state.sessionId)}`, { method: "POST" });
        renderEvaluation(report);
        state.completed = true;
        elements.answer.disabled = true;
        elements.send.disabled = true;
        elements.record.disabled = true;
      }
    } else {
      const reply = await api("/conversation/respond", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: state.sessionId, user_text: answer, mode: "daily" }),
      });
      accepted = true;
      addMessage("assistant", reply.message, reply);
    }
  } catch (error) {
    if (!accepted) {
      userMessage.remove();
      elements.answer.value = answer;
    }
    showError(`Chưa nhận được phản hồi: ${error.message}${!accepted ? " Câu trả lời đã được giữ lại; bạn có thể gửi lại." : ""}`);
  } finally {
    setBusy(false);
    if (!state.completed) elements.answer.focus();
  }
}

async function uploadRecording(blob) {
  if (!blob.size) {
    showError("Bản ghi rỗng. Hãy thử ghi âm lại hoặc gõ câu trả lời.");
    setBusy(false);
    return;
  }
  const extension = blob.type.includes("mp4") ? "m4a" : "webm";
  const form = new FormData();
  form.append("audio", blob, `speaking-answer.${extension}`);
  form.append("session_id", state.sessionId);
  try {
    const transcript = await api("/speech/transcribe", { method: "POST", body: form });
    if (!transcript.text?.trim()) throw new Error("Không nhận diện được lời nói. Hãy thử lại hoặc gõ câu trả lời.");
    setBusy(false);
    await sendAnswer(transcript.text);
  } catch (error) {
    if (error.message.toLowerCase().includes("whisper") || error.message.toLowerCase().includes("faster-whisper")) {
      state.speechAvailable = false;
      elements.record.disabled = true;
      elements.composerHint.textContent = "Ghi âm chưa dùng được trên backend này. Bạn vẫn có thể gõ câu trả lời.";
    }
    setBusy(false);
    showError(`Không xử lý được bản ghi: ${error.message}`);
  }
}

async function toggleRecording() {
  if (state.recorder?.state === "recording") {
    elements.recordLabel.textContent = "Đang xử lý…";
    state.recorder.stop();
    return;
  }
  if (!state.speechAvailable) {
    showError("Nhận dạng giọng nói chưa sẵn sàng trên backend. Bạn vẫn có thể gõ câu trả lời tiếng Anh.");
    return;
  }
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    showError("Trình duyệt này chưa hỗ trợ ghi âm. Bạn vẫn có thể gõ câu trả lời vào ô bên dưới.");
    return;
  }
  clearError();
  try {
    state.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.chunks = [];
    state.recorder = new MediaRecorder(state.stream);
    state.recorder.ondataavailable = (event) => { if (event.data.size) state.chunks.push(event.data); };
    state.recorder.onstop = async () => {
      const blob = new Blob(state.chunks, { type: state.recorder.mimeType || "audio/webm" });
      state.stream?.getTracks().forEach((track) => track.stop());
      state.stream = null;
      elements.record.classList.remove("is-recording");
      elements.recordLabel.textContent = "Ghi âm";
      setBusy(true);
      await uploadRecording(blob);
    };
    state.recorder.start();
    elements.record.classList.add("is-recording");
    elements.recordLabel.textContent = "Dừng ghi";
  } catch (error) {
    showError(`Không mở được microphone: ${error.message}`);
  }
}

function resetSession() {
  if (state.busy) return;
  state.completed = false;
  if (state.recorder?.state === "recording") {
    state.recorder.onstop = null;
    state.recorder.stop();
    state.stream?.getTracks().forEach((track) => track.stop());
  }
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

elements.start.addEventListener("click", startSession);
elements.welcomeStart.addEventListener("click", startSession);
elements.newSession.addEventListener("click", resetSession);
elements.record.addEventListener("click", toggleRecording);
elements.composer.addEventListener("submit", (event) => {
  event.preventDefault();
  sendAnswer(elements.answer.value);
});
elements.answer.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    elements.composer.requestSubmit();
  }
});

checkConnection();
checkSpeechAvailability();
