package com.ielts.ai.speaking.core.network

import com.ielts.ai.speaking.core.network.models.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.*

interface ApiService {
    @GET("api/v1/health")
    suspend fun checkHealth(): HealthResponse

    @GET("api/v1/models")
    suspend fun getModels(): ModelListResponse

    @GET("api/v1/models/status")
    suspend fun getModelStatus(): ModelStatusResponse

    @POST("api/v1/models/test-connection")
    suspend fun testModelConnection(): ModelStatusResponse

    @POST("api/v1/models/select")
    suspend fun selectModelPreference(@Body request: ModelSelectRequest): Map<String, Any>

    @POST("api/v1/sessions/")
    suspend fun createSession(@Body request: SessionCreateRequest): SessionResponse

    @GET("api/v1/sessions/{id}")
    suspend fun getSession(@Path("id") id: String): SessionDetailResponse

    @POST("api/v1/sessions/{id}/finish")
    suspend fun finishSession(@Path("id") id: String): SessionResponse

    @POST("api/v1/conversation/respond")
    suspend fun respond(@Body request: ConversationRequest): ConversationResponse

    @Multipart
    @POST("api/v1/speech/transcribe")
    suspend fun transcribeAudio(
        @Part audio: MultipartBody.Part,
        @Part("session_id") sessionId: RequestBody
    ): TranscribeResponse

    @GET("api/v1/settings")
    suspend fun getSettings(): UserSettingsDto

    @PUT("api/v1/settings")
    suspend fun updateSettings(@Body request: UserSettingsUpdateRequest): UserSettingsDto

    @GET("api/v1/mistakes")
    suspend fun getMistakes(): List<MistakeDto>

    @GET("api/v1/mistakes/frequent")
    suspend fun getFrequentMistakes(): List<MistakeDto>

    @POST("api/v1/mistakes/{id}/resolve")
    suspend fun resolveMistake(@Path("id") id: String): MistakeResolveResponse

    // Phase 3: IELTS Speaking
    @POST("api/v1/ielts/start")
    suspend fun startIeltsTest(@Body request: IeltsStartRequest): IeltsStartResponse

    @POST("api/v1/ielts/respond")
    suspend fun respondIelts(@Body request: IeltsRespondRequest): IeltsRespondResponse

    @POST("api/v1/ielts/evaluate/{session_id}")
    suspend fun evaluateIelts(@Path("session_id") sessionId: String): IeltsEvaluationResponse

    // Phase 4: Progress & Adaptive Learning
    @GET("api/v1/progress/summary")
    suspend fun getProgressSummary(@Query("user_id") userId: String = "default"): ProgressSummaryDto

    @GET("api/v1/progress/weekly")
    suspend fun getWeeklyProgress(@Query("user_id") userId: String = "default"): List<DailyStatItemDto>

    @GET("api/v1/progress/adaptive-plan")
    suspend fun getAdaptivePlan(@Query("user_id") userId: String = "default"): AdaptivePlanDto

    // Phase 5: Pronunciation Engine
    @POST("api/v1/pronunciation/analyze")
    suspend fun analyzePronunciation(@Body request: PronunciationAnalysisRequest): PronunciationReportDto

    @GET("api/v1/pronunciation/dictionary/{word}")
    suspend fun getWordPhonetics(@Path("word") word: String): WordPronunciationDto

    @POST("api/v1/pronunciation/drill")
    suspend fun evaluatePronunciationDrill(@Body request: PronunciationDrillRequest): PronunciationDrillResponseDto
}



