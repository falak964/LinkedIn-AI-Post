from llm_helper import llm
from few_shot import FewShotPosts

few_shot = FewShotPosts()

# You can expand this mapping based on your needs
TAG_ALIASES = {
    "mental": "Mental Health",
    "career": "Careers",
    "motivation": "Motivation",
    "inspire": "Motivation",
    "startup": "Entrepreneurship",
    "ai": "Artificial Intelligence",
    "tech": "Technology",
    "growth": "Personal Growth",
    "health": "Health & Wellness",
    "focus": "Productivity",
    "learn": "Learning",
    "jobs": "Careers"
}

def map_to_tag(raw_input):
    """Map raw user input to known tags."""
    raw_input = raw_input.strip().lower()
    return TAG_ALIASES.get(raw_input, raw_input.title())

def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"

def generate_post(length, language, raw_tag):
    tag = map_to_tag(raw_tag)  # Automatically map spoken/typed tag
    prompt = get_prompt(length, language, tag)
    response = llm.invoke(prompt)
    return response.content

def get_prompt(length, language, tag):
    length_str = get_length_str(length)

    prompt = f'''
Generate a LinkedIn post using the below information. No preamble.

1) Topic: {tag}
2) Length: {length_str}
3) Language: {language}
If Language is Hinglish then it means it is a mix of Hindi and English. 
The script for the generated post should always be English.
'''

    examples = few_shot.get_filtered_posts(length, language, tag)

    if len(examples) > 0:
        prompt += "\n4) Use the writing style as per the following examples."

    for i, post in enumerate(examples):
        post_text = post['text']
        prompt += f'\n\nExample {i + 1}:\n\n{post_text}'
        if i == 1:  # Limit to 2 examples
            break

    return prompt

# Optional: test directly
if __name__ == "__main__":
    print(generate_post("Medium", "English", "mental"))