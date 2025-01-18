import tkinter as tk
from tkinter import ttk
import feedparser
import requests
from PIL import Image, ImageTk
from io import BytesIO
from threading import Thread
import itertools
import os
import webbrowser
import random

# List of RSS feed URLs
RSS_FEEDS = [
    "http://rss.slashdot.org/Slashdot/slashdotMain?format=xml",
    "https://0ut3r.space/atom.xml",
    "https://www.kitploit.com//feeds/posts/default",
    "https://www.darknet.org.uk/feed",
    "https://freedomhacker.net/feed/",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "http://www.anonhack.in/feed/",
    "http://feeds.howtogeek.com/HowToGeek",
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    "https://www.theregister.com/headlines.atom",
    "https://latesthackingnews.com/feed/",
    "https://techcrunch.com/feed/",
    "https://www.vice.com/en/rss",
    "https://feeds.feedburner.com/cryptocoinsnews",
    "https://threatpost.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.zdnet.com/news/rss.xml",
    "https://www.theverge.com/rss/index.xml",
    "https://www.ufoinfo.com/feed/",
    "https://nexusnewsfeed.com/news-feed.xml",
    "https://www.wired.com/feed/rss",
]

# Keywords to filter out headlines
EXCLUDE_KEYWORDS = ["Trump", "Elon", "Musk"]

# Horse image for articles without images
DEFAULT_IMAGE_PATH = "horse.png"

# Fetch and filter RSS feeds
def fetch_feeds():
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            image = None

            # Try to find an image from the entry
            if 'media_content' in entry and len(entry.media_content) > 0:
                image = entry.media_content[0].get('url')
            elif 'links' in entry:
                for link_item in entry.links:
                    if link_item.type.startswith('image'):
                        image = link_item.href
                        break

            if not any(keyword.lower() in title.lower() for keyword in EXCLUDE_KEYWORDS):
                articles.append((title, link, image))
    
    # Shuffle articles to ensure they're mixed up from all sources
    random.shuffle(articles)
    return articles

# GUI class
def create_gui():
    class RSSViewer:
        def __init__(self, root):
            self.root = root
            self.root.title("Horse Blinders RSS Viewer")
            self.root.geometry("1200x900")
            self.root.config(bg="#0d0d1a")

            # Title Label
            self.title_label = tk.Label(
                root,
                text="Horse Blinders RSS FEED VIEWER",
                font=("Helvetica", 25, "bold"),
                fg="#39ff14",
                bg="#0d0d1a"
            )
            self.title_label.pack(pady=10)

            # Loading animation
            self.loading_label = tk.Label(
                root,
                text="",
                font=("Helvetica", 18, "bold"),
                fg="#ff007f",
                bg="#0d0d1a"
            )
            self.loading_label.pack(pady=5)

            # Canvas for news articles
            self.canvas = tk.Canvas(
                root,
                bg="#0d0d1a",
                highlightthickness=0
            )
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Scrollbar
            self.scrollbar = ttk.Scrollbar(
                root,
                orient=tk.VERTICAL,
                command=self.canvas.yview
            )
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.frame = tk.Frame(self.canvas, bg="#0d0d1a")
            self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

            # Neon-styled Refresh Button
            self.refresh_button = tk.Button(
                root,
                text="REFRESH",
                font=("Helvetica", 14, "bold"),
                fg="#0d0d1a",
                bg="#39ff14",
                activebackground="#00ff00",
                activeforeground="#0d0d1a",
                relief="raised",
                bd=3,
                command=self.refresh
            )
            self.refresh_button.pack(pady=10)

            self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        def refresh(self):
            self.loading_animation()
            for widget in self.frame.winfo_children():
                widget.destroy()
            Thread(target=self.load_feeds).start()

        def loading_animation(self):
            def animate():
                dots = itertools.cycle([".", "..", "...", ""])
                for _ in range(20):  # Run animation for 20 cycles
                    self.loading_label.config(text=f"Feeds Loading{next(dots)}")
                    self.root.update_idletasks()
                    self.root.after(200)

                self.loading_label.config(text="")

            Thread(target=animate).start()

        def load_feeds(self):
            articles = fetch_feeds()
            for title, link, image_url in articles[:50]:
                self.add_article(title, link, image_url)

        def add_article(self, title, link, image_url):
            frame = tk.Frame(self.frame, bg="#1a1a2e", pady=10, padx=10)
            frame.pack(fill=tk.X, pady=5)

            # Store the article's title and link in the frame for sharing purposes
            frame.title = title
            frame.link = link

            if image_url:
                try:
                    response = requests.get(image_url, stream=True, timeout=5)
                    image = Image.open(BytesIO(response.content))
                    image = image.resize((100, 100))
                    photo = ImageTk.PhotoImage(image)

                    img_label = tk.Label(frame, image=photo, bg="#1a1a2e")
                    img_label.image = photo  # Keep a reference to avoid garbage collection
                    img_label.pack(side=tk.LEFT, padx=5)
                except Exception:
                    image_url = None

            if not image_url:
                if os.path.exists(DEFAULT_IMAGE_PATH):
                    default_image = Image.open(DEFAULT_IMAGE_PATH).resize((100, 100))
                    photo = ImageTk.PhotoImage(default_image)

                    img_label = tk.Label(frame, image=photo, bg="#1a1a2e")
                    img_label.image = photo
                    img_label.pack(side=tk.LEFT, padx=5)

            text_frame = tk.Frame(frame, bg="#1a1a2e")
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            title_label = tk.Label(
                text_frame,
                text=title,
                font=("Helvetica", 14, "bold"),
                fg="#39ff14",
                bg="#1a1a2e",
                wraplength=600,
                justify=tk.LEFT
            )
            title_label.pack(anchor="w")

            link_label = tk.Label(
                text_frame,
                text=link,
                font=("Helvetica", 10, "italic"),
                fg="#00f9ff",
                bg="#1a1a2e",
                cursor="hand2"
            )
            link_label.pack(anchor="w")
            link_label.bind("<Button-1>", lambda e: self.open_link(link))

            # Bluesky share button for each article
            bluesky_button = tk.Button(
                frame,
                text="Share on Bluesky",
                font=("Helvetica", 10),
                fg="#1a1a2e",
                bg="#39ff14",
                relief="raised",
                bd=3,
                command=lambda: self.share_on_bluesky(title, link)
            )
            bluesky_button.pack(side=tk.RIGHT, padx=10, pady=5)

        def open_link(self, url):
            webbrowser.open(url)

        def share_on_bluesky(self, title, link):
            bluesky_url = f"https://bsky.app/intent/compose?text={title} {link}"
            webbrowser.open(bluesky_url)  # This will open the Bluesky compose post with title and link pre-filled

    root = tk.Tk()
    gui = RSSViewer(root)
    gui.refresh()
    root.mainloop()

create_gui()
