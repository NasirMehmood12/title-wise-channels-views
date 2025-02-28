
import gspread
import json
import os
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

# Load Google Sheets credentials from GitHub Secrets
creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
creds_dict = json.loads(creds_json)

# Authenticate with Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open Google Sheet
spreadsheet = client.open("YouTube Data")  # Change to your sheet name
worksheet = spreadsheet.sheet1  # Select first sheet

# YouTube API setup
api_key = "AIzaSyChELxWRZooGvU7FlhOPRAdfHU3mWAffcA"
channel_id = "UC_vt34wimdCzdkrzVejwX9g"
channel_name = "Geo news"

youtube = build("youtube", "v3", developerKey=api_key)

def get_all_video_ids(channel_id):
    """Fetch all video IDs from a given channel."""
    video_ids = []
    next_page_token = None
    while True:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            order="date",
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response.get("items", []):
            video_ids.append(item["id"]["videoId"])
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return video_ids

def get_video_stats(video_ids):
    """Fetch video titles, view counts, publish date, and channel name."""
    video_data = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="statistics,snippet",
            id=",".join(video_ids[i:i+50])
        )
        response = request.execute()
        for item in response.get("items", []):
            stats = item["statistics"]
            video_data.append([
                item["snippet"]["title"],
                int(stats.get("viewCount", 0)),
                item["snippet"]["publishedAt"],
                item["snippet"]["channelTitle"]
            ])
    return video_data

# Fetch and process data
print(f"Fetching all videos for channel: {channel_name}")
video_ids = get_all_video_ids(channel_id)
video_stats = get_video_stats(video_ids)

# Sort videos by views (highest first)
video_stats.sort(key=lambda x: x[1], reverse=True)

# Keep top 100 videos
top_100_videos = video_stats[:100]

# Append to Google Sheet
worksheet.append_rows(top_100_videos)

print("✅ Data successfully appended to Google Sheets!")
