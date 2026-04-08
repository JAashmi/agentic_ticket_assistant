def generate_map_link(lat, lng):
    return f"https://www.google.com/maps?q={lat},{lng}"


def generate_navigation_link(src_lat, src_lng, dest_lat, dest_lng):
    return f"https://www.google.com/maps/dir/{src_lat},{src_lng}/{dest_lat},{dest_lng}"