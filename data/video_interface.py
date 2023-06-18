from pathlib import Path
from typing import Any, Dict, List, Optional, cast
import requests

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document

def video_audio_interface(file_path, gladia_key = "7c5ab9ff-1d61-4969-96f7-893297725f97"):

  """
    rewrite from https://github.com/emptycrown/llama-hub/blob/main/llama_hub/file/audio_gladia/base.py

    input:  video/audio (.mp4/.mp3)
            if .mp4 is given, extracted .mp3 will be save in the same drectory
    
    Returns:
            List[Document]: A list of documents.
                            Document.text
                            Document.extra_info e.g. file_name
  """

  file=Path(file_path)
  extra_info={'file_name': file.name}

  if file.name.endswith("mp4"):
    from pydub import AudioSegment
    video = AudioSegment.from_file(file, format="mp4")
    # Extract audio from video
    audio = video.split_to_mono()[0]
    file = str(file)[:-4] + ".mp3"
    # export file
    audio.export(file, format="mp3")
  
  # make api call to Gladia
  headers = {
    "accept": "application/json",
    "x-gladia-key": gladia_key,
  }

  files = {
      "audio": (str(file), open(str(file), "rb"), "audio/mpeg"),
      "output_format": (None, "txt"),
      'target_translation_language': (None, 'english'),
      #'toggle_diarization': (None, 'true'),
  }

  response = requests.post(
      "https://api.gladia.io/audio/text/audio-transcription/",
      headers=headers,
      files=files,
  )
  response_dict = response.json()
  transcript = response_dict["prediction"]

  document = [Document(transcript, extra_info=extra_info)]
  return document
  # return [d.to_langchain_format() for d in document]
if __name__ == "__main__":
    print(video_audio_interface("./videos/coversation.mp4"))

