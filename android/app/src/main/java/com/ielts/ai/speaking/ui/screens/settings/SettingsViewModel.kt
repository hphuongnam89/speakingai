package com.ielts.ai.speaking.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import android.content.Context
import com.ielts.ai.speaking.core.network.ApiClient
import com.ielts.ai.speaking.core.network.ApiCredentialStore
import com.ielts.ai.speaking.core.network.models.SessionResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

enum class ConnectionStatus {
    Idle, Connecting, Connected, Failed
}

class SettingsViewModel : ViewModel() {
    private val _serverUrl = MutableStateFlow(ApiClient.currentBaseUrl)
    val serverUrl: StateFlow<String> = _serverUrl.asStateFlow()

    private val _email = MutableStateFlow("")
    val email: StateFlow<String> = _email.asStateFlow()
    private val _password = MutableStateFlow("")
    val password: StateFlow<String> = _password.asStateFlow()
    private val _accountStatus = MutableStateFlow("")
    val accountStatus: StateFlow<String> = _accountStatus.asStateFlow()
    private val _sessions = MutableStateFlow<List<SessionResponse>>(emptyList())
    val sessions: StateFlow<List<SessionResponse>> = _sessions.asStateFlow()

    private val _connectionStatus = MutableStateFlow(ConnectionStatus.Idle)
    val connectionStatus: StateFlow<ConnectionStatus> = _connectionStatus.asStateFlow()

    private val _isChecking = MutableStateFlow(false)
    val isChecking: StateFlow<Boolean> = _isChecking.asStateFlow()

    private val _modelName = MutableStateFlow<String?>(null)
    val modelName: StateFlow<String?> = _modelName.asStateFlow()

    private val _correctionLevel = MutableStateFlow("important")
    val correctionLevel: StateFlow<String> = _correctionLevel.asStateFlow()

    private val _isSavingSettings = MutableStateFlow(false)
    val isSavingSettings: StateFlow<Boolean> = _isSavingSettings.asStateFlow()

    init {
        loadSettings()
        loadSessions()
    }

    fun loadSettings() {
        viewModelScope.launch {
            try {
                val api = ApiClient.getService()
                val settings = api.getSettings()
                _correctionLevel.value = settings.correctionLevel
            } catch (e: Exception) {
                // If offline or first time, default remains "important"
            }
        }
    }

    fun loadSessions() {
        viewModelScope.launch {
            try {
                _sessions.value = ApiClient.getService().getSessions().take(10)
            } catch (_: Exception) {
                _sessions.value = emptyList()
            }
        }
    }

    fun setCorrectionLevel(level: String) {
        _correctionLevel.value = level
        viewModelScope.launch {
            _isSavingSettings.value = true
            try {
                val api = ApiClient.getService()
                api.updateSettings(com.ielts.ai.speaking.core.network.models.UserSettingsUpdateRequest(correctionLevel = level))
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                _isSavingSettings.value = false
            }
        }
    }

    fun updateServerUrl(url: String) {
        _serverUrl.value = url
        _connectionStatus.value = ConnectionStatus.Idle
    }

    fun updateEmail(value: String) { _email.value = value }
    fun updatePassword(value: String) { _password.value = value }

    fun authenticate(context: Context, register: Boolean) {
        viewModelScope.launch {
            _accountStatus.value = "Connecting..."
            try {
                val api = ApiClient.getService()
                val request = com.ielts.ai.speaking.core.network.models.AuthRequest(_email.value.trim(), _password.value)
                val response = if (register) api.register(request) else api.login(request)
                ApiCredentialStore.writeAccessToken(context.applicationContext, response.accessToken)
                ApiClient.updateAccessToken(response.accessToken)
                _password.value = ""
                _accountStatus.value = "Signed in. Your learning data syncs with this account."
                loadSettings()
                loadSessions()
            } catch (e: Exception) {
                _accountStatus.value = "${if (register) "Registration" else "Sign in"} failed. Check your details or account."
            }
        }
    }

    fun signOut(context: Context) {
        ApiCredentialStore.writeAccessToken(context.applicationContext, "")
        ApiClient.updateAccessToken("")
        _sessions.value = emptyList()
        _accountStatus.value = "Signed out."
    }

    fun testConnection(context: Context) {
        val targetUrl = _serverUrl.value.trim()
        val normalizedUrl = if (targetUrl.endsWith("/")) targetUrl else "$targetUrl/"
        viewModelScope.launch {
            _isChecking.value = true
            _connectionStatus.value = ConnectionStatus.Connecting
            try {
                val api = ApiClient.updateBaseUrl(normalizedUrl)
                val response = api.checkHealth()
                if (response.status == "ok") {
                    _connectionStatus.value = ConnectionStatus.Connected
                    _modelName.value = response.model
                    loadSettings()
                } else {
                    _connectionStatus.value = ConnectionStatus.Failed
                }
            } catch (e: Exception) {
                e.printStackTrace()
                _connectionStatus.value = ConnectionStatus.Failed
            } finally {
                _isChecking.value = false
            }
        }
    }
}

