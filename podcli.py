import sys
import os
import json
import requests
import subprocess
import hashlib
import time
import re
import curses
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# --- API Configuration ---
API_KEY = os.environ.get("PODCAST_INDEX_API_KEY")
API_SECRET = os.environ.get("PODCAST_INDEX_API_SECRET")
API_URL = "https://api.podcastindex.org/api/1.0"
REQUEST_TIMEOUT = 15  # seconds

# --- File Paths ---
SUBSCRIPTIONS_FILE = "subscriptions.json"
DOWNLOADS_DIR = "downloads"
HISTORY_FILE = "history.json"
OPML_EXPORT_FILE = "podcli_subscriptions.opml"
ENV_FILE = ".env"

# --- Setup Functions ---
def display_setup_banner():
    """Display welcome banner for first-time setup."""
    print("=" * 70)
    print("🎧 WELCOME TO PODCLI - Advanced Terminal Podcast Client 🎧")
    print("=" * 70)
    print()
    print("First-time setup required! This will only take 30 seconds.")
    print()

def get_api_credentials_interactive():
    """Interactive API credentials setup with validation."""
    display_setup_banner()
    
    print("📋 STEP 1: Get Your FREE API Credentials")
    print("=" * 50)
    print("1. Visit: https://podcastindex.org/login")
    print("2. Click 'Sign Up' (completely free!)")
    print("3. After signing up, go to your dashboard")
    print("4. Copy your 'API Key' and 'API Secret'")
    print()
    print("💡 Pro tip: Keep that browser tab open while you enter credentials here!")
    print()
    
    # Get credentials with validation loop
    while True:
        print("📋 STEP 2: Enter Your Credentials")
        print("=" * 50)
        
        try:
            api_key = input("🔑 Enter your API Key: ").strip()
            if not api_key:
                print("❌ API Key cannot be empty. Please try again.\n")
                continue
                
            api_secret = input("🔐 Enter your API Secret: ").strip()
            if not api_secret:
                print("❌ API Secret cannot be empty. Please try again.\n")
                continue
            
            print("\n🔄 Testing your credentials...")
            
            # Test the credentials by making a simple API call
            if validate_api_credentials(api_key, api_secret):
                print("✅ Credentials validated successfully!")
                return api_key, api_secret
            else:
                print("❌ Invalid credentials. Please check and try again.\n")
                print("💡 Make sure you copied the API Key and Secret correctly from podcastindex.org\n")
                
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled. Run 'podcli setup' to try again.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error during setup: {e}")
            print("💡 Please try again.\n")

