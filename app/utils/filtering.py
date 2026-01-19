class TofDistanceFilter:
    """
    Smooth TOF distance readings using:
      1) Outlier rejection (reject sudden large jumps)
      2) Exponential Moving Average (EMA) smoothing

    This is designed for integer millimeter readings on MicroPython:
    - No floats
    - Very fast
    - Stable in the presence of occasional spikes
    """

    def __init__(self, max_jump_mm=30, alpha_shift=3, initial_value=None):
        # Maximum allowed change from the current filtered value.
        # If a new sample differs by more than this, we treat it as a glitch and ignore it.
        self._max_jump_mm = max_jump_mm

        # EMA smoothing factor, expressed as a bit shift:
        #   alpha = 1 / (2 ** alpha_shift)
        # Example: alpha_shift=3 => alpha=1/8 (smooth but still responsive).
        self._alpha_shift = alpha_shift

        # Current filtered value (None until the first valid sample arrives).
        self._y = initial_value

    def reset(self, value=None):
        """Reset the filter state (optionally seeding it with a known value)."""
        self._y = value

    def value(self):
        """Return the current filtered value (or None if not initialized yet)."""
        return self._y

    def update(self, raw_mm):
        """
        Feed one raw distance sample (mm) into the filter and return the filtered result.

        raw_mm: integer millimeters from the TOF sensor
        returns: filtered integer millimeters
        """
        # If this is the first sample, initialize the filter immediately.
        # This avoids a big startup transient (y jumping from 0 to the real distance).
        if self._y is None:
            self._y = raw_mm
            return self._y

        # Compute how far the new reading is from our current filtered estimate.
        delta = raw_mm - self._y

        # If the jump is too large, consider it a spike and ignore it.
        if delta > self._max_jump_mm or delta < -self._max_jump_mm:
            return self._y

        # Apply EMA:
        #   y = y + alpha * (x - y)
        # Using bit shift instead of float multiply/divide:
        self._y += delta >> self._alpha_shift

        # Return the updated filtered distance.
        return self._y
