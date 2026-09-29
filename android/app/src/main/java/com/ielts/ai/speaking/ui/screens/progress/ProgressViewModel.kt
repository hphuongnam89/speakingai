package com.ielts.ai.speaking.ui.screens.progress

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ielts.ai.speaking.core.network.ApiClient
import com.ielts.ai.speaking.core.network.models.AdaptivePlanDto
import com.ielts.ai.speaking.core.network.models.DailyStatItemDto
import com.ielts.ai.speaking.core.network.models.ProgressSummaryDto
import com.ielts.ai.speaking.core.network.models.SessionCreateRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ProgressViewModel : ViewModel() {

    private val _summary = MutableStateFlow<ProgressSummaryDto?>(null)
    val summary: StateFlow<ProgressSummaryDto?> = _summary.asStateFlow()

    private val _weeklyStats = MutableStateFlow<List<DailyStatItemDto>>(emptyList())
    val weeklyStats: StateFlow<List<DailyStatItemDto>> = _weeklyStats.asStateFlow()

    private val _adaptivePlan = MutableStateFlow<AdaptivePlanDto?>(null)
    val adaptivePlan: StateFlow<AdaptivePlanDto?> = _adaptivePlan.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _isGeneratingPlan = MutableStateFlow(false)
    val isGeneratingPlan: StateFlow<Boolean> = _isGeneratingPlan.asStateFlow()

    private val _isStartingSession = MutableStateFlow(false)
    val isStartingSession: StateFlow<Boolean> = _isStartingSession.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                val api = ApiClient.getService()
                val summaryRes = api.getProgressSummary()
                val weeklyRes = api.getWeeklyProgress()
                _summary.value = summaryRes
                _weeklyStats.value = weeklyRes
            } catch (e: Exception) {
                _error.value = "Failed to load progress data: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun generateAdaptivePlan() {
        viewModelScope.launch {
            _isGeneratingPlan.value = true
            _error.value = null
            try {
                val api = ApiClient.getService()
                val plan = api.getAdaptivePlan()
                _adaptivePlan.value = plan
            } catch (e: Exception) {
                _error.value = "Failed to generate AI plan: ${e.localizedMessage}"
            } finally {
                _isGeneratingPlan.value = false
            }
        }
    }

    fun startRecommendedSession(
        topic: String,
        onSessionCreated: (sessionId: String, mode: String, topic: String) -> Unit
    ) {
        viewModelScope.launch {
            _isStartingSession.value = true
            try {
                val api = ApiClient.getService()
                val session = api.createSession(
                    SessionCreateRequest(
                        mode = "Daily Practice",
                        topic = topic.ifBlank { "Daily Routine & Work" }
                    )
                )
                onSessionCreated(session.id, session.mode, session.topic ?: "")
            } catch (e: Exception) {
                _error.value = "Failed to start session: ${e.localizedMessage}"
            } finally {
                _isStartingSession.value = false
            }
        }
    }
}
