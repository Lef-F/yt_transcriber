import io
import os
import sys
import youtube_dl
import subprocess
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.cloud import storage
# WORKAROUND to allow for big .wav files to be uploaded.
# ISSUE: Upload crashes if not finished in under 60 seconds.
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB


def upload_blob(bucket_name, source_file_name, destination_blob_name=None):
	"""Uploads a file to the bucket.
	Args:
		bucket_name The target bucket name
		source_file_name Path to file to be uploaded
		destination_blob_name The name the file should get on the bucket
	"""
	print('Uploading file to Google storage:', source_file_name)
	if destination_blob_name is None:
		destination_blob_name = source_file_name

	storage_client = storage.Client()
	bucket = storage_client.bucket(bucket_name)
	blob = bucket.blob(destination_blob_name)

	blob.upload_from_filename(source_file_name)

	print(
		'File {} uploaded to {}.'.format(
			source_file_name, 'gs://' + bucket_name + '/' + destination_blob_name
		)
	)


def speech_to_text(gcs_path_name, lang, asr=44100):
	"""
	Transcribe a long audio file using asynchronous speech recognition
	Args:
		gcs_path_name Path to audio file on Google storage, e.g. gs://bucket/audio.wav
		lang Language in audio file to be transcribed
		asr The audio sample rate frequency in Hz (above 16000Hz for best results)
	"""
	client = speech_v1.SpeechClient()

	# Encoding of audio data sent. This sample sets this explicitly.
	# This field is optional for FLAC and WAV audio formats.
	encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
	config = {
		'language_code': lang,
		'sample_rate_hertz': asr,
		'encoding': encoding,
	}
	audio = {'uri': gcs_path_name}

	operation = client.long_running_recognize(config, audio)

	print(u'Transcribing audio file...')
	response = operation.result()

	text = list()
	print('*'*10, 'BEGIN TRANSCRIPT', '*'*10)
	for result in response.results:
		# First alternative is the most probable result
		alternative = result.alternatives[0]
		text.append(alternative.transcript)
		print(u'{}'.format(alternative.transcript))
	print('*'*10, 'END TRANSCRIPT', '*'*10)

	return text

def convert_to_wav(filepath):
	"""
	Convert m4a file to wav
	Args:
		filepath Path to audio file
	"""
	print('Converting audio to WAV')
	subprocess.run(['ffmpeg', '-loglevel', 'error' ,'-y',
					'-i', filepath, 
					'-ac', '1', filepath.replace('.m4a', '.wav')])

def dl_youtube(url, lang):
	"""
	Download the YouTube video
	Args:
		url YouTube video URL
		lang YouTube video language to be transcribed
	"""
	print('Fetching data for YouTube URL:', url)
	ydl_opts = {
		'format': 'm4a',
		'outtmpl': u'%(title)s.%(ext)s',
		'restrictfilenames': True,
		'forcefilename': True,
		'quiet': True
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		_ = ydl.download([url])
		info = ydl.extract_info(url)
		output_name = ydl.prepare_filename(info)

	print('Video title:', info['title'])
	return {'name': output_name, 'asr': info['asr']}

def main(url, bucket_name, lang="en-US"):
	"""
	Transcribe a YouTube video
	Args:
		url YouTube video URL
		lang YouTube video language to be transcribed
	"""
	output = dl_youtube(url, lang)
	output_name = output['name']

	convert_to_wav(output_name)

	os.remove(output_name)
	output_name = output_name.replace('.m4a', '.wav')
	upload_blob(bucket_name, output_name)
	os.remove(output_name)
 
	transcript = speech_to_text('gs://' + bucket_name + '/' + output_name, 
								lang, output['asr'])

	output_path = os.path.join(os.getcwd(), 'transcriptions')
	if not os.path.exists(output_path):
		os.mkdir(output_path)

	output_txt = output_name.replace('.wav', '.txt')
	with open(os.path.join(output_path, output_txt), 'w') as f:
		f.write('\n'.join(transcript))

	print('Finished succesfully!', 'See your transcirpt at:', os.path.join(os.getcwd(), output_txt))

if __name__ == "__main__":
	if len(sys.argv) < 2:
		raise ValueError('Please provide youtube URL and bucket name')
	elif len(sys.argv) == 3:
		print('Proceeding with en-US language as default.')
		main(sys.argv[1], sys.argv[2])
	elif len(sys.argv) == 4:
		print('Proceeding with', sys.argv[3], 'as transcribing language.')
		main(sys.argv[1], sys.argv[2], sys.argv[3])
	else:
		raise ValueError('Too many arguments! Please provide at most three, i.e. URL, bucket name and language.')