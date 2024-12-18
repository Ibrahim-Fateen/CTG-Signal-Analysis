import sys
import pyqtgraph as pg
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QApplication,
    QTableWidgetItem, QVBoxLayout, QHeaderView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem

from signal import Signal


class CTGAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI
        loader = QUiLoader()
        file = QFile("UI/main_window.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        self.setCentralWidget(self.ui)
        self.ui.show()
        self.ui.setWindowTitle("CTG Analyzer")
        self.ui.showMaximized()

        # Initialize data
        self.signal = None
        self.current_component_index = 0

        # Setup plot widget
        self.plot_layout = QVBoxLayout(self.ui.plot_frame)
        self.plot_widget = pg.PlotWidget()
        self.plot_layout.addWidget(self.plot_widget)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Create legend
        self.plot_legend = self.plot_widget.addLegend()

        self.current_component_label = self.ui.current_component_label
        self.current_component_label.setText("No data loaded")

        # Setup signals and slots
        self.ui.load_file_button.clicked.connect(self.load_ctg_file)
        self.ui.next_component_button.clicked.connect(self.next_component)
        self.ui.prev_component_button.clicked.connect(self.previous_component)

        # Setup toggle list
        self.toggle_model = QStandardItemModel()
        self.ui.toggle_list.setModel(self.toggle_model)
        self.ui.toggle_list.clicked.connect(self.switch_component)

    def load_ctg_file(self):
        """
        Load CTG file and process the signal
        """
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load CTG File", "", "CSV Files (*.csv)"
        )
        if filename:
            # Create Signal object
            self.signal = Signal(filename)

            # Populate toggle list
            self.populate_toggle_list()

            # Plot initial component
            self.current_component_index = 0
            self.plot_current_component()
            self.populate_analysis_table()

    def populate_toggle_list(self):
        """
        Populate the toggle list with component names
        """
        self.toggle_model.clear()
        for i in range(self.signal.get_total_components()):
            item = QStandardItem(f"Component {i + 1}")
            self.toggle_model.appendRow(item)

    def plot_current_component(self):
        """
        Plot the current component's data
        """
        self.plot_widget.clear()

        # Get current component
        current_component = self.signal.get_component(self.current_component_index)

        # Plot FHR with legend
        fhr_plot = self.plot_widget.plot(
            current_component.time,
            current_component.fetal_heart_rate,
            pen=pg.mkPen(color='blue', width=2),
            name='Fetal Heart Rate (bpm)'
        )

        # Plot UC with legend
        uc_plot = self.plot_widget.plot(
            current_component.time,
            current_component.uterine_contraction,
            pen=pg.mkPen(color='red', width=2),
            name='Uterine Contraction'
        )

        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Time (seconds)')
        self.plot_widget.setTitle(f'Component {self.current_component_index + 1}')

        # Highlight accelerations and decelerations
        self._highlight_events(current_component)

        # Set labels
        self.current_component_label.setText(f"Component {self.current_component_index + 1}")

    def _highlight_events(self, component):
        """
        Highlight acceleration and deceleration regions

        Parameters:
        -----------
        component : Component
            Current component to analyze
        """
        # Get events from the component
        events = component.detect_events()

        # Highlight accelerations (light green)
        for start, end in events['accelerations']:
            region = pg.LinearRegionItem(
                values=[start, end],
                orientation='vertical',
                brush=pg.mkBrush(color=(0, 255, 0, 50)),  # Transparent green
                movable=False
            )
            self.plot_widget.addItem(region)

        # Highlight decelerations (light red)
        for start, end in events['decelerations']:
            region = pg.LinearRegionItem(
                values=[start, end],
                orientation='vertical',
                brush=pg.mkBrush(color=(255, 0, 0, 50)),  # Transparent red
                movable=False
            )
            self.plot_widget.addItem(region)

    def switch_component(self, index):
        """
        Switch to selected component

        Parameters:
        -----------
        index : QModelIndex
            Index of selected component
        """
        self.current_component_index = index.row()
        self.plot_current_component()
        self.populate_analysis_table()

    def next_component(self):
        """
        Move to next component
        """
        if self.signal and self.current_component_index < self.signal.get_total_components() - 1:
            self.current_component_index += 1
            self.plot_current_component()
            self.populate_analysis_table()

    def previous_component(self):
        """
        Move to previous component
        """
        if self.signal and self.current_component_index > 0:
            self.current_component_index -= 1
            self.plot_current_component()
            self.populate_analysis_table()

    def populate_analysis_table(self):
        if not self.signal:
            return

        # Get current component's analysis results
        current_component = self.signal.get_component(self.current_component_index)
        analyses = current_component.get_analysis_results()
        results = current_component.diagnose_condition(analyses)

        # Set table to 3 columns
        self.ui.analysis_table.setColumnCount(3)

        # Set column headers
        self.ui.analysis_table.setHorizontalHeaderLabels(['Metric', 'Value', 'Results'])

        # Populate table
        self.ui.analysis_table.setRowCount(len(analyses) - 1)  # Subtract 1 to remove 'Results' from row count
        row = 0
        for name, value in analyses.items():
            if name == 'Results':
                continue  # Skip this in the main table rows

            # Round numerical values to 3 decimal places
            if isinstance(value, (int, float)):
                formatted_value = f"{value:.3f}"
            else:
                formatted_value = str(value)

            # Metric column
            self.ui.analysis_table.setItem(row, 0, QTableWidgetItem(name))

            # Value column
            self.ui.analysis_table.setItem(row, 1, QTableWidgetItem(formatted_value))

            # Results column
            if name == "FHR Baseline":
                self.ui.analysis_table.setItem(row, 2, QTableWidgetItem(results['Baseline']))
            elif name == "Short Term Variability" or name == "Long Term Variability":
                self.ui.analysis_table.setItem(row, 2, QTableWidgetItem(results['Variability']))
            elif name == "Accelerations":
                self.ui.analysis_table.setItem(row, 2, QTableWidgetItem(results['Accelerations']))
            elif name == "Decelerations":
                self.ui.analysis_table.setItem(row, 2, QTableWidgetItem(results['Decelerations']))

            row += 1

        # Set column widths
        self.ui.analysis_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.analysis_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.analysis_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        # Overall results row
        results_row = self.ui.analysis_table.rowCount()
        self.ui.analysis_table.insertRow(results_row)
        self.ui.analysis_table.setItem(results_row, 0, QTableWidgetItem('Results'))
        self.ui.analysis_table.setItem(results_row, 2, QTableWidgetItem(results['Overall']))


def main():
    app = QApplication(sys.argv)
    ctg_app = CTGAnalyzerApp()
    ctg_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()