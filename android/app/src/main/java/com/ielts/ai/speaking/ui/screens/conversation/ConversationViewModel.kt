package com.ielts.ai.speaking.ui.screens.conversation

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ielts.ai.speaking.core.audio.AudioRecorder
import com.ielts.ai.speaking.core.audio.TtsManager
import com.ielts.ai.speaking.core.network.models.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

data class MessageItem(
    val id: String,
    val role: String,
    val text: String,
    val corrections: List<CorrectionDto> = emptyList(),
    val repeatPrompt: String? = null,
    val timestamp: Long = System.currentTimeMillis(),
    val pronunciation: PronunciationReportDto? = null
)

class ConversationViewModel : ViewModel() {
    private val _messages = MutableStateFlow<List<MessageItem>>(emptyList())
    val messages: StateFlow<List<MessageItem>> = _messages.asStateFlow()

    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording.asStateFlow()

    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()
    
    private val _isSpeakingTts = MutableStateFlow(false)
    val isSpeakingTts: StateFlow<Boolean> = _isSpeakingTts.asStateFlow()
    
    private val _autoPlayTts = MutableStateFlow(true)
    val autoPlayTts: StateFlow<Boolean> = _autoPlayTts.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    // Phase 5: Pronunciation Engine State
    private val _selectedWordPronunciation = MutableStateFlow<WordPronunciationDto?>(null)
    val selectedWordPronunciation: StateFlow<WordPronunciationDto?> = _selectedWordPronunciation.asStateFlow()

    private val _drillResult = MutableStateFlow<PronunciationDrillResponseDto?>(null)
    val drillResult: StateFlow<PronunciationDrillResponseDto?> = _drillResult.asStateFlow()

    private val _isDrilling = MutableStateFlow(false)
    val isDrilling: StateFlow<Boolean> = _isDrilling.asStateFlow()

    // Phase 3: IELTS State
    private val _isIeltsCompleted = MutableStateFlow(false)
    val isIeltsCompleted: StateFlow<Boolean> = _isIeltsCompleted.asStateFlow()

    private val _prepSeconds = MutableStateFlow(60)
    val prepSeconds: StateFlow<Int> = _prepSeconds.asStateFlow()

    private val _speakingSeconds = MutableStateFlow(120)
    val speakingSeconds: StateFlow<Int> = _speakingSeconds.asStateFlow()

    private val _timerPhase = MutableStateFlow("idle") // idle, prep, speaking, ended
    val timerPhase: StateFlow<String> = _timerPhase.asStateFlow()

    private var prepJob: kotlinx.coroutines.Job? = null
    private var speakingJob: kotlinx.coroutines.Job? = null

    private val ttsManager = TtsManager()
    private val audioRecorder = AudioRecorder()
    private var recordingFile: File? = null

    fun loadSession(sessionId: String) {
        viewModelScope.launch {
            try {
                val detail = ApiClient.getService().getSession(sessionId)
                if (_messages.value.isEmpty() && detail.turns.isNotEmpty()) {
                    val loaded = detail.turns.map { t ->
                        MessageItem(
                            id = t.id ?: System.currentTimeMillis().toString(),
                            role = t.role,
                            text = t.transcript
                        )
                    }
                    _messages.value = loaded
                    
                    // If initial turn is assistant greeting, read it
                    if (_autoPlayTts.value && loaded.size == 1 && loaded[0].role == "assistant") {
                        ttsManager.speak(
                            text = loaded[0].text,
                            onStart = { _isSpeakingTts.value = true },
                            onDone = { _isSpeakingTts.value = false }
                        )
                    }
                }
            } catch (e: Exception) {
                // Ignore load error if brand new session
            }
        }
    }

    fun startPrepTimer() {
        prepJob?.cancel()
        _prepSeconds.value = 60
        _timerPhase.value = "prep"
        prepJob = viewModelScope.launch {
            while (_prepSeconds.value > 0) {
                kotlinx.coroutines.delay(1000)
                _prepSeconds.value -= 1
            }
            startSpeakingTimer()
        }
    }

    fun startSpeakingTimer() {
        prepJob?.cancel()
        speakingJob?.cancel()
        _speakingSeconds.value = 120
        _timerPhase.value = "speaking"
        speakingJob = viewModelScope.launch {
            while (_speakingSeconds.value > 0) {
                kotlinx.coroutines.delay(1000)
                _speakingSeconds.value -= 1
            }
            _timerPhase.value = "ended"
        }
    }


    fun initTts(context: Context) {
        ttsManager.init(context) { /* ready */ }
    }

    fun setAutoPlayTts(enabled: Boolean) {
        _autoPlayTts.value = enabled
        if (!enabled) {
            ttsManager.stop()
            _isSpeakingTts.value = false
        }
    }

    fun toggleRecording(context: Context, sessionId: String, mode: String) {
        if (_isRecording.value) {
            // Stop recording & transcribe
            _isRecording.value = false
            val audioFile = audioRecorder.stopRecording()
            if (audioFile != null && audioFile.exists() && audioFile.length() > 0) {
                transcribeAndSend(audioFile, sessionId, mode)
            }
        } else {
            // Start recording
            try {
                val cacheDir = context.cacheDir
                val file = File(cacheDir, "audio_${System.currentTimeMillis()}.m4a")
                recordingFile = file
                audioRecorder.startRecording(file)
                _isRecording.value = true
            } catch (e: Exception) {
                _error.value = "Failed to start recording: ${e.localizedMessage}"
            }
        }
    }

