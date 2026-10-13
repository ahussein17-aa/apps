#!/usr/bin/env python3
"""Builds the Yalla Designs marketing pages.

  python3 build.py

Writes the hub page next to this file, rebuilds the Ayah, Daily Dhikr and
Dawah Companion pages in their repos, and patches the store buttons and the
"More apps" section into the Sahaba and 99 Names pages.

When a store link goes live, flip the flag in APPS below and run again.
"""
import html
import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent          # ~/Desktop/iOS Apps
HUB = Path(__file__).resolve().parent
SHOTS = ROOT / "Play-uploads" / "screenshots"
ICONS = [ROOT / "Sahaba/android/app/src/main/res/drawable-nodpi",
         ROOT / "Ayah/android/app/src/main/res/drawable-nodpi"]

HUB_URL = "https://ahussein17-aa.github.io/apps/"

APPS = {
    "sahaba": dict(
        name="Sahaba", full="Sahaba: Lives of Companions",
        tagline="The lives of the Companions, told simply.",
        blurb="Sixty companions of the Prophet ﷺ, each told as a full story, with reflections, collections and home screen widgets.",
        site=ROOT / "Sahaba/docs/site", url="https://ahussein17-aa.github.io/sahaba-site/",
        ios="6779983950", ios_live=True, pkg="com.yalladesigns.sahaba", play_live=False, shots="Sahaba"),
    "dailydhikr": dict(
        name="Daily Dhikr", full="Daily Dhikr: Adhkar & Tasbih",
        tagline="Morning, evening and sleep adhkar, with a daily streak.",
        blurb="More than 100 authentic adhkar, a tap counter, gentle reminders and a streak to keep you going.",
        site=ROOT / "Daily_Dhikr_App/docs/site", url="https://ahussein17-aa.github.io/daily-dhikr-site/",
        ios="6817398522", ios_live=True, pkg="com.yalladesigns.dailydhikr", play_live=False, shots="DailyDhikr"),
    "names99": dict(
        name="99 Names", full="99 Names of Allah",
        tagline="Know Allah through His Beautiful Names.",
        blurb="All ninety-nine Names with a reflection and a suggested du'a for each, flashcards, a quiz and a Name for every situation.",
        site=ROOT / "99 Names of Allah/docs", url="https://ahussein17-aa.github.io/99-names-pages/",
        ios="6779980837", ios_live=True, pkg="com.yalladesigns.names99", play_live=False, shots="99Names"),
    "ayah": dict(
        name="Ayah", full="Ayah: Signs of the Qur'an",
        tagline="Reflect on the signs within the Qur'an.",
        blurb="71 signs across ten categories, each with the ayah, its meaning and an honest note on how certain the reading is.",
        site=ROOT / "Ayah/docs/site", url="https://ahussein17-aa.github.io/ayah-site/",
        ios="6806326809", ios_live=False, pkg="com.yalladesigns.ayah", play_live=False, shots="Ayah"),
    "dawah": dict(
        name="Dawah Companion", full="Dawah Companion",
        tagline="Explain Islam clearly and with confidence.",
        blurb="Answers to the questions people really ask, with references, courses, practice drills and an Exhibition Mode for the stall.",
        site=ROOT / "Dawah Companion/AppStore/site", url="https://ahussein17-aa.github.io/dawah-companion-site/",
        ios="6817459810", ios_live=True, pkg="com.yalladesigns.dawah", play_live=False, shots="Dawah"),
}
ORDER = ["sahaba", "dailydhikr", "names99", "ayah", "dawah"]

APPLE = ('<svg width="22" height="26" viewBox="0 0 26 30" fill="currentColor" aria-hidden="true"><path d="M21.6 15.9c0-3.1 2.5-4.6 2.6-4.7-1.4-2.1-3.7-2.4-4.5-2.4-1.9-.2-3.7 1.1-4.7 1.1-1 0-2.5-1.1-4.1-1.1-2.1 0-4 1.2-5.1 3.1-2.2 3.8-.6 9.3 1.6 12.4 1 1.5 2.3 3.1 3.9 3.1 1.6-.1 2.2-1 4.1-1 1.9 0 2.4 1 4.1 1 1.7 0 2.8-1.5 3.8-3 1.2-1.7 1.7-3.4 1.7-3.5-.1 0-3.4-1.3-3.4-5zM18.4 6.3c.9-1 1.4-2.4 1.3-3.8-1.2.1-2.7.8-3.6 1.8-.8.9-1.5 2.3-1.3 3.7 1.4.1 2.7-.7 3.6-1.7z"/></svg>')
PLAY = ('<svg width="22" height="24" viewBox="0 0 24 26" fill="currentColor" aria-hidden="true"><path d="M3.2 1.1c-.5.3-.8.9-.8 1.600v20.600c0 .7.3 1.300.8 1.600L14.600 13 3.200 1.100zM16 11.500 5.800 1.300l12.700 7.300L16 11.500zM16 14.500l2.500 2.900L5.800 24.700 16 14.500zM20.300 9.700l2.600 1.500c1.400.8 1.400 2.800 0 3.600l-2.600 1.500L17.400 13l2.900-3.300z"/></svg>')

