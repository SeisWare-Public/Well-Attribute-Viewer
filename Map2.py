﻿# main.pydef well
from email.policy import default
import sys
import os
from itertools import groupby
import json
from numpy.typing import _96Bit
import pandas as pd
import math
import numpy as np
from pandas.core.base import NoNewAttributesMixin
from scipy.spatial import KDTree
from PySide2.QtWidgets import QGraphicsView, QApplication, QFileDialog, QToolButton, QMainWindow, QSpinBox, QSpacerItem, QToolBar, QCheckBox, QSlider, QLabel
from PySide2.QtWidgets import QSizePolicy, QAction, QMessageBox, QErrorMessage, QDialog, QWidget, QSystemTrayIcon, QVBoxLayout, QHBoxLayout, QMenu, QMenuBar, QPushButton, QListWidget, QComboBox, QLineEdit, QScrollArea
import atexit
from PySide2.QtGui import QIcon, QColor, QPainter, QPen, QFont, QWheelEvent, QBrush, QPixmap, QLinearGradient
from PySide2.QtCore import Qt, QPointF, QCoreApplication, QMetaObject, QPoint
from shapely.geometry import LineString
import SeisWare
#from Exporting import ExportDialog
from DataLoader import DataLoaderDialog
from ZoneViewer import ZoneViewerDialog
from SwPropertiesEdit import SWPropertiesEdit
from DataLoadWellZone import DataLoadWellZonesDialog
from GunBarrel import PlotGB
from Plot import Plot
from pystray import Icon, Menu, MenuItem
import threading
from PIL import Image
from shapely.geometry import LineString, Point, MultiPoint, GeometryCollection
from ColorEdit import ColorEditor
import time
import ujson as json 
from DrawingArea import DrawingArea
from ProjectSaver import ProjectSaver
from ProjectOpen import ProjectLoader# Import the DrawingArea class
from UiSetup import Ui_MainWindow
from Calculations import StagesCalculationDialog, ZoneAttributesDialog, WellAttributesDialog
from InZone import InZoneDialog
from CrossPlot import CrossPlot
from DataLoadSegy import DataLoadSegy
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import KDTree




