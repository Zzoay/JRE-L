
import json
import requests
import time
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

import openai

from constants import OPENAI_CONFIG
from prompts import JOURNALIST_PROMPT, PROMPT_FOR_LLAMA, STUDENT_PROMPT, TEACHER_PROMPT


def get_response(prompt, model="gpt-3.5-turbo", mode='ust'):
    if mode == 'ust':
        return get_response_ust([{"role": "user", "content": prompt}], {"model": model})
    if mode == 'llama':
        return get_response_llama(prompt)
    while True:
        try:
            completion = openai.ChatCompletion.create(model=model, temperature=1, messages=[{"role": "user", "content": prompt}])
        except Exception as e:
            print(e)
            time.sleep(3)
            continue
        break
    return completion.choices[0].message.content.strip()

def get_response_ust(messages, parameters=None):
    url = OPENAI_CONFIG['openai_api_base']
    headers = {
        "Content-Type": "application/json",
        "Authorization": OPENAI_CONFIG['openai_api_key']
        }
    data = {
        "messages": messages,
        }
    if parameters is not None:
        data.update(parameters)
    max_tries, cnt = 3, 0
    while True:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data)).json()
            with open('usage.txt', 'a') as f:
                f.write(f"{response['created']}\t{parameters['model']}\t{response['usage']}\n")
        except Exception as e:
            print(e)
            time.sleep(3)
            cnt += 1
            if cnt >= max_tries:
                break
            continue
        break
    return response['choices'][0]['message']['content'].strip()

def get_response_llama(prompt):
    url = "https://127.0.0.1:5000/predict"
    data = {"text": prompt}
    headers = {'Content-Type': 'application/json'} 
    output_text = requests.post(url, json=data, headers=headers, verify=False).json()['output_text']
    output_text = output_text[output_text.find('Output:')+7:]
    return output_text


if __name__ == "__main__":
    # prompt_template = STUDENT_PROMPT.split("\n")[0]
    input_text = """
    {
    "press": "Imagine robots that can not only lift boxes but also sculpt playdough and stir your coffee! Researchers at the Massachusetts Institute of Technology are paving the way for this future with smart technology that helps robots understand and predict how different materials behave – whether they’re solid, squishy, or runny. The secret sauce? A computer brain inspired by the tiny particles that make up everything we see and touch.

    Let's break it down a bit: everything in our world is made of particles, tiny bits of stuff that move around and interact in specific ways. These MIT scientists have essentially taught a computer program to learn from these movements and interactions. Just like how you learn to catch a ball by practicing, this program gets better the more it ‘practices’ with different materials.

    The cool part is, this isn't just about copying what happens in real life; it's about letting robots figure things out on the fly. Picture a robot in a factory that can adapt to new tasks with materials it’s never seen before, just by pushing or pulling them a little and watching what happens. That’s what MIT’s technology is aiming to achieve.

    The team's techniques have been put to the test not only in computer simulations but also in the real world, where robots have successfully molded materials like plasticine into specific shapes. Imagine the possibilities: robots that can adapt to any task, from crafting delicate artwork to making your morning latte!

    The brains behind these crafting robots say this is similar to the intuitive understanding we humans have about the physical world, and they’re excited to bring that kind of intuition to robots. They envision a future where robots can be as creative and adaptable as we are, transforming the way we think about what machines can do in our daily lives.",

    "questions": [
        "Who is leading the development of this particle-based simulation technology?",
        "What is the main goal of this technology in terms of robot functionality?",
        "How do robots learn to manipulate different materials according to this research?",
        "What are some potential practical applications for this technology?",
        "How does the program improve its performance with different materials?"
    ]
    }
    """
    # print(get_response(PROMPT_FOR_LLAMA.format(system_prompt=prompt_template, user_prompt=input_text), mode='llama'))
    input_text += "Reader's Answer:"
    input_text += """
    1. Who is leading the development of this particle-based simulation technology?
    The development of this particle-based simulation technology is being led by researchers at the Massachusetts Institute of Technology (MIT). Specifically, the team consists of scientists from the MIT Computer Science and Artificial Intelligence Laboratory (CSAIL) and the MIT Department of Physics.
    2. What is the main goal of this technology in terms of robot functionality?
    The main goal of this technology is to enable robots to understand and predict how different materials behave, regardless of their properties or composition. By achieving this level of material comprehension, robots can perform a wide range of tasks that would otherwise require human-like intuition and dexterity, such as crafting delicate artwork, manufacturing complex products, and even making personalized breakfast drinks.
    3. How do robots learn to manipulate different materials according to this research?
    Robots learn to manipulate different materials through a computer program that is trained using machine learning algorithms. This program is designed to learn from the movements and interactions of particles in various materials, much like how humans learn by observing and practicing. As the program encounters different materials, it adapts and improves its performance through trial and error, allowing it to master a wide range of manipulation tasks.
    4. What are some potential practical applications for this technology?
    Some potential practical applications for this technology include but are not limited to:
    * Manufacturing: Robots equipped with this technology could revolutionize the manufacturing industry by enabling them to adapt to new production tasks and materials with ease, leading to increased efficiency and productivity.
    * Healthcare: Robotic systems could use this technology to develop novel medical devices or to improve existing ones, such as prosthetics or surgical tools, which could lead to improved patient outcomes.
    * Space Exploration: With the ability to adapt to unfamiliar environments, robots utilizing this technology could become essential components of space missions, assisting astronauts in conducting scientific experiments or repairs without putting themselves in harm's way.
    5. How does the program improve its performance with different materials?
    The program improves its performance with different materials by continuously training itself using machine learning algorithms. Each time the program encounters a new material, it practices manipulating it, gradually refining its actions until it can accurately predict the material's behavior. Through this process, the program becomes increasingly proficient at handling diverse materials, eventually approaching the level of human intuition and dexterity.
    """
    print(get_response(TEACHER_PROMPT.format(input_text), model="gpt-4", mode='ust'))