import json
import pandas as pd
from PySide2.QtWidgets import QFileDialog
from scipy.spatial import KDTree
import os
import pickle
import numpy as np

class ProjectLoader:
    def __init__(self, parent):
        self.parent = parent

    def open_from_file(self):
        self.parent.open = True

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.parent, "Open File", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            self.parent.set_project_file_name(file_name)
            with open(file_name, 'r') as file:
                data_loaded = json.load(file)

            # Load DataFrames from JSON if they exist
            self.parent.directional_surveys_df = pd.DataFrame(data_loaded.get('directional_surveys', {}))
            self.parent.depth_grid_data_df = pd.DataFrame(data_loaded.get('depth_grid_data', {}))
            self.parent.attribute_grid_data_df = pd.DataFrame(data_loaded.get('attribute_grid_data', {}))
            self.parent.import_options_df = pd.DataFrame(data_loaded.get('import_options', {}))
            self.parent.selected_uwis = data_loaded.get('selected_uwis', [])
            self.parent.grid_info_df = pd.DataFrame(data_loaded.get('grid_info', {}))
            self.parent.well_list = data_loaded.get('well_list', [])
            self.parent.master_df = pd.DataFrame(data_loaded.get('master_df', {}))
                    # Load SEGY data and bounding box
            # Load seismic data back into a DataFrame

            seismic_data_dict = data_loaded.get('seismic_data_df', None)
            if seismic_data_dict:
                seismic_metadata_df = pd.DataFrame(seismic_data_dict)
            else:
                seismic_metadata_df = None

            # Load the trace data and time axis
            trace_data = np.array(data_loaded.get('seismic_trace_data', []))
            time_axis = np.array(data_loaded.get('seismic_time_axis', []))

            # Recombine everything back into self.parent.seismic_data
            if seismic_metadata_df is not None:
                self.parent.seismic_data = {
                    'trace_data': trace_data,
                    'time_axis': time_axis,
                    'inlines': seismic_metadata_df['Inline'].values,
                    'crosslines': seismic_metadata_df['Crossline'].values,
                    'x_coords': seismic_metadata_df['X'].values,
                    'y_coords': seismic_metadata_df['Y'].values
                }
            else:
                self.parent.seismic_data = None  # Handle missing metadata case
            try:
                with open(file_name.replace('.json', '_kdtree.pkl'), 'rb') as kdtree_file:
                    self.parent.seismic_kdtree = pickle.load(kdtree_file)
                    print("Seismic KDTree loaded successfully.")
            except FileNotFoundError:
                print("KDTree file not found.")
                self.parent.seismic_kdtree = None  # Handle missing KDTree case
            except Exception as e:
                print(f"Error loading seismic KDTree: {e}")
                self.parent.seismic_kdtree = None


            # Load the bounding box, if it exists
            self.parent.bounding_box = data_loaded.get('bounding_box', None)

            # Load zone names
            self.parent.zone_names = data_loaded.get('zone_names', [])

            self.parent.line_width = data_loaded.get('line_width', 2)
            self.parent.line_opacity = data_loaded.get('line_opacity', 0.8)
            self.parent.uwi_width = data_loaded.get('uwi_width', 80)
            self.parent.uwi_opacity = data_loaded.get('uwi_opacity', 1.0)
    


            self.parent.gridDropdown.blockSignals(True)
            self.parent.zoneDropdown.blockSignals(True)
            self.parent.zoneAttributeDropdown.blockSignals(True)
            self.parent.WellZoneDropdown.blockSignals(True)
            self.parent.WellAttributeDropdown.blockSignals(True)
            self.parent.gridColorBarDropdown.blockSignals(True)
            self.parent.zoneAttributeColorBarDropdown.blockSignals(True)
            self.parent.WellAttributeColorBarDropdown.blockSignals(True)



            # Set dropdowns to the saved values
            selected_grid = data_loaded.get('selected_grid', 'Default Grid')
            self.parent.gridDropdown.setCurrentText(selected_grid)
    
            selected_zone = data_loaded.get('selected_zone', 'Default Zone')
            self.parent.zoneDropdown.setCurrentText(selected_zone)
    
            selected_zone_attribute = data_loaded.get('selected_zone_attribute', 'Default Zone Attribute')
            self.parent.zoneAttributeDropdown.setCurrentText(selected_zone_attribute)
    
            selected_well_zone = data_loaded.get('selected_well_zone', 'Default Well Zone')
            self.parent.WellZoneDropdown.setCurrentText(selected_well_zone)
    
            selected_well_attribute = data_loaded.get('selected_well_attribute', 'Default Well Attribute')
            self.parent.WellAttributeDropdown.setCurrentText(selected_well_attribute)
    
            grid_color_bar_dropdown = data_loaded.get('grid_color_bar_dropdown', 'Default Grid Color Bar')
            self.parent.gridColorBarDropdown.setCurrentText(grid_color_bar_dropdown)
    
            zone_attribute_color_bar_dropdown = data_loaded.get('zone_attribute_color_bar_dropdown', 'Default Zone Attribute Color Bar')
            self.parent.zoneAttributeColorBarDropdown.setCurrentText(zone_attribute_color_bar_dropdown)
    
            well_attribute_color_bar_dropdown = data_loaded.get('well_attribute_color_bar_dropdown', 'Default Well Attribute Color Bar')
            self.parent.WellAttributeColorBarDropdown.setCurrentText(well_attribute_color_bar_dropdown)


            # Re-enable signals after setting the values
            self.parent.gridDropdown.blockSignals(False)
            self.parent.zoneDropdown.blockSignals(False)
            self.parent.zoneAttributeDropdown.blockSignals(False)
            self.parent.WellZoneDropdown.blockSignals(False)
            self.parent.WellAttributeDropdown.blockSignals(False)
            self.parent.gridColorBarDropdown.blockSignals(False)
            self.parent.zoneAttributeColorBarDropdown.blockSignals(False)
            self.parent.WellAttributeColorBarDropdown.blockSignals(False)
            # Load zone viewer settings if they exist
            if 'zone_viewer_settings' in data_loaded:
                self.parent.save_zone_viewer_settings = data_loaded['zone_viewer_settings']

            # Load zone criteria if they exist
            if 'zone_criteria' in data_loaded:
                self.load_zone_criteria_df(data_loaded)

            # Load the saved column filters if they exist
            if 'column_filters' in data_loaded:
                self.parent.column_filters = data_loaded['column_filters']
                # Apply the loaded column filters as needed, possibly refreshing UI elements or data
     

            # Load selected grid and zone
            grid_selected = data_loaded.get('selected_grid', 'Select Grids')
            selected_zone = data_loaded.get('selected_zone', 'Select Zones')



            # Check if 'Grid' column exists and DataFrame is not empty before constructing KDTree
            if not self.parent.depth_grid_data_df.empty and 'Grid' in self.parent.depth_grid_data_df.columns:
                self.parent.kd_tree_depth_grids = {
                    grid: KDTree(self.parent.depth_grid_data_df[self.parent.depth_grid_data_df['Grid'] == grid][['X', 'Y']].values) 
                    for grid in self.parent.depth_grid_data_df['Grid'].unique()
                }
                print("KD-Trees for depth grids constructed.")
            else:
                print("Depth grid data is empty or 'Grid' column not found.")

            if not self.parent.attribute_grid_data_df.empty and 'Grid' in self.parent.attribute_grid_data_df.columns:
                self.parent.kd_tree_att_grids = {
                    grid: KDTree(self.parent.attribute_grid_data_df[self.parent.attribute_grid_data_df['Grid'] == grid][['X', 'Y']].values) 
                    for grid in self.parent.attribute_grid_data_df['Grid'].unique()
                }
                print("KD-Trees for attribute grids constructed.")
            else:
                print("Attribute grid data is empty or 'Grid' column not found.")

            if self.parent.depth_grid_data_df is not None and self.parent.kd_tree_depth_grids is not None:
                self.parent.depth_grid_data_dict = {
                    grid: self.parent.depth_grid_data_df[self.parent.depth_grid_data_df['Grid'] == grid]['Z'].values
                    for grid in self.parent.kd_tree_depth_grids
                }

            # Check if 'attribute_grid_data_df' and 'kd_tree_att_grids' are not None
            if self.parent.attribute_grid_data_df is not None and self.parent.kd_tree_att_grids is not None:
                self.parent.attribute_grid_data_dict = {
                    grid: self.parent.attribute_grid_data_df[self.parent.attribute_grid_data_df['Grid'] == grid]['Z'].values
                    for grid in self.parent.kd_tree_att_grids
                }


            

            self.parent.setData()

            # Populate dropdowns
            self.parent.populate_well_zone_dropdown()
            self.parent.populate_grid_dropdown(grid_selected)
            self.parent.populate_zone_dropdown(selected_zone)

            # Set the selected zone and well attribute to trigger a draw
            self.parent.zoneDropdown.setCurrentText(selected_zone)
            self.parent.zoneAttributeDropdown.setCurrentText(selected_zone_attribute)
            self.parent.WellZoneDropdown.setCurrentText(selected_well_zone)
            self.parent.WellAttributeDropdown.setCurrentText(selected_well_attribute)




            # Enable menus and update window title
            self.parent.import_menu.setEnabled(True)
            self.parent.launch_menu.setEnabled(True)
            self.parent.calculate_menu.setEnabled(True)
            file_basename = os.path.basename(file_name)
            self.parent.setWindowTitle(f"Zone Analyzer - {file_basename}")

    def load_zone_criteria_df(self, data_loaded):
        """Load the zone criteria DataFrame from the project data."""
        # Load the data into a DataFrame
        zone_criteria_df = pd.DataFrame(data_loaded.get('zone_criteria', {}))

        # Retrieve and apply the column order
        column_order = data_loaded.get('zone_criteria_columns', None)
        if column_order:
            zone_criteria_df = zone_criteria_df[column_order]
    
        self.parent.zone_criteria_df = zone_criteria_df
    