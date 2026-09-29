package com.ielts.ai.speaking.ui.screens.mistakes

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ielts.ai.speaking.core.network.ApiClient
import com.ielts.ai.speaking.core.network.models.MistakeDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class MistakesViewModel : ViewModel() {
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _mistakes = MutableStateFlow<List<MistakeDto>>(emptyList())
    val mistakes: StateFlow<List<MistakeDto>> = _mistakes.asStateFlow()

    private val _frequentMistakes = MutableStateFlow<List<MistakeDto>>(emptyList())
    val frequentMistakes: StateFlow<List<MistakeDto>> = _frequentMistakes.asStateFlow()

    private val _selectedTab = MutableStateFlow(0) // 0: Frequent Mistakes, 1: All Mistakes
    val selectedTab: StateFlow<Int> = _selectedTab.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    init {
        loadData()
    }

    fun selectTab(index: Int) {
        _selectedTab.value = index
    }

    fun loadData() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                val api = ApiClient.getService()
                val freq = api.getFrequentMistakes()
                val all = api.getMistakes()
                _frequentMistakes.value = freq
                _mistakes.value = all
            } catch (e: Exception) {
                _error.value = "Failed to load mistakes: ${e.localizedMessage}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun resolveMistake(id: String) {
        viewModelScope.launch {
            try {
                val api = ApiClient.getService()
                val res = api.resolveMistake(id)
                if (res.resolved) {
                    _mistakes.value = _mistakes.value.map {
                        if (it.id == id) it.copy(resolved = true) else it
                    }
                    _frequentMistakes.value = _frequentMistakes.value.map {
                        if (it.id == id) it.copy(resolved = true) else it
                    }
                }
            } catch (e: Exception) {
                _error.value = "Failed to update mistake: ${e.localizedMessage}"
            }
        }
    }
}
