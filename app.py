import streamlit as st
import streamlit.components.v1 as components
import random
import time
import pandas as pd
import os
import json

# --- Page Config ---
st.set_page_config(page_title="Classroom Assistant v4.3", page_icon="🎓", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; color: #2c3e50; }
    .instruction { font-size:20px; color: #555; margin-bottom: 20px;}
    .sentence-box { background-color: #e8f4f8; border-left: 6px solid #3498db; padding: 20px; margin-top: 15px; border-radius: 5px; }
    .sentence-title { color: #2980b9; font-weight: bold; font-size: 18px; margin-bottom: 10px; }
    .sentence-item { font-size: 22px; color: #2c3e50; margin-bottom: 8px; font-family: sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- Initialize Session State ---
if 'students' not in st.session_state:
    st.session_state.students = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack", "Kevin", "Lily", "Mike", "Nina", "Oliver", "Paul", "Queen", "Rick", "Sam", "Tom", "Uma", "Victor", "Wendy", "Zack"]
if 'scores' not in st.session_state:
    st.session_state.scores = {name: 0 for name in st.session_state.students}
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'current_image_name' not in st.session_state:
    st.session_state.current_image_name = ""

# --- Sidebar: Settings ---
st.sidebar.header("⚙️ Settings")
st.sidebar.write("Enter student names below:")
input_names = st.sidebar.text_area("Student List", value="\n".join(st.session_state.students), height=200)
if st.sidebar.button("Update List"):
    new_list = [name.strip() for name in input_names.split('\n') if name.strip()]
    st.session_state.students = new_list
    temp_scores = st.session_state.scores
    st.session_state.scores = {name: temp_scores.get(name, 0) for name in new_list}
    st.success("List updated successfully!")

st.title("🎓 Classroom Assistant")
st.markdown("---")

# --- Seating Chart HTML Generator (Suspense Version) ---
def get_seating_chart_html(student_list):
    col_configs = [3, 4, 4, 5, 5, 3] 
    total_seats = sum(col_configs)
    
    padded_students = student_list[:total_seats] + [""] * (total_seats - len(student_list))
    students_json = json.dumps(padded_students)
    col_config_json = json.dumps(col_configs)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Arial', sans-serif; text-align: center; margin: 0; background-color: transparent;}}
            
            .blackboard {{
                width: 90%;
                background-color: #2d3436;
                color: white;
                margin: 0 auto 20px auto;
                padding: 10px;
                border-radius: 5px;
                font-size: 20px;
                letter-spacing: 2px;
                border: 4px solid #b2bec3;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
            .classroom {{
                display: flex;
                flex-direction: row;
                justify-content: center;
                gap: 15px; 
                padding: 10px;
            }}
            .column {{
                display: flex;
                flex-direction: column;
                gap: 10px; 
            }}
            .seat {{
                width: 70px;
                height: 50px;
                background-color: #dfe6e9;
                border: 2px solid #b2bec3;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 16px;
                color: #2d3436;
                transition: all 0.1s;
                position: relative;
            }}
            .seat.empty {{
                background-color: #f1f2f6;
                color: #ccc;
                border: 2px dashed #dcdde1;
            }}
            .seat.active {{
                background-color: #e17055 !important;
                color: white !important;
                border: 3px solid #d63031 !important;
                transform: scale(1.1);
                box-shadow: 0 0 15px rgba(225, 112, 85, 0.8);
                z-index: 10;
            }}
            .seat.winner {{
                background-color: #00b894 !important;
                color: white !important;
                border: 3px solid #00cec9 !important;
                transform: scale(1.2);
                animation: pulse 1s infinite;
                z-index: 10;
            }}
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(0, 184, 148, 0.7); }}
                70% {{ box-shadow: 0 0 0 10px rgba(0, 184, 148, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(0, 184, 148, 0); }}
            }}
            #runBtn {{
                margin-top: 20px;
                padding: 10px 30px;
                font-size: 20px;
                background-color: #0984e3;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            #runBtn:hover {{ background-color: #74b9ff; }}
            #runBtn:disabled {{ background-color: #ccc; cursor: not-allowed; }}
            
            #winner-display {{
                height: 40px;
                margin-top: 10px;
                font-size: 24px;
                color: #d63031;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="blackboard">BLACKBOARD</div>
        <div class="classroom" id="classroom-container"></div>
        <div id="winner-display"></div>
        <button id="runBtn" onclick="startRoulette()">🎲 Start Picker</button>

        <script>
            const students = {students_json};
            const colConfig = {col_config_json};
            let allSeats = []; 

            function initClassroom() {{
                const container = document.getElementById('classroom-container');
                let studentIndex = 0;
                colConfig.forEach((seatsInCol, colIndex) => {{
                    const colDiv = document.createElement('div');
                    colDiv.className = 'column';
                    for (let i = 0; i < seatsInCol; i++) {{
                        const seatDiv = document.createElement('div');
                        seatDiv.className = 'seat';
                        const name = students[studentIndex] || "";
                        seatDiv.innerText = name;
                        if (name === "") {{
                            seatDiv.classList.add('empty');
                        }} else {{
                            seatDiv.id = 'seat-' + studentIndex;
                            allSeats.push(seatDiv);
                        }}
                        colDiv.appendChild(seatDiv);
                        studentIndex++;
                    }}
                    container.appendChild(colDiv);
                }});
            }}

            function startRoulette() {{
                if (allSeats.length === 0) return;
                const btn = document.getElementById('runBtn');
                const winDisplay = document.getElementById('winner-display');
                btn.disabled = true;
                winDisplay.innerText = "Picking a lucky student...";
                allSeats.forEach(s => s.classList.remove('active', 'winner'));

                let steps = 0;
                // Suspense Logic: 30-40 steps total
                const totalSteps = 30 + Math.floor(Math.random() * 10); 
                let currentSpeed = 50; 
                let currentIndex = Math.floor(Math.random() * allSeats.length);

                function nextStep() {{
                    allSeats.forEach(s => s.classList.remove('active'));
                    currentIndex = (currentIndex + 1) % allSeats.length;
                    const currentSeat = allSeats[currentIndex];
                    currentSeat.classList.add('active');
                    steps++;

                    if (steps < totalSteps) {{
                        const remaining = totalSteps - steps;
                        
                        // Slow down in the last 15 steps
                        if (remaining < 15) {{
                            if (remaining < 5) {{
                                // Super slow for the last few steps
                                currentSpeed += 150; 
                            }} else {{
                                currentSpeed += 40; 
                            }}
                        }}
                        
                        setTimeout(nextStep, currentSpeed);
                    }} else {{
                        finalize(currentSeat);
                    }}
                }}
                nextStep();
            }}

            function finalize(seat) {{
                seat.classList.remove('active');
                seat.classList.add('winner');
                const name = seat.innerText;
                document.getElementById('winner-display').innerText = "🎉 " + name + " 🎉";
                document.getElementById('runBtn').disabled = false;
            }}
            initClassroom();
        </script>
    </body>
    </html>
    """
    return html_code

# --- Tabs (Removed Wheel) ---
tab_pic, tab_seat, tab_group, tab_score, tab_timer = st.tabs(["🖼️ Look & Say", "🪑 Seating Chart", "👥 Groups", "🏆 Scoreboard", "⏱️ Timer"])

# === Tab 0: Look & Say ===
with tab_pic:
    st.header("🖼️ Look & Say: What is he/she doing?")
    st.markdown('<div class="instruction">Please answer using the sentence patterns below:</div>', unsafe_allow_html=True)
    sentence_map = {
        "lie": ["He/She is lying because...", "I think he/she is telling a lie since...", "Look at his/her face! It looks fake because..."],
        "lying": ["He/She is lying because...", "I don't believe him/her because...", "He/She is hiding the truth that..."],
        "run": ["He/She is running fast because...", "He/She is in a hurry to...", "Maybe he/she is late for..."],
        "eat": ["He/She is eating ______ because...", "The food looks delicious, so he/she...", "He/She is having lunch at..."],
        "sleep": ["He/She is sleeping because...", "He/She must be very tired from...", "He/She is dreaming about..."]
    }
    default_sentences = ["He/She is [ v-ing ] because...", "I think he/she looks [ adjective ]...", "In this picture, the person is..."]
    
    col_btn, col_img = st.columns([1, 3])
    with col_btn:
        if st.button("📸 Pick Random Image", type="primary", use_container_width=True):
            script_dir = os.path.dirname(os.path.abspath(__file__)) 
            folder_path = os.path.join(script_dir, "images")
            if not os.path.exists(folder_path):
                st.error(f"⚠️ Image folder not found!\nPath: {folder_path}")
            else:
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
                try:
                    files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in valid_extensions]
                    if not files: st.warning("⚠️ The 'images' folder is empty!")
                    else:
                        selected_img = random.choice(files)
                        st.session_state.current_image = os.path.join(folder_path, selected_img)
                        st.session_state.current_image_name = selected_img.lower()
                except Exception as e: st.error(f"Error: {e}")
    with col_img:
        if st.session_state.current_image:
            st.image(st.session_state.current_image, use_container_width=True)
            current_name = st.session_state.current_image_name
            target_sentences = default_sentences
            for key, sentences in sentence_map.items():
                if key in current_name:
                    target_sentences = sentences
                    break
            st.markdown('<div class="sentence-box"><div class="sentence-title">💡 Useful Expressions:</div>', unsafe_allow_html=True)
            for s in target_sentences: st.markdown(f'<div class="sentence-item">👉 {s}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Please click the button to start.")

# === Tab NEW: Seating Chart ===
with tab_seat:
    st.header("🪑 Seating Chart Picker")
    st.markdown("Randomly picks a student from the seating chart.")
    
    if not st.session_state.students:
        st.error("Student list is empty! Please add names in the Settings sidebar.")
    else:
        chart_html = get_seating_chart_html(st.session_state.students)
        components.html(chart_html, height=600)

# === Tab 2: Groups ===
with tab_group:
    st.header("👥 Group Generator")
    g_size = st.number_input("Group Size", 2, 10, 3)
    if st.button("Generate Groups"):
        shuffled = st.session_state.students.copy()
        random.shuffle(shuffled)
        groups = [shuffled[i:i + g_size] for i in range(0, len(shuffled), g_size)]
        cols = st.columns(3)
        for i, group in enumerate(groups):
            with cols[i % 3]:
                st.markdown(f"**Group {i+1}**")
                st.success(", ".join(group))

# === Tab 3: Scoreboard ===
with tab_score:
    st.header("🏆 Scoreboard")
    cd, ca = st.columns([2, 1])
    with ca:
        sel_stu = st.selectbox("Select Student", st.session_state.students)
        pts = st.number_input("Points", -10, 10, 1)
        if st.button("Update Score"):
            st.session_state.scores[sel_stu] += pts
            st.success(f"{sel_stu}'s score updated!")
    with cd:
        df = pd.DataFrame(list(st.session_state.scores.items()), columns=['Name', 'Score']).sort_values(by='Score', ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)

# === Tab 4: Timer ===
with tab_timer:
    st.header("⏱️ Timer")
    c1, c2 = st.columns(2)
    mins = c1.number_input("Minutes", 0, 60, 1)
    secs = c2.number_input("Seconds", 0, 59, 0)
    if st.button("Start Timer"):
        t_ph = st.empty()
        bar = st.progress(1.0)
        tot = mins * 60 + secs
        for i in range(tot, -1, -1):
            m, s = divmod(i, 60)
            t_ph.metric("Time Left", f"{m:02d}:{s:02d}")
            bar.progress(i / tot if tot > 0 else 0)
            time.sleep(1)
        st.balloons()
        st.success("Time's up!")