    private fun transcribeAndSend(file: File, sessionId: String, mode: String) {
        viewModelScope.launch {
            _isProcessing.value = true
            try {
                val reqBody = file.asRequestBody("audio/mp4".toMediaTypeOrNull())
                val part = MultipartBody.Part.createFormData("audio", file.name, reqBody)
                val sessionPart = sessionId.toRequestBody("text/plain".toMediaTypeOrNull())

                val transcribeRes = ApiClient.getService().transcribeAudio(part, sessionPart)
                if (transcribeRes.text.isNotBlank()) {
                    sendMessage(transcribeRes.text, sessionId, mode, transcribeRes.pronunciation)
                } else {
                    _error.value = "No speech detected in audio."
                    _isProcessing.value = false
                }
            } catch (e: Exception) {
                _error.value = "Transcription error: ${e.localizedMessage}"
                _isProcessing.value = false
            }
        }
    }

    fun sendMessage(
        text: String,
        sessionId: String,
        mode: String,
        pronunciation: PronunciationReportDto? = null
    ) {
        if (text.isBlank()) return
        
        val userMsg = MessageItem(
            id = System.currentTimeMillis().toString(),
            role = "user",
            text = text,
            pronunciation = pronunciation
        )
        _messages.value = _messages.value + userMsg
        
        _isProcessing.value = true
        _error.value = null

        viewModelScope.launch {
            try {
                if (mode.lowercase().contains("ielts")) {
                    val part = when {
                        mode.contains("part2") -> "part2"
                        mode.contains("part3") -> "part3"
                        mode.contains("mock") -> "full_mock"
                        else -> "part1"
                    }
                    val ieltsRes = api.respondIelts(
                        com.ielts.ai.speaking.core.network.models.IeltsRespondRequest(
                            sessionId = sessionId,
                            userText = text,
                            part = part
                        )
                    )
                    if (ieltsRes.isCompleted) {
                        _isIeltsCompleted.value = true
                    }
                    val aiMsg = MessageItem(
                        id = (System.currentTimeMillis() + 1).toString(),
                        role = "assistant",
                        text = ieltsRes.message
                    )
                    _messages.value = _messages.value + aiMsg

                    if (_autoPlayTts.value && ieltsRes.ttsText.isNotBlank()) {
                        ttsManager.speak(
                            text = ieltsRes.ttsText,
                            onStart = { _isSpeakingTts.value = true },
                            onDone = { _isSpeakingTts.value = false }
                        )
                    }
                } else {
                    val response = api.respond(
                        ConversationRequest(
                            sessionId = sessionId,
                            userText = text,
                            mode = mode
                        )
                    )

                    // Phase 5: Attach pronunciation report to user's message
                    if (response.pronunciation != null) {
                        _messages.value = _messages.value.map { msg ->
                            if (msg.id == userMsg.id) msg.copy(pronunciation = response.pronunciation) else msg
                        }
                    }

                    val aiMsg = MessageItem(
                        id = response.turnId ?: (System.currentTimeMillis() + 1).toString(),
                        role = "assistant",
                        text = response.message,
                        corrections = response.corrections,
                        repeatPrompt = response.repeatPrompt
                    )
                    _messages.value = _messages.value + aiMsg

                    // Play TTS
                    if (_autoPlayTts.value && response.message.isNotBlank()) {
                        ttsManager.speak(
                            text = response.ttsText ?: response.message,
                            onStart = { _isSpeakingTts.value = true },
                            onDone = { _isSpeakingTts.value = false }
                        )
                    }
                }

            } catch (e: Exception) {
                _error.value = "Server error: ${e.localizedMessage}"
            } finally {
                _isProcessing.value = false
            }
        }
    }

    // Phase 5: Pronunciation Drill methods
    fun selectWordForPronunciation(word: WordPronunciationDto) {
        _selectedWordPronunciation.value = word
        _drillResult.value = null
    }

    fun dismissPronunciationSheet() {
        _selectedWordPronunciation.value = null
        _drillResult.value = null
    }

    fun practiceDrill(targetWord: String) {
        viewModelScope.launch {
            _isDrilling.value = true
            try {
                val api = ApiClient.getService()
                val result = api.evaluatePronunciationDrill(
                    PronunciationDrillRequest(targetWord = targetWord)
                )
                _drillResult.value = result
            } catch (e: Exception) {
                _error.value = "Drill failed: ${e.localizedMessage}"
            } finally {
                _isDrilling.value = false
            }
        }
    }

    fun speakText(text: String) {
        ttsManager.speak(
            text = text,
            onStart = { _isSpeakingTts.value = true },
            onDone = { _isSpeakingTts.value = false }
        )
    }


    fun finishSession(sessionId: String, onFinished: () -> Unit) {
        viewModelScope.launch {
            try {
                ApiClient.getService().finishSession(sessionId)
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                ttsManager.stop()
                onFinished()
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        ttsManager.shutdown()
        audioRecorder.stopRecording()
    }
}
