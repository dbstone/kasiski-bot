from pytube import YouTube 

async def download(url, path, filename):
    yt = YouTube(url) 

    best_audio_stream = yt.streams \
        .filter(only_audio=True) \
        .order_by('abr')[-1]
    
    best_audio_stream.download(output_path=path, filename=f'{filename}')