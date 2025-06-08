import os
import threading
import time
import wave

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import sounddevice as sd
import soundfile as sf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

from ColorIDManager import ColorIDManager
from ListWidget import ListWidget
from voice_effects.robot_effect import _robot_effect_core_int16
from VolumeVisualizer import VolumeVisualizer

# print(sd.query_devices())
VIRTUAL_CABLE_DEVICE_ID = 8  # 6
MICROPHONE_DEVICE_ID = 1  # 1
STEREO_MIX = 0

CHUNK = 256
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class SoundboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.color_id_manager = ColorIDManager()

        self.voices_folder = "voice_effects"
        self.sounds_folder = "sounds"

        # App configuration
        self.title("Audio Soundboard")
        self.geometry("1280x720")
        self.minsize(1280, 720)

        # Configure the grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=15)
        self.grid_columnconfigure(1, weight=1, minsize=600)
        self.grid_columnconfigure(2, weight=1, minsize=550)

        # Create main frames
        self.micro_info_frame = ctk.CTkFrame(self, corner_radius=10, width=60)
        self.micro_info_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ns")

        self.middle_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.middle_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")

        self.sound_panel_frame = ctk.CTkFrame(
            self, corner_radius=10, fg_color="transparent"
        )
        self.sound_panel_frame.grid(
            row=0, column=2, padx=(0, 15), pady=15, sticky="nsew"
        )

        # Configure middle_frame
        self.middle_frame.grid_rowconfigure(0, weight=1)
        self.middle_frame.grid_rowconfigure(1, weight=0)
        self.middle_frame.grid_columnconfigure(0, weight=1)

        self.voice_change_frame = ctk.CTkFrame(
            self.middle_frame, corner_radius=10, fg_color="transparent"
        )
        self.voice_change_frame.grid(
            row=0, column=0, padx=0, pady=(0, 15), sticky="nsew"
        )

        self.middle_lower_frame = ctk.CTkFrame(
            self.middle_frame, corner_radius=10, fg_color="transparent"
        )
        self.middle_lower_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nswe")

        self.middle_lower_frame.grid_rowconfigure(0, weight=1)
        self.middle_lower_frame.grid_columnconfigure(0, weight=3)
        self.middle_lower_frame.grid_columnconfigure(0, weight=1)

        self.micro_info_text_frame = ctk.CTkFrame(
            self.middle_lower_frame, corner_radius=10
        )
        self.micro_info_text_frame.grid(
            row=0, column=0, padx=(0, 15), pady=0, sticky="we"
        )

        self.settings_frame = ctk.CTkFrame(self.middle_lower_frame, corner_radius=10)
        self.settings_frame.grid(row=0, column=1, padx=0, pady=0, sticky="ns")

        # micro_info frame
        self.micro_info_frame.grid_columnconfigure((0, 1), weight=1)
        self.micro_info_frame.grid_rowconfigure(0, weight=1)
        self.micro_info_frame.grid_propagate(False)

        self.micro_info_left_frame = ctk.CTkFrame(
            self.micro_info_frame, corner_radius=10, fg_color="transparent"
        )
        self.micro_info_left_frame.grid(
            row=0, column=0, sticky="nsew", padx=10, pady=10
        )

        self.micro_info_right_frame = ctk.CTkFrame(
            self.micro_info_frame, corner_radius=10, fg_color="transparent"
        )
        self.micro_info_right_frame.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10
        )

        self.real_sound_visualizer = VolumeVisualizer(
            self.micro_info_left_frame,
            corner_radius=10,
            inactive_dot_color="#A2A2A2",
            active_dot_color="#ffffff",
        )
        self.real_sound_visualizer.pack(fill="y", expand=True)

        self.virtual_sound_visualizer = VolumeVisualizer(
            self.micro_info_right_frame, corner_radius=10, inactive_dot_color="#A2A2A2"
        )
        self.virtual_sound_visualizer.pack(fill="y", expand=True)

        # Make voice_changer window
        self.voice_changer_list = ListWidget(self.voice_change_frame, columns=3)
        self.voice_changer_list.pack(fill="both", expand=True)

        # Make lower text info and settings
        self.micro_info_text_label = ctk.CTkLabel(
            self.micro_info_text_frame,
            text="White is your real microphone input\nGreen is the output that goes into virtual one",
            font=("Roboto", 18),
            text_color="#A2A2A2",
        )
        self.micro_info_text_label.pack(fill="x", expand=True, padx=10)

        self.settings_button = ctk.CTkButton(
            self.settings_frame, text="Settings", font=("Roboto", 18)
        )
        self.settings_button.pack(fill="x", expand=True, padx=10)

        # Make sound panel (right)
        self.sound_panel_frame.grid_columnconfigure(0, weight=1)
        self.sound_panel_frame.grid_rowconfigure(0, weight=0)
        self.sound_panel_frame.grid_rowconfigure(1, weight=1)
        self.sound_panel_frame.grid_rowconfigure(2, weight=0)

        self.sound_panel_label_frame = ctk.CTkFrame(self.sound_panel_frame)
        self.sound_panel_label_frame.grid(
            row=0, column=0, sticky="we", padx=0, pady=(0, 10)
        )

        self.sound_panel_frame_label = ctk.CTkLabel(
            self.sound_panel_label_frame, text="Sound Panel", font=("Roboto", 18)
        )
        self.sound_panel_frame_label.pack(padx=10, pady=10)

        self.sound_panel = ListWidget(self.sound_panel_frame, columns=4)
        self.sound_panel.grid(row=1, column=0, sticky="nswe")

        self.sound_panel_settings_frame = ctk.CTkFrame(
            self.sound_panel_frame, corner_radius=10
        )
        self.sound_panel_settings_frame.grid(
            row=2, column=0, sticky="we", padx=0, pady=(10, 0)
        )

        self.sound_panel_settings_button = ctk.CTkButton(
            self.sound_panel_settings_frame,
            text="Reload or upload new",
            font=("Roboto", 18),
        )
        self.sound_panel_settings_button.pack(padx=10, pady=20)

        # Warmup voice_changer (we precompile it with first its call)

        self.init_voice_changer_list()
        self.init_sound_browser()

        # Initialize UI components
        # Not Made yet
        # self.init_micro_info()

        # self.init_sound_browser()
        # self.init_voice_changers()
        # self.init_info_panel()
        # self.init_wave_display()
        #
        # # Start audio monitoring for the wave display
        # self.monitoring = False
        # self.start_monitoring()
        #
        # # Preload variables, and preload audio
        # self.audio_cache = {}
        # self.preload_audio_files()

    # --- Voice changer list setion ---

    def warmup_voice_changers(self):
        dummy_audio = np.zeros(1024, dtype=np.int16)
        self.apply_robot_effect(dummy_audio)

    def apply_robot_effect(self, audio):
        try:
            return _robot_effect_core_int16(audio)
        except Exception as e:
            print(f"Error in robot effect: {e}")
            return audio

    def init_voice_changer_list(self):
        self.warmup_voice_changers()

        files = sorted(
            os.listdir(self.voices_folder),
            key=lambda x: os.path.getmtime(os.path.join(self.voices_folder, x)),
        )

        for file in files:
            if file in ["__pycache__", "__init__.py"]:
                continue

            if file.endswith(".py"):
                file = file[:-3]
            else:
                print("File should be python code")  # TODO: Tell a user about that
                # continue

            self.voice_changer_list.add_button(
                text=file,
                width=160,
                height=90,
                fg_color="#333333",
                hover_color="#3c3c3c",
                command=lambda c=file + ".py": self.set_voice_changer(c),
                identity_indicator_color=self.color_id_manager.set_id_color(),
            )

    # --- End of Voice changer list section ---

    # --- Sound browser section ---

    def preload_audio_files(self):
        if not os.path.exists(self.sounds_folder):
            return  #  TODO: say message to user about folder not found

        for file in os.listdir(self.sounds_folder):
            if file.endswith((".wav", ".mp3", ".flac", ".ogg")):
                file_path = os.path.join(self.sounds_folder, file)

                try:
                    data, samplerate = sf.read(file_path, dtype="int16")

                    # TODO: Give user a choice to not convert into mono, for better sound
                    if len(data.shape) > 1:
                        data = np.mean(data, axis=1).astype(np.int16)

                    self.audio_cache[file_path] = {
                        "data": data,
                        "samplerate": samplerate,
                    }

                except Exception as e:
                    print(f"Failed to preload {file}: {e}")

    def init_sound_browser(self):
        self.preload_audio_files()
        self.load_sound_files()

    def load_sound_files(self):
        self.sound_panel.clear_buttons()

        files = sorted(
            os.listdir(self.sounds_folder),
            key=lambda x: os.path.getmtime(os.path.join(self.sounds_folder, x)),
        )

        for file in files:
            if file.endswith((".wav", ".mp3", ".flac", ".ogg")):
                file_cut = file[:-3] if not file.endswith(".flac") else file[:-4]
                self.sound_panel.add_button(
                    text=file_cut,
                    width=125,
                    height=68,
                    fg_color="#333333",
                    hover_color="#3c3c3c",
                    command=lambda file=file: self.play_sound(file),
                    font_size=15,
                    identity_indicator_color=self.color_id_manager.set_id_color(),
                )

        # Add a refresh button
        # refresh_btn = ctk.CTkButton(
        #     self.sound_scroll,
        #     text="Refresh Sound List",
        #     command=self.refresh_sounds,
        #     height=30,
        #     fg_color="#4D5BCE",
        # )
        # refresh_btn.pack(fill="x", pady=10)

    # --- End of Sound browser section ---

    def refresh_sounds(self):
        """Refresh sound list and preload new files"""
        self.load_sound_files()
        self.preload_audio_files()

    def init_voice_changers(self):
        # Label
        label = ctk.CTkLabel(
            self.voice_changers,
            text="Voice Changers",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        label.pack(pady=5)

        # Voice changer options in a horizontal layout
        changer_frame = ctk.CTkFrame(self.voice_changers, fg_color="transparent")
        changer_frame.pack(fill="x", padx=10, pady=5)

        # Add voice changer options
        self.changers_label = ["Normal", "High Pitch", "Low Pitch", "Robot", "Echo"]

        self.changer_list = []

        for i, changer in enumerate(self.changers_label):
            button = ctk.CTkButton(
                changer_frame,
                text=changer,
                command=lambda c=changer: self.set_voice_changer(c),
                width=100,
                height=30,
                fg_color="#4D5BCE",
            )
            button.grid(row=0, column=i, padx=5, pady=5)
            self.changer_list.append(button)

        self.changer_list[0].configure(
            fg_color="#4CAF50"
        )  # Highlight the default option

        # Voice changer control buttons
        control_frame = ctk.CTkFrame(self.voice_changers, fg_color="transparent")
        control_frame.pack(fill="x", padx=10, pady=5)

        self.vc_toggle_btn = ctk.CTkButton(
            control_frame,
            text="Start Voice Changer",
            command=self.toggle_voice_changer,
            fg_color="#4CAF50",
            width=150,
        )
        self.vc_toggle_btn.pack(side="left")

        # Voice changer state
        self.voice_changer_active = False
        self.current_voice_changer = "Normal"
        self.voice_changer_thread = None

    def init_info_panel(self):
        self.voice_changer_panel = ctk.CTkFrame(
            self.info_panel,
            fg_color="transparent",
            border_width=1,
            border_color="#CCCCCC",
        )
        self.voice_changer_panel.grid_columnconfigure(0, weight=1)
        self.voice_changer_panel.pack(fill="x", padx=10, pady=5)

        self.name_label = ctk.CTkLabel(
            self.voice_changer_panel,
            text="Voice Changer Info",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.name_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.active_label = ctk.CTkLabel(
            self.voice_changer_panel, text=f"Active: {self.voice_changer_active}"
        )
        self.active_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.mode_label = ctk.CTkLabel(
            self.voice_changer_panel, text=f"Mode: {self.current_voice_changer}"
        )
        self.mode_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    def init_wave_display(self):
        # Create matplotlib figure for the sound wave
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(4, 2))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.wave_section)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Initial plot setup for first device
        (self.line1,) = self.ax1.plot(np.zeros(CHUNK), "g-")
        self.ax1.set_ylim(-32768, 32767)
        self.ax1.set_xlim(0, CHUNK)
        self.ax1.set_ylabel("Virtual")

        # Initial plot setup for second device
        (self.line2,) = self.ax2.plot(
            np.zeros(CHUNK), "b-"
        )  # Different color for distinction
        self.ax2.set_ylim(-32768, 32767)
        self.ax2.set_xlim(0, CHUNK)
        self.ax2.set_ylabel("Microphone")

        self.figure.tight_layout()

    def update_wave_display(self):
        try:
            device_virtual = 2  # Change to function to find
            device_microphone = 1

            p = pyaudio.PyAudio()
            # Open stream for first device
            stream1 = p.open(
                format=FORMAT,
                channels=1,
                rate=RATE,
                input=True,
                input_device_index=device_virtual,
                frames_per_buffer=CHUNK,
            )

            # Open stream for second device
            stream2 = p.open(
                format=FORMAT,
                channels=1,
                rate=RATE,
                input=True,
                input_device_index=device_microphone,
                frames_per_buffer=CHUNK,
            )

            while self.monitoring:
                try:
                    # Read and update data for first device
                    data1 = stream1.read(CHUNK, exception_on_overflow=False)
                    audio_data1 = np.frombuffer(data1, dtype=np.int16)
                    self.line1.set_ydata(audio_data1)

                    # Read and update data for second device
                    data2 = stream2.read(CHUNK, exception_on_overflow=False)
                    audio_data2 = np.frombuffer(data2, dtype=np.int16)
                    self.line2.set_ydata(audio_data2)

                    # Update both plots at once
                    self.canvas.draw_idle()
                    self.canvas.flush_events()
                    time.sleep(0.01)  # Reduce CPU usage
                except Exception as e:
                    print(f"Error updating wave displays: {e}")
                    time.sleep(0.1)

        except Exception as e:
            print(f"Error setting up audio streams: {e}")
        finally:
            # Clean up resources
            if "stream1" in locals() and stream1 is not None:
                stream1.stop_stream()
                stream1.close()
            if "stream2" in locals() and stream2 is not None:
                stream2.stop_stream()
                stream2.close()
            if "p" in locals() and p is not None:
                p.terminate()

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.update_wave_display)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if hasattr(self, "monitor_thread") and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)

    def play_sound(self, file_path):
        # ChGeck if audio is preloaded
        if file_path not in self.audio_cache:
            thread = threading.Thread(target=self.play_audio_fallback, args=(file_path))
            thread.daemon = True
            thread.start()
            return

        audio_info = self.audio_cache[file_path]

        thread = threading.Thread(
            target=self.play_audio_optimized,
            args=(audio_info["data"], audio_info["samplerate"]),
        )
        thread.daemon = True
        thread.start()

    def play_audio_optimized(self, audio_data, samplerate):
        try:
            sd.play(
                audio_data,
                samplerate=samplerate,
                device=VIRTUAL_CABLE_DEVICE_ID,
                blocksize=256,
                latency="low",  # Request low latency mode
            )

        except Exception as e:
            print(f"Error playing optimized audio: {e}")

    def play_audio_fallback(self, file_path):
        """Fallback method for playing non-preloaded audio"""
        try:
            data, samplerate = sf.read(file_path, dtype="int16")

            # Convert to mono if stereo
            # TODO: give user a choice
            if len(data.shape) > 1:
                data = np.mean(data, axis=1).astype(np.int16)

            self.play_audio_optimized(data, samplerate)

        except Exception as e:
            print(f"Error in fallback audio playback: {e}")

    def uncheck_all_other_modes(self):
        for button in self.changer_list:
            button.configure(fg_color="#4D5BCE")

    def set_voice_changer(self, changer_type):
        self.current_voice_changer = changer_type
        self.mode_label.configure(text=f"Mode: {self.current_voice_changer}")
        self.uncheck_all_other_modes()
        self.changer_list[self.changers_label.index(changer_type)].configure(
            fg_color="#4CAF50"
        )
        print(f"Voice changer set to: {changer_type}")

    def toggle_voice_changer(self):
        if self.voice_changer_active:
            # Stop voice changer
            self.voice_changer_active = False
            self.vc_toggle_btn.configure(text="Start Voice Changer", fg_color="#4CAF50")
            self.active_label.configure(text=f"Active: {self.voice_changer_active}")
        else:
            # Start voice changer
            self.voice_changer_active = True
            self.vc_toggle_btn.configure(text="Stop Voice Changer", fg_color="#F44336")
            self.active_label.configure(text=f"Active: {self.voice_changer_active}")

            # Start voice changer in a thread
            if (
                self.voice_changer_thread is None
                or not self.voice_changer_thread.is_alive()
            ):
                self.voice_changer_thread = threading.Thread(target=self.voice_changer)
                self.voice_changer_thread.daemon = True
                self.voice_changer_thread.start()

    # Your existing functions with modifications
    def voice_changer(self):
        p = pyaudio.PyAudio()

        input_device = MICROPHONE_DEVICE_ID
        output_device = VIRTUAL_CABLE_DEVICE_ID

        stream_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=input_device,
            frames_per_buffer=CHUNK,
        )

        stream_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=output_device,
            frames_per_buffer=CHUNK,
        )

        print("Voice changing active...")

        try:
            while self.voice_changer_active:
                data = stream_in.read(CHUNK, exception_on_overflow=False)
                audio = np.frombuffer(data, dtype=np.int16)

                # Apply effect based on selected voice changer
                if self.current_voice_changer == "Normal":
                    modified_audio = audio
                elif self.current_voice_changer == "High Pitch":
                    modified_audio = self.granular_pitch_shift(audio, shift_factor=1.5)
                elif self.current_voice_changer == "Low Pitch":
                    modified_audio = self.granular_pitch_shift(audio, shift_factor=0.7)
                elif self.current_voice_changer == "Robot":
                    modified_audio = self.apply_robot_effect(audio)
                elif self.current_voice_changer == "Echo":
                    modified_audio = self.apply_echo_effect(audio)
                else:
                    modified_audio = audio

                # Convert back to bytes and output
                stream_out.write(modified_audio.tobytes())
        except Exception as e:
            print(f"Error in voice changer: {e}")
        finally:
            stream_in.stop_stream()
            stream_out.stop_stream()
            stream_in.close()
            stream_out.close()
            p.terminate()
            print("Voice changer stopped")

    # TODO: Delete it, since better methods used
    def play_audio(self, file_path, virtual_device):
        try:
            # Read audio file
            with wave.open(file_path, "rb") as wf:
                data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int32)
                samplerate = wf.getframerate()

            # Play through virtual cable
            sd.play(data, samplerate=samplerate, device=virtual_device)
            sd.wait()
        except Exception as e:
            print(f"Error playing audio {file_path}: {e}")

    def on_closing(self):
        self.stop_monitoring()
        self.voice_changer_active = False

        # Wait for threads to finish
        time.sleep(0.5)
        self.destroy()


