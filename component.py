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

    def calculate_fhr_baseline(self):
        """
        Calculate the Fetal Heart Rate baseline for the component

        Returns:
        --------
        float
            Average baseline FHR
        """
        # Typical baseline FHR is between 110-160 bpm
        # Use median to reduce impact of extreme values
        return np.median(self.fetal_heart_rate)

    def diagnose_condition(self, analysis_results):
        """
        Diagnose the infant's condition based on analysis results

        Parameters:
        -----------
        analysis_results : dict
            Dictionary of analysis results

        Returns:
        --------
        str
            Diagnostic interpretation
        """
        # Diagnostic criteria based on CTG parameters
        # These are simplified and should be validated by medical professionals

        # Check baseline
        baseline = self.calculate_fhr_baseline()
        baseline_status = self._assess_baseline(baseline)

        # Variability assessment
        short_term_var = analysis_results['Short Term Variability']
        long_term_var = analysis_results['Long Term Variability']
        variability_status = self._assess_variability(short_term_var, long_term_var)

        # Acceleration and deceleration assessment
        acceleration_status = self._assess_accelerations(
            analysis_results['Accelerations'],
            analysis_results['Late Accelerations']
        )

        deceleration_status = self._assess_decelerations(
            analysis_results['Decelerations'],
            analysis_results['Early Decelerations'],
            analysis_results['Variable Decelerations']
        )

        # Combine assessments
        overall_status = self._combine_assessments(
            baseline_status,
            variability_status,
            acceleration_status,
            deceleration_status
        )

        return {
            'Baseline': baseline_status,
            'Variability': variability_status,
            'Accelerations': acceleration_status,
            'Decelerations': deceleration_status,
            'Overall': overall_status
        }

    def _assess_baseline(self, baseline):
        """
        Assess FHR baseline

        Parameters:
        -----------
        baseline : float
            Calculated baseline FHR

        Returns:
        --------
        str
            Baseline assessment
        """
        if 110 <= baseline <= 160:
            return "Normal"
        elif baseline < 110:
            return "Bradycardia"
        else:
            return "Tachycardia"

    def _assess_variability(self, short_term_var, long_term_var):
        """
        Assess FHR variability

        Parameters:
        -----------
        short_term_var : float
            Short-term variability value
        long_term_var : float
            Long-term variability value

        Returns:
        --------
        str
            Variability assessment
        """
        # Criteria for variability can vary, these are simplified
        if short_term_var > 5 and long_term_var < 10:
            return "Good Variability"
        elif short_term_var < 3:
            return "Reduced Variability"
        else:
            return "Moderate Variability"

    def _assess_accelerations(self, has_accelerations, has_late_accelerations):
        """
        Assess accelerations

        Parameters:
        -----------
        has_accelerations : bool
            Presence of accelerations
        has_late_accelerations : bool
            Presence of late accelerations

        Returns:
        --------
        str
            Acceleration assessment
        """
        if has_accelerations and not has_late_accelerations:
            return "Normal Accelerations"
        elif has_late_accelerations:
            return "Concerning Late Accelerations"
        else:
            return "Absent Accelerations"

    def _assess_decelerations(self, has_decelerations, has_early_decelerations, has_variable_decelerations):
        """
        Assess decelerations

        Parameters:
        -----------
        has_decelerations : bool
            Presence of decelerations
        has_early_decelerations : bool
            Presence of early decelerations
        has_variable_decelerations : bool
            Presence of variable decelerations

        Returns:
        --------
        str
            Deceleration assessment
        """
        if not has_decelerations:
            return "No Decelerations"
        elif has_early_decelerations:
            return "Early Decelerations (Usually Benign)"
        elif has_variable_decelerations:
            return "Variable Decelerations (Requires Attention)"
        else:
            return "Concerning Decelerations"

    def _combine_assessments(self, baseline_status, variability_status, acceleration_status, deceleration_status):
        """
        Combine individual assessments into overall condition

        Parameters:
        -----------
        baseline_status : str
            Baseline assessment
        variability_status : str
            Variability assessment
        acceleration_status : str
            Acceleration assessment
        deceleration_status : str
            Deceleration assessment

        Returns:
        --------
        str
            Overall condition assessment
        """
        # This is a simplified assessment algorithm
        concerning_factors = [
            baseline_status != "Normal",
            variability_status == "Reduced Variability",
            acceleration_status == "Concerning Late Accelerations",
            deceleration_status != "No Decelerations"
        ]

        # Count concerning factors
        concern_count = sum(concerning_factors)

        if concern_count == 0:
            return "Normal Fetal Condition"
        elif concern_count <= 1:
            return "Mild Concerns"
        elif concern_count <= 3:
            return "Moderate Concerns"
        else:
            return "Significant Concerns"

    def get_analysis_results(self):
        """
        Compile analysis results for the component

        Returns:
        --------
        dict
            Dictionary of analysis results
        """
        events = self.detect_events()

        # Include baseline calculation
        baseline = self.calculate_fhr_baseline()

        analysis_results = {
            'FHR Baseline': baseline,
            'Short Term Variability': self.calculate_short_term_variability(),
            'Long Term Variability': self.calculate_long_term_variability(),
            'Accelerations': len(events['accelerations']) > 0,
            'Late Accelerations': False,  # Placeholder
            'Decelerations': len(events['decelerations']) > 0,
            'Early Decelerations': len(events['early_decelerations']) > 0,
            'Variable Decelerations': len(events['variable_decelerations']) > 0,
            'Prolonged Decelerations': False  # Placeholder
        }

        # Add diagnosis column
        analysis_results['Results'] = self.diagnose_condition(analysis_results)

        return analysis_results

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

    def _detect_decelerations(self, threshold_low=110, min_duration=15):
        """
        Detect deceleration regions.

        Parameters:
        -----------
        threshold_low : float, optional
            Lower threshold for decelerations (default: 110 bpm).
        min_duration : float, optional
            Minimum duration for a deceleration to be considered valid (default: 15 seconds).

        Returns:
        --------
        list
            List of (start_time, end_time) tuples for decelerations.
        """
        decelerations = []
        in_deceleration = False
        decel_start = None

        for i in range(1, len(self.fetal_heart_rate)):
            # Check if current point is below the threshold
            if self.fetal_heart_rate[i] < threshold_low:
                if not in_deceleration:
                    # Start of deceleration
                    in_deceleration = True
                    decel_start = self.time[i]

                # Handle the case of the end of the signal
                if i == len(self.fetal_heart_rate) - 1:
                    decel_end = self.time[i]
                    if decel_end - decel_start >= min_duration:
                        decelerations.append((decel_start, decel_end))

            elif in_deceleration:
                # End of deceleration
                decel_end = self.time[i]
                if decel_end - decel_start >= min_duration:
                    decelerations.append((decel_start, decel_end))

                in_deceleration = False
                decel_start = None

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

    def calculate_short_term_variability(self):
        """
        Calculate short term variability of FHR

        Returns:
        --------
        float
            Short term variability value
        """
        # Placeholder for more sophisticated variability calculation
        rr_intervals = [60000 / bpm for bpm in self.fetal_heart_rate]  # 60000 ms in a minute
        differences = np.abs(np.diff(rr_intervals))  # sbsolute differences
        stv = np.mean(differences)  # mean of the differences
        return stv
        # return np.std(self.fetal_heart_rate)

    def calculate_long_term_variability(self , window_size = 5):
        """
        Calculate long term variability of FHR

        Returns:
        --------
        float
            Long term variability value
        """
        # Placeholder for more sophisticated variability calculation
        ltv_values = []
        for i in range(0, len(self.fetal_heart_rate), window_size):
            window = self.fetal_heart_rate[i:i + window_size] # window_size: number of samples per window
            if len(window) > 1:
                ltv_values.append(np.std(window))  # standard deviation of each window
        return np.mean(ltv_values) if ltv_values else 0
        # return np.std(self.fetal_heart_rate)
