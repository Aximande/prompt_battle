import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import db_manager as db
from PIL import Image
from streamlit_carousel import carousel
from utils.certificate_generator import create_winner_certificate

st.set_page_config(page_title="ESCP AI Champions - Results", layout="wide")

st.title("Prompt Battle Results")

# Get selected session
session_name = db.get_selected_session()
if not session_name:
    st.warning("No session selected. Please choose a session on the home page.")
else:
    st.header(f"Session: {session_name}")
    
    # Get reference image
    ref_url = db.get_img_ref_url(session_name)
    if ref_url:
        st.subheader("Reference Image")
        st.image(ref_url, width=400)
    
    # Get all images for this session
    images = db.get_all_images_for_session(session_name)
    
    if not images:
        st.info("No images have been submitted for this session yet.")
    else:
        # Get votes for this session
        votes = db.get_votes_for_session(session_name)
        
        # Add vote counts to images
        for img in images:
            img["votes"] = votes.get(img["title"], 0)
        
        # Sort images by votes (descending)
        images.sort(key=lambda x: x["votes"], reverse=True)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Winner & Leaderboard", "All Submissions", "Carousel View"])
        
        with tab1:
            # Display winner
            if len(images) > 0 and images[0]["votes"] > 0:
                st.subheader("🏆 Winner 🏆")
                winner = images[0]
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.image(winner["img"])
                with col2:
                    st.write(f"**Author:** {winner['title']}")
                    st.write(f"**Votes:** {winner['votes']}")
                    st.write(f"**Prompt:** {winner['text']}")
                    
                    # Add some congratulatory text
                    st.success(f"Congratulations to {winner['title']} for winning this prompt battle!")
                
                # Add certificate generation
                st.subheader("Winner Certificate")
                
                # Create certificate
                certificate_bytes = create_winner_certificate(
                    winner_image_url=winner["img"],
                    winner_name=winner["title"],
                    prompt=winner["text"],
                    votes=winner["votes"],
                    session_name=session_name
                )
                
                if certificate_bytes:
                    # Display certificate
                    st.image(certificate_bytes, caption="Winner Certificate")
                    
                    # Add download button
                    st.download_button(
                        label="Download Certificate",
                        data=certificate_bytes,
                        file_name=f"ESCP_AI_Champions_Certificate_{winner['title']}.png",
                        mime="image/png"
                    )
            
            # Display leaderboard
            st.subheader("Leaderboard")
            
            # Create dataframe for leaderboard
            leaderboard_data = []
            for img in images:
                leaderboard_data.append({
                    "Author": img["title"],
                    "Votes": img["votes"],
                    "Prompt": img["text"]
                })
            
            # Sort by votes
            leaderboard_df = pd.DataFrame(leaderboard_data).sort_values("Votes", ascending=False)
            
            # Display dataframe
            st.dataframe(leaderboard_df)
            
            # Create a bar chart of votes
            if len(leaderboard_data) > 0:
                st.subheader("Vote Distribution")
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # Only show top 10 if there are many participants
                chart_data = leaderboard_df.head(10) if len(leaderboard_df) > 10 else leaderboard_df
                
                # Create bar chart
                bars = sns.barplot(x="Author", y="Votes", data=chart_data, ax=ax)
                
                # Rotate x labels for better readability
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                
                # Highlight winner's bar
                if len(chart_data) > 0:
                    bars.patches[0].set_facecolor("gold")
                
                st.pyplot(fig)
        
        with tab2:
            # Display all submissions
            st.subheader("All Submissions")
            
            # Display images in a grid
            cols = st.columns(3)
            for i, img_data in enumerate(images):
                with cols[i % 3]:
                    st.image(img_data["img"])
                    st.write(f"**{img_data['title']}** - {img_data['votes']} votes")
                    st.write(f"Prompt: {img_data['text'][:100]}...")
        
        with tab3:
            # Display carousel view
            st.subheader("Carousel View")
            
            # Ensure items are in the correct format for carousel
            carousel_items = []
            for item in images:
                # Make sure each item has the correct format for the carousel
                carousel_item = {
                    "title": f"{item.get('title', '')} - {item.get('votes', 0)} votes",
                    "text": item.get("text", ""),
                    "img": item.get("img", "")
                }
                carousel_items.append(carousel_item)
            
            # Display carousel only if there are items
            if carousel_items:
                try:
                    carousel(items=carousel_items, width=0.9)
                except Exception as e:
                    st.error(f"Error displaying carousel: {e}")
                    # Display images in grid mode as an alternative
                    for item in carousel_items:
                        st.image(item["img"])
                        st.write(item["title"])
            else:
                st.warning("No images to display in the carousel.") 