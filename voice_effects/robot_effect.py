import numpy as np
from numba import jit


@jit(nopython=True, cache=True)
def _robot_effect_core_int16(audio_int16):
    """
    Core robot effect computation - optimized with numba
    By optimization means compiled into machine code
    Code should be warmed up, because first call is compiling
    """
    # Create modulator wave
    modulator = np.sin(np.linspace(0, 10 * np.pi, len(audio_int16))) * 0.5 + 0.5

    # Convert to float, apply modulation, then back to int16
    audio_float = audio_int16.astype(np.float32)
    robot_audio_float = audio_float * modulator

    # Clip to prevent overflow and convert back
    robot_audio_clipped = np.clip(robot_audio_float, -32768, 32767)
    return robot_audio_clipped.astype(np.int16)
