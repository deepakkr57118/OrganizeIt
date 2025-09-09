import streamlit as st
import os
import shutil
from streamlit_tree_select import tree_select

def organizer(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    filetypes = list(set([os.path.splitext(file)[1].lower().strip('.') for file in files if '.' in file]))

    for filetype in filetypes:
        folder_path = os.path.join(path, filetype.upper())
        os.makedirs(folder_path, exist_ok=True)

        for file in files:
            ext = os.path.splitext(file)[1].lower().strip('.')
            if ext == filetype:
                src = os.path.join(path, file)
                dst = os.path.join(folder_path, file)
                if not os.path.exists(dst):
                    os.rename(src, dst)
    return "✅ Files successfully organised!"

def reverse(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(path, file)
            if os.path.exists(dst):
                name, ext = os.path.splitext(file)
                dst = os.path.join(path, f"{name}_copy{ext}")
            shutil.move(src, dst)

        for d in dirs:
            folder_path = os.path.join(root, d)
            if os.path.isdir(folder_path):
                try:
                    os.rmdir(folder_path)
                except OSError:
                    pass
    return "✅ All files moved back!"

def exit_app():
    st.session_state["folder_path"] = ""

def show_tree_with_collapse(path):
    try:
        items = os.listdir(path)
    except PermissionError:
        st.warning("⚠️ Permission Denied")
        return

    folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
    files = [f for f in items if os.path.isfile(os.path.join(path, f))]

    for folder in folders:
        folder_path = os.path.join(path, folder)
        with st.expander(f"📂 {folder}", expanded=False):
            show_tree_with_collapse(folder_path)

    for file in files:
        st.markdown(f"📄 {file}")

# ------------------------------
# UI Section
# ------------------------------
st.title("📂 File Organizer Tool ")

default_path = "/app/data"
folder_path = st.text_input("Enter folder path:", value=default_path, key="folder_path")

# ---- FILE UPLOAD SECTION ----
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        save_path = os.path.join(default_path, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Saved {uploaded_file.name} to {save_path}")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📁 Organize"):
        if os.path.exists(folder_path):
            msg = organizer(folder_path)
            st.success(msg)
            with st.expander("📂 Organized Folder Structure", expanded=True):
                show_tree_with_collapse(folder_path)

with col2:
    if st.button("🔙 Original"):
        if os.path.exists(folder_path):
            msg = reverse(folder_path)
            st.success(msg)
            with st.expander("📂 Original Folder ", expanded=True):
                show_tree_with_collapse(folder_path)

with col3:
    st.button("🔄 Clear", on_click=exit_app)
