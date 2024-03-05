

JOURNALIST_PROMPT = """You are a science journalist. You have been assigned to write a press release for general public about the given research paper. Here is a scientific article and its press release, but the press is not suitable for general public to read and understand, please use easy-to-understand and lively language to make it easy to learn. If there are some prerequisite knowledge, please put it into your output in a fluent language. After the press generation, please provide some questions about the press, in json format ({{'press':'...', 'questions': [...]}}). \nInput: {}
"""

TEACHER_PROMPT = """
"""

STUDENT_PROMPT = """
"""

REVISION_PROMPT = """
"""

EVAL_PROMPT = """
"""

PROMPT_FOR_LLAMA = """<s>[INST] <<SYS>>{system_prompt}<</SYS>>
Input：{user_prompt} [/INST] Output:
"""