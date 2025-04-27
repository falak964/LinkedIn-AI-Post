import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post

# Dropdown options
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish"]

def main():
    st.subheader("💼 LinkedIn Post Generator")

    # Dropdowns in 3 columns
    col1, col2, col3 = st.columns(3)

    fs = FewShotPosts()
    tags = fs.get_tags()

    with col1:
        selected_tag = st.selectbox("📌 Topic", options=tags)

    with col2:
        selected_length = st.selectbox("📝 Length", options=length_options)

    with col3:
        selected_language = st.selectbox("🌐 Language", options=language_options)

    if st.button("🚀 Generate Post"):
        with st.spinner("Generating..."):
            post = generate_post(selected_length, selected_language, selected_tag)
            st.success("✅ Post generated!")
            st.markdown(f"### ✨ Output:\n\n{post}")

if __name__ == "__main__":
    main()