import firebase_admin
from firebase_admin import credentials, initialize_app, storage, db, firestore, auth
import streamlit as st

import threading

callback_done = threading.Event()


@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            "./auth_firebase/prompt-battle-9b72d-firebase-adminsdk-lhuc9-cc4c55a33e.json"
        )
        initialize_app(
            cred,
            {
                "storageBucket": "prompt-battle-14a49.appspot.com",
            },
        )


def add_image(session_name, username, img_url, prompt):
    db = firestore.client()
    db.collection("sessions").document(session_name).collection("images").document(
        username
    ).set({"img_url": img_url, "prompt": prompt})


def get_all_images_for_session(session_name):
    db = firestore.client()
    imgs = db.collection("sessions").document(session_name).collection("images").get()
    all_images = []
    for img in imgs:
        usr = img.id
        img = img.to_dict()
        all_images.append(
            dict(
                title=usr,
                text=img["prompt"],
                img=img["img_url"],
            )
        )
    return all_images


def get_all_session_names():
    db = firestore.client()
    docs = db.collection("sessions").get()
    names = []
    for doc in docs:
        names.append(doc.id)
        # print(f"{doc.id} => {doc.to_dict()}")
    return names


def select_session(session_name):
    db = firestore.client()
    db.collection("admin").document("lavaleexx").set(
        {"selected_session": session_name}, merge=True
    )


def get_selected_session():
    db = firestore.client()
    return (
        db.collection("admin").document("lavaleexx").get().to_dict()["selected_session"]
    )


def get_img_ref_url(session_name):
    db = firestore.client()
    return (
        db.collection("sessions").document(session_name).get().to_dict()["img_ref_url"]
    )


def _delete_collection(coll_ref, batch_size):
    if batch_size == 0:
        return

    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return _delete_collection(coll_ref, batch_size)


def clear_session(session_name):
    db = firestore.client()
    col = db.collection("sessions").document(session_name).collection("images")
    _delete_collection(col, 15)


# def get_selection_watch():
#     # Create an Event for notifying main thread.
#     db = firestore.client()
#     callback_done = threading.Event()

#     # Create a callback on_snapshot function to capture changes
#     def on_snapshot(doc_snapshot, changes, read_time):
#         for doc in doc_snapshot:
#             st.session_state["selected_session_db"] = doc.to_dict()["selected_session"]
#         callback_done.set()

#     doc_ref = db.collection("admin").document("lavaleexx")

#     # Watch the document
#     return callback_done, doc_ref.on_snapshot(on_snapshot)
