package com.ielts.ai.speaking

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.ielts.ai.speaking.ui.navigation.Screen
import com.ielts.ai.speaking.ui.screens.conversation.ConversationScreen
import com.ielts.ai.speaking.ui.screens.home.HomeScreen
import com.ielts.ai.speaking.ui.screens.settings.SettingsScreen
import com.ielts.ai.speaking.ui.theme.IeltsSpeakingAiTheme
import com.ielts.ai.speaking.core.network.ApiClient

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ApiClient.initialize(applicationContext)
        setContent {
            IeltsSpeakingAiTheme {
                // Request audio permission at launch if not granted
                val permissionLauncher = rememberLauncherForActivityResult(
                    contract = ActivityResultContracts.RequestPermission()
                ) { /* permission result callback */ }

                LaunchedEffect(Unit) {
                    val hasPermission = ContextCompat.checkSelfPermission(
                        this@MainActivity,
                        Manifest.permission.RECORD_AUDIO
                    ) == PackageManager.PERMISSION_GRANTED
                    if (!hasPermission) {
                        permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                    }
                }

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    
                    NavHost(
                        navController = navController,
                        startDestination = Screen.Home.route
                    ) {
                        composable(Screen.Home.route) {
                            HomeScreen(
                                onNavigateToSettings = {
                                    navController.navigate(Screen.Settings.route)
                                },
                                onNavigateToMistakes = {
                                    navController.navigate(Screen.Mistakes.route)
                                },
                                onNavigateToProgress = {
                                    navController.navigate(Screen.Progress.route)
                                },
                                onNavigateToConversation = { sessionId, mode, topic ->
                                    navController.navigate(Screen.Conversation.createRoute(sessionId, mode, topic))
                                }
                            )
                        }
                        
                        composable(Screen.Conversation.route) { backStackEntry ->
                            val sessionId = backStackEntry.arguments?.getString("sessionId") ?: ""
                            val mode = backStackEntry.arguments?.getString("mode") ?: ""
                            val topic = backStackEntry.arguments?.getString("topic") ?: ""
                            
                            ConversationScreen(
                                sessionId = sessionId,
                                mode = mode,
                                topic = topic,
                                onNavigateBack = {
                                    navController.popBackStack()
                                },
                                onNavigateToIeltsReport = { reportSessionId ->
                                    navController.navigate(Screen.IeltsReport.createRoute(reportSessionId))
                                }
                            )
                        }
                        
                        composable(Screen.Settings.route) {
                            SettingsScreen(
                                onNavigateBack = {
                                    navController.popBackStack()
                                }
                            )
                        }

                        composable(Screen.Mistakes.route) {
                            com.ielts.ai.speaking.ui.screens.mistakes.MistakesScreen(
                                onNavigateBack = {
                                    navController.popBackStack()
                                }
                            )
                        }

                        composable(Screen.Progress.route) {
                            com.ielts.ai.speaking.ui.screens.progress.ProgressScreen(
                                onNavigateBack = {
                                    navController.popBackStack()
                                },
                                onNavigateToMistakes = {
                                    navController.navigate(Screen.Mistakes.route)
                                },
                                onNavigateToConversation = { sessionId, mode, topic ->
                                    navController.navigate(Screen.Conversation.createRoute(sessionId, mode, topic))
                                }
                            )
                        }

                        composable(Screen.IeltsReport.route) { backStackEntry ->
                            val sessionId = backStackEntry.arguments?.getString("sessionId") ?: ""
                            com.ielts.ai.speaking.ui.screens.ielts.IeltsReportScreen(
                                sessionId = sessionId,
                                onNavigateHome = {
                                    navController.popBackStack(Screen.Home.route, false)
                                }
                            )
                        }


                    }
                }
            }
        }
    }
}
