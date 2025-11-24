import streamlit as st
import streamlit.components.v1 as components
import random
import time
import pandas as pd
import os
import json

# --- Page Config ---
st.set_page_config(page_title="Classroom Assistant v7.0", page_icon="🎓", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; color: #2c3e50; }
    .instruction { font-size:20px; color: #555; margin-bottom: 20px;}
    .sentence-box { background-color: #e8f4f8; border-left: 6px solid #3498db; padding: 20px; margin-top: 15px; border-radius: 5px; }
    .sentence-title { color: #2980b9; font-weight: bold; font-size: 18px; margin-bottom: 10px; }
    .sentence-item { font-size: 22px; color: #2c3e50; margin-bottom: 8px; font-family: sans-serif; }
    
    /* Group Card Styling */
    .group-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #d1d5db;
        margin-bottom: 10px;
        text-align: center;
    }
    .group-title { font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;}
    .group-score { font-size: 32px; font-weight: bold; color: #e74c3c; margin: 10px 0; }
    .group-members { color: #555; font-size: 14px; min-height: 40px;}
    </style>
    """, unsafe_allow_html=True)

# --- 💾 DATA PERSISTENCE ---
DATA_FILE = "classroom_data.csv"
DEFAULT_STUDENTS = [
    "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", 
    "Henry", "Ivy", "Jack", "Kevin", "Lily", "Mike", "Nina", "Oliver", 
    "Paul", "Queen", "Rick", "Sam", "Tom", "Uma", "Victor", 
    "Wendy", "Xander", "Yara", "Zoe", "Leo", "Mia", "Ben"
]

def save_data(student_list, score_dict):
    try:
        data = []
        for name in student_list:
            data.append({"Name": name, "Score": score_dict.get(name, 0)})
        df = pd.DataFrame(data)
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_data():
    default_scores = {name: 0 for name in DEFAULT_STUDENTS}
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if df.empty: return DEFAULT_STUDENTS, default_scores
            if "Name" not in df.columns or "Score" not in df.columns: return DEFAULT_STUDENTS, default_scores
            
            loaded_students = df["Name"].astype(str).tolist()
            loaded_scores = dict(zip(df["Name"].astype(str), df["Score"].astype(int)))
            for name in loaded_students:
                if name not in loaded_scores: loaded_scores[name] = 0
            return loaded_students, loaded_scores
        except: return DEFAULT_STUDENTS, default_scores
    else: return DEFAULT_STUDENTS, default_scores

# --- Initialize Session State ---
if 'students' not in st.session_state or 'scores' not in st.session_state:
    l_students, l_scores = load_data()
    st.session_state.students = l_students
    st.session_state.scores = l_scores

if 'current_image' not in st.session_state: st.session_state.current_image = None
if 'current_image_name' not in st.session_state: st.session_state.current_image_name = ""
if 'available_images' not in st.session_state: st.session_state.available_images = []

# ✨ NEW: Store Groups in Session State
if 'groups' not in st.session_state:
    st.session_state.groups = []

# --- Sidebar: Settings ---
st.sidebar.header("⚙️ Settings")
st.sidebar.subheader("Student List")
input_names = st.sidebar.text_area("Names (one per line)", value="\n".join(st.session_state.students), height=150)
if st.sidebar.button("Update List"):
    new_list = [name.strip() for name in input_names.split('\n') if name.strip()]
    if not new_list: st.sidebar.error("List cannot be empty!")
    else:
        new_scores = {}
        for name in new_list: new_scores[name] = st.session_state.scores.get(name, 0)
        st.session_state.students = new_list
        st.session_state.scores = new_scores
        save_data(new_list, new_scores)
        st.session_state.groups = [] # Reset groups if list changes
        st.success("List updated!")
        time.sleep(0.5)
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("⚠️ Reset All Data"):
    if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
    st.session_state.students = DEFAULT_STUDENTS
    st.session_state.scores = {name: 0 for name in DEFAULT_STUDENTS}
    st.session_state.groups = []
    st.sidebar.success("Data reset!")
    time.sleep(0.5)
    st.rerun()

st.title("🎓 Classroom Assistant")
st.markdown("---")

# --- HTML Generator: Seating Chart with Drag & Drop ---
def get_seating_chart_html(student_list):
    col_configs = [3, 4, 4, 5, 5, 5, 3] 
    total_seats = sum(col_configs)
    padded_students = student_list[:total_seats] + [""] * (total_seats - len(student_list))
    students_json = json.dumps(padded_students)
    col_config_json = json.dumps(col_configs)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Arial', sans-serif; text-align: center; margin: 0; background-color: transparent; user-select: none; }}
            .controls {{ margin-bottom: 10px; display: flex; justify-content: center; gap: 10px; align-items: center;}}
            .hint {{ color: #666; font-size: 14px; font-style: italic; }}
            .reset-link {{ color: #0984e3; cursor: pointer; text-decoration: underline; font-size: 14px; border: none; background: none; }}
            .blackboard {{ width: 90%; background-color: #2d3436; color: white; margin: 0 auto 10px auto; padding: 10px; border-radius: 5px; font-size: 20px; letter-spacing: 2px; border: 4px solid #b2bec3; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .classroom {{ display: flex; flex-direction: row; justify-content: center; gap: 10px; padding: 10px; overflow-x: auto; }}
            .column {{ display: flex; flex-direction: column; gap: 10px; }}
            .seat {{ width: 65px; height: 45px; background-color: #dfe6e9; border: 2px solid #b2bec3; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; color: #2d3436; position: relative; cursor: grab; transition: transform 0.2s, box-shadow 0.2s; }}
            .seat:hover {{ border-color: #74b9ff; }}
            .seat:active {{ cursor: grabbing; }}
            .seat.empty {{ background-color: #f1f2f6; color: #ccc; border: 2px dashed #dcdde1; cursor: default; }}
            .seat.dragging {{ opacity: 0.4; border: 2px dashed #0984e3; }}
            .seat.over {{ border: 3px solid #00b894; transform: scale(1.05); }}
            .seat.active {{ background-color: #e17055 !important; color: white !important; border: 3px solid #d63031 !important; transform: scale(1.1); box-shadow: 0 0 15px rgba(225, 112, 85, 0.8); z-index: 10; }}
            .seat.winner {{ background-color: #00b894 !important; color: white !important; border: 3px solid #00cec9 !important; transform: scale(1.2); animation: pulse 1s infinite; z-index: 10; }}
            @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(0, 184, 148, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(0, 184, 148, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(0, 184, 148, 0); }} }}
            #runBtn {{ margin-top: 20px; padding: 10px 30px; font-size: 20px; background-color: #0984e3; color: white; border: none; border-radius: 5px; cursor: pointer; }}
            #runBtn:hover {{ background-color: #74b9ff; }}
            #runBtn:disabled {{ background-color: #ccc; cursor: not-allowed; }}
            #winner-display {{ height: 40px; margin-top: 10px; font-size: 24px; color: #d63031; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="blackboard">BLACKBOARD</div>
        <div class="controls">
            <span class="hint">💡 Drag and drop to swap seats!</span>
            <button class="reset-link" onclick="resetToSidebarList()">🔄 Reset to Sidebar List</button>
        </div>
        <div class="classroom" id="classroom-container"></div>
        <div id="winner-display"></div>
        <button id="runBtn" onclick="startRoulette()">🎲 Start Picker</button>
        <script>
            const pythonStudents = {students_json};
            const colConfig = {col_config_json};
            let allSeats = []; 
            let dragSrcEl = null;

            function loadSeatOrder() {{
                const savedOrder = localStorage.getItem('classroom_seats_v6');
                if (savedOrder) {{ return JSON.parse(savedOrder); }}
                return pythonStudents;
            }}
            function saveSeatOrder() {{
                const currentOrder = [];
                document.querySelectorAll('.seat').forEach(seat => {{ currentOrder.push(seat.innerText); }});
                localStorage.setItem('classroom_seats_v6', JSON.stringify(currentOrder));
            }}
            function resetToSidebarList() {{
                localStorage.removeItem('classroom_seats_v6');
                location.reload(); 
            }}
            function handleDragStart(e) {{
                this.style.opacity = '0.4';
                dragSrcEl = this;
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerText);
            }}
            function handleDragOver(e) {{ if (e.preventDefault) {{ e.preventDefault(); }} e.dataTransfer.dropEffect = 'move'; return false; }}
            function handleDragEnter(e) {{ this.classList.add('over'); }}
            function handleDragLeave(e) {{ this.classList.remove('over'); }}
            function handleDrop(e) {{
                if (e.stopPropagation) {{ e.stopPropagation(); }}
                if (dragSrcEl !== this) {{
                    const srcName = dragSrcEl.innerText;
                    const destName = this.innerText;
                    dragSrcEl.innerText = destName;
                    this.innerText = srcName;
                    checkEmpty(dragSrcEl);
                    checkEmpty(this);
                    saveSeatOrder();
                }}
                return false;
            }}
            function handleDragEnd(e) {{
                this.style.opacity = '1';
                allSeats.forEach(seat => {{ seat.classList.remove('over'); }});
            }}
            function checkEmpty(seat) {{
                if (seat.innerText === "") {{ seat.classList.add('empty'); seat.draggable = false; }} 
                else {{ seat.classList.remove('empty'); seat.draggable = true; }}
            }}
            function addDnDHandlers(seat) {{
                if (seat.innerText !== "") {{
                    seat.draggable = true;
                    seat.addEventListener('dragstart', handleDragStart, false);
                }}
                seat.addEventListener('dragenter', handleDragEnter, false);
                seat.addEventListener('dragover', handleDragOver, false);
                seat.addEventListener('dragleave', handleDragLeave, false);
                seat.addEventListener('drop', handleDrop, false);
                seat.addEventListener('dragend', handleDragEnd, false);
            }}
            function initClassroom() {{
                const container = document.getElementById('classroom-container');
                const studentList = loadSeatOrder(); 
                let studentIndex = 0;
                allSeats = []; 
                colConfig.forEach((seatsInCol) => {{
                    const colDiv = document.createElement('div');
                    colDiv.className = 'column';
                    for (let i = 0; i < seatsInCol; i++) {{
                        const seatDiv = document.createElement('div');
                        seatDiv.className = 'seat';
                        const name = studentList[studentIndex] || "";
                        seatDiv.innerText = name;
                        checkEmpty(seatDiv);
                        addDnDHandlers(seatDiv);
                        if (name !== "") {{ seatDiv.id = 'seat-' + studentIndex; }}
                        allSeats.push(seatDiv);
                        colDiv.appendChild(seatDiv);
                        studentIndex++;
                    }}
                    container.appendChild(colDiv);
                }});
            }}
            function startRoulette() {{
                const activeSeats = allSeats.filter(s => s.innerText !== "");
                if (activeSeats.length === 0) return;
                const btn = document.getElementById('runBtn');
                const winDisplay = document.getElementById('winner-display');
                btn.disabled = true;
                winDisplay.innerText = "Picking a lucky student...";
                activeSeats.forEach(s => s.classList.remove('active', 'winner'));
                let steps = 0;
                const totalSteps = 30 + Math.floor(Math.random() * 10); 
                let currentSpeed = 50; 
                let currentIndex = Math.floor(Math.random() * activeSeats.length);
                function nextStep() {{
                    activeSeats.forEach(s => s.classList.remove('active'));
                    currentIndex = (currentIndex + 1) % activeSeats.length;
                    const currentSeat = activeSeats[currentIndex];
                    currentSeat.classList.add('active');
                    steps++;
                    if (steps < totalSteps) {{
                        const remaining = totalSteps - steps;
                        if (remaining < 15) {{
                            if (remaining < 5) {{ currentSpeed += 150; }} else {{ currentSpeed += 40; }}
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
                document.getElementById('winner-display').innerText = "🎉 " + seat.innerText + " 🎉";
                document.getElementById('runBtn').disabled = false;
            }}
            initClassroom();
        </script>
    </body>
    </html>
    """
    return html_code

# --- Tabs ---
tab_pic, tab_seat, tab_group, tab_score, tab_timer = st.tabs(["🖼️ Look & Say", "🪑 Seating Chart", "⚔️ Group Battle", "🏆 Scoreboard", "⏱️ Timer"])

# === Tab 0: Look & Say ===
with tab_pic:
    st.header("🖼️ Look & Say: What is he/she doing?")
    st.markdown('<div class="instruction">Please use the pattern: <b>"I think he/she is..., because..."</b></div>', unsafe_allow_html=True)
    sentence_map = {
        "lie": ["I think he/she is lying, because he looks nervous.", "I think he/she is telling a lie, because his nose is growing.", "I think he/she is being dishonest, because he is hiding something."],
        "lying": ["I think he/she is lying, because he looks uncomfortable.", "I think he/she is faking it, because his smile looks fake.", "I think he/she is not telling the truth, because..."],
        "run": ["I think he/she is running, because he is late for school.", "I think he/she is rushing, because the bus is leaving.", "I think he/she is exercising, because he wants to be healthy."],
        "eat": ["I think he/she is eating a burger, because he looks hungry.", "I think he/she is having lunch, because it is noon.", "I think he/she is enjoying the meal, because it looks delicious."],
        "sleep": ["I think he/she is sleeping, because he is very tired.", "I think he/she is taking a nap, because he worked hard today.", "I think he/she is dreaming, because he is smiling in his sleep."]
    }
    default_sentences = ["I think he/she is __________, because __________.", "I think he/she looks __________, because __________.", "I think the person is __________, because __________."]
    
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
                    all_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in valid_extensions]
                    if not all_files: st.warning("⚠️ The 'images' folder is empty!")
                    else:
                        if not st.session_state.available_images:
                            st.session_state.available_images = all_files.copy()
                            random.shuffle(st.session_state.available_images)
                            st.toast("🔄 All images shown! Reshuffling deck...", icon="🔀")
                        while st.session_state.available_images:
                            selected_img = st.session_state.available_images.pop()
                            full_path = os.path.join(folder_path, selected_img)
                            if os.path.exists(full_path):
                                st.session_state.current_image = full_path
                                st.session_state.current_image_name = selected_img.lower()
                                break
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
    if not st.session_state.students:
        st.error("Student list is empty! Please add names in the Settings sidebar.")
    else:
        chart_html = get_seating_chart_html(st.session_state.students)
        components.html(chart_html, height=600)

# === Tab 2: Group Battle (MAJOR UPDATE) ===
with tab_group:
    st.header("⚔️ Group Battle Mode")
    
    # 1. Generator Controls
    c_gen, c_info = st.columns([1, 2])
    with c_gen:
        g_size = st.number_input("Group Size", 2, 10, 4)
        if st.button("🚀 Generate New Groups"):
            shuffled = st.session_state.students.copy()
            random.shuffle(shuffled)
            # Create list of lists
            groups = [shuffled[i:i + g_size] for i in range(0, len(shuffled), g_size)]
            st.session_state.groups = groups # Save to session
            st.success("Groups generated!")
            st.rerun()
            
    with c_info:
        if st.session_state.groups:
            if st.button("🗑️ Clear Groups"):
                st.session_state.groups = []
                st.rerun()
        else:
            st.info("👈 Set size and click Generate to start battle!")

    st.divider()

    # 2. Battle Dashboard (Display Groups)
    if st.session_state.groups:
        # Calculate how many columns per row (max 4 for visibility)
        num_groups = len(st.session_state.groups)
        cols_per_row = 3 
        
        # Iterate through groups and display them
        # We process in chunks of 3 for layout
        for i in range(0, num_groups, cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < num_groups:
                    group_idx = i + j
                    group_members = st.session_state.groups[group_idx]
                    
                    with row_cols[j]:
                        # Calculate Group Total Score
                        group_total = sum(st.session_state.scores.get(s, 0) for s in group_members)
                        
                        # Render Card using HTML/CSS inside Markdown for style
                        st.markdown(f"""
                        <div class="group-card">
                            <div class="group-title">🛡️ Group {group_idx + 1}</div>
                            <div class="group-score">{group_total} pts</div>
                            <div class="group-members">
                                {', '.join(group_members)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add Point Button (Native Streamlit Button for logic)
                        if st.button(f"➕ Add Point to Group {group_idx + 1}", key=f"btn_g_{group_idx}", use_container_width=True):
                            # Add 1 point to EVERY member of this group
                            for member in group_members:
                                st.session_state.scores[member] += 1
                            
                            # Save and Refresh
                            save_data(st.session_state.students, st.session_state.scores)
                            st.toast(f"🎉 Group {group_idx + 1} scored! Everyone gets +1 point!")
                            time.sleep(0.5)
                            st.rerun()

# === Tab 3: Scoreboard ===
with tab_score:
    st.header("🏆 Scoreboard (Individual)")
    cd, ca = st.columns([2, 1])
    with ca:
        current_students = st.session_state.students
        if current_students:
            sel_stu = st.selectbox("Select Student", current_students)
            pts = st.number_input("Points", -10, 10, 1)
            if st.button("Update Score"):
                st.session_state.scores[sel_stu] += pts
                save_data(st.session_state.students, st.session_state.scores)
                st.success(f"{sel_stu}'s score updated!")
                time.sleep(0.5)
                st.rerun()
        else: st.warning("No students available.")
    with cd:
        score_data = [{"Name": n, "Score": st.session_state.scores.get(n, 0)} for n in st.session_state.students]
        if score_data:
            df = pd.DataFrame(score_data).sort_values(by='Score', ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Scoreboard is empty.")
            if st.button("Try Loading Default Data"):
                st.session_state.students = DEFAULT_STUDENTS
                st.session_state.scores = {n:0 for n in DEFAULT_STUDENTS}
                save_data(DEFAULT_STUDENTS, st.session_state.scores)
                st.rerun()

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