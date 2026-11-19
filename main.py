import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
import urllib.parse

# ---------------- DB SETUP ----------------
DB = "tuition.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, parent_name TEXT, 
        phone TEXT, student_class TEXT, monthly_fee REAL DEFAULT 0, parent_password TEXT DEFAULT 'parent123')""")
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, att_date TEXT, status TEXT, UNIQUE(student_id, att_date))""")
    c.execute("""CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, month TEXT, amount REAL, paid INTEGER DEFAULT 0, paid_on TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, subject TEXT, test_name TEXT, test_date TEXT, marks REAL, total REAL)""")
    conn.commit()
    try: conn.execute("ALTER TABLE students ADD COLUMN student_class TEXT DEFAULT 'N/A'")
    except: pass
    try: conn.execute("ALTER TABLE students ADD COLUMN parent_password TEXT DEFAULT 'parent123'")
    except: pass
    try: conn.execute("ALTER TABLE tests ADD COLUMN subject TEXT DEFAULT 'General'")
    except: pass
    conn.close()

def run_query(q, params=()):
    conn = get_conn()
    df = pd.read_sql_query(q, conn, params=params)
    conn.close()
    return df

def run_exec(q, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(q, params)
    conn.commit()
    conn.close()

def wa_link(phone, msg):
    if not phone: return "#"
    phone = str(phone).replace(" ", "").replace("+", "")
    if len(phone) == 10: phone = "91" + phone
    return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

# ---------------- UI COMPONENTS ----------------
def header(title, subtitle="", color1="#4facfe", color2="#00f2fe"):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color1},{color2});
    padding:25px;border-radius:20px;color:white;margin-bottom:20px;box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
    <h1 style="margin:0;font-size:32px;font-family: 'Segoe UI', sans-serif;">{title}</h1>
    <p style="margin:5px 0 0;opacity:0.9;font-size:16px;">{subtitle}</p></div>""",
    unsafe_allow_html=True)

def dash_card(title, value, subtitle, color1, color2, icon):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color1},{color2});padding:20px;border-radius:16px;
    color:white;margin-bottom:15px;box-shadow: 0 6px 12px rgba(0,0,0,0.15);text-align:center;">
    <div style="font-size:35px;margin-bottom:5px;">{icon}</div>
    <div style="font-size:28px;font-weight:800;font-family: 'Segoe UI', sans-serif;">{value}</div>
    <div style="font-size:14px;font-weight:600;opacity:0.8;text-transform:uppercase;letter-spacing:1px;">{title}</div>
    <div style="font-size:12px;opacity:0.9;margin-top:5px;">{subtitle}</div>
    </div>""", unsafe_allow_html=True)

