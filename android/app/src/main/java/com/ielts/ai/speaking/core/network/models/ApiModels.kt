package com.ielts.ai.speaking.core.network.models

import com.google.gson.annotations.SerializedName

data class AuthRequest(val email: String, val password: String)
data class AuthResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("expires_in") val expiresIn: Int,
    @SerializedName("user_id") val userId: String
)

data class SessionCreateRequest(
    val mode: String,
    val topic: String? = null
)

data class SessionResponse(
    val id: String,
    val mode: String,
    @SerializedName("started_at") val startedAt: String,
    @SerializedName("ended_at") val endedAt: String? = null,
    val topic: String? = null,
    @SerializedName("total_speaking_ms") val totalSpeakingMs: Int = 0
)

data class SessionDetailResponse(
    val session: SessionResponse,
    val turns: List<TurnDto>
)

data class TurnDto(
    val id: String?,
    val role: String,
    val transcript: String,
    @SerializedName("created_at") val createdAt: String?
)

data class ConversationRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("user_text") val userText: String,
    val mode: String = "daily",
    @SerializedName("correction_level") val correctionLevel: String? = null
)

data class ConversationResponse(
    val message: String,
    val corrections: List<CorrectionDto> = emptyList(),
    @SerializedName("repeat_prompt") val repeatPrompt: String? = null,
    @SerializedName("tts_text") val ttsText: String?,
    @SerializedName("turn_id") val turnId: String?,
    val pronunciation: PronunciationReportDto? = null,
    @SerializedName("provider_used") val providerUsed: String? = null,
    @SerializedName("fallback_triggered") val fallbackTriggered: Boolean? = false,
    @SerializedName("latency_ms") val latencyMs: Float? = null
)

data class CorrectionDto(
    val original: String,
    val corrected: String,
    val explanation: String,
    val category: String = "grammar",
    @SerializedName("should_repeat") val shouldRepeat: Boolean = false
)

data class MistakeDto(
    val id: String,
    @SerializedName("user_id") val userId: String,
    @SerializedName("session_id") val sessionId: String?,
    @SerializedName("turn_id") val turnId: String?,
    val category: String,
    @SerializedName("original_text") val originalText: String,
    @SerializedName("corrected_text") val correctedText: String,
    val explanation: String?,
    val severity: Int = 1,
    @SerializedName("first_seen_at") val firstSeenAt: String? = null,
    @SerializedName("last_seen_at") val lastSeenAt: String? = null,
    @SerializedName("occurrence_count") val occurrenceCount: Int = 1,
    val resolved: Boolean = false
)

data class MistakeResolveResponse(
    val id: String,
    val resolved: Boolean
)

data class UserSettingsDto(
    @SerializedName("user_id") val userId: String,
    @SerializedName("correction_level") val correctionLevel: String = "important",
    @SerializedName("local_only") val localOnly: Boolean = false,
    @SerializedName("cloud_fallback") val cloudFallback: Boolean = true,
    @SerializedName("provider_preference") val providerPreference: String = "auto",
    @SerializedName("preferred_model") val preferredModel: String? = null,
    val voice: String = "en-US"
)

data class UserSettingsUpdateRequest(
    @SerializedName("correction_level") val correctionLevel: String? = null,
    @SerializedName("local_only") val localOnly: Boolean? = null,
    @SerializedName("cloud_fallback") val cloudFallback: Boolean? = null,
    @SerializedName("provider_preference") val providerPreference: String? = null
)

data class HealthResponse(
    val status: String,
    val model: String?
)

data class ModelListResponse(
    val active: String,
    val available: List<String>,
    @SerializedName("cloud_fallback_enabled") val cloudFallbackEnabled: Boolean = false,
    @SerializedName("routing_preference") val routingPreference: String = "auto"
)

data class ProviderHealthDto(
    val available: Boolean,
    val error: String? = null,
    @SerializedName("latency_ms") val latencyMs: Float? = null,
    val model: String? = null
)

data class ModelStatusResponse(
    @SerializedName("active_provider") val activeProvider: String,
    @SerializedName("routing_preference") val routingPreference: String,
    @SerializedName("cloud_fallback_ready") val cloudFallbackReady: Boolean,
    val ollama: ProviderHealthDto? = null,
    val deepseek: ProviderHealthDto? = null
)

data class ModelSelectRequest(
    val preference: String? = null,
    val model: String? = null
)

data class TranscribeResponse(
    val text: String,
    val error: String? = null,
    val pronunciation: PronunciationReportDto? = null
)

// Phase 3: IELTS Speaking Models
data class CueCardDto(
    val id: String,
    val topic: String,
    val title: String,
    val bullets: List<String>,
    @SerializedName("follow_up") val followUp: String? = null,
    @SerializedName("part_3_questions") val part3Questions: List<String>? = null
)

data class IeltsStartRequest(
    val part: String = "part1", // part1, part2, part3, full_mock
    val topic: String? = null
)

data class IeltsStartResponse(
    @SerializedName("session_id") val sessionId: String,
    val part: String,
    @SerializedName("cue_card") val cueCard: CueCardDto? = null,
    val greeting: String,
    val question: String
)

