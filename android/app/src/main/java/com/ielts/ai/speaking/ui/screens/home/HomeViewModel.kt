package com.ielts.ai.speaking.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ielts.ai.speaking.core.network.ApiClient
import com.ielts.ai.speaking.core.network.models.SessionCreateRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class HomeViewModel : ViewModel() {
    private val _selectedMode = MutableStateFlow("Daily Practice")
    val selectedMode: StateFlow<String> = _selectedMode.asStateFlow()
    
    private val _topicInput = MutableStateFlow("")
    val topicInput: StateFlow<String> = _topicInput.asStateFlow()
    
    private val _isStarting = MutableStateFlow(false)
    val isStarting: StateFlow<Boolean> = _isStarting.asStateFlow()
    
    private val _serverStatus = MutableStateFlow("Checking...")
    val serverStatus: StateFlow<String> = _serverStatus.asStateFlow()

    init {
        checkServerStatus()
    }

    fun checkServerStatus() {
        viewModelScope.launch {
            try {
                val res = ApiClient.getService().checkHealth()
                _serverStatus.value = if (res.status == "ok") "Online (${res.model ?: "AI"})" else "Offline"
            } catch (e: Exception) {
                _serverStatus.value = "Offline"
            }
        }
    }

    private val _ieltsPart = MutableStateFlow("part1") // part1, part2, part3, full_mock
    val ieltsPart: StateFlow<String> = _ieltsPart.asStateFlow()

    fun selectIeltsPart(part: String) {
        _ieltsPart.value = part
    }

    fun selectMode(mode: String) {
        _selectedMode.value = mode
    }

    fun updateTopic(topic: String) {
        _topicInput.value = topic
    }

    fun startSession(onSuccess: (sessionId: String, mode: String, topic: String) -> Unit) {
        viewModelScope.launch {
            _isStarting.value = true
            try {
                if (_selectedMode.value == "IELTS Speaking") {
                    val part = _ieltsPart.value
                    val res = ApiClient.getService().startIeltsTest(
                        com.ielts.ai.speaking.core.network.models.IeltsStartRequest(part = part)
                    )
                    _isStarting.value = false
                    val topicName = when (part) {
                        "part2" -> res.cueCard?.title ?: "IELTS Part 2 Long Turn"
                        "part3" -> "IELTS Part 3 Discussion"
                        "full_mock" -> "IELTS Full Mock Exam"
                        else -> "IELTS Part 1 Interview"
                    }
                    onSuccess(res.sessionId, "ielts_$part", topicName)
                } else {
                    val modeKey = when (_selectedMode.value) {
                        "Free Talk" -> "freetalk"
                        "Fix My English" -> "fixmyenglish"
                        else -> "daily"
                    }
                    val topic = _topicInput.value.ifBlank { "Daily Routine" }
                    val response = ApiClient.getService().createSession(
                        SessionCreateRequest(mode = modeKey, topic = topic)
                    )
                    _isStarting.value = false
                    onSuccess(response.id, modeKey, topic)
                }
            } catch (e: Exception) {
                _isStarting.value = false
                val fallbackId = java.util.UUID.randomUUID().toString()
                val fallbackMode = if (_selectedMode.value == "IELTS Speaking") "ielts_${_ieltsPart.value}" else "daily"
                onSuccess(fallbackId, fallbackMode, _topicInput.value.ifBlank { "Speaking Practice" })
            }
        }
    }

}
