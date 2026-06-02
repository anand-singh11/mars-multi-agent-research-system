# app.py

import os
import time

import streamlit as st
from dotenv import load_dotenv

from mars import app

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🧠",
    layout="wide"
)

# --- Check for API Keys ---
def check_api_keys():
    """Check if required API keys are present."""
    groq_key = os.environ.get("GROQ_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")

    if not groq_key or not tavily_key:
        st.error("API keys not found! Please set GROQ_API_KEY and TAVILY_API_KEY in your .env file.")
        return False

    st.success("API keys loaded successfully.")
    return True

# --- Header ---
st.title("Multi-Agent Research Assistant")
st.markdown("""
Welcome to your intelligent research assistant!
Enter a research topic, and a team of AI agents will collaborate to produce a comprehensive report.

**Agent Team:**
- **Supervisor**: Manages the workflow and coordinates tasks
- **Researcher**: Gathers information using web search
- **Writer**: Creates and revises the research report
- **Critiquer**: Reviews drafts and provides feedback
""")

st.divider()


# --- Check API Keys ---
if not check_api_keys():
    st.stop()

# --- Main Application ---
st.header("Start Your Research")

# User input
topic = st.text_input(
    "Enter your research topic:",
    placeholder="e.g., Impact of quantum computing on cybersecurity",
    key="topic_input"
)

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    max_iterations = st.slider(
        "Max Workflow Iterations",
        min_value=5,
        max_value=25,
        value=15,
        help="Maximum number of agent interactions"
    )

    st.divider()
    st.subheader("How it works")
    st.markdown("""
    1. **Supervisor** analyzes the task
    2. **Researcher** gathers information
    3. **Writer** creates a draft
    4. **Critiquer** reviews quality
    5. Loop continues until approved
    """)

# Start button
if st.button("Start Research", type="primary", use_container_width=True):
    if not topic:
        st.error("Please enter a research topic.")
    else:
        # Define the initial state
        initial_state = {
            "main_task": topic,
            "research_findings": [],
            "draft": "",
            "critique_notes": "",
            "revision_number": 0,
            "next_step": "",
            "current_sub_task": ""
        }

        # Configuration
        config = {"recursion_limit": max_iterations}

        st.info("Agents are starting their work...")

        # Create containers for live updates
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        progress_container = st.container()

        # ---------------------------------------------------------------
        # IMPORTANT: LangGraph .stream() yields only per-node DELTAS,
        # not the full accumulated state. We manually merge each delta
        # into full_state so fields written by earlier nodes (e.g. `draft`
        # from writer) remain accessible after later nodes (e.g. supervisor)
        # overwrite unrelated keys.
        # ---------------------------------------------------------------
        full_state = dict(initial_state)
        full_state["research_findings"] = []  # will be extended, not replaced

        step_count = 0

        try:
            with progress_container:
                st.subheader("Agent Activity Log")

                for step in app.stream(initial_state, config=config):
                    step_count += 1
                    progress_bar.progress(min(step_count / max_iterations, 1.0))

                    # Each step is {node_name: node_output_delta}
                    node_name = list(step.keys())[0]
                    node_output = step[node_name]

                    # Merge delta into running full_state
                    for key, value in node_output.items():
                        if key == "research_findings" and isinstance(value, list):
                            # Uses operator.add annotation — extend, don't replace
                            full_state["research_findings"].extend(value)
                        else:
                            full_state[key] = value

                    # Display node output
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### Agent: `{node_name.upper()}`")
                        with col2:
                            st.caption(f"Step {step_count}")

                        if node_name == "supervisor":
                            next_step = node_output.get("next_step", "N/A")
                            task = node_output.get("current_sub_task", "N/A")
                            st.markdown(f"**Decision:** {next_step}")
                            st.markdown(f"**Task:** {task}")

                        elif node_name == "researcher":
                            findings = node_output.get("research_findings", [])
                            if findings:
                                latest = findings[-1]
                                st.success("Research completed")
                                preview_length = 300
                                if len(latest) > preview_length:
                                    st.markdown("**Research Preview:**")
                                    st.info(latest[:preview_length] + "...")
                                    with st.expander(f"Show Full Research (Step {step_count})"):
                                        st.markdown(latest)
                                else:
                                    st.info(latest)

                        elif node_name == "writer":
                            draft = node_output.get("draft", "")
                            revision = node_output.get("revision_number", 0)
                            st.success(f"Draft {revision} generated ({len(draft)} chars)")
                            preview_length = 400
                            if len(draft) > preview_length:
                                st.markdown("**Draft Preview:**")
                                st.info(draft[:preview_length] + "...")
                                with st.expander(f"Show Full Draft (Step {step_count})"):
                                    st.markdown(draft)
                            else:
                                st.info(draft)

                        elif node_name == "critiquer":
                            critique = node_output.get("critique_notes", "")
                            if "APPROVED" in critique.upper():
                                st.success("Draft APPROVED!")
                            else:
                                st.warning("Revisions requested")
                            preview_length = 300
                            if len(critique) > preview_length:
                                st.markdown("**Critique Preview:**")
                                st.info(critique[:preview_length] + "...")
                                with st.expander(f"Show Full Critique (Step {step_count})"):
                                    st.markdown(critique)
                            else:
                                st.info(critique)

                        st.divider()

                    time.sleep(0.3)

            status_placeholder.success("Research Complete!")
            progress_bar.progress(1.0)

            print(f"Workflow done. Steps: {step_count}, Draft: {len(full_state.get('draft',''))} chars, Findings: {len(full_state.get('research_findings',[]))}")

        except Exception as e:
            status_placeholder.error("Error occurred")
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

        # --- Display Final Report ---
        st.divider()

        final_draft = full_state.get("draft", "").strip()

        if final_draft and len(final_draft) > 50:
            st.header("Final Research Report")

            with st.container():
                st.markdown(final_draft)

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Report Statistics")
                st.metric("Revisions", full_state.get("revision_number", 0))
                st.metric("Research Sources", len(full_state.get("research_findings", [])))
                st.metric("Word Count", len(final_draft.split()))
                st.metric("Character Count", len(final_draft))

            with col2:
                st.subheader("Research Findings")
                research = full_state.get("research_findings", [])
                if research:
                    with st.expander("View all research data", expanded=False):
                        for idx, finding in enumerate(research, 1):
                            st.markdown(f"**Finding {idx}:**")
                            st.write(finding)
                            if idx < len(research):
                                st.divider()
                else:
                    st.info("No research findings available")

            st.download_button(
                label="Download Report",
                data=final_draft,
                file_name=f"research_report_{topic.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.error("No report was generated. Please try again.")
            with st.expander("Debug: View Final State"):
                st.json({k: (v if not isinstance(v, list) else f"[{len(v)} items]") for k, v in full_state.items()})

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "<p>Powered by LangChain, LangGraph, Groq (Llama 3.3 70B) & Tavily</p>"
    "</div>",
    unsafe_allow_html=True
)