e = html.escape


def ios_url(a): return f"https://apps.apple.com/app/id{a['ios']}"
def play_url(a): return f"https://play.google.com/store/apps/details?id={a['pkg']}"


def badge(store, a):
    """One store button. A store that is not live yet renders as a muted, unlinked badge."""
    if store == "ios":
        live, url, icon, small, big, soon = a["ios_live"], ios_url(a), APPLE, "Download on the", "App Store", "Coming soon on the"
    else:
        live, url, icon, small, big, soon = a["play_live"], play_url(a), PLAY, "Get it on", "Google Play", "Coming soon on"
    inner = f'{icon}<span class="yd-lines"><span class="yd-small">{small if live else soon}</span><span class="yd-big">{big}</span></span>'
    if live:
        return f'<a class="yd-badge" href="{url}">{inner}</a>'
    return f'<span class="yd-badge yd-soon" aria-disabled="true">{inner}</span>'


def badges(a): return f'<div class="yd-badges">{badge("ios", a)}{badge("play", a)}</div>'


def platforms(a):
    live = [n for n, on in (("iPhone", a["ios_live"]), ("Android", a["play_live"])) if on]
    return "Free on " + " and ".join(live) if live else "Free"


BADGE_CSS = """
  .yd-badges { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.75rem; }
  .yd-badge {
    display: inline-flex; align-items: center; gap: 0.65rem; min-width: 11.5rem;
    background: var(--yd-badge-bg, #1c1c1e); color: var(--yd-badge-fg, #fff);
    border: 1px solid var(--yd-badge-border, transparent);
    border-radius: 0.75rem; padding: 0.6rem 1.25rem 0.65rem 1rem;
    text-decoration: none; transition: transform 0.15s ease;
  }
  a.yd-badge:hover { transform: translateY(-2px); }
  .yd-badge svg { flex: none; }
  .yd-lines { text-align: left; line-height: 1.2; }
  .yd-small { display: block; font-size: 0.7rem; letter-spacing: 0.04em; opacity: 0.8; }
  .yd-big { display: block; font-size: 1.15rem; font-weight: 600; }
  .yd-soon { background: transparent; color: var(--yd-soon-fg, currentColor); border: 1px dashed var(--yd-soon-border, currentColor); opacity: 0.7; }
  @media (prefers-reduced-motion: reduce) { .yd-badge { transition: none; } }
"""

MORE_CSS = """
  .yd-more { padding: 3.5rem 0; border-top: 1px solid var(--yd-line, rgba(128,128,128,0.25)); }
  .yd-more .yd-wrap { max-width: 68rem; margin: 0 auto; padding: 0 1.5rem; }
  .yd-more h2 { margin: 0 0 0.4rem; }
  .yd-more .yd-sub { margin: 0 0 1.75rem; opacity: 0.75; }
  .yd-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: 1rem; }
  .yd-app {
    display: flex; align-items: center; gap: 0.9rem; padding: 0.9rem 1rem;
    border: 1px solid var(--yd-line, rgba(128,128,128,0.25)); border-radius: 1rem;
    background: var(--yd-card, transparent); color: inherit; text-decoration: none;
  }
  .yd-app:hover { border-color: currentColor; }
  .yd-app img { width: 3.25rem; height: 3.25rem; border-radius: 0.8rem; flex: none; }
  .yd-app b { display: block; font-size: 1.02rem; }
  .yd-app span { display: block; font-size: 0.88rem; opacity: 0.75; line-height: 1.35; }
  .yd-all { display: inline-block; margin-top: 1.5rem; }
"""


def more_apps(current):
    cards = "".join(
        f'<a class="yd-app" href="{APPS[k]["url"]}"><img src="icons/{k}.png" alt="" width="52" height="52">'
        f'<div><b>{e(APPS[k]["name"])}</b><span>{e(APPS[k]["tagline"])}</span></div></a>'
        for k in ORDER if k != current)
    return (f'<section class="yd-more" id="more-apps"><div class="yd-wrap"><h2>More from Yalla Designs</h2>'
            f'<p class="yd-sub">Free, offline and private, like this one.</p>'
            f'<div class="yd-grid">{cards}</div>'
            f'<a class="yd-all" href="{HUB_URL}">See all five apps</a></div></section>')


def copy_icons(site, keys):
    (site / "icons").mkdir(parents=True, exist_ok=True)
    for k in keys:
        src = next(d / f"app_{k}.png" for d in ICONS if (d / f"app_{k}.png").exists())
        shutil.copyfile(src, site / "icons" / f"{k}.png")


