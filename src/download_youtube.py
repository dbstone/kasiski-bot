from pytube import YouTube 
  
SAVE_PATH = 'downloads'
FILENAME = 'current'
  
#link of the video to be downloaded 
link="https://www.youtube.com/watch?v=IUGzY-ihqWc"
  
try: 
    #object creation using YouTube which was imported in the beginning 
    yt = YouTube(link) 
except: 
    print("Connection Error") #to handle exception 

best_audio_stream = yt.streams \
    .filter(only_audio=True) \
    .order_by('abr')[-1]
  
#get the video with the extension and resolution passed in the get() function 

try: 
    #downloading the video 
    best_audio_stream.download(output_path=SAVE_PATH, filename=FILENAME)
except: 
    print("Some Error!") 
print('Task Completed!') 