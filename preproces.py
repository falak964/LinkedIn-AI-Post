import json
import re
import os
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException


def process_posts(raw_file_path, processed_file_path, output_file_path):
    """Processes LinkedIn posts by extracting metadata, unifying tags, and saving them safely."""
    try:
        # Load raw posts
        with open(raw_file_path, encoding='utf-8') as file:
            posts = json.load(file)

        enriched_posts = []

        # Process each post
        for post in posts:
            try:
                clean_text = remove_invalid_unicode(post.get('text', ''))
                metadata = extract_metadata(clean_text)

                # Merge original post with metadata
                post_with_metadata = post | metadata
                enriched_posts.append(post_with_metadata)

                # Debugging output
                print("\n--- Extracted Metadata ---")
                print(f"Original Post: {clean_text}")
                print(f"Line Count: {metadata['line_count']}")
                print(f"Language: {metadata['language']}")
                print(f"Tags: {metadata['tags']}")
                print("--------------------------")

            except Exception as e:
                print(f"❌ Error processing post: {e}")

        # Unify tags across posts
        unified_tags = get_unified_tags(enriched_posts)

        # Apply unified tags to posts
        for post in enriched_posts:
            current_tags = post['tags']
            new_tags = {unified_tags.get(tag, tag) for tag in current_tags}  # Default to same tag if no mapping
            post['tags'] = list(new_tags)

        # Save processed data to both files
        save_json_safe(enriched_posts, processed_file_path)
        save_json_safe(enriched_posts, output_file_path)

    except Exception as e:
        print(f"❌ Error processing posts: {e}")


def extract_metadata(post_text):
    """Extracts metadata (line count, language, tags) from a LinkedIn post using LLM."""
    template = '''
    You are given a LinkedIn post. Extract the number of lines, language, and relevant tags.

    **Guidelines:**
    - **Strict JSON Output**: No extra text, just return the JSON object.
    - **Expected JSON format:** 
      ```json
      {{"line_count": <int>, "language": "<English or Hinglish>", "tags": ["tag1", "tag2"]}}
      ```
    - **Tags:** Extract up to 2 relevant tags (career, technology, leadership, etc.).
    - **Language:** Must be either "English" or "Hinglish" (Hindi + English mix).
    
    **Post Content:**
    {post_text}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm

    try:
        response = chain.invoke({"post_text": post_text}).content.strip()

        # Extract valid JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            response_json = json_match.group(0)  # Extract JSON part
        else:
            raise ValueError(f"Invalid LLM response format: {response}")

        json_parser = JsonOutputParser()
        metadata = json_parser.parse(response_json)

        return {
            "line_count": metadata.get("line_count", 0),
            "language": metadata.get("language", "Unknown"),
            "tags": metadata.get("tags", [])
        }

    except OutputParserException as e:
        print(f"❌ Parsing failed: {e}. Response: {response}")
        return {"line_count": 0, "language": "Unknown", "tags": []}

    except Exception as e:
        print(f"❌ Unexpected error in extract_metadata: {e}")
        return {"line_count": 0, "language": "Unknown", "tags": []}


def get_unified_tags(posts_with_metadata):
    """Unifies similar tags using LLM to reduce redundancy."""
    unique_tags = set()

    # Extract all unique tags
    for post in posts_with_metadata:
        unique_tags.update(post['tags'])

    unique_tags_list = ', '.join(unique_tags)

    template = '''I will give you a list of tags. You need to unify them as per these rules:
    1. Merge similar tags into a single tag.
       Example:
       - "Jobseekers", "Job Hunting" → "Job Search"
       - "Motivation", "Inspiration" → "Motivation"
       - "Personal Growth", "Self Improvement" → "Self Improvement"
    2. Use **Title Case** for final tags (e.g., "Job Search").
    3. Return a **strict JSON** object with **original tag → unified tag mapping**.
       Example: {{"Jobseekers": "Job Search", "Job Hunting": "Job Search"}}
    
    **Tags to unify:** {unique_tags_list}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm

    try:
        response = chain.invoke({"unique_tags_list": unique_tags_list}).content.strip()

        # Extract JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            response_json = json_match.group(0)  # Extract JSON part
        else:
            raise ValueError(f"Invalid LLM response format: {response}")

        json_parser = JsonOutputParser()
        unified_tags = json_parser.parse(response_json)

        return unified_tags

    except OutputParserException as e:
        print(f"❌ Parsing failed: {e}. Response: {response}")
        return {}

    except Exception as e:
        print(f"❌ Unexpected error in get_unified_tags: {e}")
        return {}


def remove_invalid_unicode(text):
    """Removes invalid Unicode characters to prevent encoding issues."""
    return text.encode("utf-8", "ignore").decode("utf-8")


def save_json_safe(data, file_path):
    """Save JSON while handling invalid Unicode characters."""
    try:
        cleaned_data = remove_invalid_unicode(json.dumps(data, ensure_ascii=False, indent=4))

        with open(file_path, "w", encoding="utf-8") as outfile:
            outfile.write(cleaned_data)
            print(f"✅ Successfully saved data to {file_path}")  # Debugging Line

        # Double-check file contents
        with open(file_path, "r", encoding="utf-8") as check_file:
            content = check_file.read()
            print(f"\n📂 Confirmed saved file content for {file_path} (first 500 chars):\n", content[:500])

    except Exception as e:
        print(f"❌ Error saving JSON file ({file_path}): {e}")


if __name__ == "__main__":
    process_posts("raw_posts.json", "processed_posts.json", "process_data.json")