def webp(src, dst, width=480):
    im = Image.open(src).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "WEBP", quality=82, method=6)


# ---------------------------------------------------------------- app pages

PAGE_CSS = """
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 1.0625rem; line-height: 1.65; -webkit-font-smoothing: antialiased; }
  h1, h2, h3 { font-family: var(--head); font-weight: var(--head-weight); text-wrap: balance; margin: 0; }
  p { margin: 0; }
  a { color: var(--accent); }
  .wrap { max-width: 68rem; margin: 0 auto; padding: 0 1.5rem; }

  .hero { padding: 4.5rem 0 3.5rem; text-align: center; background: var(--hero-bg); color: var(--hero-ink); }
  .hero .icon { width: 5.5rem; height: 5.5rem; border-radius: 1.3rem; box-shadow: 0 14px 30px -14px rgba(0,0,0,0.5); margin-bottom: 1.5rem; }
  .hero .arabic { font-family: Amiri, serif; font-size: clamp(1.9rem, 5vw, 2.7rem); line-height: 1.6; color: var(--hero-accent); margin-bottom: 0.4rem; }
  .hero h1 { font-size: clamp(2.2rem, 5.5vw, 3.4rem); letter-spacing: -0.01em; margin-bottom: 0.9rem; }
  .hero .tagline { font-size: clamp(1.1rem, 2.2vw, 1.3rem); color: var(--hero-soft); max-width: 34rem; margin: 0 auto 2rem; }
  .hero .note { font-size: 0.9rem; color: var(--hero-soft); margin-top: 1rem; }

  .screens { display: flex; justify-content: center; align-items: flex-end; gap: clamp(0.9rem, 3vw, 2.25rem); padding: 3rem 1.5rem 1rem; flex-wrap: wrap; }
  figure.phone { margin: 0; border: 1px solid var(--line); border-radius: 1.9rem; padding: 0.5rem; background: var(--card); box-shadow: var(--shadow); width: min(15rem, 76vw); }
  figure.phone.tall { width: min(17rem, 82vw); }
  .phone img { display: block; width: 100%; height: auto; border-radius: 1.45rem; }
  .phone figcaption { text-align: center; font-size: 0.85rem; color: var(--soft); padding: 0.6rem 0 0.2rem; }
  @media (max-width: 40rem) {
    .screens { flex-wrap: nowrap; overflow-x: auto; justify-content: flex-start; align-items: flex-start; scroll-snap-type: x mandatory; padding-bottom: 1.5rem; }
    .screens figure.phone, .screens figure.phone.tall { flex: none; width: 64vw; scroll-snap-align: center; }
  }

  .section { padding: 3.5rem 0; }
  .eyebrow { font-size: 0.78rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); font-weight: 600; margin-bottom: 0.7rem; }
  .section h2, .yd-more h2 { font-size: clamp(1.6rem, 3.4vw, 2.15rem); margin-bottom: 0.9rem; }
  .lede { color: var(--soft); max-width: 42rem; }
  .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: 1.1rem; margin-top: 2.25rem; }
  .feature { background: var(--card); border: 1px solid var(--line); border-radius: 1.1rem; padding: 1.5rem 1.4rem; }
  .feature h3 { font-size: 1.15rem; margin-bottom: 0.45rem; }
  .feature p { font-size: 0.97rem; color: var(--soft); }
  .feature .dot { width: 0.6rem; height: 0.6rem; border-radius: 50%; background: var(--gold); margin-bottom: 1rem; }

  .band { background: var(--band); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
  .strip { display: flex; gap: 1.1rem; overflow-x: auto; padding: 2rem 1.5rem 0.5rem; scroll-snap-type: x mandatory; }
  .strip figure.phone { flex: none; scroll-snap-align: center; width: min(13.5rem, 62vw); box-shadow: none; }
  @media (min-width: 60rem) { .strip { justify-content: center; } }

  .promise { display: grid; grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr)); gap: 2.25rem; margin-top: 2rem; }
  .promise h3 { font-size: 1.2rem; margin-bottom: 0.5rem; }
  .promise p { color: var(--soft); font-size: 1rem; }

  .cta { text-align: center; }
  .cta h2 { margin-bottom: 1.5rem; }

  footer { border-top: 1px solid var(--line); padding: 2.25rem 0 3rem; text-align: center; color: var(--soft); font-size: 0.92rem; }
  footer .links { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem 1.6rem; margin-bottom: 0.9rem; }
  footer a { color: var(--soft); }
"""

