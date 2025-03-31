import streamlit as st

def pseudo_dialog():
    """
    Display a dialog to enter a username
    """
    with st.form("pseudo_form"):
        st.write("### Welcome to ESCP AI Champions!")
        st.write("Please enter your username to continue.")
        
        pseudo = st.text_input("Username", max_chars=20)
        
        submitted = st.form_submit_button("Continue")
        
        if submitted and pseudo:
            st.session_state["pseudo"] = pseudo
            return True
        
        if submitted and not pseudo:
            st.error("Please enter a username")
            
    return False 