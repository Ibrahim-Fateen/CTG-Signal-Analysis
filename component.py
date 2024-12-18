import numpy as np


class Component:
    def __init__(self, time, fetal_heart_rate, uterine_contraction):
        """
        Initialize a component of CTG signal

        Parameters:
        -----------
        time : numpy.ndarray
            Time values for the component
        fetal_heart_rate : numpy.ndarray
            Fetal Heart Rate values
        uterine_contraction : numpy.ndarray
            Uterine Contraction values
        """
        self.time = time
        self.fetal_heart_rate = fetal_heart_rate
        self.uterine_contraction = uterine_contraction

    def calculate_short_term_variability(self):
        """
        Calculate short-term variability of fetal heart rate

        Returns:
        --------
        float
            Short-term variability value
        """
        # Calculate the standard deviation of beat-to-beat variations
        # This is a simplified implementation
        beat_variations = np.diff(self.fetal_heart_rate)
        return np.std(beat_variations)

    def calculate_long_term_variability(self):
        """
        Calculate long-term variability of fetal heart rate

        Returns:
        --------
        float
            Long-term variability value
        """
        # Calculate the variance over a moving window
        window_size = min(10, len(self.fetal_heart_rate) // 2)
        return np.var(self._moving_window_values(window_size))

    def _moving_window_values(self, window_size):
        """
        Calculate moving window values

        Parameters:
        -----------
        window_size : int
            Size of the moving window

        Returns:
        --------
        numpy.ndarray
            Values calculated over moving windows
        """
        return np.convolve(
            self.fetal_heart_rate,
            np.ones(window_size),
            mode='valid'
        ) / window_size

    def detect_events(self):
        """
        Detect comprehensive events in the signal

        Returns:
        --------
        dict
            Dictionary of event regions
        """
        return {
            'accelerations': self._detect_accelerations(),
            'decelerations': self._detect_decelerations(),
            'early_decelerations': self._detect_early_decelerations(),
            'late_decelerations': self._detect_late_decelerations(),
            'variable_decelerations': self._detect_variable_decelerations()
        }

    def _detect_accelerations(self, threshold_high=160, min_duration=15, min_amplitude=15):
        """
        Detect acceleration regions

        Parameters:
        -----------
        threshold_high : float, optional
            Upper threshold for acceleration (default: 160 bpm)
        min_duration : float, optional
            Minimum duration of acceleration (default: 15 seconds)
        min_amplitude : float, optional
            Minimum amplitude increase (default: 15 bpm)

        Returns:
        --------
        list
            List of (start_time, end_time) tuples for accelerations
        """
        accelerations = []
        in_acceleration = False
        accel_start = None
        baseline = np.median(self.fetal_heart_rate)

        for i in range(1, len(self.fetal_heart_rate)):
            # Check if current point exceeds threshold
            if (self.fetal_heart_rate[i] > threshold_high and
                    self.fetal_heart_rate[i] - baseline > min_amplitude):

                if not in_acceleration:
                    # Start of acceleration
                    in_acceleration = True
                    accel_start = self.time[i]

                # Check duration at end of loop or signal
                if i == len(self.fetal_heart_rate) - 1 or not in_acceleration:
                    accel_end = self.time[i]
                    if accel_end - accel_start >= min_duration:
                        accelerations.append((accel_start, accel_end))

                    in_acceleration = False
                    accel_start = None

            elif in_acceleration:
                # End of acceleration
                accel_end = self.time[i]
                if accel_end - accel_start >= min_duration:
                    accelerations.append((accel_start, accel_end))

                in_acceleration = False
                accel_start = None

        return accelerations

    def _detect_decelerations(self, threshold_low=110):
        """
        Detect overall deceleration regions

        Parameters:
        -----------
        threshold_low : float, optional
            Lower threshold for decelerations (default: 110 bpm)

        Returns:
        --------
        list
            List of (start_time, end_time) tuples for decelerations
        """
        decelerations = []
        in_deceleration = False
        decel_start = None

        for i in range(1, len(self.fetal_heart_rate)):
            if self.fetal_heart_rate[i] < threshold_low:
                if not in_deceleration:
                    # Start of deceleration
                    in_deceleration = True
                    decel_start = self.time[i]
            else:
                if in_deceleration:
                    # End of deceleration
                    decelerations.append((decel_start, self.time[i]))
                    in_deceleration = False
                    decel_start = None

        # Handle case where deceleration continues to end of signal
        if in_deceleration:
            decelerations.append((decel_start, self.time[-1]))

        return decelerations

    def _detect_early_decelerations(self):
        """
        Detect early deceleration regions

        Returns:
        --------
        list
            List of (start_time, end_time) tuples for early decelerations
        """
        # Placeholder for more sophisticated early deceleration detection
        # Would typically involve correlation with uterine contractions
        return []

    def _detect_late_decelerations(self):
        """
        Detect late deceleration regions

        Returns:
        --------
        list
            List of (start_time, end_time) tuples for late decelerations
        """
        # Placeholder for more sophisticated late deceleration detection
        # Would typically involve specific pattern relative to contractions
        return []

    def _detect_variable_decelerations(self):
        """
        Detect variable deceleration regions

        Returns:
        --------
        list
            List of (start_time, end_time) tuples for variable decelerations
        """
        # Placeholder for more sophisticated variable deceleration detection
        # Would involve analyzing rapid changes in FHR
        return []

    def get_analysis_results(self):
        """
        Compile analysis results for the component

        Returns:
        --------
        dict
            Dictionary of analysis results
        """
        events = self.detect_events()

        return {
            'Short Term Variability': self.calculate_short_term_variability(),
            'Long Term Variability': self.calculate_long_term_variability(),
            'Accelerations': len(events['accelerations']) > 0,
            'Late Accelerations': False,  # Placeholder
            'Decelerations': len(events['decelerations']) > 0,
            'Early Decelerations': len(events['early_decelerations']) > 0,
            'Variable Decelerations': len(events['variable_decelerations']) > 0,
            'Prolonged Decelerations': False  # Placeholder
        }