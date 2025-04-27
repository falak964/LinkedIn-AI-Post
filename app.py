import streamlit as st
from assistant import speak_and_wait, listen, map_spoken_to_tag
from post_genrator import generate_post
from few_shot import FewShotPosts
import time
import webbrowser
import pyperclip

st.title("🎙️ AI LinkedIn Post Generator")

# Initialize session state variables if they don't exist
if "manual_post" not in st.session_state:
    st.session_state.manual_post = ""
if "alternative_post" not in st.session_state:
    st.session_state.alternative_post = ""
if "show_alternative" not in st.session_state:
    st.session_state.show_alternative = False

# Define tab layout
tab1, tab2 = st.tabs(["🎤 Voice Assistant", "⌨️ Manual Input"])

# Voice Assistant Mode
with tab1:
    st.subheader("Voice-Driven Post Generator")
    
    if st.button("🎤 Start Voice Assistant", key="start_voice"):
        # Welcome message
        speak_and_wait("Welcome! Let's create your unique LinkedIn post.")
        time.sleep(1.5)  # Add pause between prompts

        # Post Length
        speak_and_wait("What should be the length of your post? Short, Medium, or Long?")
        length = listen(expected_keywords=["short", "medium", "long"])
        if length:
            length = length.capitalize()
            st.session_state.length = length
        else:
            st.warning("Couldn't detect post length. Try again.")
            st.stop()

        time.sleep(1)  # Add pause between prompts

        # Language
        speak_and_wait("Which language do you prefer? English, Hindi, or Hinglish?")
        language = listen(expected_keywords=["english", "hindi", "hinglish"])
        if language:
            language = language.capitalize()
            st.session_state.language = language
        else:
            st.warning("Couldn't detect language. Try again.")
            st.stop()

        time.sleep(1)  # Add pause between prompts

        # Tag / Topic
        speak_and_wait("What topic should the post be about? For example: AI, Motivation, Career, Startup.")
        tag = listen()
        if tag:
            tag = map_spoken_to_tag(tag)
            st.session_state.tag = tag
        else:
            st.warning("Couldn't detect topic. Try again.")
            st.stop()

        time.sleep(1)  # Add pause between prompts

        # Generate post with clear notification
        st.info(f"Generating a {length} post in {language} on {tag}...")
        speak_and_wait(f"Generating a {length} post in {language} on {tag}")
        
        post = generate_post(length, language, tag)
        st.session_state.post = post

        # Show the generated post
        st.subheader("📝 Generated LinkedIn Post")
        st.text_area("Post Content", value=post, height=300, key="voice_post")
        
        # Wait before reading post to ensure UI is updated
        time.sleep(2)
        
        # Read the post with clear introduction
        speak_and_wait("Here is your generated post. I'll read it to you now.")
        time.sleep(1.5)  # Pause before starting to read
        
        # Calculate approximate reading time based on word count
        # Average reading speed is about 150 words per minute for speaking
        words = len(post.split())
        reading_time = max(5, words / 150 * 60)  # in seconds, minimum 5 seconds
        
        speak_and_wait(post)
        time.sleep(reading_time * 0.2)  # Additional 20% buffer after reading
        
        # Ask for confirmation with significant delay to ensure post is fully read
        speak_and_wait("Do you want to post this on LinkedIn?")
        decision = listen(expected_keywords=["yes", "no"])
        if decision == "yes":
            speak_and_wait("Okay, posting it!")
            # Copy to clipboard
            pyperclip.copy(post)
            # Open LinkedIn
            webbrowser.open("https://www.linkedin.com/feed/")
            st.success("Post has been copied to clipboard and LinkedIn is open!")
        else:
            time.sleep(1)  # Add pause before next prompt
            speak_and_wait("Would you like me to suggest another version?")
            time.sleep(1.5)  # Add pause
            
            decision2 = listen(expected_keywords=["yes", "no"])
            if decision2 == "yes":
                st.info("Generating an alternative post...")
                post2 = generate_post(length, language, tag)
                st.text_area("Alternative Suggestion", value=post2, height=300, key="suggested_post")
                
                # Wait before reading the alternative
                time.sleep(2)
                
                # Read alternative with clear introduction
                speak_and_wait("Here is an alternative suggestion. I'll read it to you now.")
                time.sleep(1.5)  # Pause before starting to read
                
                # Calculate reading time for alternative post
                alt_words = len(post2.split())
                alt_reading_time = max(5, alt_words / 150 * 60)  # in seconds
                
                speak_and_wait(post2)
                time.sleep(alt_reading_time * 0.3)  # 30% buffer after reading
                
                speak_and_wait("Do you want to post this one?")
                final_decision = listen(expected_keywords=["yes", "no"])
                if final_decision == "yes":
                    speak_and_wait("Great! Okay, posting this one.")
                    # Copy to clipboard
                    pyperclip.copy(post2)
                    # Open LinkedIn
                    webbrowser.open("https://www.linkedin.com/feed/")
                    st.success("Alternative post has been copied to clipboard and LinkedIn is open!")
                else:
                    speak_and_wait("No problem. Let me know if you need help again.")
            else:
                speak_and_wait("Alright. You can manually edit or generate again.")

