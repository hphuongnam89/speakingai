package com.ielts.ai.speaking.ui.navigation

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Conversation : Screen("conversation/{sessionId}/{mode}/{topic}") {
        fun createRoute(sessionId: String, mode: String, topic: String) = "conversation/$sessionId/$mode/$topic"
    }
    object Settings : Screen("settings")
    object Mistakes : Screen("mistakes")
    object Progress : Screen("progress")
    object IeltsReport : Screen("ielts_report/{sessionId}") {
        fun createRoute(sessionId: String) = "ielts_report/$sessionId"
    }
}