THEMES = {
    "ayah": dict(
        fonts="family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@400;500;600&family=Amiri:wght@400;700",
        theme_color="#1F4D3A",
        light="--bg:#F6F1E8;--ink:#213029;--soft:#5C6B62;--card:#FFFFFF;--line:#E7DECB;--band:#EFE8DA;--accent:#1F4D3A;--gold:#A8843A;"
              "--hero-bg:radial-gradient(ellipse at 20% 10%,rgba(200,164,90,.18),transparent 45%),linear-gradient(160deg,#265A44 0%,#1F4D3A 45%,#122B20 100%);"
              "--hero-ink:#FFFFFF;--hero-soft:rgba(255,255,255,.82);--hero-accent:#C8A45A;--shadow:0 18px 40px -18px rgba(18,43,32,.45);"
              "--yd-badge-bg:#1F4D3A;--yd-badge-fg:#FFFFFF;--yd-line:#E7DECB;--yd-card:#FFFFFF;",
        dark="--bg:#12211B;--ink:#F1ECE1;--soft:#B6C2BB;--card:#1C2E26;--line:rgba(255,255,255,.1);--band:#16281F;--accent:#8FCBAB;--gold:#C8A45A;"
             "--shadow:0 18px 40px -18px rgba(0,0,0,.7);--yd-badge-bg:#F1ECE1;--yd-badge-fg:#12211B;--yd-line:rgba(255,255,255,.12);--yd-card:#1C2E26;",
        hero_vars="--yd-badge-bg:#F6F1E8;--yd-badge-fg:#122B20;--yd-soon-fg:#F6F1E8;--yd-soon-border:rgba(246,241,232,.6);",
        head='"Source Serif 4", Georgia, serif', head_weight="600", body='Inter, -apple-system, "Segoe UI", sans-serif'),
    "dailydhikr": dict(
        fonts="family=Inter:wght@400;500;600;700&family=Amiri:wght@400;700",
        theme_color="#4A7C6F",
        light="--bg:#F7F3EC;--ink:#1C1C1E;--soft:#6E6E73;--card:#FFFFFF;--line:#E8E2D9;--band:#F1ECE3;--accent:#3C6B5F;--gold:#B8963E;"
              "--hero-bg:#F7F3EC;--hero-ink:#1C1C1E;--hero-soft:#6E6E73;--hero-accent:#3C6B5F;--shadow:0 18px 40px -20px rgba(28,28,30,.3);"
              "--yd-badge-bg:#1C1C1E;--yd-badge-fg:#F7F3EC;--yd-line:#E8E2D9;--yd-card:#FFFFFF;",
        dark="--bg:#15120E;--ink:#F0EADD;--soft:#9C948A;--card:#211C16;--line:#332E26;--band:#1A1611;--accent:#7FB3A4;--gold:#D0A94F;"
             "--hero-bg:#15120E;--hero-ink:#F0EADD;--hero-soft:#9C948A;--hero-accent:#7FB3A4;--shadow:0 18px 40px -18px rgba(0,0,0,.7);"
             "--yd-badge-bg:#F0EADD;--yd-badge-fg:#15120E;--yd-line:#332E26;--yd-card:#211C16;",
        head='Inter, -apple-system, "Segoe UI", sans-serif', head_weight="700", body='Inter, -apple-system, "Segoe UI", sans-serif'),
    "dawah": dict(
        fonts="family=Source+Serif+4:opsz,wght@8..60,400;8..60,700&family=Inter:wght@400;500;600&family=Amiri:wght@400;700",
        theme_color="#1F4D3A",
        light="--bg:#F6F1E8;--ink:#213029;--soft:#5C6B62;--card:#FFFFFF;--line:#E7DECB;--band:#EFE8DA;--accent:#1F4D3A;--gold:#A8843A;"
              "--hero-bg:#F6F1E8;--hero-ink:#213029;--hero-soft:#5C6B62;--hero-accent:#1F4D3A;--shadow:0 18px 40px -18px rgba(33,48,41,.35);"
              "--yd-badge-bg:#1F4D3A;--yd-badge-fg:#FFFFFF;--yd-line:#E7DECB;--yd-card:#FFFFFF;",
        dark="--bg:#12211B;--ink:#F1ECE1;--soft:#B6C2BB;--card:#1C2E26;--line:rgba(255,255,255,.1);--band:#16281F;--accent:#8FCBAB;--gold:#C8A45A;"
             "--hero-bg:#12211B;--hero-ink:#F1ECE1;--hero-soft:#B6C2BB;--hero-accent:#8FCBAB;--shadow:0 18px 40px -18px rgba(0,0,0,.7);"
             "--yd-badge-bg:#F1ECE1;--yd-badge-fg:#12211B;--yd-line:rgba(255,255,255,.12);--yd-card:#1C2E26;",
        head='"Source Serif 4", Georgia, serif', head_weight="700", body='Inter, -apple-system, "Segoe UI", sans-serif'),
}

