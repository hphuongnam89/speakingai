package com.ielts.ai.speaking.core.network

import android.content.Context

object ProfileSelectorStore {
    private const val PREFS = "backend_credentials"
    private const val PROFILE_ID = "selected_profile_id"

    fun read(context: Context): String? = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        .getString(PROFILE_ID, null)

    fun write(context: Context, profileId: String?) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().apply {
            if (profileId.isNullOrBlank()) remove(PROFILE_ID) else putString(PROFILE_ID, profileId)
        }.apply()
    }
}
