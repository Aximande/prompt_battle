import streamlit as st

def pseudo_dialog():
    """
    Affiche une boîte de dialogue pour saisir un pseudo.
    """
    if "pseudo_submitted" not in st.session_state:
        st.session_state["pseudo_submitted"] = False
    
    if not st.session_state["pseudo_submitted"]:
        with st.container():
            st.subheader("Enter your username")
            pseudo = st.text_input("What is your username?")
            if st.button("Submit"):
                st.session_state["pseudo"] = pseudo
                st.session_state["pseudo_submitted"] = True
                st.rerun() 