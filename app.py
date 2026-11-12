from datetime import date
import altair as alt
import pandas as pd
import streamlit as st
from sqlalchemy import (Column, Date, Integer, MetaData, String, Table,
                        create_engine, delete, func, insert, select, update)

st.set_page_config(page_title="ProyekKu", layout="wide", initial_sidebar_state="collapsed")

STATUSES = ["To Do", "In Progress", "Done"]
PRIOS = ["High", "Medium", "Low"]
PAGES = ["Overview", "Task Management", "Team Members", "Reports", "Settings"]
ACCENT, MUTED, BORDER, SURFACE = "#5B9CFF", "#8A8D93", "#26282C", "#17181B"

# ---------- ICONS ----------
_I = {
 "Overview": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
 "Task Management": '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
 "Team Members": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
 "Reports": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
 "Settings": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
 "total": '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
 "done": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
 "pending": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
 "late": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
}
def icon(n, s=18):
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{_I[n]}</svg>')

# ---------- STYLE ----------
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html,body,[class*="css"],.stApp{{font-family:'Inter',system-ui,sans-serif;font-size:13px;}}
.stApp{{background:#101113;}}
header[data-testid="stHeader"]{{background:transparent;}}
#MainMenu,footer{{visibility:hidden;}}
.block-container{{max-width:1200px;padding:1rem 1rem 6rem;animation:fi .35s ease;}}
@keyframes fi{{from{{opacity:0}}to{{opacity:1}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
h1{{font-size:24px!important;font-weight:600!important;letter-spacing:-.01em;padding:0!important}}
h2,h3{{font-size:16px!important;font-weight:600!important}}
section[data-testid="stSidebar"]{{background:{SURFACE};border-right:1px solid {BORDER};}}
.sub{{color:{MUTED};font-size:12px;margin:2px 0 10px}}
.nav{{display:flex;gap:4px;margin-bottom:18px;border-bottom:1px solid {BORDER};padding-bottom:8px;overflow-x:auto}}
.nav a{{display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:6px;color:{MUTED}!important;text-decoration:none!important;font-size:12.5px;white-space:nowrap;transition:background .2s,color .2s}}
.nav a:hover{{background:#1d1f23;color:#E6E7E9!important}}
.nav a.on{{background:#22252a;color:#fff!important}}
@media(max-width:768px){{
 .nav{{position:fixed;left:0;right:0;bottom:0;z-index:999;background:#101113;border-top:1px solid {BORDER};border-bottom:0;margin:0;padding:6px;justify-content:space-around}}
 .nav a{{flex-direction:column;gap:3px;font-size:10px;padding:6px 8px;min-width:56px;align-items:center}}
}}
.kpi{{background:{SURFACE};border:1px solid {BORDER};border-radius:8px;padding:14px;transition:border-color .2s,transform .2s;height:100%}}
.kpi:hover{{border-color:#3a3d43;transform:translateY(-1px)}}
.kpi .t{{display:flex;justify-content:space-between;color:{MUTED};font-size:12px}}
.kpi .v{{font-size:28px;font-weight:600;margin-top:6px;line-height:1.1}}
.kpi .d{{color:{MUTED};font-size:11px;margin-top:4px}}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{{border-radius:6px;border:1px solid #33363b;background:#1b1d20;font-size:12.5px;min-height:40px;transition:background .2s,border-color .2s}}
.stButton>button:hover,.stFormSubmitButton>button:hover,.stDownloadButton>button:hover{{border-color:{ACCENT};background:#202226}}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{{background:{ACCENT};border-color:{ACCENT};color:#0b0c0e;font-weight:500}}
div[data-testid="stDialog"] div[role="dialog"]{{animation:fi .2s ease}}
input,textarea,[data-baseweb="select"]>div{{font-size:13px!important}}
</style>""", unsafe_allow_html=True)

# ---------- DATABASE (persistent via external SQL; SQLite fallback for local dev) ----------
meta = MetaData()
T = Table("tasks", meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nama_tugas", String(200), nullable=False), Column("anggota", String(100)),
    Column("prioritas", String(20)), Column("status", String(20)),
    Column("tanggal_mulai", Date), Column("tenggat", Date), Column("progress", Integer))
M = Table("members", meta, Column("name", String(100), primary_key=True))

@st.cache_resource
def get_engine():
    url = "sqlite:///proyekku.db"
    try:
        url = st.secrets["db"]["url"].replace("postgres://", "postgresql://", 1)
    except Exception:
        pass
    eng = create_engine(url, pool_pre_ping=True)
    meta.create_all(eng)
    with eng.begin() as c:
        empty = c.execute(select(func.count()).select_from(T)).scalar() == 0 and \
                c.execute(select(func.count()).select_from(M)).scalar() == 0
        if empty:
            try:
                d = pd.read_csv("database_project.csv").sort_values("id")
                for col in ("tanggal_mulai", "tenggat"):
                    d[col] = pd.to_datetime(d[col], errors="coerce").dt.date
                d["progress"] = pd.to_numeric(d["progress"], errors="coerce").fillna(0).astype(int)
                d = d.astype(object).where(d.notna(), None)
                cols = ["nama_tugas", "anggota", "prioritas", "status", "tanggal_mulai", "tenggat", "progress"]
                rows = d[cols].to_dict("records")
                if rows:
                    c.execute(insert(T), rows)
                names = [{"name": n} for n in d["anggota"].dropna().unique()]
                if names:
                    c.execute(insert(M), names)
            except Exception as e:
                st.warning(f"Seed from CSV skipped: {e}")
    return eng

def run(stmt):
    try:
        with get_engine().begin() as c:
            c.execute(stmt)
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def load():
    with get_engine().connect() as c:
        df = pd.read_sql(select(T).order_by(T.c.id), c)
        mem = pd.read_sql(select(M), c)["name"].tolist()
    for col in ("tanggal_mulai", "tenggat"):
        df[col] = pd.to_datetime(df[col])
    df["progress"] = pd.to_numeric(df["progress"], errors="coerce").fillna(0)
    members = sorted(set(mem) | set(df["anggota"].dropna()))
    return df, members

def overdue_mask(d):
    return (d["tenggat"].dt.date < date.today()) & (d["status"] != "Done")

# ---------- DIALOGS ----------
@st.dialog("Task")
def task_dialog(members, row=None):
    if not members:
        st.info("Add a team member first on the Team Members page.")
        return
    g = (lambda k, dflt: dflt if row is None or pd.isna(row[k]) else row[k])
    with st.form("task_form", border=False):
        name = st.text_input("Task Name", value=g("nama_tugas", ""))
        who = st.selectbox("Assigned Member", members, index=members.index(g("anggota", members[0])) if g("anggota", members[0]) in members else 0)
        c1, c2 = st.columns(2)
        prio = c1.selectbox("Priority", PRIOS, index=PRIOS.index(g("prioritas", "Medium")))
        stat = c2.selectbox("Status", STATUSES, index=STATUSES.index(g("status", "To Do")))
        d1 = c1.date_input("Start Date", value=pd.Timestamp(g("tanggal_mulai", date.today())).date())
        d2 = c2.date_input("Due Date", value=pd.Timestamp(g("tenggat", date.today())).date())
        prog = st.number_input("Progress (%)", 0, 100, int(g("progress", 0)), step=5)
        st.caption("Progress is set to 100 when status is Done.")
        a, b = st.columns(2)
        save = a.form_submit_button("Save Task", type="primary", use_container_width=True)
        b.form_submit_button("Cancel", use_container_width=True)
    if save:
        if not name.strip():
            st.error("Task name is required."); return
        if d2 < d1:
            st.error("Due date cannot be earlier than start date."); return
        vals = dict(nama_tugas=name.strip(), anggota=who, prioritas=prio, status=stat,
                    tanggal_mulai=d1, tenggat=d2, progress=100 if stat == "Done" else int(prog))
        ok = run(insert(T).values(**vals) if row is None else update(T).where(T.c.id == int(row["id"])).values(**vals))
        if ok:
            st.session_state["toast"] = "Task saved"
            st.rerun()

@st.dialog("Delete task")
def delete_dialog(row):
    st.write(f"Delete task **{row['nama_tugas']}**? This cannot be undone.")
    a, b = st.columns(2)
    if a.button("Delete", type="primary", use_container_width=True):
        if run(delete(T).where(T.c.id == int(row["id"]))):
            st.session_state["toast"] = "Task deleted"
            st.rerun()
    if b.button("Cancel", use_container_width=True):
        st.rerun()

# ---------- CHART HELPERS ----------
def style(ch):
    return (ch.configure(background="transparent").configure_view(strokeWidth=0)
        .configure_axis(labelColor=MUTED, titleColor=MUTED, gridColor=BORDER, domainColor=BORDER, labelFontSize=11, titleFontSize=11)
        .configure_legend(labelColor=MUTED, titleColor=MUTED, orient="bottom", labelFontSize=11))

def kpi(col, label, value, note, ic):
    col.markdown(f'<div class="kpi"><div class="t"><span>{label}</span>{icon(ic)}</div><div class="v">{value}</div><div class="d">{note}</div></div>', unsafe_allow_html=True)

def workload_chart(d):
    b = d.groupby("anggota").size().reset_index(name="Tasks")
    if b.empty: return st.info("No data for the current filters.")
    st.altair_chart(style(alt.Chart(b).mark_bar(color=ACCENT, cornerRadiusEnd=2).encode(
        x=alt.X("anggota:N", sort="-y", title=None, axis=alt.Axis(labelAngle=-30)), y=alt.Y("Tasks:Q", title=None, axis=alt.Axis(tickMinStep=1)),
        tooltip=[alt.Tooltip("anggota:N", title="Member"), "Tasks:Q"]).properties(height=240)), use_container_width=True)

def status_chart(d):
    s = d["status"].value_counts().rename_axis("Status").reset_index(name="Count")
    if s.empty: return st.info("No data for the current filters.")
    s["Percent"] = (s["Count"] / s["Count"].sum() * 100).round(1)
    st.altair_chart(style(alt.Chart(s).mark_arc(innerRadius=60, stroke="#101113").encode(
        theta="Count:Q", color=alt.Color("Status:N", scale=alt.Scale(domain=STATUSES, range=["#4B4F55", ACCENT, "#D4D4D8"])),
        tooltip=["Status", "Count", alt.Tooltip("Percent:Q", format=".1f")]).properties(height=240)), use_container_width=True)

def weekly_chart(d):
    w = d.dropna(subset=["tanggal_mulai"]).copy()
    if w.empty: return st.info("No data for the current filters.")
    w["Week"] = w["tanggal_mulai"].dt.to_period("W").dt.start_time
    p = w.groupby("Week")["progress"].mean().round(1).reset_index(name="Avg progress")
    st.altair_chart(style(alt.Chart(p).mark_line(color=ACCENT, point=alt.OverlayMarkDef(color=ACCENT)).encode(
        x=alt.X("Week:T", title=None, axis=alt.Axis(format="%d %b")), y=alt.Y("Avg progress:Q", title="Avg progress (%)", scale=alt.Scale(domain=[0, 100])),
        tooltip=[alt.Tooltip("Week:T", title="Week of", format="%d %b %Y"), "Avg progress:Q"]).properties(height=240)), use_container_width=True)

def member_stats(df, members):
    rows = []
    for m in members:
        d = df[df["anggota"] == m]; t = len(d); dn = int((d["status"] == "Done").sum())
        rows.append({"Member": m, "Tasks": t, "Done": dn, "In Progress": int((d["status"] == "In Progress").sum()),
                     "Completion": round(dn / t * 100) if t else 0})
    return pd.DataFrame(rows, columns=["Member", "Tasks", "Done", "In Progress", "Completion"])

PROG = st.column_config.ProgressColumn("Progress", min_value=0, max_value=100, format="%d%%")
def show(d, **kw):
    st.dataframe(d, hide_index=True, use_container_width=True, **kw)

# ---------- MAIN ----------
page = st.query_params.get("page", "Overview")
page = page if page in PAGES else "Overview"
try:
    df, members = load()
except Exception as e:
    st.error(f"Cannot read the database: {e}"); st.stop()

if "toast" in st.session_state:
    st.toast(st.session_state.pop("toast"))

st.markdown('<nav class="nav">' + "".join(
    f'<a href="?page={p.replace(" ", "%20")}" target="_self" class="{"on" if p == page else ""}">{icon(p)}<span>{p}</span></a>' for p in PAGES) + '</nav>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Filters")
    f_m = st.selectbox("Member", ["All"] + members)
    f_p = st.selectbox("Priority", ["All"] + PRIOS)
    f_s = st.selectbox("Status", ["All"] + STATUSES)
data = df.copy()
if f_m != "All": data = data[data["anggota"] == f_m]
if f_p != "All": data = data[data["prioritas"] == f_p]
if f_s != "All": data = data[data["status"] == f_s]

if page == "Overview":
    h1, h2 = st.columns([3, 1], vertical_alignment="center")
    h1.title("Project Management")
    h1.markdown(f'<div class="sub">Manage tasks, monitor team performance, and track project progress.<br>{date.today():%A, %d %B %Y}</div>', unsafe_allow_html=True)
    if h2.button("Add New Task", type="primary", use_container_width=True):
        task_dialog(members)
    total, done = len(data), int((data["status"] == "Done").sum())
    pend, late = int((data["status"] == "To Do").sum()), int(overdue_mask(data).sum())
    pct = lambda n: f"{n / total * 100:.0f}% of total" if total else "No tasks"
    st.markdown(f'<div class="sub">{done} of {total} tasks completed, {late} overdue.</div>', unsafe_allow_html=True)
    k = st.columns(4)
    kpi(k[0], "Total Tasks", total, "Matches active filters", "total")
    kpi(k[1], "Completed Tasks", done, pct(done), "done")
    kpi(k[2], "Pending Tasks", pend, pct(pend), "pending")
    kpi(k[3], "Overdue Tasks", late, pct(late), "late")
    st.write("")
    a, b = st.columns(2)
    with a.container(border=True):
        st.subheader("Team Workload"); workload_chart(data)
    with b.container(border=True):
        st.subheader("Task Status"); status_chart(data)
    with st.container(border=True):
        st.subheader("Weekly Progress"); weekly_chart(data)

elif page == "Task Management":
    st.title("Task Management")
    q = st.text_input("Search by task name", placeholder="Search tasks", label_visibility="collapsed")
    view = data[data["nama_tugas"].str.contains(q, case=False, na=False)] if q else data
    view = view.reset_index(drop=True)
    a, b, c = st.columns([1, 1, 1])
    ev = st.dataframe(view.assign(tenggat=view["tenggat"].dt.strftime("%d %b %Y"))[["id", "nama_tugas", "anggota", "prioritas", "status", "tenggat", "progress"]].rename(columns={
        "id": "ID", "nama_tugas": "Task Name", "anggota": "Assigned Member", "prioritas": "Priority", "status": "Status", "tenggat": "Due Date"}),
        hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row", column_config={"progress": PROG})
    sel = ev.selection.rows
    row = view.iloc[sel[0]] if sel else None
    if a.button("Add Task", type="primary", use_container_width=True): task_dialog(members)
    if b.button("Edit", disabled=row is None, use_container_width=True): task_dialog(members, row)
    if c.button("Delete", disabled=row is None, use_container_width=True): delete_dialog(row)
    st.caption(f"{len(view)} tasks. Select a row to edit or delete.")

elif page == "Team Members":
    st.title("Team Members")
    show(member_stats(df, members), column_config={"Completion": st.column_config.ProgressColumn("Completion", min_value=0, max_value=100, format="%d%%")})
    c1, c2 = st.columns(2)
    with c1.form("add_member", border=True, clear_on_submit=True):
        nm = st.text_input("New member name")
        if st.form_submit_button("Add Member", type="primary", use_container_width=True):
            if not nm.strip(): st.error("Name is required.")
            elif nm.strip() in members: st.error("Member already exists.")
            elif run(insert(M).values(name=nm.strip())):
                st.session_state["toast"] = "Member added"; st.rerun()
    with c2.form("del_member", border=True):
        dm = st.selectbox("Remove member", members) if members else None
        if st.form_submit_button("Remove Member", use_container_width=True) and dm:
            if (df["anggota"] == dm).any(): st.error("Member still has tasks. Reassign or delete them first.")
            elif run(delete(M).where(M.c.name == dm)):
                st.session_state["toast"] = "Member removed"; st.rerun()

elif page == "Reports":
    st.title("Reports")
    st.markdown('<div class="sub">Reports follow the active filters.</div>', unsafe_allow_html=True)
    done = int((data["status"] == "Done").sum())
    st.metric("Project completion", f"{done / len(data) * 100:.0f}%" if len(data) else "0%")
    a, b = st.columns(2)
    with a.container(border=True):
        st.subheader("Tasks by Status"); status_chart(data)
    with b.container(border=True):
        st.subheader("Priority Distribution")
        pr = data["prioritas"].value_counts().reindex(PRIOS, fill_value=0).rename_axis("Priority").reset_index(name="Tasks")
        st.altair_chart(style(alt.Chart(pr).mark_bar(color=ACCENT, cornerRadiusEnd=2).encode(
            x=alt.X("Priority:N", sort=PRIOS, title=None, axis=alt.Axis(labelAngle=0)), y=alt.Y("Tasks:Q", title=None, axis=alt.Axis(tickMinStep=1)),
            tooltip=["Priority", "Tasks"]).properties(height=240)), use_container_width=True)
    st.subheader("Member Performance")
    show(member_stats(data, sorted(data["anggota"].dropna().unique())), column_config={"Completion": st.column_config.ProgressColumn("Completion", min_value=0, max_value=100, format="%d%%")})
    st.subheader("Overdue Tasks")
    od = data[overdue_mask(data)]
    if od.empty: st.info("No overdue tasks.")
    else: show(od.assign(tenggat=od["tenggat"].dt.strftime("%d %b %Y"))[["id", "nama_tugas", "anggota", "prioritas", "status", "tenggat", "progress"]], column_config={"progress": PROG})
    st.download_button("Export CSV", data.to_csv(index=False).encode(), "proyekku_report.csv", "text/csv")

else:
    st.title("Settings")
    backend = get_engine().dialect.name
    st.markdown(f'<div class="sub">Storage backend: {backend}</div>', unsafe_allow_html=True)
    if backend == "sqlite":
        st.warning("SQLite is local and resets on Streamlit Cloud restarts. Add a Postgres URL in secrets (see README) for permanent storage.")
    else:
        st.success("Connected to external database. Data is persistent.")
    st.download_button("Download full backup (CSV)", df.to_csv(index=False).encode(), "proyekku_backup.csv", "text/csv")
