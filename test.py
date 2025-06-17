import streamlit as st
import random
from collections import defaultdict

# Preloaded flashcards
PRELOADED_CARDS = [
    {"front": "नमस्ते", "back": "Hello"},
    {"front": "पानी", "back": "Water"},
    {"front": "धन्यवाद", "back": "Thank you"},
    {"front": "मित्र", "back": "Friend"},
    {"front": "पुस्तक", "back": "Book"},
    {"front": "खाना", "back": "Food"},
    {"front": "घर", "back": "House"},
    {"front": "स्कूल", "back": "School"},
    {"front": "शुभ रात्री", "back": "Good night"},
    {"front": "कृपया", "back": "Please"},
]

# Initialize session state for cards and stats
if "cards" not in st.session_state:
    st.session_state.cards = PRELOADED_CARDS.copy()
if "reviewed" not in st.session_state:
    st.session_state.reviewed = defaultdict(lambda: {"shown": 0, "correct": 0})
if "review_index" not in st.session_state:
    st.session_state.review_index = 0
if "show_back" not in st.session_state:
    st.session_state.show_back = False

# Sidebar Navigation
st.sidebar.title("Flashcard App")
page = st.sidebar.radio("Go to", ("Review", "Search", "Create", "Statistics"))

# Review Interface
if page == "Review":
    st.header("Review Flashcards")

    # Handle out-of-bounds
    if not st.session_state.cards:
        st.info("No cards to review. Please add some cards first.")
    else:
        card = st.session_state.cards[st.session_state.review_index]
        st.markdown(
            f"""<div style='
                display: flex; justify-content: center; align-items: center; 
                height: 250px; width: 350px; 
                border-radius: 20px; background: #ffe4b2; 
                font-size: 2em; box-shadow: 0 0 20px #ccc;
                perspective: 600px; margin: 0 auto;
            '>
                <div style='
                    width: 100%; height: 100%; text-align: center;
                    transition: transform 0.6s cubic-bezier(.42,0,.58,1);
                    transform: rotateY({180 if st.session_state.show_back else 0}deg);
                '>
                    {card['back'] if st.session_state.show_back else card['front']}
                </div>
            </div>
            """, unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("⬅️ Prev"):
                st.session_state.review_index = (st.session_state.review_index - 1) % len(st.session_state.cards)
                st.session_state.show_back = False
        with col2:
            if st.button("Flip (Space)"):
                st.session_state.show_back = not st.session_state.show_back
        with col3:
            if st.button("Next ➡️"):
                st.session_state.review_index = (st.session_state.review_index + 1) % len(st.session_state.cards)
                st.session_state.show_back = False

        # Correct / Incorrect buttons
        col4, col5 = st.columns([1, 1])
        with col4:
            if st.button("👍 Got it!"):
                idx = st.session_state.review_index
                key = f"{st.session_state.cards[idx]['front']}-{st.session_state.cards[idx]['back']}"
                st.session_state.reviewed[key]["shown"] += 1
                st.session_state.reviewed[key]["correct"] += 1
                st.success("Marked correct!")
        with col5:
            if st.button("👎 Missed it"):
                idx = st.session_state.review_index
                key = f"{st.session_state.cards[idx]['front']}-{st.session_state.cards[idx]['back']}"
                st.session_state.reviewed[key]["shown"] += 1
                st.warning("Marked incorrect!")

    st.markdown("<small>Tip: Use the Flip button to show translation.</small>", unsafe_allow_html=True)

# Search Interface
elif page == "Search":
    st.header("Search Flashcards")
    query = st.text_input("Type to search (Hindi or English)...").strip().lower()
    results = []
    for card in st.session_state.cards:
        if query in card['front'].lower() or query in card['back'].lower():
            results.append(card)
    st.write(f"Found {len(results)} card(s):")
    for card in results:
        st.markdown(f"**Hindi:** {card['front']} &nbsp;&nbsp;|&nbsp;&nbsp; **English:** {card['back']}")

# Create Interface
elif page == "Create":
    st.header("Create a New Flashcard")
    with st.form("create_card"):
        front = st.text_input("Front (Hindi)")
        back = st.text_input("Back (English)")
        submitted = st.form_submit_button("Add Card")
        if submitted:
            if not front or not back:
                st.error("Both fields required.")
            else:
                st.session_state.cards.append({"front": front, "back": back})
                st.success("Card added!")

# Statistics Interface
elif page == "Statistics":
    st.header("Your Flashcard Stats")
    total = sum(st.session_state.reviewed[key]["shown"] for key in st.session_state.reviewed)
    correct = sum(st.session_state.reviewed[key]["correct"] for key in st.session_state.reviewed)
    percent = (correct / total * 100) if total > 0 else 0

    st.metric("Cards Reviewed", total)
    st.metric("Correct Answers", correct)
    st.metric("Percent Correct", f"{percent:.1f}%")

    # Bar chart per card
    import pandas as pd
    if st.session_state.reviewed:
        data = []
        for key in st.session_state.reviewed:
            shown = st.session_state.reviewed[key]["shown"]
            correct = st.session_state.reviewed[key]["correct"]
            data.append({
                "Card": key,
                "Reviewed": shown,
                "Correct": correct,
                "Accuracy %": (correct / shown * 100) if shown else 0,
            })
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index("Card")[["Reviewed", "Correct"]])
        st.dataframe(df)
    else:
        st.info("No stats yet! Review some cards.")