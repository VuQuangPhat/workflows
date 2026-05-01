name: NQ 171

on:
  schedule:
    # 22:30 UTC Thứ 2, Thứ 6 = 05:30 ICT Thứ 3, Thứ 7 (Asia/Ho_Chi_Minh)
    - cron: '30 22 * * 1,5'
  workflow_dispatch:
  
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
  TZ: Asia/Ho_Chi_Minh

concurrency:
  group: daily-news-report
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Checkout code
        uses: actions/checkout@v4.2.2

      - name: Set up Python
        uses: actions/setup-python@v5.4.0
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -U google-generativeai feedparser markdown pytz

      - name: Show environment info
        run: |
          echo "Running on $(date -u) UTC"
          echo "Local time: $(date)"
          echo "GitHub run number: $GITHUB_RUN_NUMBER"

      - name: Run daily_news script
        env:
          GMAIL_PASSWORD: ${{ secrets.GMAIL_PASSWORD }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GITHUB_RUN_NUMBER: ${{ github.run_number }}
        run: |
          python NQ_171.py
