import streamlit as st
import os
import json
import requests

# Page setup
st.set_page_config(page_title="AI Research Assistant", page_icon="🤖", layout="wide")

# ----------------- Utility Functions -----------------
SAVE_DIR = "saved_reports"
os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_papers(query, limit=10):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,url,abstract,year"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        st.error("❌ Failed to fetch results from Semantic Scholar API.")
        return []

def save_report(name, content):
    filepath = os.path.join(SAVE_DIR, f"{name}.json")
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump({"name": name, "content": content}, f)

def load_reports():
    reports = []
    for file in os.listdir(SAVE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(SAVE_DIR, file), "r", encoding='utf-8') as f:
                reports.append(json.load(f))
    return reports

def delete_report(name):
    filepath = os.path.join(SAVE_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Research", "Saved Reports"])

# ---------------- HOME PAGE ----------------
if page == "Home":
    st.title("🤖 Welcome to AI Research Assistant")
    st.subheader("Your personal assistant for business professionals!")

    st.write("""
    🚀 This app helps you:
    - Explore AI research papers quickly  
    - Summarize insights in seconds  
    - Stay ahead in your hackathon projects  
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🔍 Powerful Search")
    with col2:
        st.success("📑 Auto Summaries")
    with col3:
        st.warning("⚡ Research Ready")

    st.markdown("---")
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", 
             caption="Built with Streamlit")

# ---------------- RESEARCH PAGE ----------------
elif page == "Research":
    st.title("🔎 Research Section")
    st.write("Search for topics, papers, or ideas below:")

    query = st.text_input("Enter your research topic:", placeholder="e.g. LLM Agents, Quantum Computing")

    if query:
        st.write(f"🔍 You searched for: **{query}**")

        suggestions = [
            f"{query} in healthcare",
            f"Latest papers on {query}",
            f"Applications of {query} in robotics"
        ]
        st.write("✨ Suggested queries:")
        for s in suggestions:
            if st.button(s):
                query = s  # update query

        st.markdown("### 📑 Top Research Results")
        papers = fetch_papers(query)

        if papers:
            for idx, paper in enumerate(papers, 1):
                title = paper.get('title', 'Untitled')
                url = paper.get('url', '#')
                year = paper.get('year', 'Unknown')
                authors = ", ".join(a.get("name", "Unknown") for a in paper.get("authors", []))
                abstract = paper.get("abstract", None)

                st.markdown(f"**{idx}. [{title}]({url})** ({year})")
                st.markdown(f"_Authors_: {authors}")
                if abstract:
                    st.markdown(f"_Abstract_: {abstract[:300]}{'...' if len(abstract) > 300 else ''}")
                else:
                    st.markdown("_Abstract_: Not available.")
                st.write("---")
        else:
            st.info("No results found.")

        # Save report
        save_name = st.text_input("💾 Save this research as:", value=query.replace(" ", "_"))
        if st.button("Save Report"):
            content = f"### Report on {query}\n\n"
            for paper in papers:
                title = paper.get('title', 'Untitled')
                url = paper.get('url', '#')
                year = paper.get('year', 'Unknown')
                authors = ", ".join(a.get("name", "Unknown") for a in paper.get("authors", []))
                abstract = paper.get("abstract", "Abstract not available.")

                content += f"**{title}** ({year})\n\n"
                content += f"_Authors_: {authors}\n\n"
                content += f"{abstract}\n\n"
                content += f"[Read more]({url})\n\n---\n\n"

            save_report(save_name, content)
            st.success(f"✅ Report '{save_name}' saved!")

# ---------------- SAVED REPORTS PAGE ----------------
elif page == "Saved Reports":
    st.title("📂 Saved Reports")

    reports = load_reports()
    if reports:
        search_term = st.text_input("🔎 Search reports")
        filtered = [r for r in reports if search_term.lower() in r["name"].lower()]

        if not filtered:
            st.warning("No matching reports found.")
        else:
            for report in filtered:
                with st.expander(f"📑 {report['name']}"):
                    st.markdown(report["content"])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.download_button("⬇️ Download", report["content"], file_name=f"{report['name']}.txt"):
                            st.success("Downloaded successfully!")
                    with col2:
                        if st.button(f"🗑 Delete '{report['name']}'", key=report["name"]):
                            delete_report(report["name"])
                            st.warning(f"Deleted report '{report['name']}'")
                            st.rerun()
    else:
        st.info("No reports saved yet. Go to Research and save one!")
