import requests
from bs4 import BeautifulSoup
from gtts import gTTS, gTTSError
from pydub import AudioSegment
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import schedule
import time

# Function to split text into smaller chunks
def split_text(text, max_chars=200):
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 > max_chars:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "
        else:
            current_chunk += word + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Function to create an audio file from news summary
def create_audio_message(news_summary):
    text_chunks = split_text(news_summary)

    combined_audio = AudioSegment.silent(duration=100)
    
    for i, chunk in enumerate(text_chunks):
        tts = gTTS(text=chunk, lang='en')
        temp_filename = f"temp_audio_{i}.mp3"
        tts.save(temp_filename)
        
        audio_segment = AudioSegment.from_file(temp_filename)
        combined_audio += audio_segment
        os.remove(temp_filename)

    final_filename = "news_summary.mp3"
    combined_audio.export(final_filename, format="mp3")
    
    return final_filename

# Function to scrape news from BBC
def scrape_bbc_news():
    url = 'https://www.bbc.com/news'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headlines = soup.find_all('h3', limit=5)
    news_summary = "BBC News Headlines:\n"
    for idx, headline in enumerate(headlines, 1):
        news_summary += f"{idx}. {headline.get_text().strip()}\n"
    return news_summary

# Function to scrape news from Sky News
def scrape_sky_news():
    url = 'https://news.sky.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headlines = soup.find_all('h3', limit=5)
    news_summary = "Sky News Headlines:\n"
    for idx, headline in enumerate(headlines, 1):
        news_summary += f"{idx}. {headline.get_text().strip()}\n"
    return news_summary

# Function to scrape news from The Times
def scrape_the_times_news():
    url = 'https://www.thetimes.co.uk/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headlines = soup.find_all('h3', limit=5)
    news_summary = "The Times Headlines:\n"
    for idx, headline in enumerate(headlines, 1):
        news_summary += f"{idx}. {headline.get_text().strip()}\n"
    return news_summary

# Combine news from all sources
def get_combined_news():
    bbc_news = scrape_bbc_news()
    sky_news = scrape_sky_news()
    the_times_news = scrape_the_times_news()
    return bbc_news + "\n" + sky_news + "\n" + the_times_news

# Email function
def send_email(recipient_email, audio_file):
    sender_email = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Your Daily News Summary"
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(audio_file, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{audio_file}"')
    msg.attach(part)
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

# Main job
def job():
    print("Scraping news from multiple sources...")
    combined_news = get_combined_news()
    print("Creating audio message...")
    audio_file = create_audio_message(combined_news)
    print("Sending email...")
    send_email("drooschuck@gmail.com", audio_file)  # Update this with your recipient email
    print("Job complete!")

# Run job once (for GitHub Action trigger)
job()
