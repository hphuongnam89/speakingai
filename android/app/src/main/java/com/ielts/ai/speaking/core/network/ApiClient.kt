package com.ielts.ai.speaking.core.network

import android.content.Context
import com.ielts.ai.speaking.BuildConfig
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {
    const val DEFAULT_BASE_URL = "http://10.0.2.2:8000/"

    var currentBaseUrl: String = DEFAULT_BASE_URL
        private set

    @Volatile
    private var accessToken: String = ""

    private var currentService: ApiService? = null

    fun initialize(context: Context) {
        accessToken = ApiCredentialStore.readAccessToken(context.applicationContext).orEmpty()
    }

    fun updateAccessToken(value: String) {
        accessToken = value.trim()
    }

    fun getService(): ApiService {
        return currentService ?: create(currentBaseUrl)
    }

    fun updateBaseUrl(newUrl: String): ApiService {
        val normalizedUrl = if (newUrl.endsWith("/")) newUrl else "$newUrl/"
        currentBaseUrl = normalizedUrl
        return create(normalizedUrl)
    }

    fun create(baseUrl: String = currentBaseUrl): ApiService {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BASIC else HttpLoggingInterceptor.Level.NONE
        }

        val client = OkHttpClient.Builder()
            .addInterceptor { chain ->
                val request = chain.request().newBuilder().apply {
                    accessToken.takeIf { it.isNotBlank() }?.let { header("Authorization", "Bearer $it") }
                }.build()
                chain.proceed(request)
            }
            .addInterceptor(loggingInterceptor)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(360, TimeUnit.SECONDS)
            .writeTimeout(120, TimeUnit.SECONDS)
            .build()

        val service = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)

        currentService = service
        return service
    }
}
