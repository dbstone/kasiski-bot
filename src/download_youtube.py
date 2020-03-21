from pytube import YouTube 

SAVE_PATH = 'downloads'
FILENAME = 'current'

def download(url, path, filename):
    try: 
        yt = YouTube(url) 
    except: 
        print('Error connecting to Youtube')

    best_audio_stream = yt.streams \
        .filter(only_audio=True) \
        .order_by('abr')[-1]
    
    try: 
        best_audio_stream.download(output_path=path, filename=f'{filename}')
    except: 
        print("Download error!") 

    print('Download completed!') 