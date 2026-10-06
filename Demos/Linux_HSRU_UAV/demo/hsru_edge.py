import os
import ctypes
import ctypes.util
import platform

# Load libc for aligned malloc
if platform.system() == "Windows":
    libc = ctypes.cdll.msvcrt
else:
    libc = ctypes.CDLL(ctypes.util.find_library("c"))
libc.malloc.argtypes = [ctypes.c_size_t]
libc.malloc.restype = ctypes.c_void_p
libc.free.argtypes = [ctypes.c_void_p]

# ── Fixed-Point constants ──────────────────────────────────────────────────────
_FXP_SCALE  = 65536.0   # Q16.16: 2^16
_FXP_MAX    = (2**31 - 1) / _FXP_SCALE
_FXP_MIN    = -(2**31)   / _FXP_SCALE

# USE_FXP is injected by export.py at bundle time (True/False literal)
USE_FXP = True


class HSRUEdgeEngine:
    """
    Python ctypes wrapper for the HSRU C++ Edge Engine (libhsru_drone.so).

    Supports both float32 and Q16.16 fixed-point (FXP) libraries transparently.
    The public interface always works in physical float units regardless of mode.
    When USE_FXP=True the wrapper scales inputs to int32 before calling the C++
    engine and scales outputs back to float on return.
    """

    def __init__(self, lib_path, weights_path, num_layers, hidden_size, sensor_dim,
                 hwid="MAC:00-11-22-33-44-55"):
        self.sensor_dim = sensor_dim
        self.use_fxp    = USE_FXP

        # Load the C++ shared library
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Engine library not found at {lib_path}")

        import sys
        abs_lib = os.path.abspath(lib_path)
        if sys.platform == "win32" and sys.version_info >= (3, 8):
            self.lib = ctypes.CDLL(abs_lib, winmode=0)
        else:
            self.lib = ctypes.cdll.LoadLibrary(abs_lib)

        # ── C-API bindings ────────────────────────────────────────────────────
        self.lib.hsru_authenticate.argtypes = [ctypes.c_char_p]
        self.lib.hsru_authenticate.restype  = ctypes.c_bool

        if self.use_fxp:
            self.lib.hsru_init_context_fxp.argtypes = [
                ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
            ]
            self.lib.hsru_init_context_fxp.restype  = ctypes.c_void_p

            self.lib.hsru_step_fxp.argtypes = [
                ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
            ]
            self.lib.hsru_step_fxp.restype = None
        else:
            self.lib.hsru_init_context.argtypes = [
                ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
            ]
            self.lib.hsru_init_context.restype  = ctypes.c_void_p

            self.lib.hsru_step.argtypes = [
                ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
            ]
            self.lib.hsru_step.restype = None

        # ── 1. Authenticate ───────────────────────────────────────────────────
        hwid_bytes = hwid.encode("utf-8")
        if not self.lib.hsru_authenticate(hwid_bytes):
            raise PermissionError(f"DRM Authentication Failed for Hardware ID: {hwid}")

        # ── 2. Initialize Engine Context ──────────────────────────────────────
        weights_bytes = weights_path.encode("utf-8")
        if self.use_fxp:
            self.ctx = self.lib.hsru_init_context_fxp(
                weights_bytes, num_layers, hidden_size, sensor_dim
            )
        else:
            self.ctx = self.lib.hsru_init_context(
                weights_bytes, num_layers, hidden_size, sensor_dim
            )
        if not self.ctx:
            raise RuntimeError(f"Failed to initialize engine with weights: {weights_path}")

        # ── 3. Pre-allocate aligned I/O buffers ───────────────────────────────
        # CRITICAL for Apple Silicon / ARM NEON aligned SIMD instructions
        if self.use_fxp:
            elem_size = ctypes.sizeof(ctypes.c_int32)
            self.input_ptr  = libc.malloc(sensor_dim * elem_size)
            self.pred_ptr   = libc.malloc(sensor_dim * elem_size)
            self.input_array = ctypes.cast(self.input_ptr,  ctypes.POINTER(ctypes.c_int32))
            self.pred_array  = ctypes.cast(self.pred_ptr,   ctypes.POINTER(ctypes.c_int32))
        else:
            elem_size = ctypes.sizeof(ctypes.c_float)
            self.input_ptr  = libc.malloc(sensor_dim * elem_size)
            self.pred_ptr   = libc.malloc(sensor_dim * elem_size)
            self.input_array = ctypes.cast(self.input_ptr,  ctypes.POINTER(ctypes.c_float))
            self.pred_array  = ctypes.cast(self.pred_ptr,   ctypes.POINTER(ctypes.c_float))

    def step(self, raw_sensors):
        """
        Steps the engine forward by 1 tick.

        Args:
            raw_sensors: list or array of floats in physical sensor units.

        Returns:
            list of floats — predicted physical sensor state at t+1.
        """
        if len(raw_sensors) != self.sensor_dim:
            raise ValueError(f"Expected {self.sensor_dim} sensors, got {len(raw_sensors)}")

        if self.use_fxp:
            # Scale float → Q16.16 int32, clamped to avoid overflow
            for i in range(self.sensor_dim):
                val = max(_FXP_MIN, min(_FXP_MAX, raw_sensors[i]))
                self.input_array[i] = int(val * _FXP_SCALE)

            self.lib.hsru_step_fxp(self.ctx, self.input_ptr, self.pred_ptr)

            # Scale Q16.16 int32 → float
            return [self.pred_array[i] / _FXP_SCALE for i in range(self.sensor_dim)]
        else:
            for i in range(self.sensor_dim):
                self.input_array[i] = raw_sensors[i]

            self.lib.hsru_step(self.ctx, self.input_ptr, self.pred_ptr)

            return [self.pred_array[i] for i in range(self.sensor_dim)]

    def __del__(self):
        if hasattr(self, "input_ptr") and self.input_ptr:
            libc.free(self.input_ptr)
        if hasattr(self, "pred_ptr") and self.pred_ptr:
            libc.free(self.pred_ptr)
