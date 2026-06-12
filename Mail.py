import streamlit as st
import sqlite3
import os
import smtplib
import imaplib
import email
import json
import math
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime, timedelta
from io import BytesIO
import streamlit as st
import bcrypt
from cryptography.fernet import Fernet
from PIL import Image

st.set_page_config(page_title="Lingam Secure Mail", layout="wide", page_icon="🔐")

st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; color: #1E293B; }
    h1, h2, h3, h4 { color: #009249 !important; font-family: 'Segoe UI', Roboto, sans-serif; font-weight: 700; }

    section[data-testid="stSidebar"] { background-color: #004D26 !important; border-right: 2px solid #FFD200; }
    section[data-testid="stSidebar"] h3 { color: #FFD200 !important; }
    section[data-testid="stSidebar"] div.stButton > button {
        color: #FFFFFF !important; background-color: #009249 !important;
        border: 1px solid #FFD200 !important; font-weight: 600 !important; transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #FFD200 !important; color: #004D26 !important; border-color: #FFFFFF !important;
    }
    .nav-header { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #FFD200 !important; margin: 15px 0 5px 0; font-weight: bold;}
    .sidebar-user { color: #FFFFFF !important; font-weight: 600; }
    .sidebar-status { color: #E2E8F0 !important; font-size: 12px; }

    section[data-testid="stMain"] div[data-testid="stButton"] button p,
    section[data-testid="stMain"] div[data-testid="stButton"] button div,
    section[data-testid="stMain"] div[data-testid="stButton"] button span,
    .main div[data-testid="stButton"] button p,
    .main div[data-testid="stButton"] button div,
    div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button p,
    div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button div {
        text-align: left !important; width: 100% !important; display: block !important;
    }
    section[data-testid="stMain"] div[data-testid="stButton"] button,
    .main div[data-testid="stButton"] button,
    div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button {
        text-align: left !important; justify-content: flex-start !important;
        align-items: flex-start !important; display: flex !important; flex-direction: column !important;
    }
    .mail-row div[data-testid="stButton"] > button {
        width: 100% !important; text-align: left !important; justify-content: flex-start !important;
        align-items: flex-start !important; display: flex !important; flex-direction: column !important;
        background-color: #FFFFFF !important; color: #0F172A !important;
        border: 1px solid #E2E8F0 !important; border-left: 3px solid #009249 !important;
        border-radius: 5px !important; padding: 9px 14px !important; margin-bottom: 3px !important;
        font-size: 13.5px !important; line-height: 1.5 !important; white-space: pre-wrap !important;
        height: auto !important; min-height: 52px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important; transition: all 0.12s ease !important;
    }
    .mail-row div[data-testid="stButton"] > button p,
    .mail-row div[data-testid="stButton"] > button div,
    .mail-row div[data-testid="stButton"] > button span {
        text-align: left !important; width: 100% !important; display: block !important; margin: 0 !important;
    }
    .mail-row div[data-testid="stButton"] > button:hover {
        background-color: #F0FDF4 !important; border-left-color: #FFD200 !important;
        color: #004D26 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.08) !important;
    }
    .stTextArea textarea, .stTextInput input {
        color: #0F172A !important; background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important; font-weight: 500 !important;
    }
    .readable-plaintext-card {
        background-color: #FFFFFF !important; color: #0F172A !important;
        padding: 18px; border-radius: 6px; border: 1px solid #E2E8F0;
        border-left: 3px solid #009249 !important;
        font-size: 15px; line-height: 1.6; min-height: 150px; text-align: left;
    }
    .mail-body-fit {
        overflow-y: auto; background: #FFFFFF; padding: 20px 24px; border-radius: 6px;
        border: 1px solid #E2E8F0; border-left: 3px solid #009249;
        font-size: 15px; line-height: 1.75; color: #0F172A; text-align: left;
    }
    textarea[disabled], .stTextArea textarea[disabled], .stTextArea [data-baseweb="textarea"] textarea:disabled {
        background-color: #FFFFFF !important; color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important; opacity: 1 !important;
        border-left: 3px solid #009249 !important; border-radius: 6px !important;
        font-size: 14.5px !important; line-height: 1.75 !important;
        text-align: left !important; cursor: default !important; resize: vertical !important;
    }
    .stTextArea [data-baseweb="base-input"], .stTextArea [data-baseweb="textarea"] {
        background-color: #FFFFFF !important;
    }
    .fixed-mailbox-header { background: #FAFAFA; padding-bottom: 8px; border-bottom: 2px solid #009249; margin-bottom: 8px; }
    .mailbox-title { font-size: 21px; font-weight: 700; color: #009249; margin: 0 0 8px 0; padding: 0; }
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #009249 !important; color: white !important;
        border: 1px solid #004D26 !important; text-align: center !important; justify-content: center !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover { background-color: #007A3D !important; border-color: #FFD200 !important; }

    /* ── NOTIFICATION BANNER ── */
    .notif-banner {
        background: linear-gradient(90deg,#004D26 0%,#009249 100%);
        color: #fff; padding: 10px 18px; border-radius: 7px;
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 4px; font-size: 14px; font-weight: 500;
        border-left: 4px solid #FFD200; box-shadow: 0 2px 8px rgba(0,74,38,0.15);
    }
    .notif-banner .notif-icon { font-size: 18px; }
    .notif-banner .notif-text { flex: 1; }
    .notif-banner .notif-time { font-size: 11px; opacity: 0.75; white-space: nowrap; }
    .notif-unread-badge {
        background:#FFD200; color:#004D26; border-radius:50%;
        width:20px; height:20px; display:inline-flex; align-items:center;
        justify-content:center; font-size:11px; font-weight:700; margin-left:6px;
    }

    /* ── PERMISSION BADGE ── */
    .perm-badge { display:inline-block; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700; margin:2px 3px; }
    .perm-allow { background:#DCFCE7; color:#166534; }
    .perm-deny  { background:#FEE2E2; color:#991B1B; }

    /* ── TEMPLATE CARD ── */
    .tpl-card {
        background:#FFFFFF; border:1px solid #E2E8F0; border-left:3px solid #009249;
        border-radius:6px; padding:10px 14px; margin-bottom:6px; cursor:pointer;
        transition: box-shadow .15s;
    }
    .tpl-card:hover { box-shadow:0 2px 8px rgba(0,146,73,.12); border-left-color:#FFD200; }
    .tpl-title { font-weight:700; color:#009249; font-size:13px; }
    .tpl-preview { color:#64748B; font-size:12px; margin-top:1px; }
</style>
""", unsafe_allow_html=True)

# ── ENCRYPTION ──────────────────────────────────────────────
KEY_FILE = "secret.key"
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f: f.write(key)
    with open(KEY_FILE, "rb") as f: return f.read()
cipher = Fernet(load_key())
def encrypt(data):
    if isinstance(data, str): data = data.encode('utf-8')
    return cipher.encrypt(data)
def decrypt(data):
    if not data: return ""
    if isinstance(data, str): data = data.encode('utf-8')
    try: return cipher.decrypt(data).decode('utf-8')
    except: return "[Decryption Error]"

# ── DATABASE ────────────────────────────────────────────────
DB_FILE = "secure_mail.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30.0)
c = conn.cursor()

def log_activity(user, action, details):
    try:
        ts = datetime.now().strftime("%b %d, %Y %I:%M %p")
        c.execute("INSERT INTO audit_logs (timestamp,user,action,details) VALUES (?,?,?,?)",(ts,user,action,details))
        conn.commit()
    except: pass

def process_outbox_queue():
    try:
        c.execute("SELECT id,sender,receiver,subject,message,file_name,file_data,time,reference_id FROM mails WHERE folder='outbox'")
        for item in c.fetchall():
            try:
                c.execute("UPDATE mails SET folder='inbox',is_read=0 WHERE id=?",(item[0],))
                c.execute("INSERT INTO mails (sender,receiver,subject,message,file_name,file_data,folder,time,is_read,reference_id) VALUES (?,?,?,?,?,?,?,?,1,?)",
                          (item[1],item[2],item[3],item[4],item[5],item[6],"sent",item[7],item[0]))
                conn.commit()
                log_activity(item[1],"Scheduled Delivery",f"Released to {item[2]}")
            except: pass
    except: pass

def init_db(force_fresh=False):
    global conn, c
    if force_fresh:
        try:
            c.execute("DROP TABLE IF EXISTS users"); c.execute("DROP TABLE IF EXISTS mails")
            c.execute("DROP TABLE IF EXISTS audit_logs"); c.execute("DROP TABLE IF EXISTS notifications")
            c.execute("DROP TABLE IF EXISTS permissions"); conn.commit()
        except:
            conn.close()
            try: os.remove(DB_FILE)
            except: pass
            conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30.0); c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,full_name TEXT,email TEXT UNIQUE,
         password BLOB,role TEXT,department TEXT,allow_attachments INTEGER DEFAULT 1,
         avatar_data BLOB,gmail_user BLOB,gmail_app_password BLOB)''')

    c.execute('''CREATE TABLE IF NOT EXISTS mails
        (id INTEGER PRIMARY KEY AUTOINCREMENT,sender TEXT,receiver TEXT,subject BLOB,message BLOB,
         file_name TEXT,file_data BLOB,folder TEXT,time TEXT,is_read INTEGER DEFAULT 0,
         reference_id INTEGER DEFAULT 0,label TEXT DEFAULT 'None',read_receipt INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs
        (id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp TEXT,user TEXT,action TEXT,details TEXT)''')

    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications
        (id INTEGER PRIMARY KEY AUTOINCREMENT,recipient_email TEXT,sender_name TEXT,
         subject TEXT,time TEXT,is_read INTEGER DEFAULT 0)''')

    # Permissions table — per role
    c.execute('''CREATE TABLE IF NOT EXISTS permissions
        (id INTEGER PRIMARY KEY AUTOINCREMENT,role TEXT UNIQUE,
         can_compose INTEGER DEFAULT 1,can_read INTEGER DEFAULT 1,
         can_delete INTEGER DEFAULT 1,can_trash INTEGER DEFAULT 1,
         can_attach INTEGER DEFAULT 1,can_view_all INTEGER DEFAULT 0,
         can_manage_templates INTEGER DEFAULT 0)''')

    # Mail templates table — user-managed
    c.execute('''CREATE TABLE IF NOT EXISTS mail_templates
        (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,subject TEXT,body TEXT,
         created_by TEXT,created_at TEXT,to_addr TEXT DEFAULT '',cc_addr TEXT DEFAULT '')''')

    conn.commit()

    # Column migrations
    for col,tbl,add in [
        ("is_read","mails","ALTER TABLE mails ADD COLUMN is_read INTEGER DEFAULT 0"),
        ("reference_id","mails","ALTER TABLE mails ADD COLUMN reference_id INTEGER DEFAULT 0"),
        ("label","mails","ALTER TABLE mails ADD COLUMN label TEXT DEFAULT 'None'"),
        ("read_receipt","mails","ALTER TABLE mails ADD COLUMN read_receipt INTEGER DEFAULT 0"),
        ("allow_attachments","users","ALTER TABLE users ADD COLUMN allow_attachments INTEGER DEFAULT 1"),
        ("avatar_data","users","ALTER TABLE users ADD COLUMN avatar_data BLOB"),
        ("gmail_user","users","ALTER TABLE users ADD COLUMN gmail_user BLOB"),
        ("gmail_app_password","users","ALTER TABLE users ADD COLUMN gmail_app_password BLOB"),
        ("can_manage_templates","permissions","ALTER TABLE permissions ADD COLUMN can_manage_templates INTEGER DEFAULT 0"),
        ("to_addr","mail_templates","ALTER TABLE mail_templates ADD COLUMN to_addr TEXT DEFAULT ''"),
        ("cc_addr","mail_templates","ALTER TABLE mail_templates ADD COLUMN cc_addr TEXT DEFAULT ''"),
    ]:
        try: c.execute(f"SELECT {col} FROM {tbl} LIMIT 1")
        except: c.execute(add); conn.commit()

    # Ensure notifications table columns
    try: c.execute("SELECT recipient_email FROM notifications LIMIT 1")
    except:
        try: c.execute("ALTER TABLE notifications ADD COLUMN recipient_email TEXT")
        except: pass
        conn.commit()

    # Seed default permissions if empty
    c.execute("SELECT COUNT(*) FROM permissions")
    if c.fetchone()[0] == 0:
        defaults = [
            ("superadmin", 1, 1, 1, 1, 1, 1, 1),
            ("admin",      1, 1, 1, 1, 1, 0, 1),
            ("user",       1, 1, 0, 1, 1, 0, 0),
        ]
        c.executemany("INSERT OR IGNORE INTO permissions (role,can_compose,can_read,can_delete,can_trash,can_attach,can_view_all,can_manage_templates) VALUES (?,?,?,?,?,?,?,?)", defaults)
        conn.commit()

    # Auto-purge 30-day old trash
    try:
        c.execute("SELECT id,time FROM mails WHERE folder='trash'")
        purged=0
        for item in c.fetchall():
            try:
                if datetime.now()-datetime.strptime(item[1],"%b %d, %Y %I:%M %p")>timedelta(days=30):
                    c.execute("DELETE FROM mails WHERE id=?",(item[0],)); purged+=1
            except: pass
        if purged>0: conn.commit()
    except: pass

try:
    init_db(False)
    c.execute("INSERT INTO audit_logs VALUES (null,'test','test','test','test')")
    c.execute("DELETE FROM audit_logs WHERE timestamp='test'"); conn.commit()
except: init_db(True)

def force_rebuild_admin():
    try:
        c.execute("DELETE FROM users WHERE username='admin'")
        h=bcrypt.hashpw(b"admin@123",bcrypt.gensalt())
        c.execute("INSERT INTO users (username,full_name,email,password,role,department,allow_attachments) VALUES (?,?,?,?,?,?,1)",
                  ("admin","Administrator","admin@lingam.local",sqlite3.Binary(h),"superadmin","IT"))
        conn.commit()
    except: pass

try:
    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone(): force_rebuild_admin()
except: init_db(True); force_rebuild_admin()

# ── HELPERS ─────────────────────────────────────────────────
def get_permissions(role):
    c.execute("SELECT can_compose,can_read,can_delete,can_trash,can_attach,can_view_all,can_manage_templates FROM permissions WHERE role=?",(role,))
    row=c.fetchone()
    if row: return {"compose":bool(row[0]),"read":bool(row[1]),"delete":bool(row[2]),"trash":bool(row[3]),"attach":bool(row[4]),"view_all":bool(row[5]),"manage_templates":bool(row[6])}
    return {"compose":True,"read":True,"delete":False,"trash":True,"attach":True,"view_all":False,"manage_templates":False}

def push_notification(recipient_email, sender_name, subject):
    ts=datetime.now().strftime("%b %d, %Y %I:%M %p")
    try:
        c.execute("INSERT INTO notifications (recipient_email,sender_name,subject,time,is_read) VALUES (?,?,?,?,0)",
                  (recipient_email,sender_name,subject,ts))
        conn.commit()
    except: pass

def get_unread_notifications(email):
    try:
        c.execute("SELECT id,sender_name,subject,time FROM notifications WHERE recipient_email=? AND is_read=0 ORDER BY id DESC LIMIT 10",(email,))
        return c.fetchall()
    except: return []

def mark_notifs_read(email):
    try:
        c.execute("UPDATE notifications SET is_read=1 WHERE recipient_email=?",(email,))
        conn.commit()
    except: pass

def login(u,p):
    try:
        c.execute("SELECT id,username,full_name,email,password,role,department,allow_attachments,avatar_data FROM users WHERE username=?",(u,))
        user=c.fetchone()
        if not user: return None
        h=user[4].tobytes() if isinstance(user[4],memoryview) else user[4]
        if isinstance(h,str): h=h.encode()
        if bcrypt.checkpw(p.encode(),h): log_activity(u,"Auth","Logged in"); process_outbox_queue(); return user
    except:
        if u=="admin":
            force_rebuild_admin()
            c.execute("SELECT id,username,full_name,email,password,role,department,allow_attachments,avatar_data FROM users WHERE username='admin'")
            user=c.fetchone()
            if user:
                h=user[4].tobytes() if isinstance(user[4],memoryview) else user[4]
                if isinstance(h,str): h=h.encode()
                if bcrypt.checkpw(p.encode(),h): process_outbox_queue(); return user
    return None

def get_admin_gmail_credentials():
    c.execute("SELECT gmail_user,gmail_app_password FROM users WHERE username='admin'")
    row=c.fetchone()
    if row and row[0] and row[1]: return decrypt(row[0]),decrypt(row[1])
    return "",""

def dispatch_real_gmail(target_email,subject,body_msg,files=None):
    g_user,g_pass=get_admin_gmail_credentials()
    if not g_user or not g_pass: return False,"Gmail Credentials missing."
    try:
        msg=MIMEMultipart(); msg['From']=g_user; msg['To']=target_email; msg['Subject']=subject
        msg['Reply-To']=st.session_state.user[3]
        msg['Disposition-Notification-To']=g_user
        msg['Return-Receipt-To']=g_user
        banner=f'<div style="background:#F0FDF4;padding:12px;border-left:5px solid #009249;margin-bottom:20px;font-family:Segoe UI,Arial,sans-serif;border-radius:4px;"><small style="color:#004D26;font-weight:bold;">🌾 LINGAM SECURE</small><br><span style="font-size:14px;color:#1E293B;"><b>From:</b> {st.session_state.user[2]} ({st.session_state.user[3]})</span></div>'
        msg.attach(MIMEText(banner+body_msg,'html'))
        if files:
            from email.mime.application import MIMEApplication
            for f in files:
                f.seek(0); part=MIMEApplication(f.read(),Name=f.name)
                part['Content-Disposition']=f'attachment; filename="{f.name}"'; msg.attach(part)
        srv=smtplib.SMTP("smtp.gmail.com",587); srv.starttls(); srv.login(g_user,g_pass)
        srv.sendmail(g_user,target_email,msg.as_string()); srv.quit(); return True,"Success"
    except Exception as e: return False,str(e)

def send_mail(sender,receiver,subject,message,files_list=None,ref_id=0,target_folder="inbox",label_tag="None",delivery_time=None):
    now=datetime.now().strftime("%b %d, %Y %I:%M %p")
    folder=target_folder
    if delivery_time and delivery_time>datetime.now(): folder="outbox"; now=delivery_time.strftime("%b %d, %Y %I:%M %p")
    for rx in [r.strip() for r in receiver.split(",") if r.strip()]:
        if "@" in rx and not rx.endswith(".local") and folder not in ["draft","outbox"]:
            ok,err=dispatch_real_gmail(rx,subject,message,files_list)
            if not ok: st.error(f"⚠️ Gmail delivery failed to {rx}: {err}")
        enc_s=encrypt(subject); enc_m=encrypt(message)
        names=[]; payloads=[]
        if files_list:
            for f in files_list:
                if hasattr(f,'read'):
                    f.seek(0); fb=f.read(); enc=cipher.encrypt(fb)
                    names.append(f.name); payloads.append(enc.decode())
        fn=json.dumps(names) if names else None
        fd=json.dumps(payloads).encode() if payloads else None
        if folder=="draft":
            c.execute("INSERT INTO mails (sender,receiver,subject,message,file_name,file_data,folder,time,is_read,reference_id,label) VALUES (?,?,?,?,?,?,?,?,1,?,?)",
                      (sender,rx,enc_s,enc_m,fn,fd,"draft",now,ref_id,label_tag)); conn.commit()
        elif folder=="outbox":
            c.execute("INSERT INTO mails (sender,receiver,subject,message,file_name,file_data,folder,time,is_read,reference_id,label) VALUES (?,?,?,?,?,?,?,?,1,?,?)",
                      (sender,rx,enc_s,enc_m,fn,fd,"outbox",now,ref_id,label_tag)); conn.commit()
        else:
            c.execute("INSERT INTO mails (sender,receiver,subject,message,file_name,file_data,folder,time,is_read,reference_id,label) VALUES (?,?,?,?,?,?,?,?,0,?,?)",
                      (sender,rx,enc_s,enc_m,fn,fd,"inbox",now,ref_id,label_tag))
            iid=c.lastrowid
            c.execute("INSERT INTO mails (sender,receiver,subject,message,file_name,file_data,folder,time,is_read,reference_id,label) VALUES (?,?,?,?,?,?,?,?,1,?,?)",
                      (sender,rx,enc_s,enc_m,fn,fd,"sent",now,iid,label_tag)); conn.commit()
            # Push in-app notification to receiver
            push_notification(rx, sender, subject)

# ── MAIL TEMPLATES (DB-backed) ──────────────────────────────
_SEED_TEMPLATES = [
    {"name":"Leave Request","subject":"Leave Request – [Your Name]","to_addr":"","cc_addr":"",
     "body":"Dear Manager,\n\nI am writing to formally request leave from [Start Date] to [End Date] due to [Reason].\n\nI will ensure all pending tasks are completed before my absence. Please let me know if further details are required.\n\nThank you,\n[Your Name]"},
    {"name":"Meeting Invite","subject":"Meeting Invitation – [Topic]","to_addr":"","cc_addr":"",
     "body":"Dear Team,\n\nYou are invited to attend a meeting on [Date] at [Time] regarding [Topic].\n\nAgenda:\n1. [Point 1]\n2. [Point 2]\n3. [Point 3]\n\nPlease confirm your availability.\n\nRegards,\n[Your Name]"},
    {"name":"Task Update","subject":"Task Update – [Task Name]","to_addr":"","cc_addr":"",
     "body":"Hi,\n\nThis is to update you on the status of [Task Name].\n\nCurrent Status: [In Progress / Completed / Blocked]\nExpected Completion: [Date]\nNotes: [Any additional notes]\n\nPlease feel free to reach out for any clarifications.\n\nThanks,\n[Your Name]"},
    {"name":"Complaint","subject":"Formal Complaint – [Issue]","to_addr":"","cc_addr":"",
     "body":"Dear [Manager/HR],\n\nI am writing to formally raise a concern regarding [Issue].\n\nDetails of the issue:\n[Describe the issue clearly]\n\nThis has impacted [Describe impact]. I request that this matter be reviewed and addressed at the earliest.\n\nThank you for your attention.\n\nRegards,\n[Your Name]"},
    {"name":"Announcement","subject":"Announcement – [Topic]","to_addr":"","cc_addr":"",
     "body":"Dear All,\n\nWe are pleased to announce [Announcement Details].\n\nEffective Date: [Date]\nKey Points:\n• [Point 1]\n• [Point 2]\n\nFor queries, please contact [Contact Person].\n\nRegards,\n[Your Name / Department]"},
    {"name":"Purchase Request","subject":"Purchase Request – [Item/Service]","to_addr":"","cc_addr":"",
     "body":"Dear Finance Team,\n\nI am requesting approval for the purchase of [Item/Service] for the [Department] department.\n\nDetails:\n• Item: [Item Name]\n• Quantity: [Qty]\n• Estimated Cost: ₹[Amount]\n• Vendor: [Vendor Name]\n• Purpose: [Brief Purpose]\n\nKindly approve at the earliest.\n\nThank you,\n[Your Name]"},
]

def get_mail_templates():
    try:
        c.execute("SELECT id,name,subject,body,created_by,created_at,COALESCE(to_addr,''),COALESCE(cc_addr,'') FROM mail_templates ORDER BY id ASC")
        return c.fetchall()
    except: return []

def seed_templates_if_empty():
    try:
        c.execute("SELECT COUNT(*) FROM mail_templates")
        if c.fetchone()[0]==0:
            ts=datetime.now().strftime("%b %d, %Y %I:%M %p")
            for t in _SEED_TEMPLATES:
                c.execute("INSERT INTO mail_templates (name,subject,body,created_by,created_at,to_addr,cc_addr) VALUES (?,?,?,?,?,?,?)",
                          (t["name"],t["subject"],t["body"],"system",ts,t.get("to_addr",""),t.get("cc_addr","")))
            conn.commit()
    except: pass

seed_templates_if_empty()


# ── SESSION STATE ────────────────────────────────────────────
for k,v in [("user",None),("current_mail",None),("editing_user",None),
            ("compose_defaults",{"to":"","cc":"","bcc":"","subject":"","msg":"","files":None}),
            ("typed_recipient",""),("active_filter_label","All"),("bulk_select_matrix",{}),
            ("compose_msg_body",""),("notif_panel_open",False),("compose_reset_counter",0)]:
    if k not in st.session_state: st.session_state[k]=v

if st.session_state.user: process_outbox_queue()

# ── LOGIN ────────────────────────────────────────────────────
if not st.session_state.user:
    c1,c2,c3=st.columns([1,1.8,1])
    with c2:
        st.write("<br><br>",unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;color:#009249!important;'>🌾 LINGAM SUPER MARKET</h1>",unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center;color:#854D0E;font-weight:600;margin-top:-15px;'>Quality in Every Cart & Code.</h4>",unsafe_allow_html=True)
        with st.container(border=True):
            u=st.text_input("Username",key="li_u"); p=st.text_input("Password",type="password",key="li_p")
            if st.button("Authorize Connection",type="primary",use_container_width=True):
                ud=login(u,p)
                if ud: st.session_state.user=ud; st.session_state.bulk_select_matrix={}; st.session_state.just_logged_in=True; st.rerun()
                else:
                    if u=="admin" and p=="admin@123":
                        force_rebuild_admin(); ud=login(u,p)
                        if ud: st.session_state.user=ud; st.session_state.bulk_select_matrix={}; st.session_state.just_logged_in=True; st.rerun()
                    st.error("Access Denied: Invalid credentials.")
    st.stop()

c.execute("SELECT id,username,full_name,email,password,role,department,allow_attachments,avatar_data FROM users WHERE id=?",(st.session_state.user[0],))
st.session_state.user=c.fetchone()
user_id,username,full_name,user_email,_,user_role,user_dept,allow_attachments,avatar_data=st.session_state.user
perms=get_permissions(user_role)

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='margin-bottom:0px;'>🌾 Lingam Portal</h3>",unsafe_allow_html=True)
    if avatar_data:
        try: st.image(Image.open(BytesIO(avatar_data)),width=80)
        except: pass

    # Notification bell calculation
    unread_notifs=get_unread_notifications(user_email)
    notif_count=len(unread_notifs)
    bell_label=f"🔔 Notifications  ({notif_count} new)" if notif_count>0 else "🔔 Notifications"
    st.markdown(f'<p class="sidebar-status">● Active: <span class="sidebar-user">{full_name}</span></p>',unsafe_allow_html=True)
    st.divider()

    st.markdown('<p class="nav-header">Workspace Mailboxes</p>',unsafe_allow_html=True)
    # Kept the notifications button at top of Inbox Directory button
    if st.button(bell_label,use_container_width=True): st.session_state.menu="Notifications"
    if st.button("📥 Inbox Directory",use_container_width=True): st.session_state.menu="Inbox"; st.session_state.current_mail=None; st.session_state.bulk_select_matrix={}
    if st.button("📤 Sent Items Tracker",use_container_width=True): st.session_state.menu="Sent"; st.session_state.current_mail=None; st.session_state.bulk_select_matrix={}
    if st.button("⏳ Outbox Queue Partition",use_container_width=True): st.session_state.menu="Outbox"; st.session_state.current_mail=None; st.session_state.bulk_select_matrix={}
    if st.button("📝 Saved Drafts Archive",use_container_width=True): st.session_state.menu="Drafts"; st.session_state.current_mail=None; st.session_state.bulk_select_matrix={}
    if st.button("🗑 Trash Archives",use_container_width=True): st.session_state.menu="Trash"; st.session_state.current_mail=None; st.session_state.bulk_select_matrix={}
    if perms["compose"]:
        if st.button("✏ Compose Transmission",use_container_width=True):
            st.session_state.menu="Compose"
            st.session_state.compose_defaults={"to":"","cc":"","bcc":"","subject":"","msg":"","files":None}
            st.session_state.typed_recipient=""
            st.session_state.compose_msg_body=""

    st.markdown('<p class="nav-header">Filter Workspace Labels</p>',unsafe_allow_html=True)
    label_options=["All","None","Urgent","Finance","HR Requests","Operations","Personal"]
    st.session_state.active_filter_label=st.selectbox("Label Filter",label_options,index=label_options.index(st.session_state.get("active_filter_label","All")))

    st.markdown('<p class="nav-header">User Self-Service</p>',unsafe_allow_html=True)
    if st.button("⚙️ Profile & Security",use_container_width=True): st.session_state.menu="Profile Settings"
    if perms["manage_templates"]:
        if st.button("📋 Manage Templates",use_container_width=True): st.session_state.menu="Manage Templates"

    if user_role in ["superadmin","admin"]:
        st.markdown('<p class="nav-header">Integrations & Sync</p>',unsafe_allow_html=True)
        if user_role=="superadmin":
            if st.button("🔌 Connect Gmail Account",use_container_width=True): st.session_state.menu="Gmail Connection"
        st.markdown('<p class="nav-header">Global Administration</p>',unsafe_allow_html=True)
        if st.button("👥 Directory Access Manager",use_container_width=True): st.session_state.menu="User Management"
        if user_role=="superadmin":
            if st.button("🔍 Master Intercept Monitor",use_container_width=True): st.session_state.menu="Master Intercept"
            if st.button("🔐 Permission Manager",use_container_width=True): st.session_state.menu="Permission Manager"
        if st.button("📊 Security Event Audit",use_container_width=True): st.session_state.menu="Activity Monitor"

    st.write("<br>"*2,unsafe_allow_html=True)
    if st.button("Logout",type="secondary",use_container_width=True):
        st.session_state.user=None; st.session_state.current_mail=None; st.session_state.bulk_select_matrix={}; st.rerun()

if "menu" not in st.session_state: st.session_state.menu="Inbox"
if st.session_state.get("just_logged_in",False): st.session_state.menu="Inbox"; st.session_state.just_logged_in=False

# ═══════════════════════════════════════════════════════════════
# MENU ROUTING
# ═══════════════════════════════════════════════════════════════

# ── NOTIFICATIONS PAGE ──────────────────────────────────────
if st.session_state.menu=="Notifications":
    st.title("🔔 Notifications")
    all_notifs=[]
    try:
        c.execute("SELECT id,sender_name,subject,time,is_read FROM notifications WHERE recipient_email=? ORDER BY id DESC LIMIT 50",(user_email,))
        all_notifs=c.fetchall()
    except: pass

    if not all_notifs:
        st.info("📭 No notifications yet.")
    else:
        if st.button("✅ Mark all as read",type="primary"):
            mark_notifs_read(user_email); st.rerun()
        for n in all_notifs:
            nid,sname,subj,ntime,nread=n
            bg="#FFFFFF" if nread else "#F0FDF4"
            dot="🟢 " if not nread else ""
            st.markdown(f"""
            <div style="background:{bg};border:1px solid #E2E8F0;border-left:3px solid {'#009249' if not nread else '#CBD5E1'};
            border-radius:6px;padding:10px 16px;margin-bottom:5px;">
                <span style="font-weight:700;color:#009249;">{dot}{sname}</span>
                <span style="color:#64748B;font-size:12px;float:right;">{ntime}</span><br>
                <span style="color:#0F172A;font-size:13px;">{subj}</span>
            </div>""",unsafe_allow_html=True)

# ── PERMISSION MANAGER ───────────────────────────────────────
elif st.session_state.menu=="Permission Manager" and user_role=="superadmin":
    st.title("🔐 Permission Manager")
    st.markdown("Control what each role can do across the mail system.")

    c.execute("SELECT role,can_compose,can_read,can_delete,can_trash,can_attach,can_view_all,can_manage_templates FROM permissions ORDER BY role")
    perm_rows=c.fetchall()

    perm_labels={"can_compose":"✏ Compose","can_read":"📖 Read","can_delete":"🗑 Delete",
                 "can_trash":"🗂 Trash","can_attach":"📎 Attach","can_view_all":"👁 View All","can_manage_templates":"📋 Templates"}
    cols_h=st.columns([2,1,1,1,1,1,1,1])
    headers=["Role"]+list(perm_labels.values())
    for i,h in enumerate(headers): cols_h[i].markdown(f"**{h}**")
    st.markdown("<hr style='margin:4px 0 8px 0;border-top:2px solid #009249;'>",unsafe_allow_html=True)

    for row in perm_rows:
        role_name=row[0]
        vals=list(row[1:])
        keys=["can_compose","can_read","can_delete","can_trash","can_attach","can_view_all","can_manage_templates"]
        cols=st.columns([2,1,1,1,1,1,1,1])
        cols[0].markdown(f"**{role_name}**")
        new_vals=[]
        for i,k in enumerate(keys):
            new_v=cols[i+1].checkbox("",value=bool(vals[i]),key=f"perm_{role_name}_{k}",label_visibility="collapsed")
            new_vals.append(int(new_v))
        c.execute("UPDATE permissions SET can_compose=?,can_read=?,can_delete=?,can_trash=?,can_attach=?,can_view_all=?,can_manage_templates=? WHERE role=?",
                  (*new_vals,role_name))
        conn.commit()

    st.success("✅ Permissions are saved automatically when you toggle checkboxes.")
    st.markdown("---")
    st.markdown("##### Permission Descriptions")
    desc_map={
        "can_compose":"✏ **Compose** — Allow the user to write and send new mails (internal and external Gmail).",
        "can_read":"📖 **Read Mail** — Allow the user to open and read mail in their Inbox, Sent, Drafts, Outbox and Trash folders.",
        "can_delete":"🗑 **Delete** — Allow permanent deletion of mails (bypasses Trash). If disabled, user can only move to Trash.",
        "can_trash":"🗂 **Move to Trash** — Allow the user to move mails to the Trash folder. Mails in Trash auto-purge after 30 days.",
        "can_attach":"📎 **Attachments** — Allow the user to upload and send file attachments with their mails.",
        "can_view_all":"👁 **View All Mails** — When enabled, the user can see ALL mails in the system across every user's mailbox (not just their own). This is a sensitive admin-level permission — it lets the role act like a supervisor who can read every employee's inbox and sent items. Only grant this to trusted roles (e.g. superadmin). Normal users should have this OFF.",
        "can_manage_templates":"📋 **Manage Templates** — Allow the user to add, edit, and delete mail templates from the 'Manage Templates' page. When OFF, the user can still use templates in Compose but cannot create or modify them.",
    }
    for k,v in desc_map.items():
        st.markdown(f"- {v}")

# ── COMPOSE ──────────────────────────────────────────────────
elif st.session_state.menu=="Compose":
    if not perms["compose"]:
        st.error("🚫 Your role does not have permission to compose mail.")
        st.stop()

    st.markdown("<h3 style='margin:0 0 8px 0;color:#009249;'>✏ Compose Secure Telemetry</h3>",unsafe_allow_html=True)
    c.execute("SELECT email,full_name FROM users WHERE username!=?",(username,))
    local_users=c.fetchall()
    defaults=st.session_state.compose_defaults
    if not st.session_state.typed_recipient and defaults.get("to",""):
        st.session_state.typed_recipient=defaults["to"]

    # ── Template picker ──────────────────────────────────────
    with st.expander("📋 Use a Message Template",expanded=False):
        db_templates=get_mail_templates()
        if not db_templates:
            st.info("No templates found. Admins can add templates via 'Manage Templates' in the sidebar.")
        else:
            st.markdown("Click a template to load it into the compose form:")
            tcols=st.columns(3)
            for i,tpl in enumerate(db_templates):
                tid,tname,tsubj,tbody,tcreator,tcreated,tto,tcc=tpl
                with tcols[i%3]:
                    st.markdown(f'<div class="tpl-card"><div class="tpl-title">{tname}</div><div class="tpl-preview">{tsubj[:50]}</div></div>',unsafe_allow_html=True)
                    if st.button(f"Use '{tname}'",key=f"tpl_{tid}",use_container_width=True):
                        if tto: st.session_state.typed_recipient=tto
                        st.session_state.compose_defaults["cc"]=tcc or ""
                        st.session_state.compose_defaults["bcc"]=""
                        st.session_state.compose_defaults["subject"]=tsubj
                        st.session_state.compose_defaults["msg"]=tbody
                        st.session_state.compose_msg_body=tbody
                        st.session_state.compose_reset_counter+=1  # force widgets to re-render with template values
                        st.rerun()

    with st.container(border=True):
        # Row 1: To + Directory picker
        r1a,r1b=st.columns([5,1])
        with r1a:
            to_field=st.text_input("To",value=st.session_state.typed_recipient,placeholder="user@gmail.com, user@lingam.local",label_visibility="visible")
        with r1b:
            st.markdown("<div style='margin-top:28px;'>",unsafe_allow_html=True)
            with st.popover("👤 Pick",use_container_width=True):
                for row in local_users:
                    if st.button(f"{row[1]} ({row[0]})",key=f"sp_{row[0]}",use_container_width=True):
                        st.session_state.typed_recipient+=(", " if st.session_state.typed_recipient else "")+row[0]; st.rerun()
            st.markdown("</div>",unsafe_allow_html=True)

        # Reset counter suffix — incrementing this makes Streamlit treat widgets as brand new
        _r=st.session_state.compose_reset_counter

        # Row 2: CC + BCC side by side
        r2a,r2b=st.columns(2)
        with r2a: cc_field=st.text_input("CC",value=defaults.get("cc",""),key=f"cmp_cc_{_r}")
        with r2b: bcc_field=st.text_input("BCC",value=defaults.get("bcc",""),key=f"cmp_bcc_{_r}")

        # Row 3: Subject + Label side by side
        r3a,r3b=st.columns([3,1])
        with r3a: subject=st.text_input("Subject",value=defaults.get("subject",""),key=f"cmp_subj_{_r}")
        with r3b: msg_label=st.selectbox("Label",["None","Urgent","Finance","HR Requests","Operations","Personal"],key=f"cmp_lbl_{_r}")

        # Body
        body_value=st.session_state.compose_msg_body if st.session_state.compose_msg_body is not None else defaults.get("msg","")
        msg=st.text_area("Message",value=body_value,height=200,key=f"cmp_body_{_r}")
        if msg!=st.session_state.compose_msg_body:
            st.session_state.compose_msg_body=msg

        # Schedule row
        enable_sched=st.checkbox("⏳ Schedule Delivery")
        td=datetime.now()
        if enable_sched:
            sc1,sc2=st.columns(2)
            with sc1: sd=st.date_input("Date",datetime.now().date())
            with sc2: st_=st.time_input("Time",datetime.now().time())
            td=datetime.combine(sd,st_)

        if perms["attach"] and allow_attachments==1:
            uploaded_files=st.file_uploader("Attachments",accept_multiple_files=True)
        else:
            st.caption("⚠️ Attachments restricted for your role.")
            uploaded_files=None

        # Action buttons — Dispatch, Save Draft, Clear
        bc=st.columns([1,1,1,3])
        with bc[0]:
            if st.button("🚀 Dispatch",type="primary",use_container_width=True):
                if to_field and subject and msg:
                    send_mail(user_email,to_field.strip(),subject,msg,uploaded_files,label_tag=msg_label,delivery_time=td if enable_sched else None)
                    if cc_field:  send_mail(user_email,cc_field.strip(), subject,msg,uploaded_files,label_tag=msg_label,delivery_time=td if enable_sched else None)
                    if bcc_field: send_mail(user_email,bcc_field.strip(),subject,msg,uploaded_files,label_tag=msg_label,delivery_time=td if enable_sched else None)
                    st.session_state.compose_defaults={"to":"","cc":"","bcc":"","subject":"","msg":"","files":None}
                    st.session_state.compose_msg_body=""
                    st.session_state.typed_recipient=""
                    st.success("🔒 Mail dispatched successfully.")
                else: st.error("To, Subject and Message are required.")
        with bc[1]:
            if st.button("📝 Draft",type="secondary",use_container_width=True):
                if to_field and subject:
                    send_mail(user_email,to_field.strip(),subject,msg,uploaded_files,target_folder="draft",label_tag=msg_label)
                    st.success("📝 Saved to Drafts.")
                else: st.error("Subject required.")
        with bc[2]:
            if st.button("🗑️ Clear",type="secondary",use_container_width=True):
                st.session_state.typed_recipient=""
                st.session_state.compose_msg_body=""
                st.session_state.compose_defaults={"to":"","cc":"","bcc":"","subject":"","msg":"","files":None}
                st.session_state.compose_reset_counter+=1  # new counter = new widget keys = fresh empty fields
                st.rerun()

# ── GMAIL CONNECTION ─────────────────────────────────────────
elif st.session_state.menu=="Gmail Connection" and user_role=="superadmin":
    st.title("🔌 Gmail Integration")
    cgu,cgp=get_admin_gmail_credentials()
    already_set=(bool(cgu) and bool(cgp))
    if "gmail_edit_mode" not in st.session_state: st.session_state.gmail_edit_mode=False
    if already_set and not st.session_state.gmail_edit_mode:
        with st.container(border=True):
            st.success("✅ Gmail Gateway is active and configured.")
            st.markdown(f"**Gmail Account:** `{cgu}`")
            st.markdown(f"**App Password:** `{'●'*16}`")
            st.caption("Credentials are encrypted. Click Edit to update.")
            if st.button("✏️ Edit Credentials",use_container_width=True): st.session_state.gmail_edit_mode=True; st.rerun()
    else:
        with st.container(border=True):
            gu=st.text_input("Gmail Address",value=cgu if st.session_state.gmail_edit_mode else "")
            gp=st.text_input("App Password (16-digit)",value="",type="password",placeholder="Enter new app password")
            bc2=st.columns([1,1])
            with bc2[0]:
                if st.button("💾 Save Gmail Credentials",type="primary",use_container_width=True):
                    if gu.strip() and gp.strip():
                        c.execute("UPDATE users SET gmail_user=?,gmail_app_password=? WHERE username='admin'",
                                  (sqlite3.Binary(encrypt(gu.strip())),sqlite3.Binary(encrypt(gp.strip())))); conn.commit()
                        log_activity(username,"Gmail Updated","Gmail gateway credentials updated")
                        st.session_state.gmail_edit_mode=False
                        st.success("✅ Gmail account linked successfully! You can now sync emails from the Inbox.")
                        st.rerun()
                    else: st.error("❌ Both Gmail address and App Password are required.")
            with bc2[1]:
                if already_set:
                    if st.button("Cancel",use_container_width=True): st.session_state.gmail_edit_mode=False; st.rerun()

# ── MAILBOX FOLDERS ──────────────────────────────────────────
elif st.session_state.menu in ["Inbox","Sent","Outbox","Trash","Drafts"]:

    if not perms["read"]:
        st.error("🚫 Your role does not have permission to read mail.")
        st.stop()

    st.markdown(f'<p style="font-size:20px;font-weight:700;color:#009249;margin:0 0 6px 0;">📂 Mailbox: {st.session_state.menu}</p>',unsafe_allow_html=True)

    if st.session_state.menu=="Inbox":
        if st.button("🔄 Sync Live Gmail Inbox Bridge",type="primary",use_container_width=True):
            g_user,g_pass=get_admin_gmail_credentials()
            if g_user and g_pass:
                with st.spinner("Connecting to Gmail..."):
                    try:
                        mc=imaplib.IMAP4_SSL("imap.gmail.com"); mc.login(g_user,g_pass); mc.select("inbox")
                        _,msgs=mc.search(None,'UNSEEN')
                        mail_ids=msgs[0].split(); sync_count=0; receipt_count=0
                        for mid in mail_ids:
                            _,md=mc.fetch(mid,"(RFC822)")
                            for rp in md:
                                if isinstance(rp,tuple):
                                    rm=email.message_from_bytes(rp[1])
                                    frm=email.utils.parseaddr(rm.get("From"))[1]
                                    sr=rm.get("Subject","No Subject")
                                    ds,enc=decode_header(sr)[0]
                                    if isinstance(ds,bytes): ds=ds.decode(enc or "utf-8",errors="ignore")
                                    # ── Detect MDN read receipt replies ──
                                    content_type=rm.get_content_type()
                                    is_mdn=(content_type=="multipart/report" and rm.get_param("report-type","")=="disposition-notification")
                                    if not is_mdn and rm.is_multipart():
                                        for part in rm.walk():
                                            if part.get_content_type()=="message/disposition-notification":
                                                is_mdn=True; break
                                    if is_mdn:
                                        # Extract original subject from MDN body
                                        orig_subj=""
                                        for part in rm.walk():
                                            if part.get_content_type()=="message/disposition-notification":
                                                mdn_text=part.get_payload(decode=True)
                                                if mdn_text:
                                                    for line in mdn_text.decode(errors="ignore").splitlines():
                                                        if line.lower().startswith("original-subject:"):
                                                            orig_subj=line.split(":",1)[1].strip(); break
                                        # Find matching sent mail and mark read_receipt=1
                                        c.execute("SELECT id,subject FROM mails WHERE sender=? AND folder='sent'",(user_email,))
                                        for sent_id,sent_subj_enc in c.fetchall():
                                            try:
                                                decrypted=decrypt(sent_subj_enc)
                                                if orig_subj and orig_subj.lower() in decrypted.lower():
                                                    c.execute("UPDATE mails SET read_receipt=1 WHERE id=?",(sent_id,))
                                                    receipt_count+=1
                                            except: pass
                                        conn.commit()
                                        mc.store(mid,'+FLAGS','\\Seen'); continue
                                    body=""
                                    if rm.is_multipart():
                                        for pt in rm.walk():
                                            if pt.get_content_type()=="text/plain": body=pt.get_payload(decode=True).decode(errors="ignore"); break
                                    else: body=rm.get_payload(decode=True).decode(errors="ignore")
                                    c.execute("INSERT INTO mails (sender,receiver,subject,message,folder,time,is_read,label) VALUES (?,?,?,?,'inbox',?,0,'None')",
                                              (frm,user_email,encrypt(ds),encrypt(body),datetime.now().strftime("%b %d, %Y %I:%M %p")))
                                    conn.commit(); mc.store(mid,'+FLAGS','\\Seen'); sync_count+=1
                        mc.close(); mc.logout()
                        msgs_out=[]
                        if sync_count>0: msgs_out.append(f"✅ {sync_count} new mail{'s' if sync_count>1 else ''} synced from Gmail!")
                        if receipt_count>0: msgs_out.append(f"📬 {receipt_count} read receipt{'s' if receipt_count>1 else ''} confirmed — check Sent Items for ✅ badges.")
                        if msgs_out: [st.success(m) for m in msgs_out]; st.rerun()
                        else: st.info("📭 No new mail. Your inbox is up to date.")
                    except Exception as e: st.error(f"❌ Gmail sync failed: {str(e)}")
            else: st.warning("⚠️ Gmail credentials not configured. Go to Connect Gmail Account.")

    search_query=st.text_input("🔍 Search",placeholder="Search subject or sender...",key="sq",label_visibility="collapsed")

    qs="SELECT id,sender,receiver,subject,message,file_name,file_data,folder,time,is_read,reference_id,label,read_receipt FROM mails WHERE "
    if st.session_state.menu=="Inbox": c.execute(qs+"receiver=? AND folder='inbox' ORDER BY id DESC",(user_email,))
    elif st.session_state.menu=="Sent": c.execute(qs+"sender=? AND folder='sent' ORDER BY id DESC",(user_email,))
    elif st.session_state.menu=="Outbox": c.execute(qs+"sender=? AND folder='outbox' ORDER BY id DESC",(user_email,))
    elif st.session_state.menu=="Drafts": c.execute(qs+"sender=? AND folder='draft' ORDER BY id DESC",(user_email,))
    elif st.session_state.menu=="Trash": c.execute(qs+"(receiver=? OR sender=?) AND folder='trash' ORDER BY id DESC",(user_email,user_email))
    all_mails=c.fetchall()
    filtered_mails=[m for m in all_mails if
        (st.session_state.active_filter_label=="All" or str(m[11])==st.session_state.active_filter_label) and
        (not search_query or search_query.lower() in decrypt(m[3]).lower() or search_query.lower() in m[1].lower())]

    all_ids=[m[0] for m in filtered_mails]
    all_sel=all(st.session_state.bulk_select_matrix.get(mid,False) for mid in all_ids) if all_ids else False

    bk=st.columns([1,1.6,1.8,2])
    with bk[0]:
        if st.button("☑ Deselect All" if all_sel else "☐ Select All",use_container_width=True):
            for mid in all_ids: st.session_state.bulk_select_matrix[mid]=not all_sel
            st.rerun()
    with bk[1]:
        if st.button("✅ Mark as Read",use_container_width=True):
            for mid,v in st.session_state.bulk_select_matrix.items():
                if v:
                    c.execute("UPDATE mails SET is_read=1 WHERE id=?",(mid,))
                    c.execute("UPDATE mails SET read_receipt=1 WHERE reference_id=? AND folder='sent'",(mid,))
            conn.commit(); st.session_state.bulk_select_matrix.clear(); st.rerun()
    with bk[2]:
        if perms["trash"]:
            if st.button("🗑 Move to Trash",use_container_width=True):
                for mid,v in st.session_state.bulk_select_matrix.items():
                    if v: c.execute("UPDATE mails SET folder='trash' WHERE id=?",(mid,))
                conn.commit(); st.session_state.bulk_select_matrix.clear(); st.rerun()
        else:
            st.button("🗑 Move to Trash",use_container_width=True,disabled=True,help="Your role cannot move to trash")
    with bk[3]:
        if perms["delete"]:
            if st.button("⛔ Permanently Delete",type="primary",use_container_width=True):
                for mid,v in st.session_state.bulk_select_matrix.items():
                    if v: c.execute("DELETE FROM mails WHERE id=?",(mid,))
                conn.commit(); st.session_state.bulk_select_matrix.clear(); st.rerun()
        else:
            st.button("⛔ Permanently Delete",use_container_width=True,disabled=True,help="Your role cannot permanently delete mail")

    st.markdown("<hr style='margin:6px 0 8px 0;border:none;border-top:2px solid #009249;'>",unsafe_allow_html=True)

    # ── MAIL OPEN VIEW ───────────────────────────────────────
    if st.session_state.current_mail:
        md=st.session_state.current_mail
        c.execute("SELECT id,sender,receiver,subject,message,file_name,file_data,folder,time,is_read,reference_id,label,read_receipt FROM mails WHERE id=?",(md[0],))
        fresh=c.fetchone()
        if fresh: md=fresh; st.session_state.current_mail=fresh

        bk2,tc=st.columns([1,9])
        with bk2:
            if st.button("← Back",key="back_btn",type="secondary",use_container_width=True):
                st.session_state.current_mail=None; st.rerun()
        with tc:
            st.markdown(f"<h3 style='margin:0;padding-top:2px;color:#009249;text-align:left;'>{decrypt(md[3])}</h3>",unsafe_allow_html=True)
        st.markdown(f"<p style='color:#009249;font-size:15px;margin:2px 0 8px 0;text-align:left;'><b style='color:black;'>From:</b> <b>{md[1]}</b> &nbsp;➔&nbsp; <b style='color:black;'>To:</b> <b>{md[2]}</b> &nbsp;|&nbsp; <b>{md[8]}</b></p>",unsafe_allow_html=True)
        if md[7]=="sent":
            rr=md[12] if len(md)>12 else 0
            rr_badge="<span style='background:#DCFCE7;color:#166534;padding:2px 9px;border-radius:4px;font-size:12px;font-weight:600;'>👁️ Seen by receiver</span>" if rr==1 else "<span style='background:#FEF9C3;color:#854D0E;padding:2px 9px;border-radius:4px;font-size:12px;font-weight:600;'>📨 Not yet seen</span>"
            st.markdown(f"<div style='margin-bottom:6px;'>Read Receipt: {rr_badge}</div>",unsafe_allow_html=True)

        is_sender=(md[1]==user_email)
        ac=st.columns([2.5,1,1,4])
        with ac[0]:
            opts=["None","Urgent","Finance","HR Requests","Operations","Personal"]
            nil=st.selectbox("Label",opts,index=opts.index(md[11] if md[11] else "None"),key=f"lbl_{md[0]}",disabled=not is_sender,label_visibility="collapsed")
            if is_sender and nil!=md[11]:
                c.execute("UPDATE mails SET label=? WHERE id=?",(nil,md[0])); conn.commit(); st.session_state.current_mail=None; st.rerun()
        with ac[1]:
            if perms["compose"]:
                if st.button("↩ Reply",key=f"rp_{md[0]}",use_container_width=True):
                    import re as _re
                    ob=_re.sub(r'<[^>]+>','',decrypt(md[4]).replace("<br>","\n")).strip()
                    st.session_state.compose_defaults={"to":md[1],"subject":f"Re: {decrypt(md[3])}","msg":f"\n\n---- Original ----\n{ob}"}
                    st.session_state.typed_recipient=md[1]
                    st.session_state.compose_msg_body=f"\n\n---- Original ----\n{ob}"
                    st.session_state.menu="Compose"; st.rerun()
        with ac[2]:
            if perms["compose"]:
                if st.button("↗ Fwd",key=f"fw_{md[0]}",use_container_width=True):
                    import re as _re
                    ob=_re.sub(r'<[^>]+>','',decrypt(md[4]).replace("<br>","\n")).strip()
                    st.session_state.compose_defaults={"to":"","subject":f"Fwd: {decrypt(md[3])}","msg":f"\n\n---- Forwarded ----\n{ob}"}
                    st.session_state.compose_msg_body=f"\n\n---- Forwarded ----\n{ob}"
                    st.session_state.menu="Compose"; st.rerun()

        import re as _re2
        plain_body=_re2.sub(r'<[^>]+>','',decrypt(md[4]).replace("<br>","\n").replace("<br/>","\n").replace("&nbsp;"," ")).strip()
        st.text_area("",value=plain_body,height=420,key=f"mailbody_{md[0]}",disabled=True,label_visibility="collapsed")

        if md[5]:
            try:
                nl=json.loads(md[5]); pl=json.loads(md[6].tobytes().decode() if isinstance(md[6],memoryview) else md[6].decode())
                ac2=st.columns(min(len(nl),4))
                for i,nm in enumerate(nl):
                    fb=cipher.decrypt(pl[i].encode())
                    with ac2[i%4]: st.download_button(f"📄 {nm}",fb,file_name=nm,key=f"dl_{md[0]}_{i}",use_container_width=True)
            except: pass

    # ── MAIL LIST ────────────────────────────────────────────
    else:
        ITEMS_PER_PAGE=10
        total=len(filtered_mails)
        pages=max(1,math.ceil(total/ITEMS_PER_PAGE))
        pk=f"pg_{st.session_state.menu}"
        if pk not in st.session_state: st.session_state[pk]=1
        sl=filtered_mails[(st.session_state[pk]-1)*ITEMS_PER_PAGE:st.session_state[pk]*ITEMS_PER_PAGE]

        st.markdown("""
        <style>
        section[data-testid="stMain"] button p,
        section[data-testid="stMain"] button div,
        section[data-testid="stMain"] button span,
        div[data-testid="stVerticalBlock"] button p,
        div[data-testid="stVerticalBlock"] button div,
        div[data-testid="stVerticalBlock"] button span {
            text-align: left !important; width: 100% !important; display: block !important;
        }
        section[data-testid="stMain"] button,
        div[data-testid="stVerticalBlock"] button {
            text-align: left !important; justify-content: flex-start !important;
            align-items: flex-start !important; display: flex !important; flex-direction: column !important;
        }
        </style>""",unsafe_allow_html=True)

        st.markdown('<div class="mail-row">',unsafe_allow_html=True)
        for m in sl:
            is_unread=m[9]==0 and st.session_state.menu=="Inbox"
            dot="❤️ " if is_unread else ""
            seen="✅ Seen" if m[9]==1 else "📩 Unseen"
            if st.session_state.menu=="Sent":
                rr=m[12] if len(m)>12 else 0
                seen="👁️ Seen by receiver" if rr==1 else "📨 Not yet seen"
            lbl_txt=f"  [{m[11]}]" if m[11] and m[11]!="None" else ""
            who=f"To: {m[2]}" if st.session_state.menu in ["Sent","Drafts","Outbox"] else f"From: {m[1]}"
            subj=decrypt(m[3])
            row_txt=f"{dot}{subj}   {seen}{lbl_txt}\n{who}  •  {m[8]}"

            rc=st.columns([0.35,9.65])
            with rc[0]:
                cv=st.session_state.bulk_select_matrix.get(m[0],False)
                nv=st.checkbox("",value=cv,key=f"chk_{m[0]}_{cv}")
                st.session_state.bulk_select_matrix[m[0]]=nv
            with rc[1]:
                if st.session_state.menu=="Drafts":
                    if st.button(row_txt,key=f"ld_{m[0]}",use_container_width=True):
                        st.session_state.compose_defaults={"to":m[2],"subject":decrypt(m[3]),"msg":decrypt(m[4]),"files":None}
                        st.session_state.compose_msg_body=decrypt(m[4])
                        c.execute("DELETE FROM mails WHERE id=?",(m[0],)); conn.commit(); st.session_state.menu="Compose"; st.rerun()
                else:
                    if st.button(row_txt,key=f"v{m[0]}",use_container_width=True):
                        st.session_state.current_mail=m
                        if st.session_state.menu=="Inbox":
                            c.execute("UPDATE mails SET is_read=1 WHERE id=?",(m[0],))
                            c.execute("UPDATE mails SET read_receipt=1 WHERE reference_id=? AND folder='sent'",(m[0],))
                            conn.commit()
                        st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

        if pages>1:
            st.write("")
            pg=st.columns([1,2,1])
            with pg[0]:
                if st.session_state[pk]>1:
                    if st.button("◀ Previous",use_container_width=True): st.session_state[pk]-=1; st.rerun()
            with pg[1]:
                st.markdown(f"<p style='text-align:center;color:#009249;margin-top:8px;'><b>Page {st.session_state[pk]} of {pages}</b></p>",unsafe_allow_html=True)
            with pg[2]:
                if st.session_state[pk]<pages:
                    if st.button("Next ▶",use_container_width=True): st.session_state[pk]+=1; st.rerun()

# ── PROFILE SETTINGS ─────────────────────────────────────────
elif st.session_state.menu=="Profile Settings":
    st.title("⚙️ Profile & Security")
    with st.container(border=True):
        # Show current permissions
        st.markdown("##### 🔐 Your Role Permissions")
        perm_map={"compose":"✏ Compose","read":"📖 Read Mail","delete":"🗑 Delete","trash":"🗂 Move to Trash","attach":"📎 Attachments","view_all":"👁 View All","manage_templates":"📋 Templates"}
        pcols=st.columns(3)
        for i,(k,label) in enumerate(perm_map.items()):
            badge_cls="perm-allow" if perms[k] else "perm-deny"
            badge_txt="✅ Allowed" if perms[k] else "🚫 Denied"
            pcols[i%3].markdown(f'<span class="perm-badge {badge_cls}">{label}: {badge_txt}</span>',unsafe_allow_html=True)
        st.divider()
        ui=st.file_uploader("Upload Avatar (PNG/JPG)",type=["png","jpg"])
        if ui: c.execute("UPDATE users SET avatar_data=? WHERE id=?",(sqlite3.Binary(ui.read()),user_id)); conn.commit(); st.rerun()
        np_new=st.text_input("New Password",type="password",key="prof_np")
        np_confirm=st.text_input("Confirm New Password",type="password",key="prof_npc")
        if st.button("Update Password",type="primary") and np_new:
            if np_new!=np_confirm: st.error("❌ Passwords do not match.")
            elif len(np_new)<6: st.error("❌ Password must be at least 6 characters.")
            else:
                new_hash=bcrypt.hashpw(np_new.encode(),bcrypt.gensalt())
                c.execute("UPDATE users SET password=? WHERE id=?",(sqlite3.Binary(new_hash),user_id)); conn.commit()
                c.execute("SELECT id,username,full_name,email,password,role,department,allow_attachments,avatar_data FROM users WHERE id=?",(user_id,))
                st.session_state.user=c.fetchone()
                log_activity(username,"Password Changed","User updated own password")
                st.success("✅ Password updated successfully.")

# ── MASTER INTERCEPT ─────────────────────────────────────────
elif st.session_state.menu=="Master Intercept" and user_role=="superadmin":
    st.title("🔍 Global Intercept Monitor")
    c.execute("SELECT id,sender,receiver,subject,message,time,is_read,folder FROM mails ORDER BY id DESC LIMIT 30")
    for im in c.fetchall():
        with st.container(border=True):
            st.markdown(f"📡 **{decrypt(im[3])}** | `{im[7]}`")
            st.caption(f"From: {im[1]} ➔ To: {im[2]} | {im[5]}")
            with st.expander("Payload"):
                import re as _rim
                plain=_rim.sub(r'<[^>]+>','',decrypt(im[4]).replace("<br>","\n")).strip()
                st.text_area("",value=plain,height=150,disabled=True,label_visibility="collapsed",key=f"intcp_{im[0]}")

# ── USER MANAGEMENT ──────────────────────────────────────────
elif st.session_state.menu=="User Management" and user_role in ["superadmin","admin"]:
    st.title("👥 User Management")
    if "um_edit_id" not in st.session_state: st.session_state.um_edit_id=None
    with st.expander("➕ Create New User",expanded=False):
        with st.container(border=True):
            cu=st.columns(2)
            with cu[0]: nu=st.text_input("Username",key="um_nu"); nn=st.text_input("Full Name",key="um_nn"); ne=st.text_input("Email",key="um_ne")
            with cu[1]: np_=st.text_input("Password",type="password",key="um_np"); nr=st.selectbox("Role",["user","admin","superadmin"],key="um_nr"); nd=st.text_input("Department",value="Operations",key="um_nd"); na=st.selectbox("Allow Attachments",[1,0],format_func=lambda x:"✅ Yes" if x==1 else "❌ No",key="um_na")
            if st.button("✅ Create User",type="primary",use_container_width=True):
                if nu and nn and ne and np_ and nd:
                    try:
                        c.execute("INSERT INTO users (username,full_name,email,password,role,department,allow_attachments) VALUES (?,?,?,?,?,?,?)",
                                  (nu,nn,ne,sqlite3.Binary(bcrypt.hashpw(np_.encode(),bcrypt.gensalt())),nr,nd,na)); conn.commit()
                        log_activity(username,"User Created",f"Created {nu}"); st.success(f"✅ User '{nu}' created."); st.rerun()
                    except sqlite3.IntegrityError: st.error("❌ Username or email already exists.")
                else: st.error("All fields required.")
    st.divider(); st.markdown("### 👤 All Users")
    c.execute("SELECT id,username,full_name,email,role,department,allow_attachments FROM users ORDER BY id ASC")
    for ur in c.fetchall():
        uid,uname,ufull,uemail,urole_,udept,uatt=ur; is_self=(uid==user_id)
        with st.container(border=True):
            hc=st.columns([3,1,1])
            with hc[0]:
                # Show permission badges inline
                up=get_permissions(urole_)
                pbadges="".join([f'<span class="perm-badge {"perm-allow" if v else "perm-deny"}">{k}</span>' for k,v in up.items()])
                st.markdown(f"**{ufull}** `{uname}` {'📎✅' if uatt==1 else '📎❌'}<br><small style='color:#64748B;'>{uemail} | **{urole_}** | {udept}</small><br>{pbadges}",unsafe_allow_html=True)
            with hc[1]:
                if st.button("✏️ Edit",key=f"ue_{uid}",use_container_width=True): st.session_state.um_edit_id=uid if st.session_state.um_edit_id!=uid else None; st.rerun()
            with hc[2]:
                if not is_self:
                    if st.button("🗑️ Delete",key=f"ud_{uid}",use_container_width=True,type="primary"):
                        c.execute("DELETE FROM users WHERE id=?",(uid,)); conn.commit(); log_activity(username,"Deleted",uname)
                        if st.session_state.um_edit_id==uid: st.session_state.um_edit_id=None
                        st.success(f"Deleted '{uname}'."); st.rerun()
                else: st.button("🔒 Self",key=f"us_{uid}",disabled=True,use_container_width=True)
            if st.session_state.um_edit_id==uid:
                st.divider(); ec=st.columns(2)
                with ec[0]: ef=st.text_input("Full Name",value=ufull,key=f"ef_{uid}"); ee=st.text_input("Email",value=uemail,key=f"ee_{uid}"); edep=st.text_input("Dept",value=udept,key=f"ed_{uid}")
                with ec[1]:
                    ro=["user","admin","superadmin"]; er=st.selectbox("Role",ro,index=ro.index(urole_) if urole_ in ro else 0,key=f"er_{uid}")
                    ea=st.selectbox("Attachments",[1,0],index=0 if uatt==1 else 1,format_func=lambda x:"✅ Yes" if x==1 else "❌ No",key=f"ea_{uid}")
                    ep=st.text_input("New Password (blank=keep)",type="password",key=f"ep_{uid}")
                sc=st.columns([1,1,2])
                with sc[0]:
                    if st.button("💾 Save",key=f"es_{uid}",type="primary",use_container_width=True):
                        if ep: c.execute("UPDATE users SET full_name=?,email=?,department=?,role=?,allow_attachments=?,password=? WHERE id=?",(ef,ee,edep,er,ea,sqlite3.Binary(bcrypt.hashpw(ep.encode(),bcrypt.gensalt())),uid))
                        else: c.execute("UPDATE users SET full_name=?,email=?,department=?,role=?,allow_attachments=? WHERE id=?",(ef,ee,edep,er,ea,uid))
                        conn.commit(); log_activity(username,"Updated",uname); st.success("✅ Updated."); st.session_state.um_edit_id=None; st.rerun()
                with sc[1]:
                    if st.button("❌ Cancel",key=f"ec_{uid}",use_container_width=True): st.session_state.um_edit_id=None; st.rerun()

# ── MANAGE TEMPLATES ─────────────────────────────────────────
elif st.session_state.menu=="Manage Templates" and perms["manage_templates"]:
    st.title("📋 Manage Mail Templates")
    st.markdown("Add, edit, or delete message templates. Changes take effect immediately for all users in Compose.")

    if "tpl_edit_id" not in st.session_state: st.session_state.tpl_edit_id=None
    if "tpl_add_mode" not in st.session_state: st.session_state.tpl_add_mode=False

    # ── Add new template ──
    with st.expander("➕ Add New Template", expanded=st.session_state.tpl_add_mode):
        with st.container(border=True):
            tn=st.text_input("Template Name",key="tpl_new_name",placeholder="e.g. Vendor Follow-Up")
            tto_new=st.text_input("To (optional)",key="tpl_new_to",placeholder="e.g. manager@lingam.local, hr@lingam.local")
            tcc_new=st.text_input("CC (optional)",key="tpl_new_cc",placeholder="e.g. accounts@lingam.local")
            ts_=st.text_input("Subject Line",key="tpl_new_subj",placeholder="e.g. Follow-Up – [Vendor Name]")
            tb=st.text_area("Body",key="tpl_new_body",height=200,placeholder="Write the template body here. Use [placeholders] for variable parts.")
            if st.button("✅ Save Template",type="primary",use_container_width=True):
                if tn.strip() and ts_.strip() and tb.strip():
                    now_ts=datetime.now().strftime("%b %d, %Y %I:%M %p")
                    c.execute("INSERT INTO mail_templates (name,subject,body,created_by,created_at,to_addr,cc_addr) VALUES (?,?,?,?,?,?,?)",
                              (tn.strip(),ts_.strip(),tb.strip(),username,now_ts,tto_new.strip(),tcc_new.strip()))
                    conn.commit()
                    log_activity(username,"Template Added",f"Added template '{tn.strip()}'")
                    st.success(f"✅ Template '{tn.strip()}' added.")
                    st.session_state.tpl_add_mode=False
                    st.rerun()
                else: st.error("Name, Subject and Body are required.")

    st.divider()
    st.markdown("### 📄 Existing Templates")
    all_tpls=get_mail_templates()
    if not all_tpls:
        st.info("No templates yet. Use the form above to add one.")
    for tpl in all_tpls:
        tid,tname,tsubj,tbody,tcreator,tcreated,tto,tcc=tpl
        with st.container(border=True):
            hc=st.columns([4,1,1])
            with hc[0]:
                st.markdown(f"**{tname}**")
                if tto: st.caption(f"To: {tto}")
                if tcc: st.caption(f"CC: {tcc}")
                st.caption(f"Subject: {tsubj}")
                st.caption(f"Created by: `{tcreator}` on {tcreated}")
            with hc[1]:
                if st.button("✏️ Edit",key=f"te_{tid}",use_container_width=True):
                    st.session_state.tpl_edit_id=tid if st.session_state.tpl_edit_id!=tid else None
                    st.rerun()
            with hc[2]:
                if st.button("🗑️ Delete",key=f"td_{tid}",use_container_width=True,type="primary"):
                    c.execute("DELETE FROM mail_templates WHERE id=?",(tid,))
                    conn.commit()
                    log_activity(username,"Template Deleted",f"Deleted template '{tname}'")
                    if st.session_state.tpl_edit_id==tid: st.session_state.tpl_edit_id=None
                    st.success(f"Deleted '{tname}'.")
                    st.rerun()
            if st.session_state.tpl_edit_id==tid:
                st.divider()
                en=st.text_input("Name",value=tname,key=f"ten_{tid}")
                eto=st.text_input("To (optional)",value=tto,key=f"teto_{tid}",placeholder="e.g. manager@lingam.local")
                etc=st.text_input("CC (optional)",value=tcc,key=f"tetc_{tid}",placeholder="e.g. hr@lingam.local")
                es=st.text_input("Subject",value=tsubj,key=f"tes_{tid}")
                eb=st.text_area("Body",value=tbody,height=200,key=f"teb_{tid}")
                sc=st.columns([1,1,3])
                with sc[0]:
                    if st.button("💾 Save",key=f"tse_{tid}",type="primary",use_container_width=True):
                        if en.strip() and es.strip() and eb.strip():
                            c.execute("UPDATE mail_templates SET name=?,subject=?,body=?,to_addr=?,cc_addr=? WHERE id=?",
                                      (en.strip(),es.strip(),eb.strip(),eto.strip(),etc.strip(),tid))
                            conn.commit()
                            log_activity(username,"Template Updated",f"Updated template '{en.strip()}'")
                            st.success("✅ Updated.")
                            st.session_state.tpl_edit_id=None
                            st.rerun()
                        else: st.error("Name, Subject and Body are required.")
                with sc[1]:
                    if st.button("❌ Cancel",key=f"tce_{tid}",use_container_width=True):
                        st.session_state.tpl_edit_id=None; st.rerun()

# ── ACTIVITY MONITOR ─────────────────────────────────────────
elif st.session_state.menu=="Activity Monitor" and user_role in ["superadmin","admin"]:
    st.title("📊 Security Audit Logs")
    c.execute("SELECT timestamp,user,action,details FROM audit_logs ORDER BY id DESC LIMIT 100")
    for lg in c.fetchall(): st.write(f"`{lg[0]}` | **{lg[1]}**: {lg[2]} - {lg[3]}")
st.sidebar.caption("Lingam Secure Mail v7.0 - Enterprise Suite Active")
