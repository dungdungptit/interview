from phonemizer.separator import Separator
from phonemizer import phonemize

# from phonemizer.backend.espeak.wrapper import EspeakWrapper
from Levenshtein import distance as levenshtein_distance
from scoring import calculate_fluency_and_pronunciation

# import whisper
# import torch

# device = "cuda:0" if torch.cuda.is_available() else "cpu"

# model = whisper.load_model("base.en", device=device)
separator = Separator(
    phone=None,
    word="",
)

# EspeakWrapper.set_library(r"C:\Program Files\eSpeak NG\libespeak-ng.dll")


def transcribe(audio):
    import moviepy.editor as mp
    import speech_recognition as sr

    # Load the video
    # video = mp.VideoFileClip("qq.mp4")

    # # Extract the audio from the video
    # audio_file = video.audio
    # audio_file.write_audiofile("geeksforgeeks.wav")

    # Initialize recognizer
    r = sr.Recognizer()

    # Load the audio file
    with sr.AudioFile(audio) as source:
        data = r.record(source)

    # Convert speech to text
    text = r.recognize_google(data)

    # Print the text
    print("\nThe resultant text from video is: \n")
    print(text)
    return {"language": "en-us", "text": text}


def text2phoneme(text):
    return phonemize(
        text.lower().split(),
        backend="espeak",
        separator=separator,
        strip=True,
        with_stress=False,
        tie=False,
        language="en-us",
    )


def rate_pronunciation(expected_phonemes, actual_phonemes):
    expected_phonemes = expected_phonemes
    actual_phonemes = actual_phonemes
    # Calculate the Levenshtein distance between the two phoneme sequences
    results = []
    for i, base_word in enumerate(actual_phonemes):
        best_dist = float("inf")
        if i <= len(expected_phonemes):
            for j in range(max(0, i - 1), i + min(3, len(expected_phonemes) - i)):
                dist = levenshtein_distance(
                    expected_phonemes[j],
                    base_word,
                )
                if dist < best_dist:
                    best_dist = dist
                if best_dist == 0:  # Early stopping on perfect match
                    break
        error_threshold = len(base_word) * 0.40
        if best_dist == 0:
            results.append(3)
        elif best_dist <= error_threshold:
            results.append(2)
        else:
            results.append(1)
    return results


def Speaker_speech_analysis(audio_path, text):
    import eng_to_ipa as p

    if audio_path.endswith(".mp4"):
        import moviepy.editor as mp

        video = mp.VideoFileClip(audio_path)
        audio_file = video.audio
        audio_path = audio_path.replace(".mp4", "")
        audio_file.write_audiofile(f"{audio_path}.wav")
        audio_path = f"{audio_path}.wav"
        print(audio_path, "check")

    pre_transcribtion = transcribe(audio_path)["text"]

    print(pre_transcribtion)
    transcribtion = p.ipa_list(pre_transcribtion)
    text_phone = p.ipa_list(text)
    scores = rate_pronunciation(transcribtion, text_phone)
    FP_scores = calculate_fluency_and_pronunciation(
        audio_path, len(pre_transcribtion.split()), scores, len(text.split())
    )
    word_scores = [(word, s) for word, s in zip(text.split(), scores)]

    FP_scores["word_scores"] = word_scores
    return FP_scores


if __name__ == "__main__":

    text = "it's all dark gloomy dull and lonely that's what you see when you don't hire me hi I am Leon Joyce De Flores 23 years old and a graduate of communication Arts major in digital cinema at Far Eastern University Manila ever since I was a kid I have always loved Arts anything about Arts sketching drawing coloring designing filmmaking photography literary arts and even Performing Arts like music so that let me to continue pursuing my passion this time let's talk about why you should hire me these are my strengths hardworking creative and willing I am hard working because I have jungle and excelled in school work and church activities all at the same time so if you are going to give me a lot of tasks no worries I can handle that because I work under pressure with quality"
    # text = text2phoneme(text)
    file_path = (
        r"y2mate_com_Job_Application_Video_Sample_Video_Resume_Video_CV_PART.wav"
    )
    trans = transcribe(file_path)["text"]
    print(trans)
    # trans = text2phoneme(trans)
    print("base:", text)
    print("predicted:", trans)
    result = rate_pronunciation(trans, text)
    print(result)
