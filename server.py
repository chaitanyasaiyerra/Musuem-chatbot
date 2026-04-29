import sqlite3
from mcp.server.fastmcp import FastMCP
import pandas as pd
import requests
import os
import random
import string
from datetime import datetime

# ===== Initialize MCP Server =====
mcp = FastMCP("museumchatbot")

# ===== Load Art Data from Excel =====
art_df = pd.read_excel("Unique_Museum_Art_Plan.xlsx")
art_df.columns = [col.strip().lower().replace(" ", "_") for col in art_df.columns]

print("[MCP] Loaded artwork data columns:", art_df.columns.tolist())

# ===== Setup SQLite Connection =====
DB_PATH = "app.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ===== Tool 1: Check Painting Availability =====
@mcp.tool()
def check_painting_availability(painting_name: str) -> str:
    """Check if a painting is available in the museum collection"""
    match = art_df[art_df['art_name'].str.lower() == painting_name.strip().lower()]
    if not match.empty:
        return f"✅ Yes, '{painting_name}' is available in the museum."
    return f"❌ Sorry, '{painting_name}' is not found in the museum collection."

# ===== Tool 2: Navigate to Painting (Enhanced) =====
@mcp.tool()
def navigate_to_painting(painting_name: str) -> str:
    """
    Get detailed navigation to an artwork including room, floor, and section.
    Provides step-by-step directions to locate the artwork.
    """
    match = art_df[art_df['art_name'].str.lower() == painting_name.strip().lower()]
    if not match.empty:
        room = match.iloc[0]['room_number']
        # Try to get floor and section if columns exist
        floor = match.iloc[0].get('floor_number', 'Ground Floor')
        section = match.iloc[0].get('section_name', 'Main Gallery')
        
        navigation = f"""🖼️ Navigation to '{painting_name}':

📍 Location Details:
• Floor: {floor}
• Section: {section}
• Room: {room}

🚶 Directions:
Take the main stairs to {floor}, proceed to the {section} area, and look for Room {room}. 
The artwork will be displayed on the main wall with proper lighting and description placard."""
        
        return navigation
    return f"❌ Unable to find location for '{painting_name}'."

# ===== Tool 3: Get Painting Description =====
@mcp.tool()
def painting_description(painting_name: str) -> str:
    """Get detailed description and history of a painting"""
    match = art_df[art_df['art_name'].str.lower() == painting_name.strip().lower()]
    if not match.empty:
        desc = match.iloc[0].get('description', 'No description available')
        history = match.iloc[0].get('history', 'No history available')
        return f"📜 Description of '{painting_name}':\n{desc}\n\n📚 History:\n{history}"
    return f"❌ No description found for '{painting_name}'."

# ===== Tool 4: Get Painter Info =====
@mcp.tool()
def painting_painter(painting_name: str) -> str:
    """Get information about the artist who created the painting"""
    match = art_df[art_df['art_name'].str.lower() == painting_name.strip().lower()]
    if not match.empty:
        painter_info = match.iloc[0].get('about_painter', 'No painter information available')
        return f"👨‍🎨 About the painter of '{painting_name}':\n{painter_info}"
    return f"❌ No painter information found for '{painting_name}'."

# ===== Tool 5: Get Artwork Image =====
@mcp.tool()
def get_artwork_image(painting_name: str) -> str:
    """Get image URL for an artwork"""
    match = art_df[art_df['art_name'].str.lower() == painting_name.strip().lower()]
    if not match.empty:
        # Try to get image URL from Excel
        image_url = match.iloc[0].get('image_url', None)
        if image_url and pd.notna(image_url):
            return f"🖼️ Image URL for '{painting_name}': {image_url}"
        else:
            # Return placeholder or Unsplash API URL
            return f"🖼️ Image for '{painting_name}' is available at the museum. Please visit to view."
    return f"❌ No image found for '{painting_name}'."

# ===== Tool 6: Get Complete Artwork Info =====
@mcp.tool()
def get_complete_artwork_info(painting_name: str) -> str:
    """Get comprehensive information about an artwork including all details"""
    match = art_df[art_df['art_name'].str.lower() == painting_name.strip().lower()]
    if not match.empty:
        row = match.iloc[0]
        
        info = f"""🎨 Complete Information about '{painting_name}':

📍 Location:
• Room: {row['room_number']}
• Floor: {row.get('floor_number', 'Ground Floor')}
• Section: {row.get('section_name', 'Main Gallery')}

📜 Description:
{row.get('description', 'No description available')}

📚 History:
{row.get('history', 'No history available')}

👨‍🎨 Artist:
{row.get('about_painter', 'No artist information available')}
"""
        return info
    return f"❌ No information found for '{painting_name}'."

# ===== Start MCP Server =====
if __name__ == "__main__":
    mcp.run(transport="stdio")