# Launch the app
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Set the appearance mode
    ctk.set_default_color_theme("blue")  # Set the color theme

    app = SoundboardApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


"""
def voice_changer():
    p = pyaudio.PyAudio()
    
    input_device = MICROPHONE_DEVICE_ID
    output_device = VIRTUAL_CABLE_DEVICE_ID
    
    stream_in = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       input_device_index=input_device,
                       frames_per_buffer=CHUNK)
    
    stream_out = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        output_device_index=output_device,
                        frames_per_buffer=CHUNK)
    
    print("Voice changing active...")
    
    try:
        while True:
            data = stream_in.read(CHUNK)
            audio = np.frombuffer(data, dtype=np.int16)
            
            # Basic pitch shift effect (modify as needed)
            modified_audio = granular_pitch_shift(audio, shift_factor=1.5)
            
            stream_out.write(audio.tobytes())

    except KeyboardInterrupt:
        stream_in.stop_stream()
        stream_out.stop_stream()
        stream_in.close()
        stream_out.close()
        p.terminate()

def granular_pitch_shift(audio, shift_factor, grain_size=1024): # not working, so I will change it
    output = np.zeros(int(len(audio) / shift_factor), dtype=np.int16)
    for pos in range(0, len(audio) - grain_size, int(grain_size * shift_factor)):
        grain = audio[pos:pos + grain_size].astype(np.float32)
        grain *= np.hanning(grain_size)  # Window function
        output[pos:pos + grain_size] += grain.astype(np.int16)
    return output


def play_audio(file_path, virtual_device):
    # Read audio file
    with wave.open(file_path, 'rb') as wf:
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int32)
        samplerate = wf.getframerate()
    
    # Play through virtual cable
    sd.play(data, samplerate=samplerate, device=virtual_device)
    sd.wait()

#voice_changer()
play_audio("audio", VIRTUAL_CABLE_DEVICE_ID)"
"""
