package com.ielts.ai.speaking.ui.screens.settings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import com.ielts.ai.speaking.ui.theme.SuccessGreen
import com.ielts.ai.speaking.ui.theme.ErrorRed

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onNavigateBack: () -> Unit,
    viewModel: SettingsViewModel = viewModel()
) {
    val serverUrl by viewModel.serverUrl.collectAsState()
    val isChecking by viewModel.isChecking.collectAsState()
    val connectionStatus by viewModel.connectionStatus.collectAsState()
    val modelName by viewModel.modelName.collectAsState()
    val email by viewModel.email.collectAsState()
    val password by viewModel.password.collectAsState()
    val accountStatus by viewModel.accountStatus.collectAsState()
    val sessions by viewModel.sessions.collectAsState()
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text("Backend Server Configuration", style = MaterialTheme.typography.titleMedium)
            
            OutlinedTextField(
                value = serverUrl,
                onValueChange = { viewModel.updateServerUrl(it) },
                label = { Text("Server URL") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            Text("Account sync", style = MaterialTheme.typography.titleMedium)
            Text("Create an account or sign in to sync sessions, mistakes and progress across devices.", style = MaterialTheme.typography.bodySmall)
            OutlinedTextField(
                value = email,
                onValueChange = viewModel::updateEmail,
                label = { Text("Email") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            OutlinedTextField(
                value = password,
                onValueChange = viewModel::updatePassword,
                label = { Text("Password (10+ characters)") },
                modifier = Modifier.fillMaxWidth(),
                visualTransformation = PasswordVisualTransformation(),
                singleLine = true
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { viewModel.authenticate(context, register = false) }) { Text("Sign in") }
                OutlinedButton(onClick = { viewModel.authenticate(context, register = true) }) { Text("Create account") }
                TextButton(onClick = { viewModel.signOut(context) }) { Text("Sign out") }
            }
            if (accountStatus.isNotBlank()) Text(accountStatus, style = MaterialTheme.typography.bodySmall)
            if (sessions.isNotEmpty()) {
                Text("Synced recent sessions", style = MaterialTheme.typography.titleSmall)
                sessions.forEach { session ->
                    Text("• ${session.topic ?: session.mode} · ${session.startedAt}", style = MaterialTheme.typography.bodySmall)
                }
            }
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                OutlinedButton(
                    onClick = { viewModel.updateServerUrl("http://10.0.2.2:8000/") },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Emulator\n10.0.2.2:8000")
                }
                OutlinedButton(
                    onClick = { viewModel.updateServerUrl("http://127.0.0.1:8000/") },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Localhost\n127.0.0.1:8000")
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Button(
                    onClick = { viewModel.testConnection(context) },
                    enabled = !isChecking
                ) {
                    Text(if (isChecking) "Checking..." else "Test Connection")
                }
                
                when (connectionStatus) {
                    ConnectionStatus.Connected -> {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.CheckCircle, contentDescription = "Connected", tint = SuccessGreen)
                            Spacer(Modifier.width(4.dp))
                            Text(
                                text = if (modelName != null) "Connected ($modelName)" else "Connected",
                                color = SuccessGreen,
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                    ConnectionStatus.Failed -> {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Warning, contentDescription = "Failed", tint = ErrorRed)
                            Spacer(Modifier.width(4.dp))
                            Text("Failed", color = ErrorRed)
                        }
                    }
                    else -> {}
                }
            }

            Divider(modifier = Modifier.padding(vertical = 8.dp))

            // Phase 2 AI Tutor: Correction Level Setting
            val correctionLevel by viewModel.correctionLevel.collectAsState()
            val isSaving by viewModel.isSavingSettings.collectAsState()

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("AI Tutor: Correction Level", style = MaterialTheme.typography.titleMedium)
                if (isSaving) {
                    Text("Saving...", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.primary)
                }
            }

            Text(
                "Choose how strictly AI Coach points out your mistakes during speaking.",
                style = MaterialTheme.typography.bodySmall,
                color = Color.Gray
            )

            val levels = listOf(
                Triple("important", "Important (Recommended)", "Catches notable grammar, vocabulary mistakes and awkward phrasing."),
                Triple("aggressive", "Aggressive (Strict)", "Catches every grammatical slip, preposition, and subtle word choice."),
                Triple("none", "None (Free Flow)", "Focuses purely on fluent conversation without interrupting with corrections.")
            )

            levels.forEach { (key, title, desc) ->
                val isSelected = (correctionLevel == key)
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = if (isSelected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                    ),
                    onClick = { viewModel.setCorrectionLevel(key) }
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = isSelected,
                            onClick = { viewModel.setCorrectionLevel(key) }
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(
                                text = title,
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = if (isSelected) androidx.compose.ui.text.font.FontWeight.Bold else androidx.compose.ui.text.font.FontWeight.Normal
                            )
                            Text(
                                text = desc,
                                style = MaterialTheme.typography.bodySmall,
                                color = if (isSelected) MaterialTheme.colorScheme.onPrimaryContainer else Color.Gray
                            )
                        }
                    }
                }
            }
        }
    }
}