CONTENT = {
    "ayah": dict(
        arabic="سَنُرِيهِمْ آيَاتِنَا", h1="Ayah", sub="Signs of the Qur'an",
        tagline="Explore the signs, wisdom and remarkable features of the Qur'an. Built for curiosity and reflection.",
        description="Explore 71 signs of the Qur'an, from its language to the universe it describes, one reflection at a time. Fully offline, no ads, no tracking.",
        hero=[("04-categories", "Ten categories"), ("02-sign", "The ayah first, then the meaning"), ("01-home", "A sign and a reflection daily")],
        eyebrow="What's inside", h2="71 signs, one reflection at a time",
        lede="Each sign opens with the ayah in Arabic and in translation, then explains what it says, how scholars have read it, and how sure we can be.",
        features=[
            ("Ten categories", "Universe and Space, Human Development, Oceans, Earth, Animals, History, Prophecies, Linguistic Signs, Mathematical Patterns and the preservation of the Qur'an."),
            ("Honest about certainty", "Every sign carries a badge: clear in the text, classical, or discussed. A contested reading is never presented as settled."),
            ("A reflection every day", "A featured sign and Today's Reflection wait on the Home tab, each a one minute read."),
            ("Discover", "Swipe through signs one card at a time when you just want to wander."),
        ],
        strip=[("06-discover", "Discover"), ("05-category", "Signs in a category"), ("03-sign-detail", "What the Qur'an says"), ("07-home-dark", "Light and dark")],
        promises=[
            ("Careful with claims", "The app separates what the text states from later readings of it, and says so on every sign, so you can share a sign without overstating it."),
            ("Private by design", "Ayah works fully offline. No account, no ads, no analytics. Your saved signs never leave your device."),
        ],
        closing="Start with one sign today"),
    "dailydhikr": dict(
        arabic="أَلَا بِذِكْرِ ٱللَّهِ تَطْمَئِنُّ ٱلْقُلُوبُ", h1="Daily Dhikr", sub="Adhkar & Tasbih",
        tagline="Keep the remembrance of Allah part of every day, with the adhkar of the Sunnah and a calm, simple counter.",
        description="Morning and evening adhkar, a tap to count tasbih, gentle reminders and a daily streak. Fully offline, no ads, no tracking.",
        hero=[("03-browse", "Every occasion"), ("01-home", "Your day at a glance"), ("02-counter", "Tap to count")],
        eyebrow="What's inside", h2="Remembrance, made simple",
        lede="Open the app and the right adhkar for this time of day are already waiting. Tap to count, and watch your day and your week fill in.",
        features=[
            ("More than 100 adhkar", "Morning, evening, after prayer, before sleep, anytime, and daily life: eating, home, mosque, travel and more."),
            ("Arabic, meaning and source", "Each dhikr has the Arabic text, a transliteration you can switch off, the English meaning and its hadith reference."),
            ("A calm counter", "One large tap target, gentle haptics and a clear count of what remains. Nothing else on the screen."),
            ("Streaks and reminders", "Morning, evening and before sleep reminders at times you choose, a daily streak, and a home screen widget."),
        ],
        strip=[("05-morning-adhkar", "Morning adhkar"), ("04-category", "Free counting"), ("06-settings", "Arabic fonts"), ("07-home-dark", "Light and dark")],
        promises=[
            ("From the Sunnah", "The adhkar are taken from the authentic collections and each one shows its reference, so you know what you are reciting and where it comes from."),
            ("Private by design", "No accounts, no ads and no tracking. Everything stays on your device."),
        ],
        closing="Begin with this morning's adhkar"),
    "dawah": dict(
        arabic="ٱدْعُ إِلَىٰ سَبِيلِ رَبِّكَ بِٱلْحِكْمَةِ", h1="Dawah Companion", sub="",
        tagline="Become confident explaining Islam. Clear answers, the references behind them, and a place to practise before the conversation.",
        description="Explain Islam clearly and with confidence: answers with Qur'an, hadith and Bible references, courses, guided proofs and practice drills. Offline, no ads, no data collected.",
        hero=[("03-topics", "Topics people ask about"), ("06-topic", "A 30 second answer first"), ("02-exhibition", "Exhibition Mode")],
        eyebrow="What's inside", h2="Learn the method, then practise",
        lede="Every answer comes in a 30 second version and a 2 minute version, with the Qur'an, hadith and Bible references behind it.",
        features=[
            ("Answers that are ready", "The questions people really ask: who Allah is, who Muhammad ﷺ is, Jesus in Islam, women in Islam, the purpose of life and more."),
            ("Six courses", "Short lessons with quizzes that build from mindset and manners to the foundations of Islam and the proofs for them."),
            ("Practice drills", "Pick a question from a Christian, an atheist or a student, think through your answer, then reveal a recommended approach."),
            ("Exhibition Mode", "Big buttons for the stall. One tap takes a visitor straight to a clear answer."),
        ],
        strip=[("01-home", "Courses on the home tab"), ("05-course", "Lessons in order"), ("07-training", "Training by audience"), ("08-drill", "Think, then reveal")],
        promises=[
            ("Gentle and accurate", "The answers are written to be shared with respect, and each one shows its sources so you can check them and quote them correctly."),
            ("Private by design", "Works fully offline. No account, no ads, no data collected."),
        ],
        closing="Be ready when it matters"),
}


