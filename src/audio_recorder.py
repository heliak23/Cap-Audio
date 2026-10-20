import io
import wave
import threading
import winsound
import numpy as np
import sounddevice as sd
from src.config import Config

class AudioRecorder:
    def __init__(self):
        self.sample_rate = Config.SAMPLE_RATE
        self.channels = Config.CHANNELS
        self.is_recording = False
        self.audio_chunks = []
        self._stream = None
        self._lock = threading.Lock()

    def _play_feedback_sound(self, frequency: int, duration_ms: int):
        if Config.AUDIO_FEEDBACK:
            threading.Thread(
                target=winsound.Beep,
                args=(frequency, duration_ms),
                daemon=True
            ).start()

    def _audio_callback(self, indata, frames, time_info, status):
        if self.is_recording:
            # indata shape: (frames, channels), dtype float32
            # Converter para int16 PCM para compatibilidade máxima e baixo consumo
            pcm16 = (indata * 32767).astype(np.int16)
            with self._lock:
                self.audio_chunks.append(pcm16.copy())

    def start(self):
        with self._lock:
            if self.is_recording:
                return
            self.audio_chunks = []
            self.is_recording = True

        self._play_feedback_sound(1300, 70)
        
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._audio_callback
        )
        self._stream.start()

    def stop(self) -> bytes:
        with self._lock:
            if not self.is_recording:
                return b""
            self.is_recording = False

        self._play_feedback_sound(850, 70)

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self.audio_chunks:
                return b""
            audio_data = np.concatenate(self.audio_chunks, axis=0)

        # Empacotar em formato WAV padrão
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())

        return wav_buffer.getvalue()
