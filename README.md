# 🎧 Podcli - Advanced Terminal Podcast Client

A powerful, feature-rich command-line podcast client that brings the full podcast experience to your terminal. Built with advanced search capabilities, subscription management, OPML support, and a smooth, professional interface.

## ✨ Features

- **🔍 Advanced Search & Discovery** - Multi-term search across podcast titles and descriptions
- **📚 Subscription Management** - Local subscription storage with quick toggle options
- **🎧 Premium Playback Experience** - Resume from last position with live progress tracking
- **💾 Offline Capabilities** - Download episodes for offline listening
- **📤 OPML Import/Export** - Migrate from/to other podcast apps (Pocket Casts, Overcast, etc.)
- **🖥️ Professional Interface** - Flicker-free navigation with responsive design
- **⚡ Cross-Platform** - Works on Windows, macOS, and Linux

## 🚀 Installation

### Using pipx (Recommended)
`pipx install podcli`

### Using pip
`pip install podcli==1.0.1` 
(podcli == whatever the latest version is for example 1.0.1 or 1.0.2 and so on)

## After Podcli is installed 

### Install
- `mpv` - For optimal audio playback experience
- `socat` - For live progress tracking/ To continue the episode from where you left off.

**Ubuntu/Debian:**

`sudo apt install mpv socat`

**macOS:**

`brew install mpv socat`

**Arch Linux:**

`sudo pacman -S mpv socat`

## 🛠️ System Requirements

### Required
- Python 3.7+

## 🔧 Setup

First-time setup is required to configure your free API credentials:

`podcli setup`

This will guide you through:
1. Getting free API credentials from [podcastindex.org](https://podcastindex.org/login)
2. Interactive credential validation
3. Automatic configuration file creation

## 📖 Usage

### Basic Commands

| Command | Description |
|---------|-------------|
| `podcli search "keyword"` | Search for podcasts |
| `podcli subscriptions` | Browse your subscriptions |
| `podcli export-opml` | Export subscriptions to OPML file |
| `podcli import-opml file.opml` | Import subscriptions from OPML |

### Examples

Search for podcasts
`podcli search "huberman lab"`

`podcli search "artificial intelligence"`

`podcli search "the tim ferriss show"`

Manage subscriptions
`podcli subscriptions`

OPML operations
`podcli export-opml`
`podcli import-opml my_podcasts.opml`


## ⌨️ Keyboard Shortcuts Reference

### Universal Navigation
- `↑/↓` - Navigate menus
- `Enter` - Select item
- `q` - Back/Quit

### Search & Discovery
- `(Advanced Search)` - Deep episode search within podcasts
- `(Filter by Date)` - Time-based filtering (7/30/90 days, year, all time)
- `(Sort: X)` - Cycle through sort options (Date/Duration/Title)
- `(Clear Filters)` - Reset all filters

### Subscription Management
- `(Subscribe)/(Unsubscribe)` - Toggle subscription status
- `(Show All Episodes)` - View complete episode history
- `(Show Latest Only)` - Return to recent episodes

### Playback Controls
- `s` - Decrease speed (minimum 0.5x)
- `f` - Increase speed (maximum 3.0x)
- `q` - Save position and stop playback

## 🎯 Advanced Features

### Episode Discovery
- **Advanced Search**: Search episode titles AND descriptions
- **Date Filtering**: Find episodes from specific time periods
- **Smart Sorting**: Sort by date, duration, or alphabetically

### Playback Experience
- **Resume Functionality**: Never lose your place in long episodes
- **Speed Control**: Dynamic playback speed adjustment (0.5x - 3.0x)
- **Live Progress**: Real-time progress bar with position tracking

### Data Management
- **Local Storage**: Subscriptions and history stored locally
- **OPML Support**: Easy migration to/from other podcast apps
- **Download Management**: Organized offline storage with progress bars

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## ❤️ Support 
https://buymeacoffee.com/pawantikar

