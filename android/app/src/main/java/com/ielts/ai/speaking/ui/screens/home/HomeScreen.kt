package com.ielts.ai.speaking.ui.screens.home

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.ielts.ai.speaking.ui.theme.CardBackground
import com.ielts.ai.speaking.ui.theme.PrimaryBlue
import com.ielts.ai.speaking.ui.theme.SuccessGreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToSettings: () -> Unit,
    onNavigateToMistakes: () -> Unit,
    onNavigateToProgress: () -> Unit,
    onNavigateToConversation: (String, String, String) -> Unit,
    viewModel: HomeViewModel = viewModel()
) {
    val selectedMode by viewModel.selectedMode.collectAsState()
    val topicInput by viewModel.topicInput.collectAsState()
    val isStarting by viewModel.isStarting.collectAsState()
    val serverStatus by viewModel.serverStatus.collectAsState()
    
    val modes = listOf("Daily Practice", "IELTS Speaking", "Free Talk", "Fix My English")
    val suggestedTopics = listOf("Travel", "Hometown", "Work & Study", "Technology", "Hobbies")

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("IELTS Coach") },
                actions = {
                    // Server status pill
                    Surface(
                        color = SuccessGreen.copy(alpha = 0.2f),
                        shape = MaterialTheme.shapes.small,
                        modifier = Modifier.padding(end = 4.dp)
                    ) {
                        Text(
                            text = serverStatus,
                            color = SuccessGreen,
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                    IconButton(onClick = onNavigateToProgress) {
                        Icon(Icons.Default.TrendingUp, contentDescription = "Progress & Analytics")
                    }
                    IconButton(onClick = onNavigateToMistakes) {
                        Icon(Icons.Default.List, contentDescription = "Mistakes Notebook")
                    }
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings")
                    }
                }
            )
        }
    ) { padding ->

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Modes
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Select Practice Mode", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                modes.forEach { mode ->
                    ModeCard(
                        title = mode,
                        isSelected = mode == selectedMode,
                        onClick = { viewModel.selectMode(mode) }
                    )
                }

                // Phase 3: IELTS Part Selector
                if (selectedMode == "IELTS Speaking") {
                    val ieltsPart by viewModel.ieltsPart.collectAsState()
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("IELTS Test Part", style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, color = PrimaryBlue)
                    val parts = listOf(
                        Pair("part1", "Part 1"),
                        Pair("part2", "Part 2 (Cue Card)"),
                        Pair("part3", "Part 3"),
                        Pair("full_mock", "Full Mock")
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        parts.forEach { (key, title) ->
                            val isSel = ieltsPart == key
                            FilterChip(
                                selected = isSel,
                                onClick = { viewModel.selectIeltsPart(key) },
                                label = { Text(title, style = MaterialTheme.typography.labelSmall) }
                            )
                        }
                    }
                }
            }

            
            // Topics
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Topic", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                OutlinedTextField(
                    value = topicInput,
                    onValueChange = { viewModel.updateTopic(it) },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("E.g., Describe a memorable journey...") },
                    singleLine = true
                )
                
                LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(suggestedTopics) { topic ->
                        SuggestionChip(
                            onClick = { viewModel.updateTopic(topic) },
                            label = { Text(topic) }
                        )
                    }
                }
            }

            // Phase 4: Progress & Adaptive Learning card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onNavigateToProgress() },
                colors = CardDefaults.cardColors(containerColor = Color(0xFFEFF6FF)),
                border = BorderStroke(1.dp, Color(0xFFBFDBFE)),
                shape = MaterialTheme.shapes.medium
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text(
                            "📈 Progress & Adaptive Plan",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = PrimaryBlue
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            "Streak, weekly activity & AI daily drills",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.Gray
                        )
                    }
                    Text(
                        "View →",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = PrimaryBlue
                    )
                }
            }

            // Phase 2: Mistake Notebook card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onNavigateToMistakes() },
                colors = CardDefaults.cardColors(containerColor = Color(0xFFF1F5F9)),
                border = BorderStroke(1.dp, Color(0xFFCBD5E1)),
                shape = MaterialTheme.shapes.medium
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text(
                            "📖 Mistake Notebook (AI Tutor)",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = PrimaryBlue
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            "Review recurring errors & grammar history",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.Gray
                        )
                    }
                    Text(
                        "Review →",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = PrimaryBlue
                    )
                }
            }
            
            Spacer(modifier = Modifier.weight(1f))

            
            Button(
                onClick = {
                    viewModel.startSession { sessionId, mode, topic ->
                        onNavigateToConversation(sessionId, mode, topic)
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                enabled = !isStarting
            ) {
                if (isStarting) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Text("Start Speaking", style = MaterialTheme.typography.titleMedium)
                }
            }
        }
    }
}

@Composable
fun ModeCard(title: String, isSelected: Boolean, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) MaterialTheme.colorScheme.primaryContainer else CardBackground
        )
    ) {
        PaddingValues(16.dp).let {
            Text(
                text = title,
                modifier = Modifier.padding(16.dp),
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                color = if (isSelected) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurface
            )
        }
    }
}
