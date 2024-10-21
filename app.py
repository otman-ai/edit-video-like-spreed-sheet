import gradio as gr
from helpers import *

with gr.Blocks() as demo: 
    with gr.Row():    
        heading2 = gr.HTML("<h2>Edit your videos like SpreedSheet using  <a href='https://huggingface.co/docs/transformers/model_doc/whisper'> WhisperModel</a></h2>")
    with gr.Row():
        p = gr.Markdown('*if you have got any issues or questions reach out to me otmanheddouchai@gmail.com*')

    with gr.Row():
        p = gr.Markdown('Please upload video first then click `Transcribe` to get the full script of the video, after you can easly edit Script field by removing the unwanted words.')
    with gr.Row():
        p = gr.Markdown('Make sure you click on `Cut` to generate your edited video.')


    with gr.Row():
        video_file = gr.Video(label="Upload Video")
        script = gr.Textbox(label='Script')
        results = gr.Video(label='Result')

    with gr.Row():
       transcribe = gr.Button('Transcribe')
       cut_button = gr.Button('Cut')
       

       if video_file:
          transcribe.click(process_video, inputs=[video_file], outputs=[script])
          if script:
            
            cut_button.click(edit_video, inputs=[script,video_file], outputs=[results])
    with gr.Row():
      gr.Markdown('Made by **Otman Heddouch**')
demo.launch(share=True, debug=True)