# YouTube Transcriber

Ever needed to get the text from that unpopular video on YouTube that does not have auto-generated captions?
Look no further! The YouTube transcriber will do that for you using Google's Speech-to-Text API.

**True story:** I made this simple YouTube video transcriber for my gf, because she was translating some videos for her job.
Initially she had to listen, transcribe and then translate. Now she only needs a quick pass to correct the speech-to-text mistakes and take her time with translation, while her colleagues have to do the whole thing manually 100%. I think she likes me more now.

## Install

**Clone this repo:**

    git clone https://github.com/Lef-F/yt_transcriber.git

**Install requirements:**

    pip install requirements.txt

**Install dependencies:**

For this to work you need to install [ffmpeg](https://www.ffmpeg.org/).

**For mac users:**

    brew install ffmpeg

## Setup

Make sure to have your [Google service account credentials](https://cloud.google.com/iam/docs/creating-managing-service-accounts) available as a `.json` file and loaded. You will need permissions to create objects in the storage bucket and use the translation API. Currently known as `Cloud Translation API User` and `Storage Admin`.
You can set up a [Google cloud project](https://cloud.google.com/free) with free credits from Google, which should be enough for quite some transcriptions.

For mac/linux users:

    export GOOGLE_ACCOUNT_CREDENTIALS=/path/to/service/account/file.json

## Run

To run, simply call the `transcribe.py` script from Python 3 and add your YouTube video URL and your bucket name as arguments. An additional optional argument is the video language which by default is `en-US`. (See all supported languages at [Google's official documentation](https://cloud.google.com/speech-to-text/docs/languages))

    python3 transcribe.py "https://www.youtube.com/watch?v=kJQP7kiw5Fk" your_bucket_name es-ES
