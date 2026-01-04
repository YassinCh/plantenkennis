import streamlit as st
from pathlib import Path
from core import Plant, Quiz, load_plants, get_random_image, Progress

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "plants.csv"
CACHE_DIR = ROOT / "cache"
IMAGE_DIR = CACHE_DIR / "images_powo"

progress = Progress(CACHE_DIR)
all_plants = load_plants(DATA_PATH)

st.set_page_config(page_title="Planten Quiz", page_icon="🌿")

# Sidebar
with st.sidebar:
    st.title("🌿 Planten Quiz")
    mistakes = progress.get_mistakes()
    mode = st.radio("Modus", ["Hoofdquiz", f"Oefenen ({len(mistakes)} fouten)"])
    practice_mode = mode.startswith("Oefenen")

    if st.button("Opnieuw starten"):
        st.session_state.clear()
        st.rerun()

    prog = progress.get_progress()
    if prog["sessions"]:
        st.divider()
        st.metric("Hoogste score", f"{prog['high_score']}")
        st.caption(f"{len(prog['sessions'])} sessies voltooid")

# Initialize quiz
def get_quiz_plants() -> list[Plant]:
    if practice_mode:
        return [p for p in all_plants if p.latin in mistakes]
    return all_plants

if "quiz" not in st.session_state or st.session_state.get("mode") != mode:
    plants = get_quiz_plants()
    if plants:
        st.session_state.quiz = Quiz(plants)
        st.session_state.mode = mode
        st.session_state.feedback = None
        st.session_state.answered = False

quiz: Quiz = st.session_state.get("quiz")

# No plants for practice mode
if not quiz or not quiz.plants:
    st.success("🎉 Geen fouten om te oefenen! Start de hoofdquiz.")
    st.stop()

# Quiz done
if quiz.is_done:
    st.balloons()
    st.title(f"Klaar! Cijfer: {quiz.grade()}")
    st.write(f"**Nederlands correct:** {quiz.dutch_score}/{len(quiz.plants)}")
    st.write(f"**Latijn correct:** {quiz.latin_score}/{len(quiz.plants)}")
    st.write(f"**Totaal:** {quiz.total_score}/{quiz.max_score} punten")

    if not practice_mode:
        progress.save_session(quiz.total_score, quiz.max_score, quiz.grade())

    if st.button("Nog een keer"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# Current plant
plant = quiz.current
st.progress((quiz.index) / len(quiz.plants))
st.caption(f"Plant {quiz.index + 1} van {len(quiz.plants)} | Score: {quiz.total_score}/{quiz.index * 3}")

# Initialize image state for current plant
if st.session_state.get("current_plant_idx") != quiz.index:
    st.session_state.current_plant_idx = quiz.index
    st.session_state.current_image = get_random_image(plant.latin, IMAGE_DIR)
    st.session_state.image_changes = 0

# Display image
image_path = st.session_state.current_image
if image_path and image_path.exists():
    st.image(str(image_path), use_container_width=True)
else:
    st.warning(f"Geen afbeelding gevonden voor {plant.latin}")

# Button to get another image (max 2 times)
if not st.session_state.get("answered"):
    remaining = 2 - st.session_state.get("image_changes", 0)
    if remaining > 0:
        if st.button(f"Andere afbeelding ({remaining}x)", use_container_width=True):
            st.session_state.current_image = get_random_image(plant.latin, IMAGE_DIR)
            st.session_state.image_changes += 1
            st.rerun()

# Input form
if not st.session_state.get("answered"):
    with st.form("answer_form"):
        dutch = st.text_input("Nederlandse naam:")
        latin = st.text_input("Latijnse naam:")
        submitted = st.form_submit_button("Controleer", use_container_width=True)

        if submitted:
            dutch_ok, latin_ok = quiz.check(dutch, latin)

            # Track mistakes
            if not practice_mode:
                if not dutch_ok or not latin_ok:
                    progress.add_mistake(plant.latin)
                elif plant.latin in progress.get_mistakes():
                    progress.remove_mistake(plant.latin)

            st.session_state.feedback = (dutch_ok, latin_ok, plant)
            st.session_state.answered = True
            st.rerun()

# Show feedback
if st.session_state.get("answered"):
    dutch_ok, latin_ok, answered_plant = st.session_state.feedback

    if dutch_ok and latin_ok:
        st.success("✅ Beide correct!")
    else:
        parts = []
        if dutch_ok:
            parts.append("✅ Nederlands correct")
        else:
            parts.append(f"❌ Nederlands: **{answered_plant.dutch[0]}**")
        if latin_ok:
            parts.append("✅ Latijn correct")
        else:
            parts.append(f"❌ Latijn: **{answered_plant.latin}**")
        st.warning(" | ".join(parts))

    if st.button("Volgende plant →", use_container_width=True):
        quiz.next()
        st.session_state.answered = False
        st.session_state.feedback = None
        st.rerun()