# Custom CSS for Floating Pill Bottom Nav
st.markdown("""
<style>
    [data-testid="collapsedControl"] {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    .block-container {padding: 1rem 1rem 120px 1rem !important; max-width: 800px;}
    
    div[data-testid="stHorizontalBlock"] > div > div > div > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #666 !important;
        padding: 5px !important;
        font-size: 12px !important;
        transition: 0.3s;
    }
    div[data-testid="stHorizontalBlock"] > div > div > div > button:hover {
        color: #2874F0 !important; 
        transform: scale(1.1);
    }
    div.stButton > button[kind="primary"] {
        color: #2874F0 !important;
        font-weight: bold !important;
    }
    .floating-nav {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 500px;
        background-color: white;
        border-radius: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        padding: 10px 5px;
        z-index: 9999;
        border: 1px solid #f0f0f0;
    }
    [data-testid="stDataFrame"] { border-radius: 15px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Smart Tuition App", page_icon="🚀", layout="centered")
init_db()

# ---------------- LOGIN ----------------
if "role" not in st.session_state: st.session_state.role = None
if "parent_sid" not in st.session_state: st.session_state.parent_sid = None
if "page" not in st.session_state: st.session_state.page = "Home"

if st.session_state.role is None:
    header("🚀 Smart Tuition", "Your Child's Progress Partner")
    t1, t2, t3 = st.tabs(["👨‍💼 Owner", "👪 Parent Login", "📝 Register"])
    
    with t1:
        with st.form("owner_login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login as Owner", use_container_width=True):
                if u == "OWNER" and p == "OWNER1":
                    st.session_state.role = "owner"; st.session_state.page = "Home"; st.rerun()
                else: st.error("❌ Galat Credentials")
    with t2:
        with st.form("parent_login"):
            ph = st.text_input("Registered Phone Number")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login as Parent", use_container_width=True):
                df = run_query("SELECT id, parent_password FROM students WHERE phone=?", (ph,))
                if not df.empty and (df["parent_password"][0] or "parent123") == pw:
                    st.session_state.role = "parent"
                    st.session_state.parent_sid = int(df["id"][0])
                    st.session_state.page = "Home"; st.rerun()
                else: st.error("❌ Phone ya Password galat")
    with t3:
        with st.form("parent_register"):
            s_name = st.text_input("Student ka Naam")
            s_class = st.text_input("Class (e.g. 10th)")
            p_name = st.text_input("Parent ka Naam")
            r_phone = st.text_input("Phone Number (10 digit)")
            r_pw = st.text_input("Create Password", type="password")
            if st.form_submit_button("Register Now", use_container_width=True):
                if not s_name or not r_phone or not r_pw: st.error("Sabhi fields bharein.")
                elif len(r_phone) != 10 or not r_phone.isdigit(): st.error("10 digit ka valid number daalein.")
                else:
                    if not run_query("SELECT id FROM students WHERE phone=?", (r_phone,)).empty:
                        st.error("Ye number pehle se registered hai.")
                    else:
                        run_exec("INSERT INTO students (name, parent_name, phone, student_class, monthly_fee, parent_password) VALUES (?,?,?,?,?,?)", 
                                 (s_name, p_name, r_phone, s_class, 0, r_pw))
                        st.success("✅ Registration Successful! Ab login karein.")
    st.stop()

# ---------------- CUSTOM BOTTOM NAV ----------------
def floating_nav(menu_items):
    st.markdown('<div class="floating-nav">', unsafe_allow_html=True)
    cols = st.columns(len(menu_items))
    for i, item in enumerate(menu_items):
        with cols[i]:
            is_active = (st.session_state.page == item["label"])
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{item['icon']}\n\n{item['label']}", key=f"nav_{item['label']}", use_container_width=True, type=btn_type):
                st.session_state.page = item["label"]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- OWNER APP ----------------
if st.session_state.role == "owner":
    owner_menu = [{"label": "Home", "icon": "🏠"}, {"label": "Students", "icon": "👨‍🎓"},
                  {"label": "Attendance", "icon": "✅"}, {"label": "Fees", "icon": "💰"}, {"label": "Tests", "icon": "📝"}]
    
    if st.button("🚪 Logout", key="logout_owner"):
        st.session_state.role = None; st.rerun()

    page = st.session_state.page

    if page == "Home":
        header("👨‍💼 Admin Dashboard", "Manage your tuition centre")
        ts = run_query("SELECT COUNT(*) n FROM students")["n"][0]
        col = run_query("SELECT COALESCE(SUM(amount),0) s FROM fees WHERE paid=1")["s"][0]
        pen = run_query("SELECT COALESCE(SUM(amount),0) s FROM fees WHERE paid=0")["s"][0]
        
        c1,c2 = st.columns(2)
        with c1: dash_card("Students", ts, "Total Enrolled", "#11998e", "#38ef7d", "👨‍🎓")
        with c2: dash_card("Pending", f"₹{pen:,.0f}", "To be collected", "#ff9966", "#ff5e62", "⚠️")
        dash_card("Total Collected", f"₹{col:,.0f}", "This month", "#4facfe", "#00f2fe", "💰")

    elif page == "Students":
        header("👨‍🎓 Students", "Add or View Students")
        with st.expander("➕ Naya Student Add Karein", expanded=False):
            with st.form("add_student"):
                c1,c2 = st.columns(2)
                name = c1.text_input("Student Name")
                s_class = c2.text_input("Class (e.g. 10th)")
                parent = c1.text_input("Parent Name")
                phone = c2.text_input("Parent Phone")
                fee = c1.number_input("Monthly Fee (₹)", min_value=0.0, step=100.0)
                pw = c2.text_input("Parent Password", value="parent123")
                if st.form_submit_button("Save Student", use_container_width=True):
                    if name:
                        run_exec("INSERT INTO students (name,parent_name,phone,student_class,monthly_fee,parent_password) VALUES (?,?,?,?,?,?)", (name,parent,phone,s_class,fee,pw))
                        st.success(f"✅ {name} added!")
                    else: st.error("Name required")
        
        st.markdown("### 📋 All Students")
        st.dataframe(run_query("SELECT name as 'Name', student_class as 'Class', parent_name as 'Parent', phone as 'Phone', monthly_fee as 'Fee' FROM students ORDER BY id DESC"), use_container_width=True)

    elif page == "Attendance":
        header("✅ Attendance", "Mark today's presence")
        students = run_query("SELECT id,name,student_class FROM students")
        if students.empty: st.warning("Pehle students add karo.")
        else:
            d = st.date_input("Select Date", date.today())
            st.markdown("---")
            for _, r in students.iterrows():
                st.markdown(f"**{r['name']}** *({r['student_class']})*")
                c1,c2, _ = st.columns([1,1,2])
                if c1.button("✅ Present", key=f"p{r['id']}", use_container_width=True):
                    run_exec("INSERT OR REPLACE INTO attendance (student_id,att_date,status) VALUES (?,?,?)", (int(r["id"]), str(d), "P")); st.toast(f"{r['name']} marked Present!"); st.rerun()
                if c2.button("❌ Absent", key=f"a{r['id']}", use_container_width=True):
                    run_exec("INSERT OR REPLACE INTO attendance (student_id,att_date,status) VALUES (?,?,?)", (int(r["id"]), str(d), "A")); st.toast(f"{r['name']} marked Absent!"); st.rerun()
                st.markdown("---")

    elif page == "Fees":
        header("💰 Fees Management", "Collect and remind")
        month = st.text_input("Month (YYYY-MM)", datetime.now().strftime("%Y-%m"))
        if st.button("🔄 Generate Fee Invoices", use_container_width=True):
            students = run_query("SELECT id,monthly_fee FROM students")
            for _, r in students.iterrows():
                if run_query("SELECT id FROM fees WHERE student_id=? AND month=?", (int(r["id"]), month)).empty:
                    run_exec("INSERT INTO fees (student_id,month,amount) VALUES (?,?,?)", (int(r["id"]), month, float(r["monthly_fee"])))
            st.success("Invoices Generated!")
            
        df = run_query("SELECT f.id,s.name,s.phone,f.amount,f.paid FROM fees f JOIN students s ON s.id=f.student_id WHERE f.month=? ORDER BY f.paid, s.name", (month,))
        st.markdown("---")
        for _, r in df.iterrows():
            with st.expander(f"{'🟢' if r['paid'] else '🔴'} {r['name']} - ₹{r['amount']:,.0f}"):
                if not r["paid"]:
                    if st.button("Mark as Paid ✅", key=f"m{r['id']}", use_container_width=True):
                        run_exec("UPDATE fees SET paid=1,paid_on=? WHERE id=?", (str(date.today()), int(r['id']))); st.rerun()
                    st.markdown(f"[📲 Send WhatsApp Reminder]({wa_link(r['phone'], f'Hello, {r['name']} ki fees ₹{r['amount']} pending hai. Kripya jaldi jama karein.')})")
                else:
                    st.success("Payment Received!")

    elif page == "Tests":
        header("📝 Tests", "Add and view results")
        with st.expander("➕ Add New Marks", expanded=False):
            students = run_query("SELECT id,name FROM students")
            if not students.empty:
                with st.form("add_test"):
                    c1,c2 = st.columns(2)
                    sel = c1.selectbox("Student", students["name"]+" (#"+students["id"].astype(str)+")")
                    sid = int(sel.split("#")[-1].rstrip(")"))
                    subject = c2.selectbox("Subject", ["Maths", "Science", "English", "Hindi", "Social Science", "Computer"])
                    tname = c1.text_input("Test Name", "Unit Test 1")
                    
                    # --- NEW: EXAM DATE ADDED HERE ---
                    exam_date = c2.date_input("Exam Date", date.today()) 
                    
                    marks = c1.number_input("Obtained Marks", min_value=0.0)
                    total = c2.number_input("Total Marks", min_value=1.0, value=100.0)
                    
                    if st.form_submit_button("Save Result", use_container_width=True):
                        # Date format string conversion
                        run_exec("INSERT INTO tests (student_id,subject,test_name,test_date,marks,total) VALUES (?,?,?,?,?,?)", 
                                 (sid,subject,tname,str(exam_date),marks,total))
                        st.success("Result Saved!")
        
        st.markdown("### 📊 Recent Results")
        df = run_query("""SELECT s.name, t.subject, t.test_name, t.test_date as 'Exam Date', t.marks, t.total, ROUND(t.marks*100.0/t.total,1) as pct,
                          CASE WHEN (t.marks*100.0/t.total) >= 33 THEN '✅ Pass' ELSE '❌ Fail' END as result
                          FROM tests t JOIN students s ON s.id=t.student_id ORDER BY t.test_date DESC""")
        st.dataframe(df, use_container_width=True)

    floating_nav(owner_menu)

# ---------------- PARENT APP ----------------
elif st.session_state.role == "parent":
    parent_menu = [{"label": "Home", "icon": "🏠"}, {"label": "Attendance", "icon": "📅"},
                   {"label": "Report Card", "icon": "📝"}, {"label": "Fees", "icon": "💰"}]
    
    if st.button("🚪 Logout", key="logout_parent"):
        st.session_state.role = None; st.rerun()

    sid = st.session_state.parent_sid
    info = run_query("SELECT * FROM students WHERE id=?", (sid,)).iloc[0]
    page = st.session_state.page

    if page == "Home":
        header(f"👋 Hello, {info['parent_name']}!", f"Welcome to {info['name']}'s portal")
        
        t = run_query("SELECT status FROM attendance WHERE student_id=? AND att_date=?", (sid, str(date.today())))
        if not t.empty:
            if t["status"][0] == "A":
                st.markdown(f"<div style='background:#FFE5E5;color:#D32F2F;padding:15px;border-radius:12px;font-weight:bold;text-align:center;'>🔔 {info['name']} is ABSENT today!</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#E8F5E9;color:#2E7D32;padding:15px;border-radius:12px;font-weight:bold;text-align:center;'>✅ {info['name']} is PRESENT today!</div>", unsafe_allow_html=True)

        att = run_query("SELECT status FROM attendance WHERE student_id=?", (sid,))
        pct = ((att["status"]=="P").sum()/len(att)*100) if not att.empty else 0
        tests = run_query("SELECT marks, total FROM tests WHERE student_id=?", (sid,))
        avg = round((tests["marks"]/tests["total"]*100).mean(),1) if not tests.empty else 0
        pending = run_query("SELECT COALESCE(SUM(amount),0) s FROM fees WHERE student_id=? AND paid=0", (sid,))["s"][0]

        c1,c2 = st.columns(2)
        with c1: dash_card("Attendance", f"{pct:.0f}%", "Overall Presence", "#4facfe", "#00f2fe", "📅")
        with c2: dash_card("Avg Score", f"{avg}%", "Overall Performance", "#f093fb", "#f5576c", "🏆")
        with c1: dash_card("Pending Fees", f"₹{pending:,.0f}", "Due amount", "#ff9966", "#ff5e62", "💳")
        with c2: dash_card("Class", info['student_class'], "Enrolled Standard", "#a18cd1", "#fbc2eb", "🏫")

    elif page == "Attendance":
        header("📅 Attendance Record", f"{info['name']} ki haziri")
        att = run_query("SELECT att_date as Date, CASE WHEN status='P' THEN '✅ Present' ELSE '❌ Absent' END as Status FROM attendance WHERE student_id=? ORDER BY att_date DESC", (sid,))
        if att.empty: st.info("Abhi tak koi attendance record nahi hai.")
        else: st.dataframe(att, use_container_width=True, hide_index=True)

    elif page == "Report Card":
        header("📝 Report Card", f"{info['name']} ki performance")
        # --- NEW: EXAM DATE ADDED IN REPORT CARD ---
        tests = run_query("""SELECT subject as Subject, test_name as Test, test_date as 'Exam Date', marks as Marks, total as OutOf, 
                             ROUND(marks*100.0/total,1) as '%',
                             CASE WHEN (marks*100.0/total) >= 33 THEN 'Pass' ELSE 'Fail' END as Result
                             FROM tests WHERE student_id=? ORDER BY test_date DESC""", (sid,))
        if tests.empty:
            st.info("Abhi tak koi test result nahi aaya hai.")
        else:
            st.markdown("### 📊 Subject Progress")
            # For chart, we only need Subject and %
            sub_avg = tests.groupby("Subject")["%"].mean().reset_index()
            st.bar_chart(sub_avg.set_index("Subject"), use_container_width=True)
            
            st.markdown("### 📋 Detailed Marks")
            st.dataframe(tests, use_container_width=True, hide_index=True)

    elif page == "Fees":
        header("💰 Fees Details", "Payment history & dues")
        fr = run_query("SELECT month as Month, amount as Amount, CASE WHEN paid=1 THEN '✅ Paid' ELSE '❌ Pending' END as Status FROM fees WHERE student_id=? ORDER BY month DESC", (sid,))
        st.dataframe(fr, use_container_width=True, hide_index=True)
        
        pending = run_query("SELECT COALESCE(SUM(amount),0) s FROM fees WHERE student_id=? AND paid=0", (sid,))["s"][0]
        if pending > 0:
            st.markdown("---")
            st.warning(f"Aapke paas ₹{pending:,.0f} ki fees pending hai.")
            st.markdown(f"<a href='upi://pay?pa=tuition@upi&pn=Tuition&am={pending}&cu=INR' style='display:block;text-align:center;background:#4CAF50;color:white;padding:15px;border-radius:10px;text-decoration:none;font-weight:bold;'>Pay Now via UPI</a>", unsafe_allow_html=True)

    floating_nav(parent_menu)