package com.ielts.ai.speaking

import android.app.Application
import io.sentry.android.core.SentryAndroid

class SpeakingApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.SENTRY_ANDROID_DSN.isNotBlank()) {
            SentryAndroid.init(this) { options ->
                options.dsn = BuildConfig.SENTRY_ANDROID_DSN
                options.sendDefaultPii = false
                options.isAttachScreenshot = false
                options.isAttachViewHierarchy = false
                options.isEnableUserInteractionBreadcrumbs = false
                options.tracesSampleRate = 0.0
            }
        }
    }
}