class Map(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Map, self).__init__()
        self.setupUi(self)
        self.grid_well_data = []
        self.grid_well_data_df = pd.DataFrame()
        self.depth_grid_color_df = pd.DataFrame()
        self.well_info_df = pd.DataFrame()
        self.top_grid_df = pd.DataFrame()
        self.bottom_grid_df = pd.DataFrame()
        self.total_zone_number = 0
        self.export_options = pd.DataFrame()
        self.import_options_df = pd.DataFrame()
        self.master_df = pd.DataFrame()
        self.depth_grid_data_df = pd.DataFrame()
        self.attribute_grid_data_df = pd.DataFrame()
        self.zone_data_df = pd.DataFrame()
        self.grid_info_df = pd.DataFrame()
        self.directional_surveys_df = pd.DataFrame()
        self.zone_criteria_df = pd.DataFrame()
        self.grid_xyz_bottom = []
        self.grid_xyz_top = []
        self.intersections = []
        self.originalIntersectionPoints = []
        self.grid_scaled_min_x = None
        self.grid_scaled_max_x = None
        self.grid_scaled_min_y = None
        self.grid_scaled_max_y = None
        self.kd_tree = None
        self.uwi_points = []
        self.uwi_map = {}
        self.depth_grid_data_dict = {}
        self.kd_tree_wells = {}
        self.attribute_grid_data_dict = {}
        self.kd_tree_depth_grids = None
        self.kd_tree_att_grids = None
        self.seismic_kdtree = None

        self.drawing = False
        self.lastPoint = None
        self.data = []
        self.current_line = []
        self.originalCurrentLine = []
        self.open_windows = []
        self.plot_gb_windows = []
        self.scale = 1.0
        self.zoom_center = QPointF(0, 0)
        self.offset_x = 0
        self.offset_y = 0
        self.line_width = 25
        self.line_opacity = .5
        self.uwi_width = 80
        self.uwi_opacity = .5
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None
        self.project_file_name = None
        self.color_bars = None
        self.well_data = {}
        self.scaled_data = {}
        self.scaled_data_md = {}
        self.column_filters = {}
        self.save_zone_viewer_settings = {}
        self.intersectionPoints = []
        self.processed_data = []
        self.project_list = []
        self.zone_names = []
        self.zone_zone_names = []
        self.well_zone_names = []
        self.well_list = []  # List to store UWI
        self.seismic_data = {}
        self.bounding_box = None 
        
        self.connection = SeisWare.Connection()
        self.project_saver = None
        self.file_name = None
        self.selected_zone = None
        self.selected_zone_attribute = None
        self.selected_grid = None
        self.selected_grid_colorbar = None
        self.selected_zone_attribute_colorbar = None

        self.selected_color_palette = None 
        self.selected_color_bar = None

 
        self.set_interactive_elements_enabled(False)
        self.project_loader = ProjectLoader(self)
        atexit.register(self.shutdown_and_save_all)
                # Connect signals to slots
        # Connect signals to slots
        
     


        


        
        self.gridDropdown.currentIndexChanged.connect(self.grid_selected)
        self.zoneDropdown.currentIndexChanged.connect(self.zone_selected)
        self.zoneAttributeDropdown.currentIndexChanged.connect(self.zone_attribute_selected)
        self.WellZoneDropdown.currentIndexChanged.connect(self.well_zone_selected)
        self.WellAttributeDropdown.currentIndexChanged.connect(self.well_attribute_selected)
        self.WellAttributeColorBarDropdown.currentIndexChanged.connect(self.well_attribute_selected)

        self.gridColorBarDropdown.currentIndexChanged.connect(self.grid_color_selected)
        self.zoneAttributeColorBarDropdown.currentIndexChanged.connect(self.zone_attribute_color_selected)
        self.WellAttributeColorBarDropdown.currentIndexChanged.connect(self.well_attribute_selected)




        self.uwiCheckbox.stateChanged.connect(self.toggle_uwi_labels)
        self.uwiWidthSlider.valueChanged.connect(self.change_uwi_width)
        self.opacitySlider.valueChanged.connect(self.change_opacity)
        self.lineWidthSlider.valueChanged.connect(self.change_line_width)
        self.lineOpacitySlider.valueChanged.connect(self.change_line_opacity)
        self.plot_tool_action.triggered.connect(self.plot_data)
        self.gun_barrel_action.triggered.connect(self.toggleDrawing)
        self.cross_plot_action.triggered.connect(self.crossPlot)
        self.color_editor_action.triggered.connect(self.open_color_editor)
        self.color_action.triggered.connect(self.open_color_editor)
        self.plot_action.triggered.connect(self.plot_data)
        self.zone_viewer_action.triggered.connect(self.launch_zone_viewer)
        self.zoomOut.triggered.connect(self.zoom_out)
        self.zoomIn.triggered.connect(self.zoom_in)
        #self.exportSw.triggered.connect(self.export_to_sw)
        self.toggle_button.clicked.connect(self.toggle_draw_mode)
        self.new_project_action.triggered.connect(self.create_new_project)
        self.open_action.triggered.connect(self.open_project)
        self.calc_stage_action.triggered.connect(self.open_stages_dialog)
        self.calc_zone_attribute_action.triggered.connect(self.open_zone_attributes_dialog)
        self.calc_inzone_action.triggered.connect(self.inzone_dialog)
        self.data_loader_menu_action.triggered.connect(self.dataloader)
        self.dataload_well_zones_action.triggered.connect(self.dataload_well_zones)
        self.dataload_segy_action.triggered.connect(self.dataload_segy)

      



    def set_project_file_name(self, file_name):
        self.project_file_name = file_name
        self.project_saver = ProjectSaver(self.project_file_name)

    def closeEvent(self, event):
        # Perform any cleanup here
        self.cleanup()
        event.accept()

    def cleanup(self):
        # Ensure all connections and resources are properly closed
        if self.connection:
            self.connection.Disconnect()
            self.connection = None
        if self.project_saver:
            self.project_saver.shutdown(
                self.line_width, self.line_opacity, self.uwi_width, self.uwi_opacity,
                self.gridDropdown.currentText(), self.zoneDropdown.currentText()
            )
        QCoreApplication.quit()
        
    def setData(self):
        if self.directional_surveys_df.empty:
            return

        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_colwidth', None)

        self.well_data = {}
        self.scaled_data = {}
        self.scaled_data_md = {}

        for uwi in self.directional_surveys_df['UWI'].unique():
            df_uwi = self.directional_surveys_df[self.directional_surveys_df['UWI'] == uwi]
        
            x_offsets = df_uwi['X Offset'].tolist()
            y_offsets = df_uwi['Y Offset'].tolist()
            tvds = df_uwi['TVD'].tolist()
            mds = df_uwi['MD'].tolist()
            points = [QPointF(x, y) for x, y in zip(x_offsets, y_offsets)]

            self.well_data[uwi] = {
                'x_offsets': x_offsets,
                'y_offsets': y_offsets,
                'tvds': tvds,
                'mds': mds,
                'points': points
            }

            # Keep the scaled_data and scaled_data_md as before
            self.scaled_data[uwi] = list(zip(points, tvds))
            self.scaled_data_md[uwi] = list(zip(points, mds))

        # Calculate min/max values
        all_x = [x for well in self.well_data.values() for x in well['x_offsets']]
        all_y = [y for well in self.well_data.values() for y in well['y_offsets']]
        self.min_x, self.max_x = min(all_x), max(all_x)
        self.min_y, self.max_y = min(all_y), max(all_y)

        # Create uwi_points and uwi_map
        self.uwi_points = [(x, y) for well in self.well_data.values() for x, y in zip(well['x_offsets'], well['y_offsets'])]
        self.uwi_map = {(x, y): uwi for uwi, well in self.well_data.items() for x, y in zip(well['x_offsets'], well['y_offsets'])}

        # Build KDTree
        self.kd_tree_wells = KDTree(self.uwi_points)

        # Pass all necessary data to setScaledData
        self.drawingArea.setScaledData(self.well_data)
        self.set_interactive_elements_enabled(True)

    def populate_grid_dropdown(self, selected_grid=None):
        # Ensure grid_info_df is populated
        if self.grid_info_df.empty:
            return

        # Block signals while populating the dropdown
        self.gridDropdown.blockSignals(True)

        # Clear the dropdown and add the default item
        self.gridDropdown.clear()
        self.gridDropdown.addItem("Select Grid")

        # Get grid names from the grid_info_df, sort them alphabetically, and add them to the dropdown
        grid_names = sorted(self.grid_info_df['Grid'].tolist())
        self.gridDropdown.addItems(grid_names)

        # Unblock signals after populating the dropdown
        self.gridDropdown.blockSignals(False)

        # If a selected_grid is provided, set it as the current text
        if selected_grid and selected_grid in grid_names:
            self.gridDropdown.setCurrentText(selected_grid)

    def populate_zone_dropdown(self, selected_zone=None):
        """Populates the dropdown with zone names and sets the selected zone if provided."""
        self.selected_zone = selected_zone

        if not self.master_df.empty:
            # Filter out any entries where 'Attribute Type' is 'Well'
            zone_df = self.master_df[self.master_df['Attribute Type'] == "Zone"]

            # Get the unique zone names from the filtered DataFrame and sort them alphabetically
            self.zone_zone_names = sorted(zone_df['Zone Name'].unique().tolist())

            # Block signals to prevent unwanted triggers during population
            self.zoneDropdown.blockSignals(True)
            self.zoneDropdown.clear()
            self.zoneDropdown.addItem("Select Zone")
            self.zoneDropdown.addItems(self.zone_zone_names)
            self.zoneDropdown.blockSignals(False)

            # Set the selected zone if provided and if it exists in the dropdown
            if self.selected_zone and self.selected_zone in self.zone_zone_names:
                self.zoneDropdown.setCurrentText(selected_zone)
                self.zoneAttributeDropdown.setEnabled(True)
            else:
                self.zoneDropdown.setCurrentText('Select Zone')  # Clear selection if zone is not found
                self.zoneAttributeDropdown.setEnabled(False)
        else:
            self.zoneDropdown.clear()
            self.zoneDropdown.addItem("No Zones Available")
            self.zoneAttributeDropdown.setEnabled(False)








    def populate_zone_attributes(self):
        """Populate the zone attribute dropdown with attributes having numeric values for the selected zone."""
        # Check if master_df is empty
        if self.master_df.empty:
            print("Master DataFrame is empty. No operations performed.")
            return  # Stop further processing

        # Filter master_df for the selected zone
        zone_df = self.master_df[self.master_df['Zone Name'] == self.selected_zone]

        # Drop fixed columns that are not relevant for selection
        columns_to_exclude = [
            'Zone Name', 'Zone Type', 'Attribute Type', 
            'Top Depth', 'Base Depth', 'UWI', 
            'Top X Offset', 'Base X Offset', 'Top Y Offset', 'Base Y Offset', 'Angle Top', 'Angle Base'
        ]
        remaining_df = zone_df.drop(columns=columns_to_exclude)

        # Find columns with numeric data types
        numeric_columns = remaining_df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_columns = [col for col in numeric_columns if remaining_df[col].max() - remaining_df[col].min() > 0]

        # Further filter to only include columns with at least one non-null value
        non_null_numeric_columns = [col for col in numeric_columns if remaining_df[col].notnull().any()]

        # Ensure "Grid Name" is included if it has non-null values
        if 'Grid Name' in zone_df.columns and zone_df['Grid Name'].notnull().any():
            non_null_numeric_columns.append('Grid Name')

        # Sort the list of columns alphabetically
        non_null_numeric_columns = sorted(non_null_numeric_columns)

        # Clear the dropdown before populating
        self.zoneAttributeDropdown.blockSignals(True)
        self.zoneAttributeDropdown.clear()

        if non_null_numeric_columns:
            self.zoneAttributeDropdown.addItem("Select Zone Attribute")
            self.zoneAttributeDropdown.addItems(non_null_numeric_columns)
            self.zoneAttributeDropdown.setEnabled(True)
        else:
            self.zoneAttributeDropdown.addItem("No Attributes Available")
            self.zoneAttributeDropdown.setEnabled(False)

        self.zoneAttributeDropdown.blockSignals(False)

    def grid_selected(self, index):
        if index == 0:  # "Select Grid" is selected
            self.drawingArea.clearGrid()
            return

        self.selected_grid = self.gridDropdown.currentText()

        # Load the color palette before using it
        self.get_grid_color()

        if self.selected_grid in self.depth_grid_data_df['Grid'].unique():
            selected_grid_df = self.depth_grid_data_df[self.depth_grid_data_df['Grid'] == self.selected_grid]
        else:
            selected_grid_df = self.attribute_grid_data_df[self.attribute_grid_data_df['Grid'] == self.selected_grid]

        # Extract grid information from grid_info_df
        grid_info = self.grid_info_df[self.grid_info_df['Grid'] == self.selected_grid].iloc[0]
        min_x = grid_info['min_x']
        max_x = grid_info['max_x']
        min_y = grid_info['min_y']
        max_y = grid_info['max_y']
        min_z = grid_info['min_z']
        max_z = grid_info['max_z']
        bin_size_x = grid_info['bin_size_x']
        bin_size_y = grid_info['bin_size_y']

        # Extract X, Y, and Z values from the selected grid DataFrame
        x_values = selected_grid_df['X'].values
        y_values = selected_grid_df['Y'].values
        z_values = selected_grid_df['Z'].values

        # Map Z values to colors
        grid_points_with_values = [
            (QPointF(x, y), self.map_value_to_color(z, min_z, max_z, self.selected_color_palette))
            for x, y, z in zip(x_values, y_values, z_values)
        ]

        # Update the drawing area with the new grid points and grid info
        self.drawingArea.setGridPoints(grid_points_with_values, min_x, max_x, min_y, max_y, min_z, max_z, bin_size_x, bin_size_y)

        self.display_color_range(self.gridColorRangeDisplay, self.selected_color_palette, min_z, max_z)

    def grid_color_selected(self):
        # Get the selected color bar from the dropdown
        self.selected_color_bar = self.gridColorBarDropdown.currentText()

        # Get the current index from the grid dropdown
        index = self.gridDropdown.currentIndex()

        # Call grid_selected with the current index
        self.grid_selected(index)

    def get_grid_color(self):
        # Define the path to the color palettes directory
        self.selected_color_bar = self.gridColorBarDropdown.currentText()
        palettes_dir = os.path.join(os.path.dirname(__file__), 'Palettes')
        file_path = os.path.join(palettes_dir, self.selected_color_bar)

        # Load the color palette
        self.selected_color_palette = self.load_color_palette(file_path)
  

    def zone_selected(self):
        """Handles the selection of a zone from the dropdown."""
        self.selected_zone = self.zoneDropdown.currentText()
 
        if self.selected_zone == "Select Zone":
            # Clear the zones in the plotting area
            
            self.processed_data = []
            self.drawingArea.clearZones()
            

        else:
            self.processed_data = []
            self.plot_zones(self.selected_zone)
         
            
        for uwi, well in self.well_data.items():
            mds = well['mds']  # Get the list of measured depths
            well['md_colors'] = [QColor(Qt.black)] * len(mds) 

        
        
        
        self.zoneAttributeDropdown.blockSignals(True)
        self.zoneAttributeDropdown.clear()
        self.populate_zone_attributes()
        self.drawingArea.setScaledData(self.well_data)
        self.zoneAttributeDropdown.blockSignals(False)
        self.zoneAttributeDropdown.setEnabled(False)

        self.zoneAttributeDropdown.setEnabled(True) 
        return

    def zone_attribute_selected(self):
        self.drawingArea.clearUWILines()
        # Get the selected zone attribute from the dropdown
        self.selected_zone = self.zoneDropdown.currentText()
        self.selected_zone_attribute = self.zoneAttributeDropdown.currentText()

        # Check if a zone and zone attribute are selected
        if self.selected_zone and self.selected_zone_attribute:
            if self.selected_zone_attribute == "Grid Name":
                # If the selected attribute is "Grid Name", apply the grid name colors
                self.apply_grid_name_colors()
                self.drawingArea.setScaledData(self.well_data)


            elif self.selected_zone_attribute == "Select Zone Attribute":
                # Change all colors for the selected zone to black
                for uwi in self.well_data:
                    well_data = self.well_data[uwi]
                    well_data['md_colors'] = [QColor(Qt.black) for _ in well_data['mds']]
                # Update the drawing area with the blackened data
                self.drawingArea.setScaledData(self.well_data)
            else:
                # Process zone attribute data for other attributes
                self.preprocess_zone_attribute_data()
                # Update the drawing area with the processed data
                self.drawingArea.setScaledData(self.well_data)

    def apply_grid_name_colors(self):
        """Simplified method to apply grid name colors directly when Zone Name equals Grid Name."""
        # Filter the DataFrame for the selected zone
        zone_df = self.master_df[self.master_df['Zone Name'] == self.selected_zone]

        if zone_df.empty:
            QMessageBox.warning(self, "Warning", f"No data found for zone '{self.selected_zone}'.")
            return

        # Create a color map for each UWI with top depth, base depth, and the associated color
        uwi_color_map = {}

        # Iterate through each zone and populate the color map
        for _, zone in zone_df.iterrows():
            uwi = zone['UWI']
            grid_name = zone['Grid Name']
            top_depth = zone['Top Depth']
            base_depth = zone['Base Depth']

            # Retrieve the color for the grid from grid_info_df
            grid_color = self.grid_info_df.loc[self.grid_info_df['Grid'] == grid_name, 'Color (RGB)'].values
            if grid_color.size == 0:
                qcolor = QColor(Qt.black)  # Default color if not found
            else:
                rgb_values = grid_color[0]  # Extract the RGB list
                qcolor = QColor(*rgb_values)

            # If the UWI is not already in the color map, add it
            if uwi not in uwi_color_map:
                uwi_color_map[uwi] = []

            # Add the top depth, base depth, and color as a tuple
            uwi_color_map[uwi].append(( top_depth, base_depth, qcolor))
  

        for _, zone in zone_df.iterrows():
            uwi = zone['UWI']
            attribute_value = zone[self.selected_zone_attribute]
            top_depth = zone['Top Depth']
            base_depth = zone['Base Depth']
            top_x_offset = zone['Top X Offset']
            top_y_offset = zone['Top Y Offset']
            base_x_offset = zone['Base X Offset']
            base_y_offset = zone['Base Y Offset']
            top_point = QPointF(top_x_offset, top_y_offset)
            base_point = QPointF(base_x_offset, base_y_offset)


            # Insert top depth data
            self.well_data[uwi]['x_offsets'].append(top_x_offset)
            self.well_data[uwi]['y_offsets'].append(top_y_offset)
            self.well_data[uwi]['mds'].append(top_depth)
            self.well_data[uwi]['points'].append(top_point)

        # After adding all points, sort each well's data by MD
        for uwi in self.well_data:
            well_data = self.well_data[uwi]
            sorted_indices = sorted(range(len(well_data['mds'])), key=lambda i: well_data['mds'][i])
            well_data['x_offsets'] = [well_data['x_offsets'][i] for i in sorted_indices]
            well_data['y_offsets'] = [well_data['y_offsets'][i] for i in sorted_indices]
            well_data['mds'] = [well_data['mds'][i] for i in sorted_indices]
            well_data['points'] = [well_data['points'][i] for i in sorted_indices]

        # Apply the colors to the well data
        for uwi, well_data in self.well_data.items():
            mds = well_data['mds']
            well_data['md_colors'] = []  # Clear and prepare the list for new colors

            if uwi in uwi_color_map:
                depth_color_list = uwi_color_map[uwi]
               

                # Iterate through the measured depths and assign colors
                for md in mds:
                    assigned_color = QColor(Qt.black)  # Default color

                    # Iterate over the depth_color_list in the given order
                    for top_depth, base_depth, color in depth_color_list:
                        # Ensure both UWI and depth range match
                        if top_depth <= md < base_depth:
                            assigned_color = color
                       
                            break  # Exit once the first matching color is found

                    well_data['md_colors'].append(assigned_color)
            

    def zone_attribute_color_selected(self):
        self.selected_zone_attribute_colorbar = self.zoneAttributeColorBarDropdown.currentText()
    
        palettes_dir = os.path.join(os.path.dirname(__file__), 'Palettes')
        file_path = os.path.join(palettes_dir, self.selected_zone_attribute_colorbar)

        try:
            self.preprocess_zone_attribute_data()
        
            # Pass updated well_data only, as processed_data is no longer needed
            self.drawingArea.setScaledData(self.well_data)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while updating colors: {e}")

    def preprocess_zone_attribute_data(self):
        zone_df = pd.DataFrame
        """Populates the well data with colors based on the selected zone."""
        zone_df = self.master_df[self.master_df['Zone Name'] == self.selected_zone]
    

        if zone_df.empty:
            QMessageBox.warning(self, "Warning", f"No data found for zone '{self.selected_zone}'.")
            return

        # Load the selected color palette
        color_bar_name = self.zoneAttributeColorBarDropdown.currentText()
        palettes_dir = os.path.join(os.path.dirname(__file__), 'Palettes')
        file_path = os.path.join(palettes_dir, color_bar_name)

        try:
            color_palette = self.load_color_palette(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load color palette: {e}")
            return

        # Determine min and max values for the selected zone attribute
        min_value = zone_df[self.selected_zone_attribute].min()
        max_value = zone_df[self.selected_zone_attribute].max()

        # Create a dictionary for quick lookup
        uwi_color_map = {}

        for _, zone in zone_df.iterrows():
            uwi = zone['UWI']
            attribute_value = zone[self.selected_zone_attribute]
            top_depth = zone['Top Depth']
            base_depth = zone['Base Depth']

            if uwi not in self.well_data or pd.isna(attribute_value):
                continue

            color = self.map_value_to_color(attribute_value, min_value, max_value, color_palette)

            if uwi not in uwi_color_map:
                uwi_color_map[uwi] = []

            uwi_color_map[uwi].append((top_depth, base_depth, color))
          

        for _, zone in zone_df.iterrows():
            uwi = zone['UWI']
            attribute_value = zone[self.selected_zone_attribute]
            top_depth = zone['Top Depth']
            base_depth = zone['Base Depth']
            top_x_offset = zone['Top X Offset']
            top_y_offset = zone['Top Y Offset']
            base_x_offset = zone['Base X Offset']
            base_y_offset = zone['Base Y Offset']
            top_point = QPointF(top_x_offset, top_y_offset)
            base_point = QPointF(base_x_offset, base_y_offset)


            # Insert top depth data
            self.well_data[uwi]['x_offsets'].append(top_x_offset)
            self.well_data[uwi]['y_offsets'].append(top_y_offset)
            self.well_data[uwi]['mds'].append(top_depth)
            self.well_data[uwi]['points'].append(top_point)
    

        # After adding all points, sort each well's data by MD
        for uwi in self.well_data:
            well_data = self.well_data[uwi]
            sorted_indices = sorted(range(len(well_data['mds'])), key=lambda i: well_data['mds'][i])
            well_data['x_offsets'] = [well_data['x_offsets'][i] for i in sorted_indices]
            well_data['y_offsets'] = [well_data['y_offsets'][i] for i in sorted_indices]
            well_data['mds'] = [well_data['mds'][i] for i in sorted_indices]
            well_data['points'] = [well_data['points'][i] for i in sorted_indices]

        # Apply the colors to the well data
        for uwi, well in self.well_data.items():
            mds = well['mds']
            well['md_colors'] = []  # Clear and prepare the list for new colors

            if uwi in uwi_color_map:
                depth_color_list = uwi_color_map[uwi]
              
                for md in mds:
                    assigned_color = QColor(Qt.black)  # Default color

                    # Perform binary search for quick range matching
                    for top_depth, base_depth, color in depth_color_list:
                        if top_depth <= md < base_depth:
                            assigned_color = color

                            break
                 
                    well['md_colors'].append(assigned_color)
        self.display_color_range(self.zoneAttributeColorRangeDisplay, color_palette, min_value, max_value)



    def zone_attribute_color_selected(self):
        """Handles the selection of a new color bar for zone attributes."""
        self.selected_zone_attribute_colorbar = self.WellAttributeColorBarDropdown.currentText()
    
        # Construct the path to the palette file
        palettes_dir = os.path.join(os.path.dirname(__file__), 'Palettes')
        file_path = os.path.join(palettes_dir, self.selected_zone_attribute_colorbar)

        try:
            # Preprocess data and apply the selected color palette
            self.preprocess_zone_attribute_data()
        
            # Pass the updated well_data only, as processed_data is no longer needed
            self.drawingArea.setScaledData(self.well_data)
        
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"The palette file '{file_path}' was not found.")
        except Exception as e:
            # Log the error and display a message box
        
            QMessageBox.warning(self, "Error", f"An error occurred while updating colors: {e}")




    def get_color_for_md(self, uwi, md):
        """Get color for a specific UWI and MD from well_data."""
        if uwi not in self.well_data or 'md_colors' not in self.well_data[uwi]:
            return QColor(Qt.black)  # Default color if UWI does not exist or has no MD color mappings

        # Return the color associated with the specific MD
        return self.well_data[uwi]['md_colors'].get(md, QColor(Qt.black))  # Return black if no color exists for MD

    
    def draw_grid_on_map(self, grid_df):
        # Clear current drawing
       
        self.drawingArea.clearCurrentLineAndIntersections()

        if grid_df.empty:
            return

        # Collect points and their values, prepare them for drawing
        points_with_values = []
        for index, row in grid_df.iterrows():
            x = row['X']
            y = row['Y']
            value = row['Z']  # Assuming the grid values are stored in a column named 'Value'
            # Convert to scaled coordinates
            scaled_x = (x - self.min_x) * self.scale + self.offset_x
            scaled_y = (self.max_y - y) * self.scale + self.offset_y
            points_with_values.append((QPointF(scaled_x, scaled_y), value))

        # Draw the points on the map
   
        self.drawingArea.setGridPoints(points_with_values)

    def plot_zones(self, zone_name):

        if self.master_df.empty:
            return  # Do nothing if the DataFrame is empty
        # Filter for the relevant zones
        zones = self.master_df[(self.master_df['Attribute Type'] == 'Zone') & (self.master_df['Zone Name'] == zone_name)]

        # Check if the required columns already contain data
        if all(col in self.master_df.columns for col in ['Top X Offset', 'Top Y Offset', 'Base X Offset', 'Base Y Offset', 'Angle Top', 'Angle Base']) \
                and not self.master_df[['Top X Offset', 'Top Y Offset', 'Base X Offset', 'Base Y Offset', 'Angle Top', 'Angle Base']].isna().any().any():
            # Create zone_data_df directly from master_df if the columns contain data
            self.zone_data_df = self.master_df[
                (self.master_df['Attribute Type'] == 'Zone') &
                (self.master_df['Zone Name'] == zone_name)
            ][['UWI', 'Zone Name', 'Top X Offset', 'Top Y Offset', 'Base X Offset', 'Base Y Offset', 'Top Depth', 'Base Depth', 'Angle Top', 'Angle Base']]

            self.zone_data_df.columns = [
                'UWI', 'Zone Name', 'Top X Offset', 'Top Y Offset', 'Base X Offset', 'Base Y Offset', 'Top Depth', 'Base Depth', 'Angle Top', 'Angle Base'
            ]
                      
          
          
        else:
            # Perform calculations and update master_df if the columns are missing data
            self.zone_data_df = pd.DataFrame()

            for _, zone in zones.iterrows():
                uwi = zone['UWI']
                top_md = zone['Top Depth']
                base_md = zone['Base Depth']
                top_x, top_y, base_x, base_y = self.calculate_offsets(uwi, top_md, base_md)

                if top_x is not None and top_y is not None and base_x is not None and base_y is not None:
                    # Append to the DataFrame
                    self.zone_data_df = self.zone_data_df.append({
                        'UWI': uwi,
                        'Zone Name': zone_name,
                        'Top X Offset': top_x,
                        'Top Y Offset': top_y,
                        'Base X Offset': base_x,
                        'Base Y Offset': base_y,
                        'Top Depth': top_md,
                        'Base Depth': base_md,
                    }, ignore_index=True)

            # Calculate angles after all data has been appended
            for uwi in self.zone_data_df['UWI'].unique():
                uwi_data = self.zone_data_df[self.zone_data_df['UWI'] == uwi]

                # Get the first and last X, Y offsets
                first_row = uwi_data.iloc[0]
                last_row = uwi_data.iloc[-1]
                x2 = last_row['Base X Offset']
                x1 = first_row['Top X Offset']
                y1 = first_row['Top Y Offset']
                y2 = last_row['Base Y Offset']
                last_row = uwi_data.iloc[-1]

                dx = x2 - x1
                dy = y1 - y2  

                angle = np.arctan2(dy, dx)  # Calculate the angle in radians

                # Normalize the angle to the range [0, 2π)
                if angle < 0:
                    angle += 2 * np.pi

                # Define the target angles (0, π/2, π, 3π/2, 2π) in radians
                target_angles = [0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]

                # Round to the nearest target angle
                rounded_angle = min(target_angles, key=lambda x: abs(x - angle))

                # Rotate the angle by 90 degrees (π/2 radians)
                rotated_angle = rounded_angle + np.pi/2

                # Normalize the rotated angle to the range [0, 2π)
                if rotated_angle >= 2 * np.pi:
                    rotated_angle -= 2 * np.pi

                # Update the angle in the DataFrame
                self.zone_data_df.loc[self.zone_data_df['UWI'] == uwi, 'Angle Top'] = rotated_angle
                self.zone_data_df.loc[self.zone_data_df['UWI'] == uwi, 'Angle Base'] = rotated_angle
 

            for _, row in self.zone_data_df.iterrows():
                uwi = row['UWI']
                top_md = row['Top Depth']
                base_md = row['Base Depth']
                top_x = row['Top X Offset']
                top_y = row['Top Y Offset']
                base_x = row['Base X Offset']
                base_y = row['Base Y Offset']
                rotated_angle = row['Angle Top']  # Angle Top and Base should be the same

                # Create a mask to identify the correct row in master_df
                mask = (
                    (self.master_df['UWI'] == uwi) &
                    (self.master_df['Zone Name'] == zone_name) &
                    (self.master_df['Top Depth'] == top_md) &
                    (self.master_df['Base Depth'] == base_md)
                )

                # Update the master_df with the corresponding data
                if not self.master_df[mask].empty:
                    self.master_df.loc[mask, 'Top X Offset'] = top_x
                    self.master_df.loc[mask, 'Top Y Offset'] = top_y
                    self.master_df.loc[mask, 'Base X Offset'] = base_x
                    self.master_df.loc[mask, 'Base Y Offset'] = base_y
                    self.master_df.loc[mask, 'Angle Top'] = rotated_angle
                    self.master_df.loc[mask, 'Angle Base'] = rotated_angle

        # Save the updated master_df
            self.save_master_df()
   
        # Plot all collected zones
        self.plot_all_zones()

    def calculate_offsets(self, uwi, top_md_ft, base_md_ft):
        # Convert top and base MD from feet to meters
        top_md_m = top_md_ft 
        base_md_m = base_md_ft 

        well_data = self.directional_surveys_df[self.directional_surveys_df['UWI'] == uwi]

        if well_data.empty:
            return None, None, None, None, None, None

        # Interpolate for top and base MDs
        top_x, top_y, below_top_x, below_top_y, above_top_x, above_top_y = self.interpolate(top_md_m, well_data)
        base_x, base_y, below_base_x, below_base_y, above_base_x, above_base_y = self.interpolate(base_md_m, well_data)



        return top_x, top_y, base_x, base_y

    def interpolate(self, md, data):




        # Find the two bracketing points
        below = data[data['MD'] <= (md +.1)]
        above = data[data['MD'] >= (md -.1)]
        if below.empty or above.empty:
            return None, None, None, None, None, None

        below = below.iloc[-1]
        above = above.iloc[0]

        if below['MD'] == above['MD']:  # Exact match
            return below['X Offset'], below['Y Offset'], below['X Offset'], below['Y Offset'], above['X Offset'], above['Y Offset']

        # Linear interpolation
        x = below['X Offset'] + (above['X Offset'] - below['X Offset']) * (md - below['MD']) / (above['MD'] - below['MD'])
        y = below['Y Offset'] + (above['Y Offset'] - below['Y Offset']) * (md - below['MD']) / (above['MD'] - below['MD'])
        return x, y, below['X Offset'], below['Y Offset'], above['X Offset'], above['Y Offset']

    def plot_all_zones(self):
        try:
            zone_ticks = []
          
            for _, row in self.zone_data_df.iterrows():
                top_x, top_y = row['Top X Offset'], row['Top Y Offset']
                base_x, base_y = row['Base X Offset'], row['Base Y Offset']
                top_md, base_md = row['Top Depth'], row['Base Depth']
                angle_top, angle_base = row['Angle Top'], row['Angle Base']

                # Append tick information for top and base
                zone_ticks.append((top_x, top_y, top_md, angle_top))
                zone_ticks.append((base_x, base_y, base_md, angle_base))
        
            self.drawingArea.clearZones()
            self.drawingArea.setZoneTicks(zone_ticks)
        except Exception as e:
            print(f"Error plotting zones: {e}")
            



        except Exception as e:
            print(f"Error in plot_all_zones: {e}")


    def populate_well_zone_dropdown(self):
        """Populates the dropdown with unique zone names where the Attribute Type is 'Well'."""

        # Clear the dropdown and set a default option
        self.WellZoneDropdown.blockSignals(True)
        self.WellZoneDropdown.clear()
        self.WellZoneDropdown.addItem("Select Well Zone")

        if not self.master_df.empty:
            # Filter the DataFrame to include only entries where 'Attribute Type' is 'Well'
            well_df = self.master_df[self.master_df['Attribute Type'] == "Well"]

            # Get the unique zone names from the filtered DataFrame
            self.well_zone_names = well_df['Zone Name'].unique().tolist()

            # Sort the zone names alphabetically
            self.well_zone_names.sort()

            # Populate the dropdown with the filtered and sorted zone names
            if self.well_zone_names:
                self.WellZoneDropdown.addItems(self.well_zone_names)

        self.WellZoneDropdown.blockSignals(False)

    def well_zone_selected(self):
        """Handles the selection of a zone from the dropdown."""
        self.selected_zone = self.WellZoneDropdown.currentText()

        self.WellAttributeDropdown.blockSignals(True)
        self.WellAttributeDropdown.clear()
        self.drawingArea.clearWellAttributeBoxes()
        self.WellAttributeDropdown.addItem("Select Well Attribute")
        
        self.WellAttributeDropdown.blockSignals(False)
        self.WellAttributeDropdown.setEnabled(False)

         
 
        if self.selected_zone == "Select Well Zone":
            self.WellAttributeDropdown.setEnabled(False)

             
            # Clear the zones in the plotting area

        else:
            self.populate_well_attribute_dropdown()
            self.WellAttributeDropdown.setEnabled(True)
      
        
 

    def populate_well_attribute_dropdown(self):
        """Populate the well attribute dropdown with numeric attributes for the selected well zone."""
    
        # Get the selected well zone from the well zone dropdown
        selected_well_zone = self.WellZoneDropdown.currentText()

        # Check if master_df is empty or no valid zone is selected
        if self.master_df.empty or selected_well_zone == "Select Well Zone":
            print("No well zone selected or Master DataFrame is empty. No operations performed.")
            return  # Stop further processing

        # Filter master_df for the selected well zone
        well_zone_df = self.master_df[(self.master_df['Zone Name'] == selected_well_zone) & 
                                      (self.master_df['Attribute Type'] == "Well")]

        # Drop fixed columns that are not relevant for selection
        columns_to_exclude = [
            'Zone Name', 'Zone Type', 'Attribute Type', 
            'Top Depth', 'Base Depth', 'UWI', 
            'Top X Offset', 'Base X Offset', 'Top Y Offset', 'Base Y Offset', 'Angle Top', 'Angle Base'
        ]
        remaining_df = well_zone_df.drop(columns=columns_to_exclude, errors='ignore')

        # Find columns with numeric data types
        numeric_columns = remaining_df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_columns = [col for col in numeric_columns if remaining_df[col].max() - remaining_df[col].min() > 0]

        # Further filter to only include columns with at least one non-null value
        non_null_numeric_columns = [col for col in numeric_columns if remaining_df[col].notnull().any()]
        non_null_numeric_columns.sort()

        # Clear the dropdown before populating
        self.WellAttributeDropdown.blockSignals(True)
        self.WellAttributeDropdown.clear()

        if non_null_numeric_columns:
            self.WellAttributeDropdown.addItem("Select Well Attribute")
            self.WellAttributeDropdown.addItems(non_null_numeric_columns)
            self.WellAttributeDropdown.setEnabled(True)
        else:
            self.WellAttributeDropdown.addItem("No Attributes Available")
            self.WellAttributeDropdown.setEnabled(False)

        self.WellAttributeDropdown.blockSignals(False)


    def well_attribute_selected(self):
        """Handle the event when a well attribute is selected."""
    
        # Get the selected attribute from the dropdown
        selected_attribute = self.WellAttributeDropdown.currentText()
    
        # Ensure a valid attribute is selected
        if selected_attribute == "Select Well Attribute" or not selected_attribute:
            return

        # Filter the master_df for the selected well zone and attribute type
        selected_well_zone = self.WellZoneDropdown.currentText()
        well_zone_df = self.master_df[(self.master_df['Zone Name'] == selected_well_zone) &
                                      (self.master_df['Attribute Type'] == "Well")]

        # Check if the selected attribute is in the filtered DataFrame
        if selected_attribute not in well_zone_df.columns:
            return

        # Load the selected color palette
        color_bar_name = self.WellAttributeColorBarDropdown.currentText()
        palettes_dir = os.path.join(os.path.dirname(__file__), 'Palettes')
        file_path = os.path.join(palettes_dir, color_bar_name)

        try:
            color_palette = self.load_color_palette(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load color palette: {e}")
            return

        # Calculate the min and max values for the selected attribute
        min_value = well_zone_df[selected_attribute].min()
        max_value = well_zone_df[selected_attribute].max()

        # Update the color bar display
        self.display_color_range(self.WellAttributeColorRangeDisplay, color_palette, min_value, max_value)

        # Map each value in the selected attribute to a color
        well_zone_df['color'] = well_zone_df[selected_attribute].apply(
            lambda value: self.map_value_to_color(value, min_value, max_value, color_palette)
        )

        # Prepare data to send to the drawing area using the Top X and Top Y Offsets
        points_with_colors = [
            (QPointF(row['Top X Offset'], row['Top Y Offset']), row['color'] if pd.notnull(row['color']) else QColor(0, 0, 0))
            for _, row in well_zone_df.iterrows()
        ]

        # Clear existing well attribute boxes and add new ones
        self.drawingArea.clearWellAttributeBoxes()
        self.drawingArea.add_well_attribute_boxes(points_with_colors)










    def load_color_palette(self, file_path):
        color_palette = []
        try:
            with open(file_path + '.pal', 'r') as file:
                lines = file.readlines()
                start_index = 2  # Assuming the first two lines are metadata
                for line in lines[start_index:]:
                    if line.strip():  # Check if the line is not empty
                        try:
                            r, g, b = map(int, line.strip().split())
                            color_palette.append(QColor(r, g, b))
                        except ValueError:
                            # Skip lines that do not contain valid color values
                            continue
        except FileNotFoundError:
            print(f"Error: The file '{file_path}.pal' was not found.")
        except IOError:
            print(f"Error: An IOError occurred while trying to read '{file_path}.pal'.")
        return color_palette

    def map_value_to_color(self, value, min_value, max_value, color_palette):
        """Map a value to a color based on the min and max range."""
        if max_value == min_value:
            return color_palette[0] if color_palette else QColor(0, 0, 0)

        # Normalize the value to a range between 0 and 1
        normalized_value = (value - min_value) / (max_value - min_value)
    
        # Scale the normalized value to the length of the color palette
        if pd.isna(normalized_value):
            index = 0  # Or any default value or behavior you want when encountering NaN
        else:
            # Scale the normalized value to the length of the color palette
            index = int(normalized_value * (len(color_palette) - 1))
    
        # Clamp the index to be within the bounds of the color_palette list
        index = max(0, min(index, len(color_palette) - 1))
    
        return color_palette[index]


    def display_color_range(self, color_range_display, color_palette, min_attr, max_attr):
        """Display the color range gradient with dashes and values above it."""
        if not color_palette or min_attr is None or max_attr is None:
            print("Unable to display color range.")
            color_range_display.setPixmap(QPixmap(color_range_display.size()))
            return

        pixmap = QPixmap(color_range_display.size())
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
    
        # Calculate dimensions
        margin = 5
        dash_height = 5
        text_height = 10  # Reduced text height to accommodate smaller font
        color_bar_height = 20
        total_height = margin + text_height + dash_height + color_bar_height + margin
        color_bar_y = total_height - color_bar_height - margin
        edge_padding = 10  # Increased padding

        # Draw color gradient (left to right: min to max)
        gradient = QLinearGradient(edge_padding, color_bar_y, 
                                   color_range_display.width() - edge_padding, color_bar_y)
        for i, color in enumerate(color_palette):
            gradient.setColorAt(i / (len(color_palette) - 1), color)

        painter.setBrush(QBrush(gradient))
        painter.drawRect(edge_padding, color_bar_y, 
                         color_range_display.width() - 2 * edge_padding, color_bar_height)

        # Prepare for drawing text and dashes
        painter.setPen(Qt.black)
        font = painter.font()
        font.setPointSize(5)  # Smaller font size
        painter.setFont(font)

        # Calculate intermediate values
        num_intervals = 4
        interval = (max_attr - min_attr) / num_intervals
        values = [round(min_attr + i * interval) for i in range(num_intervals + 1)]  # Rounded to nearest integer

        for i, value in enumerate(values):
            x = int(i * (color_range_display.width() - 2 * edge_padding) / num_intervals) + edge_padding
    
            # Draw dash
            painter.drawLine(x, color_bar_y - dash_height, x, color_bar_y)
    
            # Draw value
            text = f"{value}"
            text_width = painter.fontMetrics().width(text)
    
            # Adjust text position for edge values
            if i == 0:  # Leftmost value
                text_x = edge_padding
            elif i == num_intervals:  # Rightmost value
                text_x = color_range_display.width() - text_width - edge_padding
            else:
                text_x = x - text_width / 2
    
            painter.drawText(text_x, margin + text_height, text)

        painter.end()
        color_range_display.setPixmap(pixmap)







    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("MainWindow", "Zone Analyzer", None))

    def set_interactive_elements_enabled(self, enabled):
        self.plot_action.setEnabled(enabled)
        self.export_action.setEnabled(enabled)
        self.export_properties.setEnabled(enabled)
        for action in self.toolbar.actions():
            action.setEnabled(enabled)






