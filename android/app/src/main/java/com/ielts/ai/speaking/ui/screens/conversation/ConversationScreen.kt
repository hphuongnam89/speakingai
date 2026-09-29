package com.ielts.ai.speaking.ui.screens.conversation

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn

import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.foundation.clickable
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.ielts.ai.speaking.core.network.models.CorrectionDto
import com.ielts.ai.speaking.core.network.models.PronunciationDrillResponseDto
import com.ielts.ai.speaking.core.network.models.WordPronunciationDto
import com.ielts.ai.speaking.ui.theme.PrimaryBlue
import com.ielts.ai.speaking.ui.theme.ErrorRed
import com.ielts.ai.speaking.ui.theme.SuccessGreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConversationScreen(
    sessionId: String,
    mode: String,
    topic: String,
    onNavigateBack: () -> Unit,
    onNavigateToIeltsReport: (String) -> Unit = {},
    viewModel: ConversationViewModel = viewModel()
) {
    val context = LocalContext.current
    val messages by viewModel.messages.collectAsState()
    val isRecording by viewModel.isRecording.collectAsState()
    val isProcessing by viewModel.isProcessing.collectAsState()
    val isSpeakingTts by viewModel.isSpeakingTts.collectAsState()
    val autoPlayTts by viewModel.autoPlayTts.collectAsState()
    val error by viewModel.error.collectAsState()

    // Phase 5: Pronunciation state
    val selectedWord by viewModel.selectedWordPronunciation.collectAsState()
    val drillResult by viewModel.drillResult.collectAsState()
    val isDrilling by viewModel.isDrilling.collectAsState()

    val isIeltsCompleted by viewModel.isIeltsCompleted.collectAsState()
    val timerPhase by viewModel.timerPhase.collectAsState()
    val prepSeconds by viewModel.prepSeconds.collectAsState()
    val speakingSeconds by viewModel.speakingSeconds.collectAsState()
    val isPart2 = mode.lowercase().contains("part2")
    
    val listState = rememberLazyListState()
    var textInput by remember { mutableStateOf("") }

    // Init TTS and load session turns
    LaunchedEffect(sessionId) {
        viewModel.initTts(context)
        viewModel.loadSession(sessionId)
    }


    // Scroll to bottom on new message
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    // Pulse animation when recording
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (isRecording) 1.25f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(600, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseScale"
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Column {
                        Text(mode.replaceFirstChar { it.uppercase() }, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Text(topic, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                    }
                },
                navigationIcon = {
                    IconButton(onClick = {
                        viewModel.finishSession(sessionId) { onNavigateBack() }
                    }) {
                        Icon(Icons.Default.Close, contentDescription = "Finish Session")
                    }
                },
                actions = {
                    if (isSpeakingTts) {
                        Surface(
                            color = PrimaryBlue.copy(alpha = 0.15f),
                            shape = CircleShape,
                            modifier = Modifier.padding(end = 8.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Icon(Icons.Default.VolumeUp, contentDescription = "Speaking", tint = PrimaryBlue, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("AI Speaking", style = MaterialTheme.typography.labelSmall, color = PrimaryBlue)
                            }
                        }
                    }
                }
            )
        },
        bottomBar = {
            Surface(
                tonalElevation = 4.dp,
                shadowElevation = 8.dp
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp)
                ) {
                    // Controls row
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Switch(
                                checked = autoPlayTts,
                                onCheckedChange = { viewModel.setAutoPlayTts(it) },
                                modifier = Modifier.scale(0.8f)
                            )
                            Text("Voice Output (TTS)", style = MaterialTheme.typography.bodySmall)
                        }
                        if (isRecording) {
                            Text("Recording... Tap to send", color = ErrorRed, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // Input row
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        OutlinedTextField(
                            value = textInput,
                            onValueChange = { textInput = it },
                            modifier = Modifier.weight(1f),
                            placeholder = { Text("Speak or type response...") },
                            maxLines = 3,
                            shape = RoundedCornerShape(24.dp),
                            enabled = !isProcessing
                        )
                        
                        Spacer(modifier = Modifier.width(8.dp))
                        
                        if (textInput.isNotBlank()) {
                            IconButton(
                                onClick = {
                                    val textToSend = textInput.trim()
                                    textInput = ""
                                    viewModel.sendMessage(textToSend, sessionId, mode)
                                },
                                enabled = !isProcessing
                            ) {
                                Icon(Icons.Default.Send, contentDescription = "Send", tint = PrimaryBlue)
                            }
                        } else {
                            FloatingActionButton(
                                onClick = { viewModel.toggleRecording(context, sessionId, mode) },
                                containerColor = if (isRecording) ErrorRed else PrimaryBlue,
                                shape = CircleShape,
                                modifier = Modifier
                                    .size(56.dp)
                                    .scale(pulseScale)
                            ) {
                                Icon(Icons.Default.Mic, contentDescription = "Record Speech", tint = Color.White)
                            }
                        }
                    }
                }
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Error banner
            AnimatedVisibility(visible = error != null) {
                Surface(
                    color = ErrorRed.copy(alpha = 0.15f),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = error ?: "",
                        color = ErrorRed,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(12.dp)
                    )
                }
            }

            // Phase 3: IELTS Part 2 Timer Card
            if (isPart2) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 4.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFF8FAFC)),
                    border = BorderStroke(1.dp, PrimaryBlue.copy(alpha = 0.5f))
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        when (timerPhase) {
                            "idle" -> {
                                Column {
                                    Text("IELTS Part 2: Long Turn", style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = PrimaryBlue)
                                    Text("60s prep + 120s speak", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                                }
                                Button(
                                    onClick = { viewModel.startPrepTimer() },
                                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                                    modifier = Modifier.height(34.dp)
                                ) {
                                    Text("Start 60s Prep", style = MaterialTheme.typography.labelSmall)
                                }
                            }
                            "prep" -> {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    CircularProgressIndicator(
                                        progress = { prepSeconds / 60f },
                                        modifier = Modifier.size(24.dp),
                                        strokeWidth = 3.dp,
                                        color = PrimaryBlue
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("Prep: ${prepSeconds}s", fontWeight = FontWeight.Bold, color = PrimaryBlue)
                                }
                                OutlinedButton(
                                    onClick = { viewModel.startSpeakingTimer() },
                                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                                    modifier = Modifier.height(30.dp)
                                ) {
                                    Text("Speak Now", style = MaterialTheme.typography.labelSmall)
                                }
                            }
                            "speaking" -> {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(Icons.Default.Mic, contentDescription = null, tint = ErrorRed, modifier = Modifier.size(20.dp))
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text("Speaking: ${speakingSeconds}s left", fontWeight = FontWeight.Bold, color = ErrorRed)
                                }
                            }
                            else -> {
                                Text("Time's Up! Wrap up your turn.", fontWeight = FontWeight.SemiBold, color = SuccessGreen)
                            }
                        }
                    }
                }
            }

            // Phase 3: Test Completed Banner
            AnimatedVisibility(visible = isIeltsCompleted) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 6.dp),
                    colors = CardDefaults.cardColors(containerColor = PrimaryBlue),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Test Completed! 🏆", color = Color.White, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleSmall)
                            Text("Assessment ready. View your Band score.", color = Color.White.copy(alpha = 0.85f), style = MaterialTheme.typography.bodySmall)
                        }
                        Button(
                            onClick = { onNavigateToIeltsReport(sessionId) },
                            colors = ButtonDefaults.buttonColors(containerColor = Color.White, contentColor = PrimaryBlue)
                        ) {
                            Text("View Band", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }


            LazyColumn(
                state = listState,
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                if (messages.isEmpty() && !isProcessing) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 48.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = "Tap the microphone or type to start your speaking practice.",
                                color = Color.Gray,
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                }

                items(messages) { msg ->
                    MessageBubble(
                        message = msg,
                        onApplyPrompt = { phrase ->
                            // If prompt is in format 'Try saying: "..."', extract inside quotes or use full phrase
                            val extracted = if (phrase.contains("\"")) {
                                phrase.substringAfter("\"").substringBeforeLast("\"")
                            } else {
                                phrase
                            }
                            textInput = extracted
                        },
                        onSpeak = { text ->
                            viewModel.speakText(text)
                        },
                        onSelectWord = { word ->
                            viewModel.selectWordForPronunciation(word)
                        }
                    )
                }

                if (isProcessing) {
                    item {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(8.dp)
                        ) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(18.dp),
                                strokeWidth = 2.dp,
                                color = PrimaryBlue
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("AI Coach is thinking...", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                        }
                    }
                }
            }
        }
    }

    // Phase 5: Pronunciation Drill & Phonetic Dialog
    if (selectedWord != null) {
        PronunciationDrillDialog(
            word = selectedWord!!,
            drillResult = drillResult,
            isDrilling = isDrilling,
            onDismiss = { viewModel.dismissPronunciationSheet() },
            onListen = { viewModel.speakText(selectedWord!!.word) },
            onPractice = { viewModel.practiceDrill(selectedWord!!.word, selectedWord!!.word) }
        )
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun MessageBubble(
    message: MessageItem,
    onApplyPrompt: (String) -> Unit = {},
    onSpeak: (String) -> Unit = {},
    onSelectWord: (WordPronunciationDto) -> Unit = {}
) {
    val isUser = message.role == "user"
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
    ) {
        Text(
            text = if (isUser) "You" else "AI Coach",
            style = MaterialTheme.typography.labelSmall,
            color = Color.Gray,
            modifier = Modifier.padding(bottom = 4.dp, start = 4.dp, end = 4.dp)
        )

        Surface(
            color = if (isUser) PrimaryBlue else Color(0xFFF1F5F9),
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (isUser) 16.dp else 4.dp,
                bottomEnd = if (isUser) 4.dp else 16.dp
            ),
            modifier = Modifier.widthIn(max = 320.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                // Phase 5: Interactive word highlighting for user pronunciation feedback
                if (isUser && message.pronunciation != null && message.pronunciation.words.isNotEmpty()) {
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        message.pronunciation.words.forEach { wordItem ->
                            val isProblem = wordItem.needsReview
                            Surface(
                                color = if (isProblem) Color(0xFFF59E0B) else Color.White.copy(alpha = 0.2f),
                                shape = RoundedCornerShape(6.dp),
                                modifier = Modifier.clickable { onSelectWord(wordItem) }
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                ) {
                                    Text(
                                        text = wordItem.word,
                                        color = if (isProblem) Color(0xFF78350F) else Color.White,
                                        style = MaterialTheme.typography.bodyMedium,
                                        fontWeight = if (isProblem) FontWeight.Bold else FontWeight.Normal
                                    )
                                    if (isProblem) {
                                        Spacer(modifier = Modifier.width(2.dp))
                                        Text("⚠️", fontSize = 10.sp)
                                    }
                                }
                            }
                        }
                    }
                } else {
                    Text(
                        text = message.text,
                        color = if (isUser) Color.White else Color(0xFF1E293B),
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }

        // Phase 5: Pronunciation score pill below user bubble
        if (isUser && message.pronunciation != null) {
            val pron = message.pronunciation
            Surface(
                color = Color(0xFFECFDF5),
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, Color(0xFFA7F3D0)),
                modifier = Modifier.padding(top = 4.dp, end = 4.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "🎙️ Pronunciation: ${pron.overallScore.toInt()}% (Band ${pron.estimatedBand})",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color(0xFF065F46),
                        fontWeight = FontWeight.SemiBold
                    )
                    if (pron.problemWords.isNotEmpty()) {
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "• Tap highlighted words to practice",
                            style = MaterialTheme.typography.labelSmall,
                            color = Color(0xFFD97706)
                        )
                    }
                }
            }
        }
        
        // Phase 2: Say-it-again card
        if (!message.repeatPrompt.isNullOrBlank()) {
            SayItAgainCard(
                prompt = message.repeatPrompt,
                onSpeak = {
                    val phrase = if (message.repeatPrompt.contains("\"")) {
                        message.repeatPrompt.substringAfter("\"").substringBeforeLast("\"")
                    } else {
                        message.repeatPrompt
                    }
                    onSpeak(phrase)
                },
                onApply = { onApplyPrompt(message.repeatPrompt) }
            )
        }

        if (message.corrections.isNotEmpty()) {
            Spacer(modifier = Modifier.height(6.dp))
            message.corrections.forEach { correction ->
                CorrectionCard(
                    correction = correction,
                    onSpeak = { onSpeak(correction.corrected) }
                )
            }
        }
    }
}

