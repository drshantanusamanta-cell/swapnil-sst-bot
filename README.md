# SST Tutor - ICSE Class V Social Studies

An interactive Streamlit app that helps Class V students learn Social Studies (Geography, History, Civics) using a hybrid approach combining three data sources:

1. **Wikipedia API** - Rich, encyclopedic content fetched live
2. **Open Trivia Database** - Fun quiz questions to test knowledge
3. **Web Resources** - Supplementary study links and educational videos

## Features

- 📚 **Learn Mode** - Read key concepts + deep-dive into Wikipedia content
- 🧠 **Quiz Mode** - Test your knowledge with fun trivia questions (with fallback to concept-based quizzes)
- 🔍 **Explore Mode** - Find study links and educational videos
- 📊 **Progress Tracking** - Track chapters read and quiz scores
- 🎨 **Beautiful UI** - Kid-friendly, colorful interface

## All 21 Chapters Covered

**Geography (Ch 1-10):** Motions of Earth, Latitudes & Longitudes, Weather & Climate, Temperature Zones, Climate of India, Natural Vegetation, Natural Resources, Agriculture, Industry, Natural Disasters

**History (Ch 11-17):** Material Heritage, Non-material Heritage, New Ideas in Europe, English Come to India, Freedom, Social Reformers, Sources of History

**Civics (Ch 18-21):** Constitution of India, Democratic Government, Elections, United Nations

## Local Development

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/icse-sst-tutor.git
cd icse-sst-tutor

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub account
4. Select this repository
5. Set `app.py` as the main file
6. Click **Deploy**

## Tech Stack

- **Streamlit** - Web UI framework
- **Wikipedia API** (free, no key needed) - Content source
- **Open Trivia DB API** (free, no key needed) - Quiz questions
- **Requests** - HTTP client for all API calls
- **Python 3.9+** - No external database needed

## API Sources Used (All Free, No Keys Required)

| Source | Purpose | Rate Limits |
|--------|---------|-------------|
| Wikipedia REST API | Article content & images | Generous (200 req/sec) |
| Open Trivia DB | Quiz questions | 1 req/5sec (cached) |
| Google Search | Supplementary links | Limited |

## License

MIT