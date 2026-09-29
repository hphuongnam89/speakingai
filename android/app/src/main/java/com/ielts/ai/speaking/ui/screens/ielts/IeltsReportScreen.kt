package com.ielts.ai.speaking.ui.screens.ielts

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.ielts.ai.speaking.core.network.models.IeltsEvaluationResponse
import com.ielts.ai.speaking.core.network.models.SuggestedExpressionDto
import com.ielts.ai.speaking.ui.theme.ErrorRed
import com.ielts.ai.speaking.ui.theme.PrimaryBlue
import com.ielts.ai.speaking.ui.theme.SuccessGreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IeltsReportScreen(
    sessionId: String,
    onNavigateHome: () -> Unit,
    viewModel: IeltsReportViewModel = viewModel()
) {
    val evaluation by viewModel.evaluation.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()

    LaunchedEffect(sessionId) {
        viewModel.loadEvaluation(sessionId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("IELTS Speaking Assessment") },
                navigationIcon = {
                    IconButton(onClick = onNavigateHome) {
                        Icon(Icons.Default.Home, contentDescription = "Home")
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            if (isLoading) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    CircularProgressIndicator(color = PrimaryBlue, modifier = Modifier.size(48.dp))
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        "AI Examiner is assessing your test...",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        "Analyzing Fluency, Lexical Resource, and Grammar.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.Gray
                    )
                }
            } else if (error != null) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(24.dp),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("Assessment Error", style = MaterialTheme.typography.titleMedium, color = ErrorRed)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(error ?: "", color = Color.Gray)
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { viewModel.loadEvaluation(sessionId) }) {
                        Text("Retry Assessment")
                    }
                }
            } else if (evaluation != null) {
                val report = evaluation!!
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 16.dp),
                    contentPadding = PaddingValues(vertical = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Overall Band Card
                    item {
                        OverallBandCard(report)
                    }

                    // Disclaimer Pill
                    item {
                        Surface(
                            color = Color(0xFFFEF3C7),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(Icons.Default.Info, contentDescription = null, tint = Color(0xFFD97706), modifier = Modifier.size(18.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = report.disclaimer,
                                    style = MaterialTheme.typography.labelSmall,
                                    color = Color(0xFF92400E)
                                )
                            }
                        }
                    }

                    // 3 Criteria Breakdown
                    item {
                        Text("Band Descriptors Breakdown", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    }

                    item {
                        CriteriaCard("🗣️ Fluency & Coherence", report.fluencyScore, report.fluencyFeedback)
                    }
                    item {
                        CriteriaCard("📚 Lexical Resource", report.lexicalScore, report.lexicalFeedback)
                    }
                    item {
                        CriteriaCard("✍️ Grammatical Range & Accuracy", report.grammarScore, report.grammarFeedback)
                    }
                    if (report.pronunciationScore != null) {
                        item {
                            CriteriaCard("🎙️ Pronunciation (Acoustic)", report.pronunciationScore, "Acoustic assessment of phonemes, syllable stress, and speech rhythm.")
                        }
                    }

                    // Strengths
                    if (report.strengths.isNotEmpty()) {
                        item {
                            Text("Key Strengths", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        }
                        item {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color(0xFFF0FDF4)),
                                shape = RoundedCornerShape(12.dp),
                                border = BorderStroke(1.dp, Color(0xFFBBF7D0))
                            ) {
                                Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                    report.strengths.forEach { s ->
                                        Row(verticalAlignment = Alignment.Top) {
                                            Icon(Icons.Default.Check, contentDescription = null, tint = SuccessGreen, modifier = Modifier.size(16.dp))
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Text(s, style = MaterialTheme.typography.bodySmall, color = Color(0xFF14532D))
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Areas for improvement
                    if (report.areasForImprovement.isNotEmpty()) {
                        item {
                            Text("Areas for Improvement", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        }
                        item {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color(0xFFFFFBEB)),
                                shape = RoundedCornerShape(12.dp),
                                border = BorderStroke(1.dp, Color(0xFFFDE68A))
                            ) {
                                Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                    report.areasForImprovement.forEach { area ->
                                        Row(verticalAlignment = Alignment.Top) {
                                            Text("•", color = Color(0xFFD97706), fontWeight = FontWeight.Bold)
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Text(area, style = MaterialTheme.typography.bodySmall, color = Color(0xFF78350F))
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Suggested Expressions (Band 7.5+ Upgrades)
                    if (report.suggestedExpressions.isNotEmpty()) {
                        item {
                            Text("Vocabulary & Phrasing Upgrades", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        }
                        items(report.suggestedExpressions) { exp ->
                            ExpressionUpgradeCard(exp)
                        }
                    }

                    // Examiner Summary
                    if (report.examinerSummary.isNotBlank()) {
                        item {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color(0xFFF8FAFC)),
                                border = BorderStroke(1.dp, Color(0xFFE2E8F0))
                            ) {
                                Column(modifier = Modifier.padding(14.dp)) {
                                    Text("EXAMINER SUMMARY", style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = Color.Gray)
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(report.examinerSummary, style = MaterialTheme.typography.bodyMedium)
                                }
                            }
                        }
                    }

                    // Return Home Button
                    item {
                        Button(
                            onClick = onNavigateHome,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(52.dp)
                        ) {
                            Text("Done — Return Home", style = MaterialTheme.typography.titleSmall)
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }
            }
        }
    }
}

@Composable
fun OverallBandCard(report: IeltsEvaluationResponse) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = PrimaryBlue)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("OVERALL ESTIMATED BAND", style = MaterialTheme.typography.labelMedium, color = Color.White.copy(alpha = 0.8f))
            Spacer(modifier = Modifier.height(8.dp))
            Surface(
                color = Color.White,
                shape = CircleShape,
                modifier = Modifier.size(80.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = String.format("%.1f", report.overallBand),
                        fontSize = 32.sp,
                        fontWeight = FontWeight.Bold,
                        color = PrimaryBlue
                    )
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Text("Good Competent User", style = MaterialTheme.typography.bodyMedium, color = Color.White, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
fun CriteriaCard(title: String, score: Float, feedback: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = BorderStroke(1.dp, Color(0xFFE2E8F0))
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Surface(
                    color = PrimaryBlue.copy(alpha = 0.12f),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = "Band " + String.format("%.1f", score),
                        color = PrimaryBlue,
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.labelMedium,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }
            if (feedback.isNotBlank()) {
                Spacer(modifier = Modifier.height(6.dp))
                Text(feedback, style = MaterialTheme.typography.bodySmall, color = Color(0xFF475569))
            }
        }
    }
}

@Composable
fun ExpressionUpgradeCard(expression: SuggestedExpressionDto) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF8FAFC)),
        shape = RoundedCornerShape(10.dp),
        border = BorderStroke(1.dp, Color(0xFFE2E8F0))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("Original: ", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                Text(expression.original, style = MaterialTheme.typography.bodySmall, color = ErrorRed, fontWeight = FontWeight.Medium)
            }
            Spacer(modifier = Modifier.height(4.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("Band 7.5+ Upgrade: ", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                Text(expression.upgraded, style = MaterialTheme.typography.bodySmall, color = SuccessGreen, fontWeight = FontWeight.Bold)
            }
            if (!expression.context.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(4.dp))
                Text("Context: ${expression.context}", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
            }
        }
    }
}
