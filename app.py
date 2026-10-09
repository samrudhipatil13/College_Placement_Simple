import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="College Placement Analysis",
    page_icon="🎓",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title  { font-size:2rem; font-weight:700; color:#1a1a2e; margin-bottom:0; }
    .sub-title   { font-size:1rem; color:#555; margin-bottom:1.5rem; }
    .insight-box { background:#f0f4ff; border-left:4px solid #4361ee;
                   padding:12px 16px; border-radius:6px; font-size:0.9rem;
                   color:#1a1a2e; margin-top:8px; }
    .section-head{ font-size:1.1rem; font-weight:600; color:#1a1a2e;
                   margin-top:1.5rem; margin-bottom:0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("placement_data.csv")
    df["Placed_Flag"] = df["Placed"].apply(lambda x: 1 if x == "Yes" else 0)
    df["Internship_Flag"] = df["Internship"].apply(lambda x: 1 if x == "Yes" else 0)
    df["Package_LPA"] = pd.to_numeric(df["Package_LPA"], errors="coerce").fillna(0)
    return df

df = load_data()

# ── Sidebar Filters ────────────────────────────────────────────────────────────
st.sidebar.markdown("## Filters")

branches = ["All"] + sorted(df["Branch"].unique().tolist())
years    = ["All"] + sorted(df["Year"].unique().tolist())

sel_branch = st.sidebar.selectbox("Branch", branches)
sel_year   = st.sidebar.selectbox("Batch Year", years)
sel_placed = st.sidebar.radio("Placement Status", ["All", "Placed", "Not Placed"])

# Apply filters
fdf = df.copy()
if sel_branch != "All":
    fdf = fdf[fdf["Branch"] == sel_branch]
if sel_year != "All":
    fdf = fdf[fdf["Year"] == sel_year]
if sel_placed == "Placed":
    fdf = fdf[fdf["Placed"] == "Yes"]
elif sel_placed == "Not Placed":
    fdf = fdf[fdf["Placed"] == "No"]

placed_df = fdf[fdf["Placed"] == "Yes"]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🎓 College Placement Analysis Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">2020–2024 Batch Data | Interactive Placement Insights</p>', unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total     = len(fdf)
placed_n  = fdf["Placed_Flag"].sum()
place_pct = round((placed_n / total * 100) if total > 0 else 0, 1)
avg_pkg   = round(placed_df["Package_LPA"].mean(), 2) if len(placed_df) > 0 else 0
max_pkg   = round(placed_df["Package_LPA"].max(), 2) if len(placed_df) > 0 else 0

k1.metric("Total Students", total)
k2.metric("Placed Students", int(placed_n))
k3.metric("Placement %", f"{place_pct}%")
k4.metric("Avg Package", f"{avg_pkg} LPA")

st.markdown("---")

# ── Row 1: Branch Placement % + Year-wise Trend ───────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="section-head">Branch-wise Placement %</p>', unsafe_allow_html=True)
    branch_data = df.groupby("Branch")["Placed_Flag"].mean().mul(100).round(1).reset_index()
    branch_data.columns = ["Branch", "Placement %"]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    colors = ["#4361ee" if b == sel_branch else "#adb5bd" for b in branch_data["Branch"]]
    if sel_branch == "All":
        colors = ["#4361ee"] * len(branch_data)
    sns.barplot(data=branch_data, x="Branch", y="Placement %", palette=colors, ax=ax)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylim(0, 110)
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.0f}%",
                    (p.get_x() + p.get_width() / 2, p.get_height() + 1),
                    ha="center", va="bottom", fontsize=9)
    ax.set_xlabel(""); ax.set_ylabel("Placement %")
    sns.despine()
    st.pyplot(fig)
    plt.close()
    best_branch = branch_data.loc[branch_data["Placement %"].idxmax(), "Branch"]
    best_pct    = branch_data["Placement %"].max()
    st.markdown(f'<div class="insight-box">💡 <b>{best_branch}</b> mein sabse zyada placement rate hai — <b>{best_pct}%</b></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<p class="section-head">Year-wise Placement Trend</p>', unsafe_allow_html=True)
    year_data = df.groupby("Year")["Placed_Flag"].mean().mul(100).round(1).reset_index()
    year_data.columns = ["Year", "Placement %"]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.plot(year_data["Year"], year_data["Placement %"],
            marker="o", color="#4361ee", linewidth=2.5, markersize=7)
    ax.fill_between(year_data["Year"], year_data["Placement %"], alpha=0.1, color="#4361ee")
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    for _, row in year_data.iterrows():
        ax.annotate(f"{row['Placement %']:.0f}%",
                    (row["Year"], row["Placement %"] + 2),
                    ha="center", fontsize=9)
    ax.set_xlabel("Batch Year"); ax.set_ylabel("Placement %")
    sns.despine()
    st.pyplot(fig)
    plt.close()
    min_year = year_data.loc[year_data["Placement %"].idxmin(), "Year"]
    min_pct  = year_data["Placement %"].min()
    st.markdown(f'<div class="insight-box">💡 <b>{min_year}</b> batch mein placement <b>{min_pct}%</b> raha — COVID ya economic slowdown ka asar ho sakta hai</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Row 2: CGPA vs Package + Top Companies ────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<p class="section-head">CGPA vs Salary Package</p>', unsafe_allow_html=True)
    scatter_df = fdf[fdf["Placed"] == "Yes"]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    branches_list = scatter_df["Branch"].unique()
    palette = sns.color_palette("Set2", len(branches_list))
    for i, br in enumerate(branches_list):
        sub = scatter_df[scatter_df["Branch"] == br]
        ax.scatter(sub["CGPA"], sub["Package_LPA"],
                   label=br, color=palette[i], alpha=0.8, s=60)
    ax.set_xlabel("CGPA"); ax.set_ylabel("Package (LPA)")
    ax.legend(fontsize=8, loc="upper left")
    sns.despine()
    st.pyplot(fig)
    plt.close()
    high_cgpa = scatter_df[scatter_df["CGPA"] >= 8.5]["Package_LPA"].mean()
    low_cgpa  = scatter_df[scatter_df["CGPA"] < 8.5]["Package_LPA"].mean()
    ratio     = round(high_cgpa / low_cgpa, 1) if low_cgpa > 0 else 0
    st.markdown(f'<div class="insight-box">💡 CGPA 8.5+ students ko average <b>{ratio}x zyada package</b> mila — CGPA maintain karna zaroori hai</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<p class="section-head">Top 8 Hiring Companies</p>', unsafe_allow_html=True)
    top_companies = (df[df["Placed"] == "Yes"]["Company"]
                     .value_counts().head(8).reset_index())
    top_companies.columns = ["Company", "Count"]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    sns.barplot(data=top_companies, x="Count", y="Company",
                palette="Blues_d", ax=ax)
    for p in ax.patches:
        ax.annotate(f"{int(p.get_width())}",
                    (p.get_width() + 0.1, p.get_y() + p.get_height() / 2),
                    va="center", fontsize=9)
    ax.set_xlabel("Students Hired"); ax.set_ylabel("")
    sns.despine()
    st.pyplot(fig)
    plt.close()
    top1 = top_companies.iloc[0]["Company"]
    top1_count = top_companies.iloc[0]["Count"]
    st.markdown(f'<div class="insight-box">💡 <b>{top1}</b> sabse badi recruiter hai — <b>{top1_count} students</b> hire kiye 2020-2024 mein</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Row 3: Internship Impact + Salary Distribution ───────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown('<p class="section-head">Internship ka Placement pe Impact</p>', unsafe_allow_html=True)
    intern_data = df.groupby("Internship")["Placed_Flag"].mean().mul(100).round(1).reset_index()
    intern_data.columns = ["Internship", "Placement %"]
    intern_data["Internship"] = intern_data["Internship"].map({"Yes": "Internship Kiya", "No": "Internship Nahi"})
    fig, ax = plt.subplots(figsize=(5, 3.5))
    colors2 = ["#4361ee", "#adb5bd"]
    sns.barplot(data=intern_data, x="Internship", y="Placement %",
                palette=colors2, ax=ax)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylim(0, 110)
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.0f}%",
                    (p.get_x() + p.get_width() / 2, p.get_height() + 1),
                    ha="center", fontsize=10, fontweight="bold")
    ax.set_xlabel(""); ax.set_ylabel("Placement %")
    sns.despine()
    st.pyplot(fig)
    plt.close()
    with_intern    = df[df["Internship"] == "Yes"]["Placed_Flag"].mean() * 100
    without_intern = df[df["Internship"] == "No"]["Placed_Flag"].mean() * 100
    diff = round(with_intern - without_intern, 1)
    st.markdown(f'<div class="insight-box">💡 Internship karne wale students ki placement rate <b>{diff}% zyada</b> hai — internship experience bahut important hai</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<p class="section-head">Salary Package Distribution</p>', unsafe_allow_html=True)
    pkg_df = fdf[fdf["Package_LPA"] > 0]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    sns.histplot(pkg_df["Package_LPA"], bins=10, color="#4361ee", alpha=0.8, ax=ax, kde=True)
    ax.set_xlabel("Package (LPA)"); ax.set_ylabel("Students")
    ax.axvline(pkg_df["Package_LPA"].mean(), color="red", linestyle="--",
               linewidth=1.5, label=f"Mean: {pkg_df['Package_LPA'].mean():.1f} LPA")
    ax.legend(fontsize=9)
    sns.despine()
    st.pyplot(fig)
    plt.close()
    median_pkg = round(pkg_df["Package_LPA"].median(), 1)
    st.markdown(f'<div class="insight-box">💡 Median package <b>{median_pkg} LPA</b> hai — zyada tar students 5-8 LPA range mein placed hue</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Raw Data Table ────────────────────────────────────────────────────────────
with st.expander("Raw Data Table Dekho"):
    display_cols = ["Roll_No", "Name", "Branch", "Year", "CGPA", "Placed", "Company", "Package_LPA", "Internship"]
    st.dataframe(fdf[display_cols].reset_index(drop=True), use_container_width=True)

# ── Recommendations ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-head">Data-based Recommendations</p>', unsafe_allow_html=True)
r1, r2, r3 = st.columns(3)
with r1:
    st.info("**Internship Mandatory Karo**\n\nData dikhata hai ki internship karne wale students ki placement rate significantly zyada hai.")
with r2:
    st.info("**CGPA 7.5+ Target Set Karo**\n\nCGPA 7.5 se neeche students ko extra coaching aur mock interview sessions provide karo.")
with r3:
    st.info("**Core Branch Companies Bulao**\n\nMechanical aur Civil students ke liye dedicated core company drives organize karo.")

st.markdown("---")
st.caption("Project by: BTech CSE Final Year | Data: College Placement Records 2020-2024")