@Composable
fun PronunciationDrillDialog(
    word: WordPronunciationDto,
    drillResult: PronunciationDrillResponseDto?,
    isDrilling: Boolean,
    onDismiss: () -> Unit,
    onListen: () -> Unit,
    onPractice: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("🎙️ Pronunciation Drill", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Surface(
                    color = if (word.needsReview) Color(0xFFFEF3C7) else Color(0xFFDCFCE7),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = if (word.needsReview) "Needs Review" else "Good (${(word.confidence * 100).toInt()}%)",
                        color = if (word.needsReview) Color(0xFF92400E) else Color(0xFF15803D),
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                // Word and IPA
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = word.word,
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = PrimaryBlue
                    )
                    Surface(
                        color = Color(0xFFEFF6FF),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(
                            text = word.expectedIpa,
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF1E40AF),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }

                // Syllables breakdown
                if (word.syllables.isNotEmpty()) {
                    Column {
                        Text("SYLLABLES & STRESS", style = MaterialTheme.typography.labelSmall, color = Color.Gray, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            word.syllables.forEachIndexed { index, syl ->
                                val isStressed = index == word.stressIndex
                                Surface(
                                    color = if (isStressed) PrimaryBlue else Color(0xFFE2E8F0),
                                    shape = RoundedCornerShape(6.dp)
                                ) {
                                    Text(
                                        text = if (isStressed) syl.uppercase() else syl.lowercase(),
                                        color = if (isStressed) Color.White else Color.DarkGray,
                                        style = MaterialTheme.typography.labelMedium,
                                        fontWeight = if (isStressed) FontWeight.Bold else FontWeight.Normal,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                    )
                                }
                            }
                        }
                    }
                }

                // Phonetic Tip
                if (!word.feedback.isNullOrBlank()) {
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFFFFBEB)),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Row(modifier = Modifier.padding(10.dp), verticalAlignment = Alignment.Top) {
                            Text("💡", fontSize = 16.sp)
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = word.feedback,
                                style = MaterialTheme.typography.bodySmall,
                                color = Color(0xFF92400E)
                            )
                        }
                    }
                }

                // Drill Result if available
                if (drillResult != null) {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = if (drillResult.score >= 80) Color(0xFFF0FDF4) else Color(0xFFFEF2F2)
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Column(modifier = Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween,
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text(
                                    text = "Your Score: ${drillResult.score.toInt()}%",
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = if (drillResult.score >= 80) Color(0xFF15803D) else Color(0xFFDC2626)
                                )
                                Text(
                                    text = drillResult.accuracy,
                                    style = MaterialTheme.typography.labelSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = if (drillResult.score >= 80) Color(0xFF15803D) else Color(0xFFDC2626)
                                )
                            }
                            Text(
                                text = "Example: \"${drillResult.sampleSentence}\"",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.Gray
                            )
                        }
                    }
                }

                // Action Buttons: Listen & Practice
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(
                        onClick = onListen,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("🔊 Listen", fontWeight = FontWeight.Bold)
                    }
                    Button(
                        onClick = onPractice,
                        modifier = Modifier.weight(1f),
                        enabled = !isDrilling,
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                    ) {
                        if (isDrilling) {
                            CircularProgressIndicator(modifier = Modifier.size(16.dp), color = Color.White, strokeWidth = 2.dp)
                        } else {
                            Text("🎙️ Practice", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Close", fontWeight = FontWeight.Bold)
            }
        }
    )
}