data class IeltsRespondRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("user_text") val userText: String,
    val part: String = "part1"
)

data class IeltsRespondResponse(
    val message: String,
    @SerializedName("tts_text") val ttsText: String,
    @SerializedName("is_completed") val isCompleted: Boolean = false,
    @SerializedName("next_part") val nextPart: String? = null
)

data class SuggestedExpressionDto(
    val original: String,
    val upgraded: String,
    val context: String? = null
)

data class IeltsEvaluationResponse(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("overall_band") val overallBand: Float,
    @SerializedName("fluency_score") val fluencyScore: Float,
    @SerializedName("fluency_feedback") val fluencyFeedback: String,
    @SerializedName("lexical_score") val lexicalScore: Float,
    @SerializedName("lexical_feedback") val lexicalFeedback: String,
    @SerializedName("grammar_score") val grammarScore: Float,
    @SerializedName("grammar_feedback") val grammarFeedback: String,
    @SerializedName("pronunciation_score") val pronunciationScore: Float? = null,
    val strengths: List<String> = emptyList(),
    @SerializedName("areas_for_improvement") val areasForImprovement: List<String> = emptyList(),
    @SerializedName("suggested_expressions") val suggestedExpressions: List<SuggestedExpressionDto> = emptyList(),
    @SerializedName("examiner_summary") val examinerSummary: String,
    val disclaimer: String = "Estimated score — not an official IELTS result."
)

// Phase 4: Progress & Adaptive Learning Models
data class ProgressSummaryDto(
    val streak: Int,
    @SerializedName("total_speaking_minutes") val totalSpeakingMinutes: Float,
    @SerializedName("total_sessions") val totalSessions: Int,
    @SerializedName("avg_wpm") val avgWpm: Float,
    @SerializedName("latest_band") val latestBand: Float? = null,
    @SerializedName("total_mistakes") val totalMistakes: Int
)

data class DailyStatItemDto(
    val date: String,
    @SerializedName("day_of_week") val dayOfWeek: String,
    @SerializedName("speaking_minutes") val speakingMinutes: Float,
    @SerializedName("session_count") val sessionCount: Int,
    @SerializedName("mistake_count") val mistakeCount: Int
)

data class AdaptivePlanDto(
    @SerializedName("today_objective") val todayObjective: String,
    @SerializedName("top_weaknesses") val topWeaknesses: List<String> = emptyList(),
    @SerializedName("recommended_topic") val recommendedTopic: String,
    @SerializedName("challenge_phrases") val challengePhrases: List<String> = emptyList()
)

// Phase 5: Pronunciation Engine Models
data class WordPronunciationDto(
    val word: String,
    @SerializedName("expected_ipa") val expectedIpa: String,
    val confidence: Float? = null,
    val start: Float? = null,
    val end: Float? = null,
    @SerializedName("needs_review") val needsReview: Boolean = false,
    val syllables: List<String> = emptyList(),
    @SerializedName("stress_index") val stressIndex: Int? = null,
    val feedback: String? = null
)

data class RhythmMetricsDto(
    @SerializedName("speech_rate_wpm") val speechRateWpm: Float? = null,
    @SerializedName("pause_count") val pauseCount: Int? = null,
    @SerializedName("pause_duration_ratio") val pauseDurationRatio: Float? = null,
    @SerializedName("rhythm_consistency_score") val rhythmConsistencyScore: Float? = null
)

data class PronunciationAnalysisRequest(
    val text: String,
    @SerializedName("session_id") val sessionId: String? = "default",
    @SerializedName("audio_duration_ms") val audioDurationMs: Long? = null
)

data class PronunciationReportDto(
    @SerializedName("recognition_confidence") val recognitionConfidence: Float? = null,
    @SerializedName("pronunciation_score") val pronunciationScore: Float? = null,
    @SerializedName("pronunciation_errors") val pronunciationErrors: List<PronunciationErrorDto> = emptyList(),
    val scorer: String? = null,
    @SerializedName("word_count") val wordCount: Int,
    val words: List<WordPronunciationDto> = emptyList(),
    @SerializedName("problem_words") val problemWords: List<WordPronunciationDto> = emptyList(),
    val rhythm: RhythmMetricsDto? = null,
    @SerializedName("feedback_summary") val feedbackSummary: String,
    val disclaimer: String = "Whisper confidence is not pronunciation accuracy. Optional OpenPronounce scoring is experimental and is not an IELTS result."
)

data class PronunciationErrorDto(
    val word: String,
    @SerializedName("expected_ipa") val expectedIpa: String,
    @SerializedName("heard_ipa") val heardIpa: String,
    val confidence: Float? = null
)

data class PronunciationDrillRequest(
    @SerializedName("target_word") val targetWord: String
)

data class PronunciationDrillResponseDto(
    val word: String,
    @SerializedName("expected_ipa") val expectedIpa: String,
    val syllables: List<String> = emptyList(),
    val score: Float? = null,
    val accuracy: String,
    val tips: List<String> = emptyList(),
    @SerializedName("sample_sentence") val sampleSentence: String
)




