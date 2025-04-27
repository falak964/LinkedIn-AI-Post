import pandas as pd
import json
from tabulate import tabulate


class FewShotPosts:
    def __init__(self, file_path="process_data.json"):
        self.df = None
        self.unique_tags = None
        self.load_posts(file_path)

    def load_posts(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            posts = json.load(f)
            self.df = pd.json_normalize(posts)
            self.df['length'] = self.df['line_count'].apply(self.categorize_length)

            # Make sure tags are lists
            self.df['tags'] = self.df['tags'].apply(lambda x: x if isinstance(x, list) else [x])

            # Collect unique tags
            all_tags = self.df['tags'].sum()
            self.unique_tags = sorted(set(all_tags))

    def get_filtered_posts(self, length, language, tag):
        df_filtered = self.df[
            (self.df['tags'].apply(lambda tags: tag in tags)) &
            (self.df['language'].str.lower() == language.lower()) &
            (self.df['length'] == length)
        ]
        return df_filtered.to_dict(orient='records')

    def categorize_length(self, line_count):
        if line_count < 5:
            return "Short"
        elif 5 <= line_count <= 10:
            return "Medium"
        else:
            return "Long"

    def get_tags(self):
        return self.unique_tags


if __name__ == "__main__":
    fs = FewShotPosts()

    print("\n📌 Available Tags:")
    print(fs.get_tags())

    # Change filters here
    length = "Short"
    language = "English"
    tag = "Motivation"

    posts = fs.get_filtered_posts(length, language, tag)

    if posts:
        print(f"\n✅ {len(posts)} post(s) found for → Length: {length}, Language: {language}, Tag: {tag}")
        print("\n📦 Posts in Table Format:\n")

        table_data = [
            [post['text'], post['engagement'], ", ".join(post['tags']), post['length'], post['language']]
            for post in posts
        ]
        headers = ["Text", "Engagement", "Tags", "Length", "Language"]

        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid", maxcolwidths=[60, None, None, None, None]))

    else:
        print(f"\n❌ No posts found for → Length: {length}, Language: {language}, Tag: {tag}")