def validate_api_credentials(api_key, api_secret):
    """Validate API credentials by making a test request."""
    try:
        # Generate headers for test request
        epoch_time = int(time.time())
        auth_string = api_key + api_secret + str(epoch_time)
        sha1_hash = hashlib.sha1(auth_string.encode()).hexdigest()
        
        headers = {
            "X-Auth-Date": str(epoch_time),
            "X-Auth-Key": api_key,
            "Authorization": sha1_hash,
            "User-Agent": "Podcli/1.0"
        }
        
        # Make a simple test request (search for a common term)
        response = requests.get(
            f"{API_URL}/search/byterm", 
            headers=headers, 
            params={"q": "test", "max": 1},
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception:
        return False

def create_env_file(api_key, api_secret):
    """Create .env file with API credentials."""
    env_content = f"""# Podcli API Configuration
# Get your free credentials at: https://podcastindex.org/login
PODCAST_INDEX_API_KEY="{api_key}"
PODCAST_INDEX_API_SECRET="{api_secret}"
"""
    
    try:
        with open(ENV_FILE, 'w') as f:
            f.write(env_content)
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def setup_podcli():
    """Main setup function."""
    try:
        # Check if .env already exists
        if os.path.exists(ENV_FILE):
            print("⚠️  Configuration file (.env) already exists!")
            print()
            response = input("Do you want to reconfigure? (y/N): ").lower().strip()
            if response not in ['y', 'yes']:
                print("Setup cancelled. Your existing configuration is preserved.")
                return
            print()
        
        # Get credentials interactively
        api_key, api_secret = get_api_credentials_interactive()
        
        # Create .env file
        print("\n📝 Creating configuration file...")
        if create_env_file(api_key, api_secret):
            print("✅ Configuration saved successfully!")
            print()
            print("🎉 SETUP COMPLETE! 🎉")
            print("=" * 50)
            print("You can now use all podcli commands:")
            print("• podcli search 'huberman lab'")
            print("• podcli subscriptions")
            print("• podcli export-opml")
            print("• podcli import-opml file.opml")
            print()
            print("🚀 Try it now: podcli search 'your favorite podcast'")
            print()
        else:
            print("❌ Failed to save configuration. Please run 'podcli setup' again.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please run 'podcli setup' to try again.")
        sys.exit(1)

def check_api_setup():
    """Check if API credentials are properly configured."""
    # Try to load from environment
    load_dotenv()
    api_key = os.environ.get("PODCAST_INDEX_API_KEY")
    api_secret = os.environ.get("PODCAST_INDEX_API_SECRET")
    
    if not api_key or not api_secret:
        return False
    
    # Basic validation (non-empty and reasonable length)
    if len(api_key.strip()) < 10 or len(api_secret.strip()) < 10:
        return False
        
    return True

# --- Helper Functions ---
def get_api_headers():
    """Generates the necessary headers for API requests."""
    if not API_KEY or not API_SECRET:
        raise Exception("API credentials not configured. Run 'podcli setup' first.")
    
    epoch_time = int(time.time())
    auth_string = API_KEY + API_SECRET + str(epoch_time)
    sha1_hash = hashlib.sha1(auth_string.encode()).hexdigest()
    return {
        "X-Auth-Date": str(epoch_time),
        "X-Auth-Key": API_KEY,
        "Authorization": sha1_hash,
        "User-Agent": "Podcli/1.0"
    }

def handle_api_error(response):
    """Raises an exception if the API request was not successful."""
    if response.status_code != 200:
        error_info = {
            "status_code": response.status_code,
            "response": response.json() if response.content else "No content"
        }
        raise Exception(f"APIError: {json.dumps(error_info)}")

def sanitize_filename(filename):
    """Removes invalid characters from a filename."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def format_duration(seconds):
    """Convert seconds to human readable duration."""
    if not seconds:
        return "Unknown"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, _ = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

def format_date(timestamp):
    """Convert timestamp to readable date."""
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "Unknown"

# --- OPML Functions ---
def export_subscriptions_to_opml():
    """Export subscriptions to OPML format."""
    subscriptions = get_subscriptions()
    if not subscriptions:
        print("No subscriptions to export.")
        return
    
    print("Fetching podcast details for OPML export...")
    podcasts = get_podcasts_by_ids(subscriptions)
    
    # Create OPML structure
    opml = ET.Element("opml", version="1.0")
    head = ET.SubElement(opml, "head")
    ET.SubElement(head, "title").text = "Podcli Subscriptions"
    ET.SubElement(head, "dateCreated").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    body = ET.SubElement(opml, "body")
    
    for podcast in podcasts:
        outline = ET.SubElement(body, "outline", 
                               type="rss",
                               text=podcast.get('title', 'Unknown'),
                               title=podcast.get('title', 'Unknown'),
                               xmlUrl=podcast.get('url', ''),
                               htmlUrl=podcast.get('link', ''))
        if podcast.get('description'):
            outline.set('description', podcast['description'][:200])
    
    # Write to file
    tree = ET.ElementTree(opml)
    ET.indent(tree, space="  ")
    tree.write(OPML_EXPORT_FILE, xml_declaration=True, encoding='utf-8')
    print(f"Subscriptions exported to {OPML_EXPORT_FILE}")

def import_subscriptions_from_opml(opml_file):
    """Import subscriptions from OPML file."""
    if not os.path.exists(opml_file):
        print(f"OPML file not found: {opml_file}")
        return
    
    try:
        tree = ET.parse(opml_file)
        root = tree.getroot()
        
        imported_feeds = []
        for outline in root.findall(".//outline[@type='rss']"):
            xml_url = outline.get('xmlUrl')
            if xml_url:
                imported_feeds.append(xml_url)
        
        if not imported_feeds:
            print("No RSS feeds found in OPML file.")
            return
        
        print(f"Found {len(imported_feeds)} feeds in OPML file.")
        print("Searching for matching podcasts...")
        
        # Search for each feed URL to get podcast IDs
        current_subs = get_subscriptions()
        new_subs = 0
        
        for feed_url in imported_feeds:
            try:
                headers = get_api_headers()
                response = requests.get(f"{API_URL}/podcasts/byfeedurl", 
                                      headers=headers, 
                                      params={"url": feed_url}, 
                                      timeout=REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    feed_data = response.json().get("feed")
                    if feed_data and str(feed_data['id']) not in current_subs:
                        update_subscription(feed_data['id'], subscribe=True)
                        new_subs += 1
                        print(f"Added: {feed_data.get('title', 'Unknown')}")
                
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Error processing feed {feed_url}: {e}")
                continue
        
        print(f"Import complete. Added {new_subs} new subscriptions.")
        
    except ET.ParseError:
        print("Invalid OPML file format.")
    except Exception as e:
        print(f"Error importing OPML: {e}")

# --- Playback History ---
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

# --- Core Functions ---
def search_podcasts(keyword):
    headers = get_api_headers()
    params = {"q": keyword}
    response = requests.get(f"{API_URL}/search/byterm", headers=headers, params=params, timeout=REQUEST_TIMEOUT)
    handle_api_error(response)
    return response.json().get("feeds", [])

def get_podcasts_by_ids(podcast_ids):
    """Fetches details for multiple podcasts efficiently."""
    valid_ids = sorted(list(set([str(pid) for pid in podcast_ids if str(pid).strip()])))
    if not valid_ids:
        return []
    
    podcasts = []
    headers = get_api_headers()
    
    # Try batch request first
    try:
        data = {'ids': ",".join(valid_ids)}
        response = requests.post(f"{API_URL}/podcasts/byfeedid", 
                               headers=headers, 
                               data=data, 
                               timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            feeds = response.json().get("feeds", [])
            if feeds:
                return feeds
    except:
        pass  # Fall back to individual requests
    
    # Individual requests fallback
    for pid in valid_ids:
        try:
            response = requests.get(f"{API_URL}/podcasts/byfeedid", 
                                  headers=headers, 
                                  params={"id": pid}, 
                                  timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                feed_data = response.json().get("feed")
                if feed_data:
                    podcasts.append(feed_data)
        except Exception:
            continue
    
    return podcasts

def get_episodes(podcast_id):
    headers = get_api_headers()
    params = {"id": podcast_id, "max": 1000}  # Reduced for better performance
    response = requests.get(f"{API_URL}/episodes/byfeedid", headers=headers, params=params, timeout=REQUEST_TIMEOUT)
    handle_api_error(response)
    return response.json().get("items", [])

def filter_episodes(episodes, search_term="", date_range=None, sort_by="date"):
    """Filter and sort episodes based on criteria."""
    filtered = episodes
    
    # Search filter (title + description)
    if search_term:
        search_lower = search_term.lower()
        filtered = []
        for episode in episodes:
            title_match = search_lower in episode.get('title', '').lower()
            desc_match = search_lower in episode.get('description', '').lower()
            if title_match or desc_match:
                filtered.append(episode)
    
    # Date range filter
    if date_range:
        start_date, end_date = date_range
        date_filtered = []
        for episode in filtered:
            episode_date = episode.get('datePublished', 0)
            if start_date <= episode_date <= end_date:
                date_filtered.append(episode)
        filtered = date_filtered
    
    # Sort episodes
    if sort_by == "date":
        filtered.sort(key=lambda x: x.get('datePublished', 0), reverse=True)
    elif sort_by == "duration":
        filtered.sort(key=lambda x: x.get('duration', 0), reverse=True)
    elif sort_by == "title":
        filtered.sort(key=lambda x: x.get('title', '').lower())
    
    return filtered

def play_episode(stdscr, episode, podcast, speed=1.0, player="mpv"):
    audio_url = episode.get("enclosureUrl")
    if not audio_url:
        curses.flash()
        return

    history = load_history()
    episode_id = str(episode['id'])
    start_time = history.get(episode_id, {}).get('position', 0)
    socket_path = f"/tmp/podcli_mpvsocket_{os.getpid()}"

    try:
        if player == "vlc":
            args = ["vlc", "-I", "dummy", f"--rate={speed}", f"--start-time={start_time}", audio_url]
            player_process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            stdscr.nodelay(True)
            
            while True:
                stdscr.clear()
                h, w = stdscr.getmaxyx()
                stdscr.addstr(0, 0, f"Playing: {episode['title']}"[:w-1])
                stdscr.addstr(2, 0, "VLC playback does not support live progress.")
                stdscr.addstr(4, 0, "Press 'q' to stop playback.")
                stdscr.refresh()
                
                if player_process.poll() is not None: 
                    break
                if stdscr.getch() == ord('q'):
                    player_process.terminate()
                    break
                time.sleep(0.1)
            return

        # MPV specific playback with IPC - FIXED VERSION
        args = ["mpv", f"--speed={speed}", f"--start={start_time}", audio_url, f"--input-ipc-server={socket_path}"]
        player_process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        stdscr.nodelay(True)
        current_speed = speed
        
        # Initial screen setup - draw static elements once
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        stdscr.addstr(0, 0, f"Playing: {episode['title']}"[:w-1])
        stdscr.addstr(2, 0, f"Speed: {current_speed:.2f}x ([s]lower, [f]aster)")
        stdscr.addstr(3, 0, "Press 'q' to stop playback.")
        stdscr.refresh()
        
        while True:
            try:
                if os.path.exists(socket_path):
                    position_cmd = f"echo '{{ \"command\": [\"get_property\", \"playback-time\"] }}' | socat - {socket_path}"
                    position_output = subprocess.check_output(position_cmd, shell=True, stderr=subprocess.PIPE).decode('utf-8')
                    position_data = json.loads(position_output)
                    position = position_data.get('data', 0) or 0
                    
                    duration_cmd = f"echo '{{ \"command\": [\"get_property\", \"duration\"] }}' | socat - {socket_path}"
                    duration_output = subprocess.check_output(duration_cmd, shell=True, stderr=subprocess.PIPE).decode('utf-8')
                    duration_data = json.loads(duration_output)
                    duration = duration_data.get('data', 1) or 1
                    
                    progress = position / duration
                    bar_width = w - 2
                    filled_width = int(bar_width * progress)
                    progress_bar = '[' + '#' * filled_width + '-' * (bar_width - filled_width) + ']'
                    
                    # Only update the progress bar line - no screen clear!
                    stdscr.addstr(1, 0, progress_bar.ljust(w-1))
                else:
                    # Only update the progress line when loading
                    stdscr.addstr(1, 0, "[Loading...]".ljust(w-1))
            except:
                # Only update the progress line on error
                stdscr.addstr(1, 0, "(Could not get playback status)".ljust(w-1))
            
            stdscr.refresh()
            
            if player_process.poll() is not None:
                history[episode_id] = {'position': 0}
                save_history(history)
                break
            
            key = stdscr.getch()
            if key == ord('q'):
                try:
                    if os.path.exists(socket_path):
                        position_cmd = f"echo '{{ \"command\": [\"get_property\", \"playback-time\"] }}' | socat - {socket_path}"
                        position_output = subprocess.check_output(position_cmd, shell=True, stderr=subprocess.PIPE).decode('utf-8')
                        position_data = json.loads(position_output)
                        current_position = position_data.get('data', 0) or 0
                        history[episode_id] = {'position': current_position}
                        save_history(history)
                except:
                    pass
                
                player_process.terminate()
                try:
                    player_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    player_process.kill()
                break
            elif key == ord('s'):
                current_speed = max(0.5, current_speed - 0.25)
                subprocess.run(f"echo '{{ \"command\": [\"set_property\", \"speed\", {current_speed}] }}' | socat - {socket_path}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Update speed display
                stdscr.addstr(2, 0, f"Speed: {current_speed:.2f}x ([s]lower, [f]aster)".ljust(w-1))
            elif key == ord('f'):
                current_speed = min(3.0, current_speed + 0.25)
                subprocess.run(f"echo '{{ \"command\": [\"set_property\", \"speed\", {current_speed}] }}' | socat - {socket_path}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Update speed display
                stdscr.addstr(2, 0, f"Speed: {current_speed:.2f}x ([s]lower, [f]aster)".ljust(w-1))
            
            time.sleep(0.1)
            
    except FileNotFoundError:
        stdscr.clear()
        stdscr.addstr(0, 0, f'Error: Could not find "{player}". Please install it.')
        stdscr.addstr(2, 0, "Press any key to continue.")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
    finally:
        stdscr.nodelay(False)
        if os.path.exists(socket_path):
            os.remove(socket_path)

def download_episode(stdscr, episode, podcast_title):
    curses.endwin()
    audio_url = episode.get("enclosureUrl")
    if not audio_url:
        print("Could not find audio URL for this episode.")
        input("Press Enter to continue.")
        return

    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    title = sanitize_filename(episode['title'])
    sanitized_podcast_title = sanitize_filename(podcast_title)
    filename = f"{sanitized_podcast_title} - {title}.mp3"
    filepath = os.path.join(DOWNLOADS_DIR, filename)

    print(f"Downloading: {filename}")
    try:
        with requests.get(audio_url, stream=True, timeout=REQUEST_TIMEOUT) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            with open(filepath, 'wb') as f, tqdm(
                desc=title, total=total_size, unit='iB',
                unit_scale=True, unit_divisor=1024,
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    bar.update(size)

        print(f"\nSuccessfully downloaded to: {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"\nError downloading episode: {e}")
    
    input("Press Enter to continue.")
    stdscr.clear()
    stdscr.refresh()

def get_subscriptions():
    try:
        with open(SUBSCRIPTIONS_FILE, "r") as f:
            subscriptions = json.load(f)
        return sorted(list(set([str(pid) for pid in subscriptions if str(pid).strip()])))
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def update_subscription(podcast_id, subscribe=True):
    subscriptions = get_subscriptions()
    podcast_id_str = str(podcast_id)
    
    if subscribe:
        if podcast_id_str not in subscriptions:
            subscriptions.append(podcast_id_str)
    else:
        if podcast_id_str in subscriptions:
            subscriptions.remove(podcast_id_str)
    
    with open(SUBSCRIPTIONS_FILE, "w") as f:
        json.dump(subscriptions, f, indent=4)

# --- Enhanced UI Functions ---
def get_date_range_input(stdscr):
    """Get date range input from user."""
    h, w = stdscr.getmaxyx()
    
    # Default to last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    options = [
        "Last 7 days",
        "Last 30 days", 
        "Last 90 days",
        "Last year",
        "All time",
        "Custom range"
    ]
    
    selection = interactive_menu(stdscr, options, "--- Select Date Range ---")
    
    if selection == -1 or selection == 4:  # All time or quit
        return None
    elif selection == 0:  # Last 7 days
        start_timestamp = int((end_date - timedelta(days=7)).timestamp())
        end_timestamp = int(end_date.timestamp())
    elif selection == 1:  # Last 30 days
        start_timestamp = int((end_date - timedelta(days=30)).timestamp())
        end_timestamp = int(end_date.timestamp())
    elif selection == 2:  # Last 90 days
        start_timestamp = int((end_date - timedelta(days=90)).timestamp())
        end_timestamp = int(end_date.timestamp())
    elif selection == 3:  # Last year
        start_timestamp = int((end_date - timedelta(days=365)).timestamp())
        end_timestamp = int(end_date.timestamp())
    else:  # Custom range - simplified to last 30 days
        start_timestamp = int((end_date - timedelta(days=30)).timestamp())
        end_timestamp = int(end_date.timestamp())
    
    return (start_timestamp, end_timestamp)

def interactive_menu(stdscr, items, title):
    """Ultra-smooth interactive menu with zero flickering and boundary protection."""
    if not items:
        stdscr.clear()
        stdscr.addstr(0, 0, "No items to display")
        stdscr.addstr(2, 0, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return -1
    
    current_row_idx = 0
    top_row_idx = 0
    curses.curs_set(0)
    
    # Get screen dimensions with safety margin
    h, w = stdscr.getmaxyx()
    display_height = max(1, h - 3)  # Ensure at least 1 line
    
    # Initial full render with bounds checking
    try:
        stdscr.clear()
        if h > 0 and w > 1:
            stdscr.addstr(0, 0, title[:w-1], curses.A_BOLD)
        
        # Draw all visible items initially with bounds checking
        for i in range(display_height):
            item_idx = top_row_idx + i
            if item_idx >= len(items):
                break
                
            item_text = items[item_idx][:max(1, w-1)]
            display_y = i + 2
            
            # Ensure we don't write outside screen boundaries
            if display_y >= h - 1:
                break
                
            try:
                if item_idx == current_row_idx:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(display_y, 0, item_text.ljust(min(len(item_text) + 1, w-1)))
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(display_y, 0, item_text)
            except curses.error:
                # Skip this line if it causes boundary issues
                continue
        
        # Draw initial scroll indicator with bounds checking
        if len(items) > display_height and h > 1:
            scroll_msg = f"({current_row_idx + 1}/{len(items)})"
            if len(scroll_msg) < w - 2:
                try:
                    stdscr.addstr(h - 1, w - len(scroll_msg) - 2, scroll_msg)
                except curses.error:
                    pass  # Skip if it would cause boundary issues
        
        stdscr.refresh()
    except curses.error:
        # If initial render fails, try a simpler approach
        stdscr.clear()
        stdscr.addstr(0, 0, "Loading...")
        stdscr.refresh()

    while True:
        try:
            key = stdscr.getch()
            
            if key == curses.KEY_UP:
                # Store old position
                old_current = current_row_idx
                old_top = top_row_idx
                
                # Update position with proper wrap-around
                current_row_idx = (current_row_idx - 1) % len(items)
                
                # Adjust scroll if needed - handle wrap-around case
                if current_row_idx < top_row_idx or (old_current == 0 and current_row_idx == len(items) - 1):
                    # Handle wrap from first to last item
                    if old_current == 0 and current_row_idx == len(items) - 1:
                        top_row_idx = max(0, len(items) - display_height)
                    else:
                        top_row_idx = current_row_idx
                
                # Efficient update with bounds checking
                if old_top != top_row_idx:
                    # Scroll happened - redraw all visible items safely
                    for i in range(display_height):
                        item_idx = top_row_idx + i
                        display_y = i + 2
                        
                        # Bounds checking
                        if display_y >= h - 1:
                            break
                            
                        try:
                            if item_idx >= len(items):
                                stdscr.addstr(display_y, 0, " " * min(w-1, 50))  # Clear empty lines
                                continue
                                
                            item_text = items[item_idx][:max(1, w-1)]
                            
                            if item_idx == current_row_idx:
                                stdscr.attron(curses.A_REVERSE)
                                stdscr.addstr(display_y, 0, item_text.ljust(min(len(item_text) + 1, w-1)))
                                stdscr.attroff(curses.A_REVERSE)
                            else:
                                stdscr.addstr(display_y, 0, item_text)
                        except curses.error:
                            continue  # Skip problematic lines
                else:
                    # No scroll - just update the two affected lines safely
                    try:
                        # Remove highlight from old position
                        old_display_y = (old_current - top_row_idx) + 2
                        if 0 <= old_display_y < h-1 and old_current < len(items):
                            old_item_text = items[old_current][:max(1, w-1)]
                            stdscr.addstr(old_display_y, 0, old_item_text.ljust(min(len(old_item_text) + 1, w-1)))
                        
                        # Add highlight to new position
                        new_display_y = (current_row_idx - top_row_idx) + 2
                        if 0 <= new_display_y < h-1 and current_row_idx < len(items):
                            new_item_text = items[current_row_idx][:max(1, w-1)]
                            stdscr.attron(curses.A_REVERSE)
                            stdscr.addstr(new_display_y, 0, new_item_text.ljust(min(len(new_item_text) + 1, w-1)))
                            stdscr.attroff(curses.A_REVERSE)
                    except curses.error:
                        # If selective update fails, do a full redraw
                        try:
                            stdscr.clear()
                            if h > 0 and w > 1:
                                stdscr.addstr(0, 0, title[:w-1], curses.A_BOLD)
                            # Redraw visible items
                            for i in range(min(display_height, len(items))):
                                item_idx = top_row_idx + i
                                if item_idx >= len(items) or i + 2 >= h - 1:
                                    break
                                item_text = items[item_idx][:max(1, w-1)]
                                if item_idx == current_row_idx:
                                    stdscr.attron(curses.A_REVERSE)
                                    stdscr.addstr(i + 2, 0, item_text.ljust(min(len(item_text) + 1, w-1)))
                                    stdscr.attroff(curses.A_REVERSE)
                                else:
                                    stdscr.addstr(i + 2, 0, item_text)
                        except curses.error:
                            pass  # Give up on this update
                
            elif key == curses.KEY_DOWN:
                # Store old position
                old_current = current_row_idx
                old_top = top_row_idx
                
                # Update position with proper wrap-around
                current_row_idx = (current_row_idx + 1) % len(items)
                
                # Adjust scroll if needed - handle wrap-around case
                if current_row_idx >= top_row_idx + display_height or (old_current == len(items) - 1 and current_row_idx == 0):
                    # Handle wrap from last to first item
                    if old_current == len(items) - 1 and current_row_idx == 0:
                        top_row_idx = 0
                    else:
                        top_row_idx = current_row_idx - display_height + 1
                
                # Same bounds-checked update logic as UP key
                if old_top != top_row_idx:
                    # Scroll happened - redraw all visible items safely
                    for i in range(display_height):
                        item_idx = top_row_idx + i
                        display_y = i + 2
                        
                        # Bounds checking
                        if display_y >= h - 1:
                            break
                            
                        try:
                            if item_idx >= len(items):
                                stdscr.addstr(display_y, 0, " " * min(w-1, 50))  # Clear empty lines
                                continue
                                
                            item_text = items[item_idx][:max(1, w-1)]
                            
                            if item_idx == current_row_idx:
                                stdscr.attron(curses.A_REVERSE)
                                stdscr.addstr(display_y, 0, item_text.ljust(min(len(item_text) + 1, w-1)))
                                stdscr.attroff(curses.A_REVERSE)
                            else:
                                stdscr.addstr(display_y, 0, item_text)
                        except curses.error:
                            continue  # Skip problematic lines
                else:
                    # No scroll - just update the two affected lines safely
                    try:
                        # Remove highlight from old position
                        old_display_y = (old_current - top_row_idx) + 2
                        if 0 <= old_display_y < h-1 and old_current < len(items):
                            old_item_text = items[old_current][:max(1, w-1)]
                            stdscr.addstr(old_display_y, 0, old_item_text.ljust(min(len(old_item_text) + 1, w-1)))
                        
                        # Add highlight to new position
                        new_display_y = (current_row_idx - top_row_idx) + 2
                        if 0 <= new_display_y < h-1 and current_row_idx < len(items):
                            new_item_text = items[current_row_idx][:max(1, w-1)]
                            stdscr.attron(curses.A_REVERSE)
                            stdscr.addstr(new_display_y, 0, new_item_text.ljust(min(len(new_item_text) + 1, w-1)))
                            stdscr.attroff(curses.A_REVERSE)
                    except curses.error:
                        # If selective update fails, do a full redraw
                        try:
                            stdscr.clear()
                            if h > 0 and w > 1:
                                stdscr.addstr(0, 0, title[:w-1], curses.A_BOLD)
                            # Redraw visible items
                            for i in range(min(display_height, len(items))):
                                item_idx = top_row_idx + i
                                if item_idx >= len(items) or i + 2 >= h - 1:
                                    break
                                item_text = items[item_idx][:max(1, w-1)]
                                if item_idx == current_row_idx:
                                    stdscr.attron(curses.A_REVERSE)
                                    stdscr.addstr(i + 2, 0, item_text.ljust(min(len(item_text) + 1, w-1)))
                                    stdscr.attroff(curses.A_REVERSE)
                                else:
                                    stdscr.addstr(i + 2, 0, item_text)
                        except curses.error:
                            pass  # Give up on this update
            
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return current_row_idx
            elif key == ord('q'):
                return -1
            else:
                continue  # Ignore other keys
            
            # Update scroll indicator safely
            if len(items) > display_height and h > 1:
                scroll_msg = f"({current_row_idx + 1}/{len(items)})"
                if len(scroll_msg) < w - 2:
                    try:
                        # Clear old scroll indicator area
                        stdscr.addstr(h - 1, max(0, w - 20), " " * min(20, w-1))
                        stdscr.addstr(h - 1, w - len(scroll_msg) - 2, scroll_msg)
                    except curses.error:
                        pass  # Skip scroll indicator if it causes issues
            
            # Single refresh call for all updates
            stdscr.refresh()
            
        except curses.error:
            # If any curses operation fails, try to recover
            try:
                stdscr.refresh()
            except:
                pass
            continue
        except Exception as e:
            # Log other errors but don't crash
            continue

def display_episodes_interactive(stdscr, podcast):
    """Enhanced episode display with CLEAN visual separation and no overlapping."""
    podcast_id = podcast['id']
    podcast_title = podcast['title']
    
    stdscr.clear()
    stdscr.addstr(0, 0, "Loading episodes...")
    stdscr.refresh()
    
    episodes = get_episodes(podcast_id)
    show_all = False
    search_term = ""
    date_range = None
    sort_by = "date"

    while True:
        subscriptions = get_subscriptions()
        is_subscribed = str(podcast_id) in subscriptions

        # Apply filters
        filtered_episodes = filter_episodes(episodes, search_term, date_range, sort_by)
        
        if search_term:
            episodes_to_display = filtered_episodes
            title = f"--- Search: '{search_term}' in {podcast_title} ---"
        elif show_all:
            episodes_to_display = filtered_episodes
            title = f"--- All Episodes: {podcast_title} (Sort: {sort_by.title()}) ---"
        else:
            episodes_to_display = filtered_episodes[:20]  # Show top 20 filtered
            title = f"--- Latest Episodes: {podcast_title} ---"

        # Build formatted menu items with proper table formatting
        menu_items = []
        
        # Calculate terminal width for proper column sizing
        h, w = stdscr.getmaxyx()
        
        # Column widths: Title takes most space, duration and date get fixed width
        duration_width = 12  # e.g., "(45m)      "
        date_width = 12     # e.g., "2025-01-15 "
        title_width = w - duration_width - date_width - 4  # Leave some padding
        
        for episode in episodes_to_display:
            duration = format_duration(episode.get('duration', 0))
            date = format_date(episode.get('datePublished', 0))
            
            # Truncate and pad episode title to fit column width
            episode_title = episode['title']
            if len(episode_title) > title_width:
                episode_title = episode_title[:title_width-3] + "..."
            
            # Format as table with proper column alignment
            formatted_item = f"{episode_title:<{title_width}} ({duration:>8}) {date:>12}"
            menu_items.append(formatted_item)
        
        # ADD CLEAR VISUAL SEPARATION - This fixes the UI problem!
        if menu_items:  # Only add separator if there are episodes
            # Add empty line for spacing
            menu_items.append("")
            # Add visual separator line
            separator_line = "─" * min(w-4, 80)  # Horizontal line
            menu_items.append(separator_line)
            # Add another empty line for clean spacing
            menu_items.append("")
        
        # CLEANER CONTROL OPTIONS with proper spacing
        if show_all:
            # When browsing all episodes, keep it simple and clean
            menu_items.append("↵ Back to Latest Episodes")
        else:
            # Regular episode view with all options, properly spaced
            if len(filtered_episodes) > 20:
                menu_items.append("📄 Browse All Episodes")
                
            menu_items.extend([
                "🔍 Advanced Search",
                "📅 Filter by Date", 
                f"🔄 Sort: {sort_by.title()}",
                "🧹 Clear Filters" if (search_term or date_range) else None,
                "❌ Unsubscribe" if is_subscribed else "➕ Subscribe"
            ])
            # Remove None items
            menu_items = [item for item in menu_items if item is not None]

        selection_index = interactive_menu(stdscr, menu_items, title)

        if selection_index == -1:  # User quit
            break

        selected_item_text = menu_items[selection_index]

        # Handle separator lines and empty lines - skip them
        if selected_item_text == "" or "─" in selected_item_text:
            continue

        if selected_item_text == "📄 Browse All Episodes":
            show_all = True
            continue
        elif selected_item_text == "↵ Back to Latest Episodes":
            show_all = False
            continue
        elif selected_item_text == "🔍 Advanced Search":
            h, w = stdscr.getmaxyx()
            stdscr.addstr(h - 1, 0, "Search (title/description): ")
            curses.echo()
            search_term = stdscr.getstr(h - 1, 28, w - 29).decode("utf-8")
            curses.noecho()
            continue
        elif selected_item_text == "📅 Filter by Date":
            date_range = get_date_range_input(stdscr)
            continue
        elif selected_item_text.startswith("🔄 Sort:"):
            sort_options = ["date", "duration", "title"]
            current_idx = sort_options.index(sort_by)
            sort_by = sort_options[(current_idx + 1) % len(sort_options)]
            continue
        elif selected_item_text == "🧹 Clear Filters":
            search_term = ""
            date_range = None
            continue
        elif selected_item_text == "➕ Subscribe":
            update_subscription(podcast_id, subscribe=True)
            continue
        elif selected_item_text == "❌ Unsubscribe":
            update_subscription(podcast_id, subscribe=False)
            continue

        # Handle episode selection - make sure we're selecting an actual episode
        episode_count = len(episodes_to_display)
        if selection_index < episode_count:
            selected_episode = episodes_to_display[selection_index]
            action_index = interactive_menu(stdscr, ["Play", "Download", "Back"], 
                                          f"Action for: {selected_episode['title'][:50]}...")

            if action_index == 0:  # Play
                play_episode(stdscr, selected_episode, podcast)
            elif action_index == 1:  # Download
                download_episode(stdscr, selected_episode, podcast_title)
            elif action_index == 2 or action_index == -1:  # Back
                continue

def main_curses_app(stdscr, initial_podcasts, title):
    curses.use_default_colors()
    stdscr.clear()
    podcasts = initial_podcasts

    while True:
        if not podcasts:
            stdscr.addstr(0, 0, "Nothing to display.")
            stdscr.addstr(2, 0, "Press any key to exit.")
            stdscr.getch()
            return

        podcast_titles = [p['title'] for p in podcasts]
        selected_index = interactive_menu(stdscr, podcast_titles, title)

        if selected_index == -1:
            break

        selected_podcast = podcasts[selected_index]
        display_episodes_interactive(stdscr, selected_podcast)

# --- Main Execution ---
def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    # Handle setup command first (before checking API credentials)
    if command == "setup":
        setup_podcli()
        return

    # Check if API credentials are configured
    if not check_api_setup():
        print("🚨 API credentials not configured!")
        print()
        print("🎧 Welcome to podcli! First-time setup required.")
        print("This will only take 30 seconds and is completely free.")
        print()
        response = input("Start setup now? (Y/n): ").lower().strip()
        if response in ['', 'y', 'yes']:
            setup_podcli()
            return
        else:
            print("Setup cancelled. Run 'podcli setup' when you're ready!")
            return

    # Show usage if no command provided
    if not command:
        print("Usage: python podcli.py [command] [options]")
        print("Commands:")
        print("  setup                 - Configure API credentials")
        print("  search [keyword]      - Search for podcasts")
        print("  subscriptions         - Browse subscriptions")
        print("  export-opml          - Export subscriptions to OPML")
        print("  import-opml [file]   - Import subscriptions from OPML")
        return

    try:
        if command == "search":
            if not args:
                print("Please provide a search term.")
                print("Usage: python podcli.py search 'huberman lab'")
                return
                
            def search_app(stdscr):
                keyword = " ".join(args)
                stdscr.addstr(0, 0, f"Searching for '{keyword}'...")
                stdscr.refresh()
                podcasts = search_podcasts(keyword)
                main_curses_app(stdscr, podcasts, "--- Podcast Search Results ---")
            curses.wrapper(search_app)

        elif command == "subscriptions":
            def subscriptions_app(stdscr):
                try:
                    sub_ids = get_subscriptions()
                    if not sub_ids:
                        stdscr.addstr(0, 0, "You have no subscriptions.")
                        stdscr.addstr(2, 0, "Press any key to exit.")
                        stdscr.getch()
                        return

                    stdscr.addstr(0, 0, "Loading subscriptions...")
                    stdscr.refresh()
                    
                    try:
                        podcasts = get_podcasts_by_ids(sub_ids)
                    except Exception as e:
                        stdscr.addstr(2, 0, f"API call failed: {str(e)}")
                        stdscr.addstr(4, 0, "Press any key to exit.")
                        stdscr.getch()
                        return
                    
                    if not podcasts:
                        stdscr.addstr(2, 0, "Could not find any podcasts matching your subscribed IDs.")
                        stdscr.addstr(4, 0, "Press any key to exit.")
                        stdscr.getch()
                        return

                    main_curses_app(stdscr, podcasts, "--- Your Subscriptions ---")
                    
                except Exception as e:
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"Unexpected error: {str(e)}")
                    stdscr.addstr(2, 0, "Press any key to exit.")
                    stdscr.getch()
            curses.wrapper(subscriptions_app)

        elif command == "export-opml":
            export_subscriptions_to_opml()

        elif command == "import-opml":
            if not args:
                print("Please specify OPML file path.")
                print("Usage: python podcli.py import-opml [file.opml]")
                return
            import_subscriptions_from_opml(args[0])

        else:
            print(f"Invalid command: {command}")
            print("Valid commands: setup, search, subscriptions, export-opml, import-opml")

    except Exception as e:
        if "API credentials not configured" in str(e):
            print("🚨 API credentials error. Please run 'podcli setup' to reconfigure.")
        elif "APIError" not in str(e):
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
