package com.ielts.ai.speaking.ui.screens.ielts

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ielts.ai.speaking.core.network.ApiClient
import com.ielts.ai.speaking.core.network.models.IeltsEvaluationResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class IeltsReportViewModel : ViewModel() {
    private val _evaluation = MutableStateFlow<IeltsEvaluationResponse?>(null)
    val evaluation: StateFlow<IeltsEvaluationResponse?> = _evaluation.asStateFlow()

    private val _isLoading = MutableStateFlow(true)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    fun loadEvaluation(sessionId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                val api = ApiClient.getService()
                val result = api.evaluateIelts(sessionId)
                _evaluation.value = result
            } catch (e: Exception) {
                _error.value = "Failed to evaluate test: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }
}
