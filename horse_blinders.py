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

# Files for saving feeds and exclusion keywords
FEEDS_FILE = "feeds.txt"
EXCLUSIONS_FILE = "exclusions.txt"

# Load saved RSS feeds and exclusion words
def load_feeds_from_file():
    if os.path.exists(FEEDS_FILE):
        with open(FEEDS_FILE, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

def load_exclusions_from_file():
    if os.path.exists(EXCLUSIONS_FILE):
        with open(EXCLUSIONS_FILE, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

# Save RSS feeds and exclusion keywords to file
def save_feeds_to_file():
    with open(FEEDS_FILE, 'w') as file:
        for feed in RSS_FEEDS:
            file.write(feed + "\n")

def save_exclusions_to_file():
    with open(EXCLUSIONS_FILE, 'w') as file:
        for word in EXCLUDE_KEYWORDS:
            file.write(word + "\n")

# Initial list of RSS feed URLs and exclusion keywords
RSS_FEEDS = load_feeds_from_file()
EXCLUDE_KEYWORDS = load_exclusions_from_file()

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

            if 'media_content' in entry and len(entry.media_content) > 0:
                image = entry.media_content[0].get('url')
            elif 'links' in entry:
                for link_item in entry.links:
                    if link_item.type.startswith('image'):
                        image = link_item.href
                        break

            if not any(keyword.lower() in title.lower() for keyword in EXCLUDE_KEYWORDS):
                articles.append((title, link, image))
    
    random.shuffle(articles)
    return articles

# GUI class
def create_gui():
    class RSSViewer:
        def __init__(self, root):
            self.root = root
            self.root.title("Horse Blinders")
            self.root.geometry("1200x900")
            self.root.config(bg="#0d0d1a")

            # Title Label
            self.title_label = tk.Label(
                root,
                text="HORSE BLINDERS FEED VIEWER",
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

            # RSS Feed management section
            self.rss_entry_label = tk.Label(root, text="RSS Feed URL:", font=("Helvetica", 12), fg="#39ff14", bg="#0d0d1a")
            self.rss_entry_label.pack(pady=5)

            self.rss_entry = tk.Entry(root, font=("Helvetica", 12), width=30)
            self.rss_entry.pack(pady=5)

            self.add_rss_button = tk.Button(
                root,
                text="Add Feed",
                font=("Helvetica", 12),
                fg="#0d0d1a",
                bg="#39ff14",
                activebackground="#00ff00",
                relief="raised",
                bd=3,
                command=self.add_rss_feed
            )
            self.add_rss_button.pack(pady=5)

            self.remove_rss_button = tk.Button(
                root,
                text="Remove Feed",
                font=("Helvetica", 12),
                fg="#0d0d1a",
                bg="#ff007f",
                relief="raised",
                bd=3,
                command=self.remove_rss_feed
            )
            self.remove_rss_button.pack(pady=5)

            # Listbox for RSS feeds
            self.rss_listbox = tk.Listbox(
                root,
                height=6,
                width=50,
                font=("Helvetica", 12),
                bg="#1a1a2e",
                fg="#39ff14",
                selectmode=tk.SINGLE
            )
            self.rss_listbox.pack(pady=5)

            # Exclusion word management section
            self.exclude_entry_label = tk.Label(root, text="Exclusion Keyword:", font=("Helvetica", 12), fg="#39ff14", bg="#0d0d1a")
            self.exclude_entry_label.pack(pady=5)

            self.exclude_entry = tk.Entry(root, font=("Helvetica", 12), width=30)
            self.exclude_entry.pack(pady=5)

            self.add_exclude_button = tk.Button(
                root,
                text="Add Exclusion Word",
                font=("Helvetica", 12),
                fg="#0d0d1a",
                bg="#39ff14",
                activebackground="#00ff00",
                relief="raised",
                bd=3,
                command=self.add_exclusion_word
            )
            self.add_exclude_button.pack(pady=5)

            self.remove_exclude_button = tk.Button(
                root,
                text="Remove Exclusion Word",
                font=("Helvetica", 12),
                fg="#0d0d1a",
                bg="#ff007f",
                relief="raised",
                bd=3,
                command=self.remove_exclusion_word
            )
            self.remove_exclude_button.pack(pady=5)

            # Listbox for exclusion keywords
            self.exclude_listbox = tk.Listbox(
                root,
                height=6,
                width=50,
                font=("Helvetica", 12),
                bg="#1a1a2e",
                fg="#39ff14",
                selectmode=tk.SINGLE
            )
            self.exclude_listbox.pack(pady=5)

            self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

            # Load initial data into listboxes
            self.load_rss_feeds()
            self.load_exclude_keywords()

        def refresh(self):
            self.loading_animation()
            for widget in self.frame.winfo_children():
                widget.destroy()
            Thread(target=self.load_feeds).start()

        def loading_animation(self):
            def animate():
                dots = itertools.cycle([".", "..", "...", ""])
                for _ in range(20):
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
            webbrowser.open(bluesky_url)

        def load_rss_feeds(self):
            self.rss_listbox.delete(0, tk.END)
            for feed in RSS_FEEDS:
                self.rss_listbox.insert(tk.END, feed)

        def load_exclude_keywords(self):
            self.exclude_listbox.delete(0, tk.END)
            for keyword in EXCLUDE_KEYWORDS:
                self.exclude_listbox.insert(tk.END, keyword)

        def add_rss_feed(self):
            feed_url = self.rss_entry.get().strip()
            if feed_url and feed_url not in RSS_FEEDS:
                RSS_FEEDS.append(feed_url)
                self.rss_entry.delete(0, tk.END)
                self.load_rss_feeds()
                save_feeds_to_file()

        def remove_rss_feed(self):
            selected = self.rss_listbox.curselection()
            if selected:
                feed_url = self.rss_listbox.get(selected)
                if feed_url in RSS_FEEDS:
                    RSS_FEEDS.remove(feed_url)
                    self.load_rss_feeds()
                    save_feeds_to_file()

        def add_exclusion_word(self):
            word = self.exclude_entry.get().strip()
            if word and word not in EXCLUDE_KEYWORDS:
                EXCLUDE_KEYWORDS.append(word)
                self.exclude_entry.delete(0, tk.END)
                self.load_exclude_keywords()
                save_exclusions_to_file()

        def remove_exclusion_word(self):
            selected = self.exclude_listbox.curselection()
            if selected:
                word = self.exclude_listbox.get(selected)
                if word in EXCLUDE_KEYWORDS:
                    EXCLUDE_KEYWORDS.remove(word)
                    self.load_exclude_keywords()
                    save_exclusions_to_file()

    root = tk.Tk()
    gui = RSSViewer(root)
    gui.refresh()
    root.mainloop()

create_gui()
