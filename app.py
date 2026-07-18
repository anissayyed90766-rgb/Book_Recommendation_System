import os
import pickle
import pandas as pd
import streamlit as st
import gdown

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="📚 Book Recommendation System",
    page_icon="📚",
    layout="wide",
)

# ==========================================================
# GOOGLE DRIVE MODEL
# ==========================================================

FILE_ID = "1Cm50Z9m6pE-SC7869TvMdcdOBgNkO5Wk"
SIMILARITY_FILE = "similarity.pkl"


def download_similarity():
    if os.path.exists(SIMILARITY_FILE):
        return

    with st.spinner("Downloading recommendation model..."):
        url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

        try:
            gdown.download(url, SIMILARITY_FILE, quiet=False)
        except Exception as e:
            st.error("Failed to download similarity.pkl")
            st.exception(e)
            st.stop()


download_similarity()

# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

.main{
    background:#0f172a;
}

.block-container{
    padding-top:2rem;
}

h1,h2,h3{
    color:white;
}

.card{
    background:#1e293b;
    padding:15px;
    border-radius:15px;
    border:1px solid #334155;
    text-align:center;
    margin-bottom:20px;
    transition:0.3s;
}

.card:hover{
    transform:scale(1.03);
    border-color:#00E5FF;
}

.metric-card{
    background:#1e293b;
    padding:20px;
    border-radius:15px;
    text-align:center;
}

.stButton>button{
    width:100%;
    border-radius:10px;
    background:#00E5FF;
    color:black;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# LOAD MODEL
# ==========================================================

@st.cache_resource
def load_model():

    with open("books.pkl", "rb") as f:
        books = pickle.load(f)

    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)

    return books, similarity


books, similarity = load_model()

# ==========================================================
# RECOMMENDATION
# ==========================================================

def recommend(book_name):

    match = books[
        books["Title"].str.lower() == book_name.lower()
    ]

    if match.empty:
        return pd.DataFrame()

    index = match.index[0]

    distances = list(enumerate(similarity[index]))

    distances = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True
    )[1:11]

    recommended = books.iloc[
        [i[0] for i in distances]
    ]

    return recommended.reset_index(drop=True)

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<h1 style='text-align:center;color:#00E5FF;font-size:55px;'>
📚 Book Recommendation System
</h1>

<p style='text-align:center;font-size:22px;color:white;'>
Discover your next favourite book with AI-powered recommendations
</p>
""", unsafe_allow_html=True)

st.divider()

# ==========================================================
# METRICS
# ==========================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("📚 Total Books", len(books))
c2.metric("✍ Authors", books["Author"].nunique())
c3.metric("📖 Genres", books["Genre"].nunique())
c4.metric("🌍 Languages", books["Language"].nunique())

st.divider()

# ==========================================================
# SEARCH
# ==========================================================

# ==========================================================
# SEARCH WITH AUTOCOMPLETE
# ==========================================================

st.subheader("🔍 Search Your Favourite Book")

book_titles = sorted(books["Title"].dropna().unique())

selected_book = st.selectbox(
    "Search Book",
    options=book_titles,
    index=None,
    placeholder="Type a book title..."
)

if selected_book:

    book = books[books["Title"] == selected_book].iloc[0]

    left, right = st.columns([1,2])

    with left:
        st.image(
            "https://placehold.co/300x450/png?text=Book+Cover",
            use_container_width=True
        )

    with right:

        st.markdown(f"## 📖 {book['Title']}")
        st.write(f"**👤 Author:** {book['Author']}")
        st.write(f"**📚 Genre:** {book['Genre']}")
        st.write(f"**🌍 Language:** {book['Language']}")
        st.write(f"**⭐ Rating:** {book['Rating']}")
        st.write(f"**💰 Price:** ₹{book['Price']}")

        st.markdown("### Description")
        st.write(book["Description"])

    if st.button("✨ Recommend Similar Books"):

        recommendations = recommend(selected_book)

        st.divider()
        st.subheader("❤️ Recommended Books")

        cols = st.columns(5)

        for i, (_, row) in enumerate(recommendations.iterrows()):

            with cols[i % 5]:

                st.markdown("<div class='card'>", unsafe_allow_html=True)

                st.image(
                    "https://placehold.co/250x350/png?text=Book",
                    use_container_width=True
                )

                st.markdown(f"### {row['Title']}")
                st.caption(row["Author"])
                st.write(f"⭐ {row['Rating']}")
                st.write(f"📚 {row['Genre']}")
                st.write(f"🌍 {row['Language']}")

                st.markdown("</div>", unsafe_allow_html=True)