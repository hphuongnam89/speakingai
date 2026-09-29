package com.ielts.ai.speaking.core.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {
    const val DEFAULT_BASE_URL = "http://10.0.2.2:8000/"

    var currentBaseUrl: String = DEFAULT_BASE_URL
        private set

    private var currentService: ApiService? = null

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
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
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