####################################Display Properties######################################    
    def zoom_in(self):
        self.drawingArea.zoom(1.25, self.drawingArea.viewport().rect().center())

    def zoom_out(self):
        self.drawingArea.zoom(0.8, self.drawingArea.viewport().rect().center())

    def updateScrollBars(self):
        self.drawingArea.horizontalScrollBar().setValue(int(self.drawingArea.horizontalScrollBar().value()))
        self.drawingArea.verticalScrollBar().setValue(int(self.drawingArea.verticalScrollBar().value()))
    
    def toggle_draw_mode(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setIcon(QIcon('icons/draw_icon.png'))
            self.drawingArea.setDragMode(QGraphicsView.NoDrag)
        else:
            self.toggle_button.setIcon(QIcon('icons/pan_icon.png'))
            self.drawingArea.setDragMode(QGraphicsView.ScrollHandDrag)
    def updateOffset(self):
        x = self.scrollArea.horizontalScrollBar().value()
        y = self.scrollArea.verticalScrollBar().value()
        self.drawingArea.setOffset(QPointF(-x, -y))
    def toggle_uwi_labels(self, state):
        self.drawingArea.toggleUWIVisibility(state == Qt.Checked)

    def change_uwi_width(self, value=80):
        self.uwi_width = value
        self.drawingArea.updateUWIWidth(value)

    def change_opacity(self, value):
        self.uwi_opacity = value / 100.0
        self.drawingArea.setUWIOpacity(self.uwi_opacity)

    def change_line_width(self, value):
       
        self.line_width = value
        self.drawingArea.updateLineWidth(value)

    def change_line_opacity(self, value):
        self.line_opacity = value / 100.0
        self.drawingArea.updateLineOpacity(self.line_opacity)

########################################CREATE OPEN


    def clear_current_project(self):
        # Clear all the DataFrames
        self.directional_surveys_df = pd.DataFrame()
        self.depth_grid_data_df = pd.DataFrame()
        self.attribute_grid_data_df = pd.DataFrame()
        self.import_options_df = pd.DataFrame()
        self.selected_uwis = []
        self.grid_info_df = pd.DataFrame()
        self.well_list = []
        self.master_df = pd.DataFrame()

        # Reset any other state variables
        self.zone_names = []
        self.line_width = 2
        self.line_opacity = 0.8
        self.uwi_width = 80
        self.uwi_opacity = 1.0

        # Reset KD-Trees and other computed structures
        self.kd_tree_depth_grids = None
        self.kd_tree_att_grids = None
        self.depth_grid_data_dict = {}
        self.attribute_grid_data_dict = {}







    def open_project(self):
        self.clear_current_project()
        self.project_loader.open_from_file()
        self.drawingArea.setScaledData(self.well_data)
        self.drawingArea.fitSceneInView()

    def create_new_project(self):
        self.project_data = {
            'project_name': '',
            'filter_name': '',
            'selected_uwis': [],
            'top_grid': '',
            'bottom_grid': '',
            'number_of_zones': 0,
            'export_options': {}
        }

        options = QFileDialog.Options()
        self.file_name, _ = QFileDialog.getSaveFileName(self, "Create New Project", "", "JSON Files (*.json);;All Files (*)", options=options)
        if self.file_name:
            self.project_file_name = self.file_name
            self.project_saver = ProjectSaver(self.file_name)
            self.project_saver.project_data = self.project_data
            self.project_saver.save_project_data()

            self.set_interactive_elements_enabled(False)
            self.import_menu.setEnabled(True)
            self.data_loader_menu_action.setEnabled(True)

            self.grid_well_data_df = pd.DataFrame()
            self.well_info_df = pd.DataFrame()
            self.zonein_info_df = pd.DataFrame()
            self.top_grid_df = pd.DataFrame()
            self.bottom_grid_df = pd.DataFrame()
            self.total_zone_number = 0
            self.export_options = pd.DataFrame()
            self.zone_color_df = pd.DataFrame()
        
        file_basename = os.path.basename(self.file_name)
        self.setWindowTitle(QCoreApplication.translate("MainWindow", f"Zone Analyzer - {file_basename}", None))

    def dataloader(self):
        dialog = DataLoaderDialog(self.import_options_df)
        if dialog.exec_() == QDialog.Accepted:
            self.directional_surveys_df = dialog.directional_surveys_df
         
       
            self.depth_grid_data_df = dialog.depth_grid_data_df
            self.attribute_grid_data_df = dialog.attribute_grid_data_df
       
            self.import_options_df = dialog.import_options_df
            self.selected_uwis = dialog.selected_uwis
            self.depth_grid_color_df = dialog.depth_grid_color_df
            self.grid_info_df = dialog.grid_info_df
            self.well_list = dialog.well_list

            # Construct KD-Trees
            self.kd_tree_depth_grids = {
                grid: KDTree(self.depth_grid_data_df[self.depth_grid_data_df['Grid'] == grid][['X', 'Y']].values)
                for grid in self.depth_grid_data_df['Grid'].unique()
            }

            self.kd_tree_att_grids = {
                grid: KDTree(self.attribute_grid_data_df[self.attribute_grid_data_df['Grid'] == grid][['X', 'Y']].values)
                for grid in self.attribute_grid_data_df['Grid'].unique()
            }

            # Prepare data dictionaries for quick Z value access
            self.depth_grid_data_dict = {
                grid: self.depth_grid_data_df[self.depth_grid_data_df['Grid'] == grid]['Z'].values
                for grid in self.kd_tree_depth_grids
            }

            self.attribute_grid_data_dict = {
                grid: self.attribute_grid_data_df[self.attribute_grid_data_df['Grid'] == grid]['Z'].values
                for grid in self.kd_tree_att_grids
            }

            self.populate_grid_dropdown()
            self.setData()
     

            # Enable menus and interactive elements
            self.export_menu.setEnabled(True)
            self.launch_menu.setEnabled(True)
            self.calculate_menu.setEnabled(True)
            self.set_interactive_elements_enabled(True)
            if hasattr(self, 'project_file_name') and self.project_file_name:
                # Use the ProjectSaver class to save specific parts of the project data
                self.project_saver = ProjectSaver(self.project_file_name)
                self.project_saver.save_directional_surveys(self.directional_surveys_df)
                self.project_saver.save_depth_grid_data(self.depth_grid_data_df)
                self.project_saver.save_attribute_grid_data(self.attribute_grid_data_df)
                self.project_saver.save_import_options(self.import_options_df)
                self.project_saver.save_selected_uwis(self.selected_uwis)
                self.project_saver.save_depth_grid_colors(self.depth_grid_color_df)
                self.project_saver.save_grid_info(self.grid_info_df)
                self.project_saver.save_well_list(self.well_list)

                self.export_menu.setEnabled(True)
                self.launch_menu.setEnabled(True)
                self.calculate_menu.setEnabled(True)


    def dataload_well_zones(self):

        if not self.selected_uwis:
            # Show error message if no UWI is selected
            QMessageBox.warning(self, "Error", "Load Wells First")
            return
        dialog = DataLoadWellZonesDialog(self.selected_uwis, self.directional_surveys_df)
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.import_data()
            if result:
                df, attribute_type, zone_name, zone_type, uwi_header, top_depth_header, base_depth_header = result
                           # Append the new data to the existing DataFrame
                # Ensure zone_name is a list, even if it's a single item
                if isinstance(zone_name, str):
                    zone_name = [zone_name]

                # Append the new data to the existing DataFrame
                if not self.master_df.empty:
                    self.master_df = pd.concat([self.master_df, df], ignore_index=True)
               
                else:
                    self.master_df = df

                # Update zone names
                self.zone_names.extend(zone_name)
                self.zone_names = list(set(self.zone_names))  # Remove duplicates
           
                
                # Ensure the project saver is initialized
                if not hasattr(self, 'project_saver'):
                    self.project_saver = ProjectSaver(self.project_file_name)

                # Save the updated master_df using the ProjectSaver
                self.project_saver.save_master_df(self.master_df)
                self.project_saver.save_zone_names(self.zone_names)

                print("Project data updated and saved")
                self.populate_zone_dropdown()
                self.populate_well_attribute_dropdown()
                self.populate_well_zone_dropdown()
                self.export_menu.setEnabled(True)
                self.launch_menu.setEnabled(True)


    def dataload_segy(self):
        # Create and launch the DataLoadSegy dialog
        dialog = DataLoadSegy(self)

        if dialog.exec_() == QDialog.Accepted:
            # Access the saved SEGY settings
            self.seismic_data = dialog.get_seismic_data()
            print(self.seismic_data)
            self.bounding_box = dialog.get_bounding_box()

            if self.seismic_data and 'x_coords' in self.seismic_data and 'y_coords' in self.seismic_data:
                # Build the KDTree for seismic data
                seismic_coords = np.column_stack((self.seismic_data['x_coords'], self.seismic_data['y_coords']))
                self.seismic_kdtree = KDTree(seismic_coords)
            
                # Save the seismic data, bounding box, and KDTree
                self.project_saver.save_seismic_data(self.seismic_data, self.bounding_box, self.seismic_kdtree)

            else:
                print("Invalid seismic data: Missing 'x_coords' or 'y_coords'.")

    


        self.project_saver.save_seismic_data(self.seismic_data, self.bounding_box)

        self.display_seismic_data(10)

    def display_seismic_data(self, inline_number):
        trace_data = self.seismic_data['trace_data']
        time_axis = self.seismic_data['time_axis']
        inlines = self.seismic_data['inlines']

        # Find all traces where inline == inline_number
        trace_indices = np.where(inlines == inline_number)[0]

        if len(trace_indices) == 0:
            print(f"No traces found for inline {inline_number}.")
            return

        # Extract the traces corresponding to the selected inline
        inline_traces = trace_data[trace_indices, :]

        # Create a figure and axis
        fig, ax = plt.subplots()

        # Plot the seismic data as a color image with 'lower' origin to place time correctly
        im = ax.imshow(inline_traces.T, cmap='seismic', aspect='auto',
                       extent=[0, len(trace_indices), np.min(time_axis), np.max(time_axis)],
                       origin='lower')  # Corrects the upside-down issue by setting origin to 'lower'

        ax.set_title(f"Seismic Section for Inline {inline_number}")
        ax.set_xlabel("Trace Number")
        ax.set_ylabel("Time (ms)")
        plt.colorbar(im, ax=ax, label="Amplitude")

        # Display the plot
        plt.show()


###############################################Zone DISPLAYS###################################



    def handle_well_attributes(self, df, uwi_header):
        # Implement logic to handle well attributes
        pass

    def handle_zone_attributes(self, df, uwi_header, top_depth_header, base_depth_header, zone_name, zone_type):
        # Implement logic to handle zone attributes
        pass















    def toggle_draw_mode(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setIcon(QIcon('icons/draw_icon.png'))
            self.drawing_area.toggleDrawMode()
        else:
            self.toggle_button.setIcon(QIcon('icons/pan_icon.png'))
            self.drawing_area.toggleDrawMode()

    def getScenePositionFromEvent(self, event):
        # Get the position relative to the view
        view_pos = event.pos()
    
        # Adjust the coordinates based on the view's scale and scroll bars
        adjusted_x = (view_pos.x() + self.horizontalScrollBar().value()) / self.scale_factor
        adjusted_y = (view_pos.y() + self.verticalScrollBar().value()) / self.scale_factor
    
        return QPointF(adjusted_x, adjusted_y)

    def handle_left_click(self, position):
        if self.drawing:
            # Convert position to QPointF
            point = QPointF(position)

            # Update the current line and click points
            self.currentLine.append(point)
            self.originalCurrentLine.append(position)  # Assuming originalCurrentLine stores raw coordinates
            self.drawingArea.setCurrentLine(self.currentLine)
            self.drawingArea.addClickPoint(point)

            # Add this line to add a node
            self.lastPoint = point
            self.scaled_points.append(position)  # Assuming scaled_points stores raw coordinates

            # Update the scene to reflect changes
            self.drawingArea.scene.update()
        else:
            # Print the position if not in drawing mode
            print(f"Left click at: {position}")

    def handle_right_click(self, position):
        if not self.drawing:
            closest_uwi = self.find_closest_uwi(QPointF(position))
            if closest_uwi:
                print(closest_uwi)
                self.plot_data(closest_uwi)
                self.drawingArea.updateHoveredUWI(closest_uwi)  
                self.drawingArea.update()
        else:

            self.drawing = False
            self.lastPoint = None

            self.intersections = []
            self.intersectionPoints = []
            self.originalIntersectionPoints = []

            if len(self.currentLine) > 1:
                # Convert current line points to the scaled_data coordinate system
                new_line_coords = [(point.x(), point.y()) for point in self.currentLine]


                segment_lengths = []
                for i in range(len(new_line_coords) - 1):
                    first_x, first_y = new_line_coords[i]
                    last_x, last_y = new_line_coords[i + 1]

                    segment_length = math.sqrt((last_x - first_x) ** 2 + (last_y - first_y) ** 2)
                    segment_lengths.append(segment_length)

                segment_number = 0
                total_cumulative_distance = 0

    
                for i in range(len(new_line_coords) - 1):
                    first_x, first_y = new_line_coords[i]
                    last_x, last_y = new_line_coords[i + 1]
                    segment = LineString([(first_x, first_y), (last_x, last_y)])

                    for uwi, scaled_offsets in self.scaled_data.items():
                        well_line_points = [(point.x(), point.y(), tvd) for point, tvd in scaled_offsets]
                        well_line_coords = [(x, y) for x, y, tvd in well_line_points]
                        well_line = LineString(well_line_coords)

                        if segment.intersects(well_line):
                            intersection = segment.intersection(well_line)

                            if isinstance(intersection, Point):
                                points = [intersection]
                            elif isinstance(intersection, MultiPoint):
                                points = list(intersection.geoms)
                            elif isinstance(intersection, GeometryCollection):
                                points = [geom for geom in intersection.geoms if isinstance(geom, Point)]
                            else:
                                points = []

                            for point in points:
                                intersection_qpoint = QPointF(point.x, point.y)
                                self.originalIntersectionPoints.append(intersection_qpoint)

                                # Find the two closest well points to the intersection
                                well_line_points_sorted = sorted(well_line_points, key=lambda wp: ((wp[0] - point.x) ** 2 + (wp[1] - point.y) ** 2) ** 0.5)
                                p1, p2 = well_line_points_sorted[0], well_line_points_sorted[1]

                                # Perform linear interpolation
                                x1, y1, tvd1 = p1
                                x2, y2, tvd2 = p2
                                tvd_value = self.calculate_interpolated_tvd(point, [(x1, y1, tvd1), (x2, y2, tvd2)])

                   # Ensure tvd_value is numeric and check for finiteness
                                try:
                                    tvd_value = float(tvd_value)
                                except (TypeError, ValueError):
                                    tvd_value = float('nan')


                                if not np.isfinite(tvd_value):
                                    print(f"Warning: Non-finite TVD Value encountered for UWI: {uwi}, Point: ({point.x}, {point.y})")

                                cumulative_distance = total_cumulative_distance + math.sqrt((point.x - first_x) ** 2 + (point.y - first_y) ** 2)
                                self.intersections.append((uwi, point.x, point.y, tvd_value, cumulative_distance))

                    total_cumulative_distance += segment_lengths[i]
                    segment_number += 1

            actions_to_toggle = [self.plot_tool_action, self.gun_barrel_action, self.data_loader_menu_action]
            self.set_interactive_elements_enabled(True)
            for action in actions_to_toggle:
                action.setEnabled(True)
            self.drawingArea.setIntersectionPoints(self.originalIntersectionPoints)
            self.plot_gun_barrel()

    def map_to_data_coords(self, point):
        """Convert point from map coordinates to data coordinates."""
        scale_x = self.drawingArea.width() / (self.drawingArea.max_x - self.drawingArea.min_x)
        scale_y = self.drawingArea.height() / (self.drawingArea.max_y - self.drawingArea.min_y)
        data_x = point.x() / scale_x + self.drawingArea.min_x
        data_y = self.drawingArea.max_y - point.y() / scale_y
        return data_x, data_y

    def data_to_map_coords(self, point):
        """Convert point from data coordinates to map coordinates."""
        scale_x = self.drawingArea.width() / (self.drawingArea.max_x - self.drawingArea.min_x)
        scale_y = self.drawingArea.height() / (self.drawingArea.max_y - self.drawingArea.min_y)
        map_x = (point.x() - self.drawingArea.min_x) * scale_x
        map_y = (self.drawingArea.max_y - point.y()) * scale_y
        return QPointF(map_x, map_y)

    def calculate_interpolated_tvd(self, intersection, well_line_points):
        intersection_coords = (intersection.x, intersection.y)
        for i in range(len(well_line_points) - 1):
            x1, y1, tvd1 = well_line_points[i]
            x2, y2, tvd2 = well_line_points[i + 1]

            if self.is_between(intersection_coords, (x1, y1), (x2, y2)):
                dist_total = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                dist_to_intersection = ((intersection.x - x1) ** 2 + (intersection.y - y1) ** 2) ** 0.5
                weight = dist_to_intersection / dist_total
                tvd_value = tvd1 + weight * (tvd2 - tvd1)
                return tvd_value
        return None

    def is_between(self, point, point1, point2):
        cross_product = (point[1] - point1[1]) * (point2[0] - point1[0]) - (point[0] - point1[0]) * (point2[1] - point1[1])
        if abs(cross_product) > 1e-6:
            print(f"Point {point} is not between {point1} and {point2} due to cross product")
            return False

        dot_product = (point[0] - point1[0]) * (point2[0] - point1[0]) + (point[1] - point1[1]) * (point2[1] - point1[1])
        if dot_product < 0:
            print(f"Point {point} is not between {point1} and {point2} due to dot product")
            return False

        squared_length = (point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2
        if dot_product > squared_length:
            print(f"Point {point} is not between {point1} and {point2} due to squared length")
            return False

        return True

    def find_closest_uwi(self, point):

        if self.kd_tree_wells is None:
            return None

        point_array = np.array([point.x(), point.y()])
        distance, index = self.kd_tree_wells.query(point_array)
        closest_point = self.uwi_points[index]
        closest_uwi = self.uwi_map[closest_point]
        print(f"Found closest UWI: {closest_uwi} with distance: {distance}")

        return closest_uwi

    def toggleDrawing(self):
        self.drawing = True
        self.intersectionPoints = []
        self.currentLine = []
        self.scaled_points = []

        actions_to_toggle = [self.plot_tool_action, self.export_action, self.data_loader_menu_action]
        if self.drawing:
            print("Drawing mode is ON")
            self.gun_barrel_action.setChecked(True)
            self.drawingArea.clearCurrentLineAndIntersections()
            actions_to_toggle = [self.plot_tool_action, self.gun_barrel_action, self.data_loader_menu_action]
            self.set_interactive_elements_enabled(False) 
            for action in actions_to_toggle:
                action.setEnabled(False)
        else:
            print("Drawing mode is OFF")
            for action in actions_to_toggle:
                action.setEnabled(True)
        self.update()
######################################Launch####################################
    def launch_zone_viewer(self):
        # Create the dialog with settings if available
        self.zone_viewer_dialog = ZoneViewerDialog(
            self.master_df, 
            self.zone_names, 
            self.selected_uwis, 
            self.save_zone_viewer_settings, 
            self.zone_criteria_df,
            self.column_filters
        )

        # Connect the signal for saving settings when the dialog is closed
        self.zone_viewer_dialog.settingsClosed.connect(self.save_zone_settings)
        self.zone_viewer_dialog.dataUpdated.connect(self.update_master_df)
        self.zone_viewer_dialog.newAttributeAdded.connect(self.add_new_attribute_to_dropdowns)
        self.zone_viewer_dialog.zoneNamesUpdated.connect(self.update_zone_names)

        self.zone_viewer_dialog.show()

    def update_master_df(self, updated_df):
        self.master_df = updated_df
        self.save_master_df()

    def update_zone_names(self, updated_zone_names):
        """Slot to update the zone names in the main application."""
        self.zone_names = updated_zone_names
        self.populate_zone_dropdown()
        # Handle any additional logic required when the zone names are updated
        print("Zone names updated in main application.")

    def add_new_attribute_to_dropdowns(self, attribute_name):
        # Add the new attribute to the dropdowns if not already present
        if attribute_name not in [self.zoneAttributeDropdown.itemText(i) for i in range(self.zoneAttributeDropdown.count())]:
            self.zoneAttributeDropdown.addItem(attribute_name)

        if attribute_name not in [self.WellAttributeDropdown.itemText(i) for i in range(self.WellAttributeDropdown.count())]:
            self.WellAttributeDropdown.addItem(attribute_name)


    def save_zone_settings(self, data):
        # Extract the settings, criteria DataFrame, and column filters from the data dictionary
        settings = data.get("settings")
        criteria_df = data.get("criteria")
        self.column_filters = data.get("columns")
        self.save_master_df()



        # Save the settings
        if settings is not None:
            self.save_zone_viewer_settings = settings
            self.project_saver.save_zone_viewer_settings(self.save_zone_viewer_settings)

        # Save the column filters
        if self.column_filters is not None:
            self.project_saver.save_column_filters(self.column_filters)

        # Save the criteria DataFrame
        if criteria_df is not None:
            self.zone_criteria_df = criteria_df
            self.project_saver.save_zone_criteria_df(self.zone_criteria_df)

    def plot_data(self, uwi=None):
    
        if not self.directional_surveys_df.empty and not self.depth_grid_data_df.empty:
            try:
                if uwi:
                    # Select data for the specified UWI
                    current_uwi = uwi

                else:
                    # Select data for the first UWI in the list (assuming this is the "current" UWI)
                    current_uwi = self.well_list[0]
                

                if current_uwi not in self.well_list:
                    raise ValueError(f"UWI {current_uwi} not found in well list.")
                
                navigator = Plot(self.well_list, self.directional_surveys_df, self.depth_grid_data_df, self.grid_info_df, self.kd_tree_depth_grids, current_uwi, self.depth_grid_data_dict, self.master_df, self.seismic_data, self.seismic_kdtree, parent=self)
                self.open_windows.append(navigator)
                
                navigator.show()
                navigator.closed.connect(lambda: self.open_windows.remove(navigator))


            except Exception as e:
                print(f"Error initializing Plot: {e}")
                self.show_info_message("Error", f"Failed to initialize plot navigator: {e}")
        else:
            self.show_info_message("Info", "No grid well data available to plot.")


    def plot_gun_barrel(self):
        new_line_coords = [(point.x(), point.y()) for point  in self.currentLine]
        
        if len(new_line_coords) < 2:
            QMessageBox.warning(self, "Warning", "You need to draw a line first.")
            return

        self.plot_gb = PlotGB(
            self.depth_grid_data_df, 
            self.grid_info_df, 
            new_line_coords, 
            self.kd_tree_depth_grids,
            self.depth_grid_data_dict,
            self.intersections,
            self.zone_names,
            self.master_df,
            self.seismic_data,
            main_app=self
        )
        # Add to the list of windows
        self.plot_gb_windows.append(self.plot_gb)

        # Show the window
        self.plot_gb.show()
        self.plot_gb.closed.connect(lambda: self.plot_gb_windows.remove(self.plot_gb))

    def crossPlot(self):
        self.cross_plot_dialog = CrossPlot(self.master_df)
        self.cross_plot_dialog.show()


    def update_plot_gb_windows(self):
        for window in self.plot_gb_windows:
            window.update_data(
                self.depth_grid_data_df, 
                self.grid_info_df, 
                self.kd_tree_depth_grids,
                self.depth_grid_data_dict,
                self.intersections
            )

    def open_color_editor(self):
        if self.project_saver is None:
            raise ValueError("Project saver is not initialized. Ensure the project file is set.")

        editor = ColorEditor(self.grid_info_df, self)
        editor.color_changed.connect(self.update_grid_info_df)
        editor.exec_()  # Display the color editor dialog

    def update_grid_info_df(self, updated_grid_info_df):
        self.grid_info_df = updated_grid_info_df
        self.project_saver.save_grid_info(self.grid_info_df)
        self.refresh_open_windows()
        print("Updated grid colors saved")

    def refresh_open_windows(self):
        for window in self.open_windows:
            window.update_plot(self.grid_info_df)
        for window in self.plot_gb_windows:  # Fixed this to use the correct list
            window.update_data(self.grid_info_df)

    def handle_hover_event(self, uwi):
        print(uwi)
        self.drawingArea.updateHoveredUWI(uwi)

            
##################################Map############################################




###########################Calcs#################################

    def open_stages_dialog(self):
        dialog = StagesCalculationDialog(self.master_df, self.directional_surveys_df, self.zone_names)
        
        dialog.exec_()
        self.master_df = dialog.master_df

        self.zone_names = dialog.zone_names
        self.populate_zone_dropdown()
        self.project_saver.save_master_df(self.master_df)
    
        self.project_saver.save_zone_names(self.zone_names)

        self.populate_zone_dropdown()


        save_dir = os.path.dirname(os.path.abspath(__file__))
        master_file_path = os.path.join(save_dir, 'master_data.csv')


        # Ensure the directory exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
        # Save the updated master_df to a CSV file
        self.master_df.to_csv(master_file_path, index=False)
        print(f"Master DataFrame saved to '{master_file_path}'")
        if hasattr(self, 'selected_zone') and self.selected_zone:
            self.zone_selected(self.selected_zone)
   



    def open_zone_attributes_dialog(self):
        dialog = ZoneAttributesDialog(
            self.master_df,
            self.directional_surveys_df,
            self.grid_info_df,
            self.kd_tree_depth_grids,
            self.kd_tree_att_grids,
            self.zone_names,
            self.depth_grid_data_dict,
            self.attribute_grid_data_dict
        )
        dialog.exec_()
        if dialog.result() == QDialog.Accepted:
            self.master_df = dialog.updated_master
            self.populate_zone_attributes()
            self.save_master_df()

    def open_well_attributes_dialog(self):
        dialog = WellAttributesDialog(self)
        dialog.exec_()

    def inzone_dialog(self):
        dialog = InZoneDialog(
            self.master_df,
            self.directional_surveys_df,
            self.grid_info_df,
            self.kd_tree_depth_grids,
            self.kd_tree_att_grids,
            self.zone_names,
            self.depth_grid_data_dict,
            self.attribute_grid_data_dict
              )
        dialog.exec_()

        self.master_df = dialog.master_df
        self.zone_names = dialog.zone_names
        self.project_saver.save_zone_names(self.zone_names)
        self.populate_zone_dropdown()
     
        self.master_df.fillna(0)
        self.save_master_df()

    def save_master_df(self):
        self.project_saver.save_master_df(self.master_df)

    def shutdown_and_save_all(self):
        selected_grid = self.gridDropdown.currentText()
        gridColorBarDropdown = self.gridColorBarDropdown.currentText()
        selected_zone = self.zoneDropdown.currentText()
        selected_zone_attribute = self.zoneAttributeDropdown.currentText()
        zoneAttributeColorBarDropdown = self.zoneAttributeColorBarDropdown.currentText()
        selected_well_zone = self.WellZoneDropdown.currentText()
        selected_well_attribute = self.WellAttributeDropdown.currentText()
        WellAttributeColorBarDropdown = self.WellAttributeColorBarDropdown.currentText()

        self.project_saver.shutdown(
        self.line_width, 
        self.line_opacity, 
        self.uwi_width, 
        self.uwi_opacity, 
        selected_grid, 
        selected_zone,
        selected_zone_attribute, 
        selected_well_zone, 
        selected_well_attribute, 
        gridColorBarDropdown,
        zoneAttributeColorBarDropdown,
        WellAttributeColorBarDropdown
    )
 
        
###########################################Export#############################################

    def export(self):
        pass

    def mapproperties(self):
        # Create a copy of the DataFrame
        zone_color_df_copy = self.zone_color_df.copy()
        # Pass the copy to the dialog
        dialog = SWPropertiesEdit(zone_color_df_copy)
        dialog.exec_()

    def export_to_sw(self):
        pass
        #self.connection = SeisWare.Connection()
        #try:
        #    serverInfo = SeisWare.Connection.CreateServer()
        #    self.connection.Connect(serverInfo.Endpoint(), 50000)
        #except RuntimeError as err:
        #    self.show_error_message("Connection Error", f"Failed to connect to the server: {err}")
        #    return

        #self.project_list = SeisWare.ProjectList()
        #try:
        #    self.connection.ProjectManager().GetAll(self.project_list)
        #except RuntimeError as err:
        #    self.show_error_message("Error", f"Failed to get the project list from the server: {err}")
        #    return

        #project_name = self.import_options_df.get('Project', [''])[0]

        #self.projects = [project for project in self.project_list if project.Name() == project_name]
      
        #if not self.projects:
        #    self.show_error_message("Error", "No project was found")
        #    return

        #self.login_instance = SeisWare.LoginInstance()
        #try:
        #    self.login_instance.Open(self.connection, self.projects[0])
        #except RuntimeError as err:
        #    self.show_error_message("Error", "Failed to connect to the project: " + str(err))
        #    return

        #well_manager = self.login_instance.WellManager()
        #zone_manager = self.login_instance.ZoneManager()
        #zone_type_manager = self.login_instance.ZoneTypeManager()
        #well_zone_manager = self.login_instance.WellZoneManager()

        #well_list = SeisWare.WellList()
        #zone_list = SeisWare.ZoneList()
        #zone_type_list = SeisWare.ZoneTypeList()

        #try:
        #    well_manager.GetAll(well_list)
        #    zone_manager.GetAll(zone_list)
        #    zone_type_manager.GetAll(zone_type_list)
        #except SeisWare.SDKException as e:
        #    print("Failed to get necessary data.")
        #    print(e)
        #    return 1

        #zone_type_name = "DrilledZone"
        #zone_type_exists = any(zone_type.Name() == zone_type_name for zone_type in zone_type_list)

        #if not zone_type_exists:
        #    new_zone_type = SeisWare.ZoneType()
        #    new_zone_type.Name(zone_type_name)
        #    try:
        #        zone_type_manager.Add(new_zone_type)
        #        zone_type_manager.GetAll(zone_type_list)
        #        print(f"Successfully added new zone type: {zone_type_name}")
        #    except SeisWare.SDKException as e:
        #        print(f"Failed to add the new zone type: {zone_type_name}")
        #        print(e)
        #        return 1
        #else:
        #    print(f"Zone type '{zone_type_name}' already exists.")

        #drilled_zone_type_id = next((zone_type.ID() for zone_type in zone_type_list if zone_type.Name() == zone_type_name), None)
        #if drilled_zone_type_id is None:
        #    print(f"Failed to retrieve the ID for zone type: {zone_type_name}")
        #    return 1

        #for index, row in self.zonein_info_df.iterrows():
        #    zone_name = row['Zone Name']
        #    if not any(zone.Name() == zone_name for zone in zone_list):
        #        new_zone = SeisWare.Zone()
        #        new_zone.Name(zone_name)
        #        try:
        #            zone_manager.Add(new_zone)
        #            zone_manager.GetAll(zone_list)
        #            print(f"Successfully added new zone: {zone_name}")
        #        except SeisWare.SDKException as e:
        #            print(f"Failed to add the new zone: {zone_name}")
        #            print(e)
        #            return 1
        #    else:
        #        print(f"Zone '{zone_name}' already exists.")

        #well_map = {well.UWI(): well for well in well_list}
        #zone_map = {zone.Name(): zone for zone in zone_list}

        #for index, row in self.zonein_info_df.iterrows():
        #    well_uwi = row['UWI']
        #    if well_uwi not in well_map:
        #        print(f"No well was found for UWI {well_uwi} in row {index}")
        #        continue

        #    well = well_map[well_uwi]
        #    well_id = well.ID()

        #    zone_name = row['Zone Name']
        #    if zone_name not in zone_map:
        #        print(f"No zone was found for name {zone_name} in row {index}")
        #        continue

        #    zone = zone_map[zone_name]

        #    new_well_zone = SeisWare.WellZone()

        #    try:
        #        new_well_zone.WellID(well_id)
        #        new_well_zone.Zone(zone)
        #        new_well_zone.ZoneTypeID(drilled_zone_type_id)
        #        new_well_zone.TopMD(SeisWare.Measurement(row['MD Top Depth Meters'], SeisWare.Unit.Meter))
        #        new_well_zone.BaseMD(SeisWare.Measurement(row['MD Base Depth Meters'], SeisWare.Unit.Meter))
        #    except KeyError as e:
        #        print(f"Invalid data for well zone in row {index}: {e}")
        #        continue
          
        #    try:
        #        well_zone_manager.Add(new_well_zone)
        #        print(f"Successfully added well zone for UWI {well_uwi}")
        #    except SeisWare.SDKException as e:
        #        print(f"Failed to add well zone for UWI {well_uwi}")
        #        print(e)
        #        continue

        #return 0





    def show_error_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def show_info_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = Map()
    window.show()


    sys.exit(app.exec_())
