# events.py
def extract_city_from_event(event):
    """Extract the city name from a metro-level selection event."""
    if event and event.selection and event.selection.points:
        clicked_point = event.selection.points[0]
        cd = clicked_point.get("customdata", None)
        if isinstance(cd, (list, tuple)) and len(cd) > 0:
            return cd[0]
    return None

def extract_zip_from_event(event, gdf_zip=None):
    """
    Extract the ZIP code string from a ZIP-level selection event.
    Improved to handle multiple selection methods for better reliability.
    """
    if not event or not event.selection or not event.selection.points:
        return None
    
    # Try all points in the selection (in case multiple are selected)
    for clicked_point in event.selection.points:
        # Method 1: Try customdata first (most reliable)
        cd = clicked_point.get("customdata", None)
        if isinstance(cd, (list, tuple)) and len(cd) > 0:
            zip_code = str(cd[0])
            # Validate that this ZIP exists in gdf_zip
            if gdf_zip is not None:
                if (gdf_zip["zip_code_str"] == zip_code).any():
                    return zip_code
            else:
                return zip_code
        
        # Method 2: Try location (from Choroplethmapbox)
        location = clicked_point.get("location", None)
        if location is not None and gdf_zip is not None:
            match = gdf_zip[gdf_zip["id"] == str(location)]
            if not match.empty:
                return str(match.iloc[0]["zip_code_str"])
        
        # Method 3: Try point_index as last resort
        point_idx = clicked_point.get("point_index", None)
        if point_idx is not None and gdf_zip is not None and point_idx < len(gdf_zip):
            return str(gdf_zip.iloc[point_idx]["zip_code_str"])
    
    return None
