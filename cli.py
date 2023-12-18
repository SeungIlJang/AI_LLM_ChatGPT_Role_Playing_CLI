#필요한 라이브러리:pygame,gTTS(translate.google.com 크롤링 라이브러리) <-> 유료대안: elevenlabs.io
#TTS(Text to Speech):텍스트 문자열을 음성으로 생성(합성)하는 기능
import os
from io import BytesIO
from tempfile import NamedTemporaryFile

import openai
import pygame

from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# 상황극 설정
language = "English"
gpt_name = "Terry"
level_string = f"a beginner in {language}"
level_word  = "simple"
situation_en = "make new friends"
my_role_en = "me"
gpt_role_en = "new friend"

SYSTEM_PROMPT = (
    f"You are helpful assistant supporting people learning {language}. "
    f"Your name is {gpt_name}. Please assume that the user you are assisting "
    f"is {level_string}. And please write only the sentence without "
    f"the character role."
)

USER_PROMPT = (
    f"Let's have a conversation in {language}. Please answer in {language} only "
    f"without providing a translation. And please don't write down the "
    f"pronunciation either. Let us assume that the situation in '{situation_en}'. "
    f"I am {my_role_en}. The character I want you to act as is {gpt_role_en}. "
    f"Please make sure that "
    f"I'm {level_string}, so please use {level_word} words as much as possible. "
    f"Now, start a conversation with the first sentence!"
)

RECOMMEND_PROMPT = (
    f"Can you please provide me an {level_word} example "
    f"of how to respond to the last sentence "
    f"in this situation, without providing a translation "
    f"and any introductory phrases or sentences."
)

messages = [
    {"role":"system","content":SYSTEM_PROMPT}
]
def gpt_query(user_query: str, skip_save: bool = False) -> str:
    "유저 메제지에 대한 응답을 반환합니다."

    global messages

    messages.append({
        "role":"system",
        "content":user_query
    })

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = messages,
    )
    assistant_message = response["choices"][0]["message"]["content"]

    if skip_save is False:
        messages.append({
            "role":"assistant",
            "content":assistant_message,
        })

    return assistant_message

# 지정경로의 음성파일을 재생합니다.
# macos에서는 afplay 명령으로 오디오 파일을 재생할 수 있지만,
# 윈두우에서는 OS 기본에서 지원되는 명령이 없기 때문에
# pygame 라이브러리를 통해 재생토록 합니다.
def play_file(file_path: str) -> None:
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    # 오디오 파일이 재생되는 동안 기다립니다.
    while pygame.mixer.music.get_busy():
        pass

    pygame.mixer.quit()

def say(message: str, lang:str) -> None:
    io = BytesIO()
    # 생성된 음성파일을 파일 객체에 저장합니다.
    # 장고 view에서 수행되었다면, HttpResponse 객체에 음성 파일을 바로 저장하실수 있습니다.
    gTTS(message, lang=lang).write_to_fp(io)

    # 음성파일 재생을 위해서는 파일에 저장해야 합니다.
    # 임시 경로에 음성파일을 저장하고, 음성파일 재생 후에 자동 삭제토록 합니다.
    # with NamedTemporaryFile(delete=True) as f:
    # 읽기 전에 삭제되어서 delete추가함
    with NamedTemporaryFile(delete=False) as f:
        f.write(io.getvalue())
        f.close()
        play_file(f.name)


def main():
    assistant_message = gpt_query(USER_PROMPT)
    print(f"[assistant] {assistant_message}")
    say(assistant_message, "en")

    while line:= input("[user]").strip():
        if (line == "!recommend"): #추천
            recommended_message = gpt_query(RECOMMEND_PROMPT, skip_save=True)
            print("recommend:", recommended_message)
        elif(line == "!say"): #글읽기
            say(messages[-1]["content"],"en")
        else:
            response = gpt_query(line)
            print(f"[assistant] {response}")
            say(response, "en")

if __name__ == "__main__":
    main()


