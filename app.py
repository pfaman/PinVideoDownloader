from flask import Flask, render_template, request
from datetime import datetime
import sys
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import system
import re

system("cls")

app = Flask(__name__)

# Function to download Pinterest video
def download_pinterest_video(page_url):
    # Download function
    def download_file(url, filename):
        response = requests.get(url, stream=True)

        file_size = int(response.headers.get('Content-Length', 0))
        progress = tqdm(response.iter_content(1024), f'Downloading {filename}', total=file_size, unit='B', unit_scale=True, unit_divisor=1024)

        with open(filename, 'wb') as f:
            for data in progress.iterable:
                # write data read to the file
                f.write(data)
                # update the progress bar manually
                progress.update(len(data))

    # checking entered url is correct
    if("pinterest.com/pin/" not in page_url and "https://pin.it/" not in page_url):
        return "Entered URL is invalid"

    if("https://pin.it/" in page_url): # pin url short check
        print("extracting original pin link")
        t_body = requests.get(page_url)
        if(t_body.status_code != 200):
            return "Entered URL is invalid or not working."
        soup = BeautifulSoup(t_body.content,"html.parser")
        href_link = (soup.find("link",rel="alternate"))['href']
        match = re.search('url=(.*?)&', href_link)
        page_url = match.group(1) # update page url 

    print("fetching content from given url")
    body = requests.get(page_url) # GET response from url
    if(body.status_code != 200): # checks status code
        return "Entered URL is invalid or not working."
    else:
        soup = BeautifulSoup(body.content, "html.parser") # parsing the content
        print("Fetched content Successfully.")
        ''' extracting the url
        <video
            autoplay="" class="hwa kVc MIw L4E"
            src="https://v1.pinimg.com/videos/mc/hls/......m3u8"
            ....
        ></video>
        '''
        extract_url = (soup.find("video",class_="hwa kVc MIw L4E"))['src'] 
        # converting m3u8 to V_720P's url
        convert_url = extract_url.replace("hls","720p").replace("m3u8","mp4")
        print("Downloading file now")
        # downloading the file 
        download_file(convert_url, datetime.now().strftime("%d_%m_%H_%M_%S_")+".mp4")
        return convert_url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    page_url = request.form['page_url']
    video_url = download_pinterest_video(page_url)
    return render_template('result.html', video_url=video_url)

if __name__ == '__main__':
    app.run(debug=True)