@Composable
fun SayItAgainCard(
    prompt: String,
    onSpeak: () -> Unit,
    onApply: () -> Unit
) {
    Card(
        modifier = Modifier
            .widthIn(max = 320.dp)
            .padding(top = 6.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF0FDF4)),
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.5f))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "🔁 SAY IT AGAIN",
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                    color = SuccessGreen
                )
                IconButton(onClick = onSpeak, modifier = Modifier.size(24.dp)) {
                    Icon(
                        Icons.Default.VolumeUp,
                        contentDescription = "Listen correct sentence",
                        tint = SuccessGreen,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = prompt,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
                color = Color(0xFF166534)
            )
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedButton(
                onClick = onApply,
                modifier = Modifier.fillMaxWidth(),
                contentPadding = PaddingValues(vertical = 4.dp, horizontal = 8.dp)
            ) {
                Text("Practice this sentence", style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}

@Composable
fun CorrectionCard(
    correction: CorrectionDto,
    onSpeak: () -> Unit = {}
) {
    Card(
        modifier = Modifier
            .widthIn(max = 320.dp)
            .padding(top = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFFEF2F2)),
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, Color(0xFFFECACA))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Surface(
                    color = Color(0xFFFEE2E2),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text(
                        text = correction.category.uppercase(),
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = ErrorRed,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
                IconButton(onClick = onSpeak, modifier = Modifier.size(24.dp)) {
                    Icon(
                        Icons.Default.VolumeUp,
                        contentDescription = "Listen to corrected",
                        tint = SuccessGreen,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(6.dp))
            Text("✗ ${correction.original}", color = ErrorRed, style = MaterialTheme.typography.bodyMedium)
            Text("✓ ${correction.corrected}", color = SuccessGreen, fontWeight = FontWeight.SemiBold, style = MaterialTheme.typography.bodyMedium)
            if (correction.explanation.isNotBlank()) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(correction.explanation, style = MaterialTheme.typography.bodySmall, color = Color(0xFF64748B))
            }
        }
    }
}

