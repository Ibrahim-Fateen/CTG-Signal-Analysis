import pandas as pd
from component import Component


class Signal:
    def __init__(self, file_path):
        """
        Initialize Signal by loading data from a file

        Parameters:
        -----------
        file_path : str
            Path to the CSV file containing CTG data
        """
        # Load data
        self.data = pd.read_csv(file_path)

        # Estimate sampling rate
        self.sampling_rate = self._estimate_sampling_rate()

        # Create components
        self.components = self._create_components(1000)

    def _estimate_sampling_rate(self):
        """
        Estimate sampling rate from time differences

        Returns:
        --------
        float
            Estimated sampling rate
        """
        time_diffs = self.data['time'].diff()
        return 1 / time_diffs.median()

    def _create_components(self, component_duration=120):
        """
        Divide signal into components

        Parameters:
        -----------
        component_duration : int, optional
            Duration of each component in seconds (default: 120)

        Returns:
        --------
        list
            List of Component objects
        """
        # Calculate number of samples in a component
        samples_per_component = int(component_duration * self.sampling_rate)

        # Create components
        components = []
        for i in range(0, len(self.data), samples_per_component):
            component_data = self.data.iloc[i:i + samples_per_component]

            # Ensure we have a full component
            if len(component_data) == samples_per_component:
                component = Component(
                    time=component_data['time'].values,
                    fetal_heart_rate=component_data['FHR'].values,
                    uterine_contraction=component_data['UC'].values
                )
                components.append(component)

        return components

    def get_component(self, index):
        """
        Get a specific component

        Parameters:
        -----------
        index : int
            Index of the component

        Returns:
        --------
        Component
            The requested component
        """
        return self.components[index]

    def get_total_components(self):
        """
        Get total number of components

        Returns:
        --------
        int
            Number of components in the signal
        """
        return len(self.components)