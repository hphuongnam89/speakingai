package com.ielts.ai.speaking.ui.screens.progress

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.ielts.ai.speaking.core.network.models.AdaptivePlanDto
import com.ielts.ai.speaking.core.network.models.DailyStatItemDto
import com.ielts.ai.speaking.core.network.models.ProgressSummaryDto
import com.ielts.ai.speaking.ui.theme.CardBackground
import com.ielts.ai.speaking.ui.theme.PrimaryBlue
import com.ielts.ai.speaking.ui.theme.SuccessGreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProgressScreen(
    onNavigateBack: () -> Unit,
    onNavigateToMistakes: () -> Unit,
    onNavigateToConversation: (String, String, String) -> Unit,
    viewModel: ProgressViewModel = viewModel()
) {
    val summary by viewModel.summary.collectAsState()
    val weeklyStats by viewModel.weeklyStats.collectAsState()
    val adaptivePlan by viewModel.adaptivePlan.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val isGeneratingPlan by viewModel.isGeneratingPlan.collectAsState()
    val isStartingSession by viewModel.isStartingSession.collectAsState()
    val error by viewModel.error.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Progress & Adaptive Plan", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.loadData() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        }
    ) { padding ->
        if (isLoading && summary == null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp)
            ) {
                if (error != null) {
                    Card(
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = error ?: "",
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            modifier = Modifier.padding(12.dp),
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }

                // Streak Banner
                StreakBanner(streak = summary?.streak ?: 0)

                // Key Performance Indicators (Bento Grid)
                KpiGrid(summary = summary)

                // 7-Day Consistency & Activity Chart
                WeeklyActivityCard(weeklyStats = weeklyStats)

                // AI Adaptive Learning Plan (Ollama powered)
                AdaptivePlanCard(
                    adaptivePlan = adaptivePlan,
                    isGenerating = isGeneratingPlan,
                    isStartingSession = isStartingSession,
                    onGeneratePlan = { viewModel.generateAdaptivePlan() },
                    onStartSession = { topic ->
                        viewModel.startRecommendedSession(topic) { sessionId, mode, sessionTopic ->
                            onNavigateToConversation(sessionId, mode, sessionTopic)
                        }
                    }
                )

                // Mistakes Notebook Link
                MistakesLinkCard(
                    mistakeCount = summary?.totalMistakes ?: 0,
                    onClick = onNavigateToMistakes
                )

                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
fun StreakBanner(streak: Int) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFFEF3C7) // warm amber
        ),
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, Color(0xFFFDE68A))
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(52.dp)
                    .clip(CircleShape)
                    .background(Color(0xFFF59E0B)),
                contentAlignment = Alignment.Center
            ) {
                Text("🔥", fontSize = 26.sp)
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(
                    text = if (streak > 0) "$streak-Day Practice Streak!" else "Start Your Practice Streak!",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF92400E)
                )
                Text(
                    text = if (streak > 0) "Consistency is the fastest route to Band 7.5+" else "Complete 1 session today to begin your streak",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFFB45309)
                )
            }
        }
    }
}

@Composable
fun KpiGrid(summary: ProgressSummaryDto?) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text("Your Performance", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            KpiMetricBox(
                modifier = Modifier.weight(1f),
                emoji = "⏱️",
                title = "Speaking Time",
                value = "${String.format("%.1f", summary?.totalSpeakingMinutes ?: 0f)}m",
                subtitle = "Total practiced"
            )
            KpiMetricBox(
                modifier = Modifier.weight(1f),
                emoji = "⚡",
                title = "Avg Speed",
                value = "${String.format("%.0f", summary?.avgWpm ?: 0f)} WPM",
                subtitle = "Fluency rate"
            )
        }

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            KpiMetricBox(
                modifier = Modifier.weight(1f),
                emoji = "🎯",
                title = "Total Sessions",
                value = "${summary?.totalSessions ?: 0}",
                subtitle = "Mock & drills"
            )
            KpiMetricBox(
                modifier = Modifier.weight(1f),
                emoji = "⭐",
                title = "Estimated Band",
                value = if (summary?.latestBand != null) String.format("%.1f", summary.latestBand) else "N/A",
                subtitle = "Latest assessment",
                highlightColor = PrimaryBlue
            )
        }
    }
}

@Composable
fun KpiMetricBox(
    modifier: Modifier = Modifier,
    emoji: String,
    title: String,
    value: String,
    subtitle: String,
    highlightColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = CardBackground),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(emoji, fontSize = 18.sp)
                Spacer(modifier = Modifier.width(6.dp))
                Text(title, style = MaterialTheme.typography.labelMedium, color = Color.Gray)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = highlightColor
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(subtitle, style = MaterialTheme.typography.labelSmall, color = Color.Gray)
        }
    }
}

