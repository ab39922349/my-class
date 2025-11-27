import streamlit as st
import streamlit.components.v1 as components
import random
import time
import pandas as pd
import os
import json

# --- Page Config ---
st.set_page_config(page_title="Bodies Speak Louder than Language", page_icon="🎓", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    /* Hide Streamlit UI */
    header[data-testid="stHeader"] {display: none !important; visibility: hidden !important;}
    footer[data-testid="stFooter"] {display: none !important; visibility: hidden !important;}
    div[data-testid="stToolbar"] {display: none !important; visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* App Styles */
    .big-font { font-size:30px !important; font-weight: bold; color: #2c3e50; }
    .instruction { font-size:20px; color: #555; margin-bottom: 20px;}
    
    /* Sentence Box */
    .sentence-box { background-color: #e8f4f8; border-left: 6px solid #3498db; padding: 20px; margin-top: 15px; border-radius: 5px; }
    .sentence-title { color: #2980b9; font-weight: bold; font-size: 20px; margin-bottom: 15px; }
    .sentence-item { font-size: 24px; color: #2c3e50; margin-bottom: 15px; font-family: sans-serif; line-height: 1.6; }
    
    /* Group Card */
    .group-card {
        background-color: #fff; padding: 15px; border-radius: 10px; border: 2px solid #d1d5db;
        margin-bottom: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .group-title { font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;}
    .group-score { font-size: 36px; font-weight: 900; color: #e74c3c; margin: 5px 0; }
    .group-members { color: #555; font-size: 14px; min-height: 40px; border-top: 1px dashed #eee; padding-top: 5px;}
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

# --- Session State ---
if 'students' not in st.session_state or 'scores' not in st.session_state:
    l_students, l_scores = load_data()
    st.session_state.students = l_students
    st.session_state.scores = l_scores

if 'current_image' not in st.session_state: st.session_state.current_image = None
if 'current_image_name' not in st.session_state: st.session_state.current_image_name = ""
if 'available_images' not in st.session_state: st.session_state.available_images = []
if 'groups' not in st.session_state: st.session_state.groups = []
if 'group_scores' not in st.session_state: st.session_state.group_scores = {}
if 'timer_end_time' not in st.session_state: st.session_state.timer_end_time = 0
if 'timer_running' not in st.session_state: st.session_state.timer_running = False

# ✨ MIND MAP STATE
if 'mindmap_input' not in st.session_state:
    st.session_state.mindmap_input = """Body Language -> Posture
Body Language -> Gestures
Body Language -> Facial Expressions
Posture -> Open
Posture -> Closed
Gestures -> Handshake
Facial Expressions -> Smile"""

# --- Sidebar ---
st.sidebar.header("⏱️ Floating Timer")
t_min = st.sidebar.number_input("Minutes", 0, 60, 5)
t_sec = st.sidebar.number_input("Seconds", 0, 59, 0)
col_t1, col_t2 = st.sidebar.columns(2)
with col_t1:
    if st.sidebar.button("▶ Start", type="primary"):
        duration = (t_min * 60) + t_sec
        st.session_state.timer_end_time = time.time() + duration
        st.session_state.timer_running = True
        st.rerun()
with col_t2:
    if st.sidebar.button("⏹ Stop"):
        st.session_state.timer_end_time = 0
        st.session_state.timer_running = False
        st.rerun()

st.sidebar.divider()
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
        st.session_state.groups = [] 
        st.session_state.group_scores = {}
        st.success("List updated!")
        time.sleep(0.5)
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("⚠️ Factory Reset"):
    if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
    st.session_state.students = DEFAULT_STUDENTS
    st.session_state.scores = {name: 0 for name in DEFAULT_STUDENTS}
    st.session_state.groups = []
    st.session_state.group_scores = {}
    st.session_state.mindmap_input = "Topic -> Subtopic 1\nTopic -> Subtopic 2"
    st.sidebar.success("Data reset!")
    time.sleep(0.5)
    st.rerun()

# --- 🕒 Timer Script ---
def get_timer_script(end_time, is_running):
    if not is_running:
        return """<script>const d=window.parent.document;const e=d.getElementById('custom-floating-timer');if(e){e.remove();}</script>"""
    return f"""
    <script>
        (function() {{
            const endTime = {end_time};
            const doc = window.parent.document;
            let timerDiv = doc.getElementById('custom-floating-timer');
            if (!timerDiv) {{
                timerDiv = doc.createElement('div');
                timerDiv.id = 'custom-floating-timer';
                timerDiv.style.position = 'fixed';
                timerDiv.style.bottom = '20px';
                timerDiv.style.right = '20px';
                timerDiv.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                timerDiv.style.color = 'white';
                timerDiv.style.padding = '15px 25px';
                timerDiv.style.borderRadius = '50px';
                timerDiv.style.fontFamily = 'Arial, sans-serif';
                timerDiv.style.fontSize = '28px';
                timerDiv.style.fontWeight = 'bold';
                timerDiv.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
                timerDiv.style.zIndex = '999999';
                timerDiv.style.transition = 'transform 0.2s, background 0.5s';
                timerDiv.innerHTML = '00:00';
                doc.body.appendChild(timerDiv);
            }}
            function updateTimer() {{
                const now = Date.now() / 1000;
                const remaining = endTime - now;
                if (remaining > 0) {{
                    const m = Math.floor(remaining / 60);
                    const s = Math.floor(remaining % 60);
                    const text = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                    timerDiv.innerText = text;
                    if (remaining < 10) {{
                        timerDiv.style.background = 'linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%)';
                        timerDiv.style.transform = (Math.floor(remaining * 2) % 2 === 0) ? 'scale(1.1)' : 'scale(1)';
                    }} else {{
                        timerDiv.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                        timerDiv.style.transform = 'scale(1)';
                    }}
                }} else {{
                    timerDiv.innerText = "TIME'S UP!";
                    timerDiv.style.background = '#e74c3c';
                    timerDiv.style.transform = 'scale(1.2)';
                }}
            }}
            if (window.myTimerInterval) clearInterval(window.myTimerInterval);
            window.myTimerInterval = setInterval(updateTimer, 500);
            updateTimer();
        }})();
    </script>
    """
script_html = get_timer_script(st.session_state.timer_end_time, st.session_state.timer_running)
components.html(script_html, height=0)

# --- ✨ Vis.js Interactive Map (EDITABLE) ---
def get_visjs_html(text_input):
    # Parse text input into nodes and edges
    lines = text_input.split('\n')
    nodes = set()
    edges = []
    
    for line in lines:
        if "->" in line:
            parts = line.split("->")
            if len(parts) == 2:
                src = parts[0].strip()
                dst = parts[1].strip()
                nodes.add(src)
                nodes.add(dst)
                edges.append({"from": src, "to": dst})
    
    node_list = []
    for node in nodes:
        color = "#97C2FC" 
        shape = "box"
        font_size = 20
        if "Body" in node or "Root" in node:
            color = "#FB7E81"
            font_size = 28
            shape = "ellipse"
        node_list.append({"id": node, "label": node, "color": color, "shape": shape, "font": {"size": font_size}})
    
    nodes_json = json.dumps(node_list)
    edges_json = json.dumps(edges)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
            #mynetwork {{ width: 100%; height: 600px; border: 2px solid #ddd; border-radius: 10px; background-color: #fcfcfc; }}
        </style>
    </head>
    <body>
        <div id="mynetwork"></div>
        <script type="text/javascript">
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});
            var container = document.getElementById('mynetwork');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{ borderWidth: 2, shadow: true, font: {{ face: 'Arial' }} }},
                edges: {{ width: 2, shadow: true, arrows: 'to', color: {{ color: '#848484' }} }},
                physics: {{
                    enabled: true,
                    barnesHut: {{ gravitationalConstant: -2000, centralGravity: 0.3, springLength: 95, springConstant: 0.04, damping: 0.09, avoidOverlap: 0 }},
                    stabilization: {{ iterations: 100 }}
                }},
                interaction: {{ dragNodes: true, dragView: true, zoomView: true, hover: true }},
                manipulation: {{
                    enabled: true,
                    initiallyActive: true,
                    addNode: true,
                    addEdge: true,
                    editEdge: true,
                    deleteNode: true,
                    deleteEdge: true,
                    editNode: function (data, callback) {{
                        // Pop-up for renaming
                        var newLabel = prompt("Edit Node Name:", data.label);
                        if (newLabel !== null) {{
                            data.label = newLabel;
                            callback(data);
                        }} else {{
                            callback(null);
                        }}
                    }}
                }}
            }};
            var network = new vis.Network(container, data, options);
            
            // Double click trigger edit
            network.on("doubleClick", function(params) {{
                if (params.nodes.length === 1) {{
                    network.editNode();
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html

# --- HTML Generator: Seating Chart ---
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
tab_pic, tab_mindmap, tab_seat, tab_group, tab_score = st.tabs(["🖼️ Look & Say", "🧠 Interactive Map", "🪑 Seating Chart", "⚔️ Group Battle", "🏆 Scoreboard"])

# === Tab 0: Look & Say (WITH UPDATED SENTENCES) ===
with tab_pic:
    st.header("🖼️ Look & Say: What is he/she doing?")
    st.markdown('<div class="instruction">Please use the pattern: <b>"I think he/she is..., because..."</b></div>', unsafe_allow_html=True)
    sentence_map = {
        "lie": [
            "I think he/she is lying, because he/she looks __________.",
            "I think he/she is not lying, because __________.",
            "I think he/she is telling a lie, because his/her face looks __________."
        ],
        "lying": [
            "I think he/she is lying, because he/she looks __________.",
            "I think he/she is not lying, because __________.",
            "I think he/she is telling a lie, because his/her face looks __________."
        ],
        "love": [
            "I think they are in love, because __________.",
            "I think he/she falls in love with him/her, because he/she is __________.",
            "I think they really like each other, because __________."
        ],
        "run": [
            "I think he/she is running, because he/she is late for __________.",
            "I think he/she is rushing, because __________.",
            "I think he/she is exercising, because he/she wants to be __________."
        ],
        "eat": [
            "I think he/she is eating __________, because he/she looks __________.",
            "I think he/she is having lunch, because it is __________.",
            "I think the food looks __________, so he/she is __________."
        ],
        "sleep": [
            "I think he/she is sleeping, because he/she feels __________.",
            "I think he/she is taking a nap, because __________.",
            "I think he/she is dreaming about __________."
        ]
    }
    default_sentences = [
        "I think he/she is __________, because __________.", 
        "I think he/she looks __________, because __________.", 
        "I think the person is __________, because __________."
    ]
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
            for s in target_sentences: 
                st.markdown(f'<div class="sentence-item">👉 {s}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👈 Please click the button to start.")

# === Tab NEW: Interactive Mind Map ===
with tab_mindmap:
    st.header("🧠 Interactive Concept Map")
    
    # Hidden Text Area for "Persistence" (Source Code)
    with st.expander("📝 Edit Source (Permanent Save)"):
        st.caption("Editing here saves permanently. Edits on the whiteboard below are temporary for this session.")
        new_map_input = st.text_area(
            "Structure Code", 
            value=st.session_state.mindmap_input,
            height=200
        )
        if new_map_input != st.session_state.mindmap_input:
            st.session_state.mindmap_input = new_map_input
            st.rerun()

    # Whiteboard Area
    st.info("💡 **Double Click** a node to rename. Use the toolbar to Add/Delete nodes.")
    
    if st.session_state.mindmap_input.strip():
        html_vis = get_visjs_html(st.session_state.mindmap_input)
        components.html(html_vis, height=600)
    else:
        st.info("Start typing in the Source Code to build your map!")

# === Tab NEW: Seating Chart ===
with tab_seat:
    st.header("🪑 Seating Chart Picker")
    if not st.session_state.students:
        st.error("Student list is empty! Please add names in the Settings sidebar.")
    else:
        chart_html = get_seating_chart_html(st.session_state.students)
        components.html(chart_html, height=600)

# === Tab 2: Group Battle ===
with tab_group:
    st.header("⚔️ Group Battle Mode")
    c_gen, c_info = st.columns([1, 2])
    with c_gen:
        g_size = st.number_input("Group Size", 2, 10, 4)
        if st.button("🚀 Generate New Groups"):
            shuffled = st.session_state.students.copy()
            random.shuffle(shuffled)
            groups = [shuffled[i:i + g_size] for i in range(0, len(shuffled), g_size)]
            st.session_state.groups = groups 
            st.session_state.group_scores = {i: 0 for i in range(len(groups))}
            st.success("Groups generated & Scores reset!")
            st.rerun()
            
    with c_info:
        if st.session_state.groups:
            if st.button("🗑️ Reset Group Scores"):
                st.session_state.group_scores = {i: 0 for i in range(len(st.session_state.groups))}
                st.toast("Group scores cleared!")
                time.sleep(0.5)
                st.rerun()
        else:
            st.info("👈 Set size and click Generate to start battle!")

    st.divider()

    if st.session_state.groups:
        num_groups = len(st.session_state.groups)
        cols_per_row = 3 
        for i in range(0, num_groups, cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < num_groups:
                    group_idx = i + j
                    group_members = st.session_state.groups[group_idx]
                    with row_cols[j]:
                        if group_idx not in st.session_state.group_scores:
                            st.session_state.group_scores[group_idx] = 0
                        g_score = st.session_state.group_scores[group_idx]
                        st.markdown(f"""
                        <div class="group-card">
                            <div class="group-title">🛡️ Group {group_idx + 1}</div>
                            <div class="group-score">{g_score} pts</div>
                            <div class="group-members">{', '.join(group_members)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"➕ Add Point to G{group_idx + 1}", key=f"btn_g_{group_idx}", use_container_width=True):
                            st.session_state.group_scores[group_idx] += 1
                            st.rerun()

# === Tab 3: Scoreboard (Individual) ===
with tab_score:
    st.header("🏆 Scoreboard (Individual)")
    cd, ca = st.columns([2, 1])
    with ca:
        current_students = st.session_state.students
        if current_students:
            sel_stu = st.selectbox("Select Student", current_students)
            pts = st.number_input("Points", -10, 10, 1)
            c_update, c_clear = st.columns(2)
            with c_update:
                if st.button("Update Score", use_container_width=True):
                    st.session_state.scores[sel_stu] += pts
                    save_data(st.session_state.students, st.session_state.scores)
                    st.success(f"Updated!")
                    time.sleep(0.5)
                    st.rerun()
            with c_clear:
                if st.button("🗑️ Reset Individuals", use_container_width=True):
                    st.session_state.scores = {name: 0 for name in st.session_state.students}
                    save_data(st.session_state.students, st.session_state.scores)
                    st.success("Individual scores cleared!")
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
