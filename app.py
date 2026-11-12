
import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# =========================
# KONFIGURASI DASHBOARD
# =========================

st.set_page_config(
    page_title="ProyekKu Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================
# MEMBACA DATABASE
# =========================

@st.cache_data
def load_data():
    df = pd.read_csv("database_project.csv")

    df["tanggal_mulai"] = pd.to_datetime(
        df["tanggal_mulai"], errors="coerce"
    )

    df["tenggat"] = pd.to_datetime(
        df["tenggat"], errors="coerce"
    )

    df["progress"] = pd.to_numeric(
        df["progress"], errors="coerce"
    ).fillna(0)

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal membaca database: {e}")
    st.stop()

# =========================
# JUDUL
# =========================

st.title("📊 ProyekKu")
st.subheader("Dashboard Manajemen Tugas & Proyek")

st.write(
    "Pantau tugas, produktivitas tim, "
    "dan perkembangan proyek."
)

st.divider()

# =========================
# FILTER
# =========================

st.sidebar.title("🔎 Filter Dashboard")

anggota_list = ["Semua"] + sorted(
    df["anggota"].dropna().unique().tolist()
)

prioritas_list = ["Semua", "High", "Medium", "Low"]

anggota_pilih = st.sidebar.selectbox(
    "Pilih Anggota Tim",
    anggota_list
)

prioritas_pilih = st.sidebar.selectbox(
    "Pilih Prioritas",
    prioritas_list
)

data = df.copy()

if anggota_pilih != "Semua":
    data = data[data["anggota"] == anggota_pilih]

if prioritas_pilih != "Semua":
    data = data[data["prioritas"] == prioritas_pilih]

# =========================
# KPI
# =========================

total = len(data)

selesai = len(
    data[data["status"] == "Done"]
)

pending = len(
    data[data["status"] == "To Do"]
)

terlambat = len(
    data[
        (data["tenggat"].dt.date < date.today()) &
        (data["status"] != "Done")
    ]
)

st.subheader("📌 Indikator Utama")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Tugas", total)
c2.metric("Tugas Selesai", selesai)
c3.metric("Tugas Pending", pending)
c4.metric("Tugas Terlambat", terlambat)

st.divider()

# =========================
# GRAFIK BEBAN KERJA
# =========================

st.subheader("👥 Beban Kerja Anggota Tim")

beban = (
    data.groupby("anggota")
    .size()
    .reset_index(name="Jumlah Tugas")
)

st.bar_chart(
    beban,
    x="anggota",
    y="Jumlah Tugas",
    color="#2563EB"
)

# =========================
# GRAFIK STATUS DONUT
# =========================

st.subheader("🍩 Status Tugas")

status_data = (
    data["status"]
    .value_counts()
    .rename_axis("Status")
    .reset_index(name="Jumlah")
)

if not status_data.empty:
    donut = alt.Chart(status_data).mark_arc(
        innerRadius=65
    ).encode(
        theta=alt.Theta("Jumlah:Q"),
        color=alt.Color(
            "Status:N",
            scale=alt.Scale(
                domain=["To Do", "In Progress", "Done"],
                range=["#F59E0B", "#3B82F6", "#16A34A"]
            )
        ),
        tooltip=["Status", "Jumlah"]
    )

    st.altair_chart(donut, use_container_width=True)
else:
    st.info("Belum ada data status tugas.")

# =========================
# PROGRES MINGGUAN
# =========================

st.subheader("📈 Progres Mingguan")

mingguan = data.dropna(
    subset=["tanggal_mulai"]
).copy()

if not mingguan.empty:
    mingguan["Minggu"] = (
        mingguan["tanggal_mulai"]
        .dt.to_period("W")
        .astype(str)
    )

    progres = (
        mingguan.groupby("Minggu")["progress"]
        .mean()
        .reset_index()
    )

    progres = progres.sort_values("Minggu")

    st.line_chart(
        progres,
        x="Minggu",
        y="progress",
        color="#16A34A"
    )
else:
    st.info("Belum ada data progres mingguan.")

# =========================
# TABEL DAFTAR TUGAS
# =========================

st.divider()

st.subheader("📋 Daftar Tugas")

kolom = [
    "id",
    "nama_tugas",
    "anggota",
    "prioritas",
    "status",
    "tenggat",
    "progress"
]

st.dataframe(
    data[kolom],
    use_container_width=True,
    hide_index=True
)

# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "ProyekKu | Dashboard Manajemen Tugas "
    "dan Proyek menggunakan Python & Streamlit"
)
