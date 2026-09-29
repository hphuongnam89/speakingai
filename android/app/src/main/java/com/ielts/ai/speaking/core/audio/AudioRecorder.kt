package com.ielts.ai.speaking.core.audio

import android.media.MediaRecorder
import java.io.File

class AudioRecorder {
    private var recorder: MediaRecorder? = null
    private var currentOutputFile: File? = null
    private var recording = false

    fun startRecording(outputFile: File) {
        if (recording) stopRecording()
        
        currentOutputFile = outputFile
        recorder = MediaRecorder().apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setOutputFile(outputFile.absolutePath)
            
            try {
                prepare()
                start()
                recording = true
            } catch (e: Exception) {
                e.printStackTrace()
                release()
                recording = false
            }
        }
    }

    fun stopRecording(): File? {
        if (!recording) return null
        
        return try {
            recorder?.stop()
            recorder?.release()
            recording = false
            currentOutputFile
        } catch (e: Exception) {
            e.printStackTrace()
            recorder?.release()
            recording = false
            null
        } finally {
            recorder = null
        }
    }

    fun isRecording(): Boolean {
        return recording
    }
}