def build_app(key):
    a, t, c = APPS[key], THEMES[key], CONTENT[key]
    site = a["site"]
    used = [s for s, _ in c["hero"] + c["strip"]]
    for s in used:
        webp(SHOTS / a["shots"] / f"{s}.png", site / "shots" / f"{s}.webp")
    copy_icons(site, ORDER)
    fig = lambda s, cap, cls="": f'<figure class="phone{cls}"><img src="shots/{s}.webp" alt="{e(cap)}" width="480" height="853" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>'
    hero_figs = "".join(fig(s, cap, " tall" if i == 1 else "") for i, (s, cap) in enumerate(c["hero"]))
    strip = "".join(fig(s, cap) for s, cap in c["strip"])
    feats = "".join(f'<div class="feature"><div class="dot"></div><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in c["features"])
    proms = "".join(f'<div><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in c["promises"])
    title = a["full"]
    stores = "".join(f'<a href="{u}">{n}</a>' for n, u, on in (("App Store", ios_url(a), a["ios_live"]), ("Google Play", play_url(a), a["play_live"])) if on)
    sub = f'<p class="eyebrow" style="color:var(--hero-accent)">{e(c["sub"])}</p>' if c["sub"] else ""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(c['description'])}">
<meta name="theme-color" content="{t['theme_color']}">
<link rel="canonical" href="{a['url']}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(a['tagline'])}">
<meta property="og:url" content="{a['url']}">
<meta property="og:image" content="{a['url']}icons/{key}.png">
<link rel="icon" href="icons/{key}.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{t['fonts']}&display=swap">
<style>
  :root {{ {t['light']} --head:{t['head']}; --head-weight:{t['head_weight']}; --body:{t['body']}; }}
  @media (prefers-color-scheme: dark) {{ :root {{ {t['dark']} }} }}
  .hero {{ {t.get('hero_vars', '')} }}
{PAGE_CSS}{BADGE_CSS}{MORE_CSS}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <img class="icon" src="icons/{key}.png" alt="{e(a['name'])} app icon" width="88" height="88">
    <p class="arabic" lang="ar" dir="rtl">{c['arabic']}</p>
    <h1>{e(c['h1'])}</h1>
    {sub}
    <p class="tagline">{e(c['tagline'])}</p>
    {badges(a)}
    <p class="note">{platforms(a)} · works fully offline · no account, no ads</p>
  </div>
</header>

<section class="screens" aria-label="App screenshots">{hero_figs}</section>

<section class="section">
  <div class="wrap">
    <p class="eyebrow">{e(c['eyebrow'])}</p>
    <h2>{e(c['h2'])}</h2>
    <p class="lede">{e(c['lede'])}</p>
    <div class="features">{feats}</div>
  </div>
</section>

<section class="section band">
  <div class="wrap">
    <p class="eyebrow">A closer look</p>
    <h2>Made to be opened every day</h2>
  </div>
  <div class="strip" aria-label="More screenshots">{strip}</div>
</section>

<section class="section">
  <div class="wrap">
    <p class="eyebrow">Built with care</p>
    <h2>Two promises</h2>
    <div class="promise">{proms}</div>
  </div>
</section>

<section class="section band cta">
  <div class="wrap">
    <h2>{e(c['closing'])}</h2>
    {badges(a)}
  </div>
</section>

{more_apps(key)}

<footer>
  <div class="wrap">
    <div class="links">{stores}<a href="support.html">Support</a><a href="privacy.html">Privacy</a><a href="{HUB_URL}">All apps</a></div>
    <p>© 2026 Yalla Designs</p>
  </div>
</footer>

</body>
</html>
"""
    (site / "index.html").write_text(page, encoding="utf-8")
    print("built", site.relative_to(ROOT))


# ---------------------------------------------------------------- hub page

def build_hub():
    copy_icons(HUB, ORDER)
    lead = APPS["sahaba"]
    webp(SHOTS / "Sahaba" / "01-home.png", HUB / "shots" / "sahaba-home.webp")
    webp(SHOTS / "Sahaba" / "02-person.png", HUB / "shots" / "sahaba-person.webp")
    cards = "".join(f"""
      <article class="app">
        <img src="icons/{k}.png" alt="{e(APPS[k]['name'])} app icon" width="72" height="72">
        <h3>{e(APPS[k]['full'])}</h3>
        <p class="tag">{e(APPS[k]['tagline'])}</p>
        <p class="blurb">{e(APPS[k]['blurb'])}</p>
        {badges(APPS[k])}
        <a class="learn" href="{APPS[k]['url']}">See more about {e(APPS[k]['name'])}</a>
      </article>""" for k in ORDER if k != "sahaba")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Yalla Designs: five apps for learning and living Islam</title>
<meta name="description" content="Sahaba, Daily Dhikr, 99 Names, Ayah and Dawah Companion. Free, offline and private apps for iPhone and Android.">
<meta name="theme-color" content="#1B582A">
<link rel="canonical" href="{HUB_URL}">
<meta property="og:type" content="website">
<meta property="og:title" content="Yalla Designs: five apps for learning and living Islam">
<meta property="og:description" content="Sahaba, Daily Dhikr, 99 Names, Ayah and Dawah Companion. Free, offline and private.">
<meta property="og:url" content="{HUB_URL}">
<meta property="og:image" content="{HUB_URL}icons/sahaba.png">
<link rel="icon" href="icons/sahaba.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&display=swap">
<style>
  :root {{
    --bg:#FAF5EB; --ink:#29302A; --soft:#615C52; --card:#FFFFFF; --line:#E1D6C2; --green:#1B582A; --gold:#B08A3E; --wash:#F3ECDD;
    --yd-badge-bg:#29302A; --yd-badge-fg:#FAF5EB;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#1A1714; --ink:#F0EBDC; --soft:#B8B1A4; --card:#262119; --line:#3D362C; --green:#5CBD75; --gold:#E0B86B; --wash:#211C16;
      --yd-badge-bg:#F0EBDC; --yd-badge-fg:#1A1714; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, -apple-system, "Segoe UI", sans-serif; font-size: 1.0625rem; line-height: 1.6; -webkit-font-smoothing: antialiased; }}
  h1, h2, h3 {{ font-family: "Source Serif 4", Georgia, serif; font-weight: 600; text-wrap: balance; margin: 0; }}
  p {{ margin: 0; }}
  a {{ color: var(--green); }}
  .wrap {{ max-width: 68rem; margin: 0 auto; padding: 0 1.5rem; }}

  .top {{ padding: 4rem 0 2.5rem; text-align: center; }}
  .brand {{ font-size: 0.8rem; letter-spacing: 0.24em; text-transform: uppercase; color: var(--gold); font-weight: 600; margin-bottom: 1rem; }}
  .top h1 {{ font-size: clamp(2.1rem, 5.2vw, 3.3rem); letter-spacing: -0.01em; margin-bottom: 1rem; }}
  .top p {{ color: var(--soft); max-width: 36rem; margin: 0 auto; font-size: clamp(1.05rem, 2vw, 1.2rem); }}
  .pills {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem; margin-top: 1.5rem; }}
  .pill {{ border: 1px solid var(--line); border-radius: 2rem; padding: 0.3rem 0.9rem; font-size: 0.88rem; color: var(--soft); background: var(--card); }}

  .lead {{ display: grid; grid-template-columns: 1.1fr 1fr; gap: 2.5rem; align-items: center; background: var(--card); border: 1px solid var(--line); border-radius: 1.75rem; padding: 2.5rem; margin: 1.5rem 0 2rem; }}
  .lead .label {{ font-size: 0.78rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); font-weight: 600; margin-bottom: 1rem; }}
  .lead .head {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }}
  .lead .head img {{ width: 4.5rem; height: 4.5rem; border-radius: 1.1rem; }}
  .lead h2 {{ font-size: clamp(1.6rem, 3.4vw, 2.2rem); }}
  .lead .tag {{ color: var(--green); font-weight: 600; margin-bottom: 0.6rem; }}
  .lead .blurb {{ color: var(--soft); margin-bottom: 1.5rem; }}
  .lead .yd-badges {{ justify-content: flex-start; }}
  .lead .learn {{ display: inline-block; margin-top: 1.1rem; }}
  .lead .shots {{ display: flex; justify-content: center; gap: 1rem; }}
  .lead .shots img {{ width: 46%; max-width: 13rem; height: auto; border-radius: 1.4rem; border: 1px solid var(--line); box-shadow: 0 18px 40px -20px rgba(41,48,42,.45); }}
  .lead .shots img:last-child {{ margin-top: 2rem; }}
  @media (max-width: 52rem) {{
    .lead {{ grid-template-columns: 1fr; padding: 1.6rem; }}
    .lead .yd-badges {{ justify-content: center; }}
    .lead .text {{ text-align: center; }} .lead .head {{ justify-content: center; flex-direction: column; }}
  }}

  .apps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(14.5rem, 1fr)); gap: 1.25rem; padding-bottom: 4rem; }}
  .app {{ background: var(--card); border: 1px solid var(--line); border-radius: 1.4rem; padding: 1.75rem 1.5rem; text-align: center; display: flex; flex-direction: column; align-items: center; }}
  .app img {{ width: 4.5rem; height: 4.5rem; border-radius: 1.1rem; margin-bottom: 1rem; }}
  .app h3 {{ font-size: 1.3rem; margin-bottom: 0.35rem; }}
  .app .tag {{ color: var(--green); font-weight: 600; font-size: 0.98rem; margin-bottom: 0.6rem; }}
  .app .blurb {{ color: var(--soft); font-size: 0.96rem; margin-bottom: 1.4rem; flex: 1; }}
  .app .yd-badge {{ min-width: 0; width: 100%; justify-content: center; }}
  .app .yd-badges {{ width: 100%; flex-direction: column; }}
  .app .learn {{ margin-top: 1.1rem; font-size: 0.95rem; }}

  footer {{ border-top: 1px solid var(--line); padding: 2.25rem 0 3rem; text-align: center; color: var(--soft); font-size: 0.92rem; }}
{BADGE_CSS}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <p class="brand">Yalla Designs</p>
    <h1>Five apps for learning and living Islam</h1>
    <p>Stories of the Companions, daily adhkar, the Names of Allah, signs of the Qur'an, and help explaining Islam to others.</p>
    <div class="pills"><span class="pill">Free</span><span class="pill">Works offline</span><span class="pill">No account</span><span class="pill">No ads</span><span class="pill">No tracking</span></div>
  </div>
</header>

<main class="wrap">
  <section class="lead">
    <div class="text">
      <p class="label">Start here</p>
      <div class="head"><img src="icons/sahaba.png" alt="Sahaba app icon" width="72" height="72"><h2>{e(lead['full'])}</h2></div>
      <p class="tag">{e(lead['tagline'])}</p>
      <p class="blurb">{e(lead['blurb'])}</p>
      {badges(lead)}
      <a class="learn" href="{lead['url']}">See more about Sahaba</a>
    </div>
    <div class="shots">
      <img src="shots/sahaba-home.webp" alt="Sahaba home screen with the Sahabi of the Day" width="480" height="853">
      <img src="shots/sahaba-person.webp" alt="A companion's story in Sahaba" width="480" height="853" loading="lazy">
    </div>
  </section>

  <section class="apps" aria-label="More apps">{cards}
  </section>
</main>

<footer>
  <div class="wrap"><p>© 2026 Yalla Designs · Made in Ireland</p></div>
</footer>

</body>
</html>
"""
    (HUB / "index.html").write_text(page, encoding="utf-8")
    print("built hub")


# ---------------------------------------------------------------- patches

def patch(key, hero_badge_re, footer_store_re):
    """Sahaba and 99 Names keep their own design. Add the second store button,
    the More apps section and the hub link, and keep the edit repeatable."""
    a = APPS[key]
    f = a["site"] / "index.html"
    s = f.read_text(encoding="utf-8")
    s = re.sub(r"\n<!-- yd:start -->.*?<!-- yd:end -->", "", s, flags=re.S)
    s = re.sub(r"<!-- yd:play -->.*?<!-- /yd:play -->", "", s, flags=re.S)
    s = re.sub(r"<!-- yd:hub -->.*?<!-- /yd:hub -->", "", s, flags=re.S)
    css = f"\n<!-- yd:start --><style>{BADGE_CSS}{MORE_CSS}  .yd-play {{ margin-top: 0.75rem; display: flex; justify-content: center; }}\n</style><!-- yd:end -->"
    s = s.replace("</head>", css + "\n</head>", 1)
    s, n1 = re.subn(hero_badge_re, lambda m: m.group(0) + f'<!-- yd:play --><div class="yd-play">{badge("play", a)}</div><!-- /yd:play -->', s, count=1, flags=re.S)
    s = s.replace("<footer>", f"<!-- yd:start -->{more_apps(key)}<!-- yd:end -->\n\n<footer>", 1)
    s, n2 = re.subn(footer_store_re, lambda m: m.group(0) + f'<!-- yd:hub --><a href="{HUB_URL}">All apps</a><!-- /yd:hub -->', s, count=1, flags=re.S)
    copy_icons(a["site"], ORDER)
    f.write_text(s, encoding="utf-8")
    print("patched", f.relative_to(ROOT), "hero badge:", n1, "footer:", n2)


if __name__ == "__main__":
    for k in ("ayah", "dailydhikr", "dawah"):
        build_app(k)
    build_hub()
    patch("sahaba", r'<a class="store-badge".*?</a>', r'<a href="privacy\.html">Privacy</a>')
    patch("names99", r'<a class="cta rise".*?</a>', r'<a href="privacy\.html">Privacy Policy</a>')
