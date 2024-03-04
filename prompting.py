
from constants import OPENAI_CONFIG
from data_helper import load_origin_data
from prompts import JOURNALIST_PROMPT, TEACHER_PROMPT, STUDENT_PROMPT, REVISION_PROMPT, EVAL_PROMPT
from utils import get_response

def act(input_text, agent_type, model):
    if agent_type == "journalist":
        prompt_template = JOURNALIST_PROMPT
    elif agent_type == "teacher":
        prompt_template = TEACHER_PROMPT
    elif agent_type == "student":
        prompt_template = STUDENT_PROMPT
    else:
        # TODO: Implement revision and evaluation
        raise ValueError("Invalid agent type")
    
    prompt = prompt_template.format(input_text)
    if model == "gpt-3.5-turbo":
        return get_response(prompt, model=model)
    elif model == "gpt-4":
        return get_response(prompt, model=model)
    elif model == "llama":
        # TODO: Implement llama
        raise ValueError("Invalid agent type")
    else:
        raise ValueError("Invalid agent type")


if __name__ == "__main__":
    for d in load_origin_data():
        print(act(d, agent_type="journalist", model='gpt-3.5-turbo'))
        raise RuntimeError
        print("===")