# Manual Input Mode
with tab2:
    st.subheader("Manual LinkedIn Post Generator")
    
    # Initialize FewShotPosts to get available tags
    fs = FewShotPosts()
    available_tags = fs.get_tags()
    
    # Define the input form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_tag = st.selectbox("📌 Topic", options=available_tags)
    
    with col2:
        selected_length = st.selectbox("📝 Length", options=["Short", "Medium", "Long"])
    
    with col3:
        selected_language = st.selectbox("🌐 Language", options=["English", "Hindi", "Hinglish"])
    
    # Generate post button
    if st.button("🚀 Generate Post", key="generate_manual"):
        with st.spinner("Generating your LinkedIn post..."):
            # Generate post ensuring it matches the selected tag
            generated_post = generate_post(selected_length, selected_language, selected_tag)
            st.session_state.manual_post = generated_post
            st.session_state.current_tag = selected_tag  # Store current tag for verification
            
    # Display the generated post if it exists
    if st.session_state.manual_post:
        st.subheader("📝 Generated LinkedIn Post")
        post_area = st.text_area("Post Content", value=st.session_state.manual_post, height=300, key="manual_post_area")
        
        # Action buttons
        st.subheader("Actions")
        col1, col2, col3 = st.columns(3)
        
        # Read post aloud button
        with col1:
            if st.button("🔊 Read Post Aloud", key="read_post_button"):
                with st.spinner("Reading post aloud..."):
                    # Create a progress bar for reading
                    progress_bar = st.progress(0)
                    
                    # Start reading
                    speak_and_wait("Here is your LinkedIn post:")
                    time.sleep(1)  # Pause before reading
                    
                    # Calculate reading time based on word count
                    words = len(st.session_state.manual_post.split())
                    reading_time = max(5, words / 150 * 60)  # in seconds
                    
                    # Update progress bar at start
                    progress_bar.progress(10)
                    
                    # Read the post
                    speak_and_wait(st.session_state.manual_post)
                    
                    # Update progress while reading
                    for i in range(10, 101, 10):
                        time.sleep(reading_time / 10)
                        progress_bar.progress(i)
                    
                    st.success("Reading complete!")
        
        # Post to LinkedIn button
        with col2:
            if st.button("📤 Post to LinkedIn", key="post_linkedin_button"):
                # Copy to clipboard
                pyperclip.copy(st.session_state.manual_post)
                # Open LinkedIn
                webbrowser.open("https://www.linkedin.com/feed/")
                st.success("Your post has been copied to clipboard and LinkedIn is open!")
                
                # Show instructions
                with st.expander("How to post on LinkedIn"):
                    st.markdown("""
                    1. Your post has been copied to clipboard
                    2. LinkedIn should be opening in a new tab
                    3. Click on 'Start a post' at the top of your feed
                    4. Paste your post (Ctrl+V or Cmd+V)
                    5. Click 'Post' to publish
                    """)
        
        # Generate alternative button
        with col3:
            if st.button("🔄 Generate Alternative", key="alt_post_button"):
                with st.spinner("Creating an alternative post..."):
                    # Generate alternative ensuring it matches the selected tag
                    alt_post = generate_post(selected_length, selected_language, selected_tag)
                    st.session_state.alternative_post = alt_post
                    st.session_state.show_alternative = True
        
        # Show alternative post if it exists
        if st.session_state.show_alternative and st.session_state.alternative_post:
            st.subheader("📝 Alternative Post")
            alt_post_area = st.text_area("Alternative Content", value=st.session_state.alternative_post, height=300, key="alt_post_area")
            
            # Alternative post actions
            st.subheader("Alternative Post Actions")
            alt_col1, alt_col2 = st.columns(2)
            
            # Read alternative post aloud button
            with alt_col1:
                if st.button("🔊 Read Alternative Aloud", key="read_alt_button"):
                    with st.spinner("Reading alternative post aloud..."):
                        # Create a progress bar for reading
                        alt_progress_bar = st.progress(0)
                        
                        # Start reading
                        speak_and_wait("Here is your alternative LinkedIn post:")
                        time.sleep(1)  # Pause before reading
                        
                        # Calculate reading time based on word count
                        alt_words = len(st.session_state.alternative_post.split())
                        alt_reading_time = max(5, alt_words / 150 * 60)  # in seconds
                        
                        # Update progress bar at start
                        alt_progress_bar.progress(10)
                        
                        # Read the post
                        speak_and_wait(st.session_state.alternative_post)
                        
                        # Update progress while reading
                        for i in range(10, 101, 10):
                            time.sleep(alt_reading_time / 10)
                            alt_progress_bar.progress(i)
                        
                        st.success("Reading complete!")
            
            # Post alternative to LinkedIn button
            with alt_col2:
                if st.button("📤 Post Alternative to LinkedIn", key="post_alt_button"):
                    # Copy to clipboard
                    pyperclip.copy(st.session_state.alternative_post)
                    # Open LinkedIn
                    webbrowser.open("https://www.linkedin.com/feed/")
                    st.success("Your alternative post has been copied to clipboard and LinkedIn is open!")
                    
                    # Show instructions
                    with st.expander("How to post on LinkedIn"):
                        st.markdown("""
                        1. Your alternative post has been copied to clipboard
                        2. LinkedIn should be opening in a new tab
                        3. Click on 'Start a post' at the top of your feed
                        4. Paste your post (Ctrl+V or Cmd+V)
                        5. Click 'Post' to publish
                        """)