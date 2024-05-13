# load openai api key from file .env
from dotenv import load_dotenv
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from simphile import jaccard_similarity, euclidian_similarity, compression_similarity
from getpass import getpass
import os
from openai import OpenAI

load_dotenv()

def xu_ly_video(list_filename):
    # %%

    # %%
    client = OpenAI()
    res = []

    for filename, i in enumerate(list_filename):
        
        audio_file = open(filename, "rb")
        transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file, 
        response_format="text",
            language = "en",
        )

        # %%
        transcription

        # %%
        text_b = "Understanding of Software Development Process: Assess the candidate’s knowledge of software development methodologies and practices (e.g., Agile, Waterfall, Scrum).Consider their ability to apply these principles and methods in a project context.Teamwork and Collaboration:Evaluate their ability to work effectively within a team.Consider their communication skills and ability to collaborate with other team members.Communication Skills:Assess how clearly and logically the candidate presents details about the project and their contributions"

        print(f"Jaccard Similarity: {jaccard_similarity(transcription, text_b)}")
        print(f"Euclidian Similarity: {euclidian_similarity(transcription, text_b)}")
        print(f"Compression Similarity: {compression_similarity(transcription, text_b)}")
        res.append({i: euclidian_similarity(transcription, text_b)})
    return res



    