@Composable
fun WeeklyActivityCard(weeklyStats: List<DailyStatItemDto>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = CardBackground),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Weekly Activity", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text("Last 7 days speaking minutes", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                }
                val totalWeeklyMin = weeklyStats.sumOf { it.speakingMinutes.toDouble() }
                Text(
                    text = "${String.format("%.1f", totalWeeklyMin)}m total",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = PrimaryBlue
                )
            }

            // 7 Days Bar Chart
            val maxMinutes = (weeklyStats.maxOfOrNull { it.speakingMinutes } ?: 10f).coerceAtLeast(5f)

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(130.dp),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.Bottom
            ) {
                if (weeklyStats.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("No weekly activity recorded yet", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                    }
                } else {
                    weeklyStats.forEach { stat ->
                        val ratio = (stat.speakingMinutes / maxMinutes).coerceIn(0.08f, 1f)
                        val isToday = stat == weeklyStats.lastOrNull()

                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Bottom,
                            modifier = Modifier.width(36.dp)
                        ) {
                            if (stat.speakingMinutes > 0f) {
                                Text(
                                    text = "${String.format("%.0f", stat.speakingMinutes)}m",
                                    style = MaterialTheme.typography.labelSmall,
                                    fontSize = 10.sp,
                                    color = if (isToday) PrimaryBlue else Color.Gray,
                                    textAlign = TextAlign.Center
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                            }

                            // The bar
                            Box(
                                modifier = Modifier
                                    .width(22.dp)
                                    .height((ratio * 80).dp)
                                    .clip(RoundedCornerShape(topStart = 6.dp, topEnd = 6.dp))
                                    .background(
                                        when {
                                            isToday -> PrimaryBlue
                                            stat.speakingMinutes > 0f -> Color(0xFF93C5FD)
                                            else -> Color(0xFFE2E8F0)
                                        }
                                    )
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                text = stat.dayOfWeek,
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = if (isToday) FontWeight.Bold else FontWeight.Normal,
                                color = if (isToday) PrimaryBlue else Color.DarkGray
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun AdaptivePlanCard(
    adaptivePlan: AdaptivePlanDto?,
    isGenerating: Boolean,
    isStartingSession: Boolean,
    onGeneratePlan: () -> Unit,
    onStartSession: (topic: String) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFF0FDF4) // Soft green highlight
        ),
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, Color(0xFFBBF7D0))
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.AutoAwesome,
                        contentDescription = "AI Plan",
                        tint = Color(0xFF16A34A),
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        "AI Adaptive Daily Plan",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF166534)
                    )
                }
                Surface(
                    color = Color(0xFFDCFCE7),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        text = "Ollama Powered",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color(0xFF15803D),
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }

            if (adaptivePlan == null) {
                Text(
                    text = "Your AI Tutor examines your recurring grammar & vocabulary slips to craft today's targeted drills and high-impact phrases.",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF14532D)
                )

                Button(
                    onClick = onGeneratePlan,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF16A34A)),
                    enabled = !isGenerating
                ) {
                    if (isGenerating) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = Color.White,
                            strokeWidth = 2.dp
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("AI Generating Plan...")
                    } else {
                        Icon(Icons.Default.AutoAwesome, contentDescription = null, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Generate Today's Plan", fontWeight = FontWeight.Bold)
                    }
                }
            } else {
                // Today's Target Objective
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(
                        "🎯 TODAY'S OBJECTIVE",
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF15803D)
                    )
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color.White),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(
                            text = adaptivePlan.todayObjective,
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.padding(10.dp),
                            color = Color(0xFF1F2937)
                        )
                    }
                }

                // Weaknesses to Tackle
                if (adaptivePlan.topWeaknesses.isNotEmpty()) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            "⚠️ WEAKNESSES TO CONQUER",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFFB45309)
                        )
                        adaptivePlan.topWeaknesses.forEach { weakness ->
                            Row(
                                verticalAlignment = Alignment.Top,
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Icon(
                                    Icons.Default.Warning,
                                    contentDescription = null,
                                    tint = Color(0xFFD97706),
                                    modifier = Modifier.size(16.dp).padding(top = 2.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = weakness,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = Color(0xFF374151)
                                )
                            }
                        }
                    }
                }

                // Challenge Phrases
                if (adaptivePlan.challengePhrases.isNotEmpty()) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            "💡 CHALLENGE PHRASES TO USE",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF2563EB)
                        )
                        adaptivePlan.challengePhrases.forEach { phrase ->
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(Color(0xFFEFF6FF), RoundedCornerShape(6.dp))
                                    .padding(horizontal = 8.dp, vertical = 6.dp)
                            ) {
                                Icon(
                                    Icons.Default.CheckCircle,
                                    contentDescription = null,
                                    tint = PrimaryBlue,
                                    modifier = Modifier.size(14.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = phrase,
                                    style = MaterialTheme.typography.bodySmall,
                                    fontWeight = FontWeight.Medium,
                                    color = Color(0xFF1E3A8A)
                                )
                            }
                        }
                    }
                }

                // Recommended Topic & Action Button
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        "📌 RECOMMENDED TOPIC",
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF15803D)
                    )
                    Text(
                        text = adaptivePlan.recommendedTopic,
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF111827)
                    )
                }

                Button(
                    onClick = { onStartSession(adaptivePlan.recommendedTopic) },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF16A34A)),
                    enabled = !isStartingSession
                ) {
                    if (isStartingSession) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = Color.White,
                            strokeWidth = 2.dp
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Launching Session...")
                    } else {
                        Icon(Icons.Default.PlayArrow, contentDescription = null)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Start Targeted Session", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun MistakesLinkCard(
    mistakeCount: Int,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = CardBackground),
        shape = RoundedCornerShape(12.dp)
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
                    text = "📖 Mistake Notebook ($mistakeCount logged)",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Review all grammatical and lexical feedback",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
            }
            Text("Review →", color = PrimaryBlue, fontWeight = FontWeight.Bold)
        }
    }
}
