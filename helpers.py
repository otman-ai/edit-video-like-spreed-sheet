from faster_whisper import WhisperModel # use WhisperModel for transcribe
import moviepy.editor as mp # moviepy for editing the video
import re
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips



## Helper functions

def load_model(model_size="medium"):
  """
  Load the model
  """
  model = WhisperModel(model_size)
  return model

def transribe(video_path, model, audio_path = 'audio.wav'):
  """
  Transcribe the video into mapped segments.

  Parametres:
  ------
  video_path : the path of the video to be transcribe
  model : the model we will use to extract the script from the video
  audio_path : path of the audio to be exported to

  """
  # Load the video
  video = mp.VideoFileClip(video_path)

  # Extract the audio from the video
  audio_file = video.audio
  audio_file.write_audiofile(audio_path)

  # Run the transcription
  segments, info = model.transcribe(audio_path, word_timestamps=True)
  segments = list(segments)  # The transcription will actually run here.
  return segments

def mapping_segments(segments):
  """
  Mapped the subtitles, each word with it correspond start and end time

  Parametres:
  ----
  segments: the segements results from runing the model

  return dictionairy of each word with it's own start and end time as well as the entire script in single string.
  """
  # Empty dictionairy to store the subtitles with it's own start and end time
  subtitles_word = {}
  # list of all the words
  transcript = []
  # looping for every segments
  for segment in segments:
      for word in segment.words:
        # clean the word from any space or punctuation.
        text_without_punctuation = re.sub(r'[^\w\s]', '', word.word.strip())
        # Store the cleaned word in dic
        subtitles_word[f"{word.start}-{word.end}"] =  text_without_punctuation
        # as well as in list
        transcript.append(text_without_punctuation)

  return subtitles_word, transcript


def find_time_range_cutted(subtitles_word, edited_script_list_word):

  """
  Return the time range that correspond to cutted word

  Parametres
  ----
  subtitles_word : mapped words with their own time(start and end)
  edited_script_list_word : list of words with no punctuation and space comming from user submition.

  """
  # assign 0 to tracked_index which track the word index in original script with index in new edited script
  tracked_index = 0
  # empty list to store the time range to cut
  time_range_to_cut = []
  # loop through all the original word
  for i, (range_, sub) in enumerate(subtitles_word.items()):
    # get the correspond word of the new script
    compared_value = edited_script_list_word[tracked_index]
    print(f"Comparing '{compared_value}' of index {tracked_index} with '{sub}' of index {i}")
    # if the index of old script is  equal to new script then it hasnt cutted move to the next word.
    if sub == compared_value:
      tracked_index += 1
    # otherwise add its range as it removed by th user and assign  tracked_index same number as it is
    # This is will not shift the index of the new script until we found its own range from the old one
    else :
      time_range_to_cut.append(range_)
      tracked_index += 0

  return   time_range_to_cut



  

def process_video(video_file):
  """
  Process video and return text to be edited
  """
  print(video_file)
  print("Transribe.....")
  segments = transribe(video_file, model)
  print('Mapping the segments....')
  subtitles_word, list_words = mapping_segments(segments)
  # Plain string to be edited as sheet
  text_to_edited = ' '.join(list_words)
  return text_to_edited


def cut_video(input_video, output_video, cut_ranges):
    cut_ranges_cleaned = cut_ranges.copy()
    # cut_ranges_cleaned = [(i.split('-')[0], i.split('-')[1]) for i in cut_ranges_cleaned]
    print(cut_ranges_cleaned)
    # Load the video clip
    video_clip = VideoFileClip(input_video)
    # Cut and concatenate the specified ranges
    cut_clips = [video_clip.subclip(start, end) for start, end in cut_ranges_cleaned]
    final_clip = concatenate_videoclips(cut_clips)
    # Write the result to a new video file
    final_clip.write_videofile(output_video, codec="libx264", audio_codec="aac")

def edit_video(script, video_file):
  segments = transribe(video_file, model)
  subtitles_word_text, list_words = mapping_segments(segments)
  print("subtiles word mapped: ", subtitles_word_text)
  # Plain string to be edited as sheet
  file_content = re.sub(r'[^\w\s]', '', script)
  # after text has been edited transform it to list of words
  edited_script_list_word = [ i   for i in file_content.split(' ') if i != '']
  time_range_to_cut = find_time_range_cutted(subtitles_word_text, edited_script_list_word)
  # sort and transform it to list and sorted range
  sorted_range = []
  time_range_to_cut_cleaned = [(i.split('-')[0], i.split('-')[1]) for i in time_range_to_cut]
  print("Cleaned range ", time_range_to_cut_cleaned)
  for range_time in time_range_to_cut_cleaned:
    for r in range_time:
        sorted_range.append(r)
  if sorted_range!=[]:
    started_range = (0, sorted_range[0])
    video_clip = VideoFileClip(video_file)
    video_duration = video_clip.duration
    ended_range = (sorted_range[-1], video_duration)
    
    complete_range = []
    complete_range.append(started_range)
    print('sorted range ', sorted_range)
    if len(sorted_range) > 2:
      new_X = sorted_range[1:-1]
      print("new x ", new_X)
      print('len ', len(new_X))
      for i in range(0, len(sorted_range)-2, 2):
          print("Before the error ", i)
          print(new_X[i:i+2])
          pair_of_items = new_X[i:i+2]
          complete_range.append((pair_of_items[0], pair_of_items[1]))
    
    complete_range.append(ended_range)
    print("Time range : ", complete_range)
    output_video_path = "output.mp4"
    cut_video(video_file, output_video_path, complete_range)
    return output_video_path
  return video_file

model = load_model()
