class TofDistanceFilter:
    def __init__(self, median_n=5, alpha=0.25, deadband_mm=2.0):
        self.n = median_n
        self.alpha = alpha
        self.deadband = deadband_mm
        self.buf = []
        self.y = None

    def update(self, x_mm):
        # Median stage (reject spikes)
        self.buf.append(x_mm)
        if len(self.buf) > self.n:
            self.buf.pop(0)
        m = sorted(self.buf)[len(self.buf) // 2]

        # EMA stage (smooth)
        if self.y is None:
            self.y = m
        else:
            self.y = self.y + self.alpha * (m - self.y)

        # Deadband (stop tiny wiggle)
        if abs(m - self.y) < self.deadband:
            return self.y
        return self.y
