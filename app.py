import streamlit as st
import pandas as pd
import openai
import io

# --- Initialize session state ---
if 'summaries_df' not in st.session_state:
    st.session_state.summaries_df = None

# --- Helper Function to convert DataFrame to Excel in memory ---
def to_excel(df):
    """
    Converts a pandas DataFrame to an Excel file in memory (bytes).
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Summaries')
    processed_data = output.getvalue()
    return processed_data

# --- Master Prompt 1: For Score-Based Summaries ---
def create_summary_prompt(person_name, person_data):
    """
    Creates the prompt for generating the main executive summary from scores.
    """
    return f"""
You are a senior talent assessment consultant specializing in writing executive summaries for leadership assessment centers. Your writing style adheres strictly to British English and maintains a professional, constructive, and positive tone. Your primary skill is to weave competency scores into a fluid, professional narrative.

## Core Objective
Your task is to synthesize the provided competency scores for {person_name} into a formal, narrative-based executive summary.

## Input Data for {person_name}
{person_data}

## Primary Directives & Rules

1.  **Writing Style: Describe, Don't Label.**
    * **CRITICAL RULE:** Do not simply name the competency. Instead, describe the behaviors that were observed, using the competency name as your guide. The summary must be a story of the person's actions.
    * **Incorrect (Labeling):** "{person_name} demonstrated Strategic Thinking."
    * **Correct (Describing):** "{person_name} consistently displayed the ability to anticipate future challenges and proactively aligned his actions with the organisation’s long-term goals and vision."

2.  **Structure Based on Profile Type:**
    * **High-Scorer Profile (No scores of 1 or 2):** Write a single, flowing narrative paragraph. Start with a general opening like "{person_name} displayed strengths in multiple competencies assessed." Then, seamlessly describe the observed strengths for all competencies.
    * **Mixed-Score Profile (Contains scores of 1 or 2):** Use an integrated narrative structure. Begin with the main strengths, then transition smoothly to growth opportunities using phrases like "...however, he may need to..." or "To further develop his competence...". The goal is a single, cohesive story, not two separate lists.

3.  **Tense and Perspective:**
    * Use **past tense** for all observed behaviors (e.g., "He demonstrated...", "She showcased...").
    * Use **present or future tense** for all development suggestions ("He could enhance...", "She would benefit from...").
    * Use the candidate's first name, "{person_name}", only at the beginning. Use pronouns (He/She) thereafter.

4.  **Actionable Development (For Mixed Profiles Only):**
    * For each growth opportunity (scores 1, 2), you MUST provide a **specific, actionable, and context-relevant suggestion**. Avoid generic advice.
    * **Incorrect (Generic):** "He could benefit from a course on decision-making."
    * **Correct (Specific):** "He may strengthen his decision-making skills by conducting in-depth analysis, comprehensive risk assessments and offering broader alternatives while gaining buy-in beforehand, to minimise resistance."

5.  **General Rules:**
    * **Word Count:** The entire summary must not exceed 280 words.
    * **Coverage:** All 8 competencies must be addressed, either as a described strength or a growth opportunity.
    * **Language:** British English. Professional synonyms for "good/bad". Correct punctuation.
    * **ABSOLUTE RULE:** Never mention the numerical scores in the final text.

## Final Instruction for {person_name}
Now, process the provided competency scores for {person_name}. First, determine if it is a High-Scorer or Mixed-Score profile. Then, write a concise executive summary under 280 words, adhering to all the rules above. Focus on describing behaviors, not labeling competencies. Use the correct narrative structure for the profile type and NEVER mention the scores.
"""

# --- Master Prompt 2: For Rewriting Comments ---
def create_comment_rewriting_prompt(person_name, raw_comments, score_summary):
    """
    Creates the prompt for cleaning and rewriting raw comments.
    """
    return f"""
You are an expert HR communications specialist, skilled in reframing raw feedback into professional, constructive, and developmental recommendations. Your writing style is concise and adheres to British English.

## Core Objective
Your task is to analyze a set of raw, unstructured comments about {person_name}. You will filter, synthesize, and rewrite them into a single, professional paragraph that can be appended to an existing executive summary.

## Existing Executive Summary (For Context & Contradiction Check)
"{score_summary}"

## Raw Comments for {person_name}
{raw_comments}

## Primary Directives & Rules

1.  **Filter Aggressively:** Your first step is to filter the raw comments.
    * **IGNORE** any comments that are purely positive ("He is great"), offensive, unprofessional, or not relevant to professional development.
    * **FOCUS ONLY** on comments that suggest a developmental need.

2.  **Synthesize and Theme:**
    * If multiple comments point to the same developmental area (e.g., "not strategic," "no long-term view"), group them into a single, cohesive theme about strategic thinking.
    * If comments point to separate themes, address them separately but concisely.

3.  **Rewrite with Professionalism:**
    * Rephrase any blunt or judgmental feedback into constructive, forward-looking advice.
    * **Incorrect (Judgmental):** "He is direct and rude in meetings."
    * **Correct (Constructive):** "He may benefit from adapting his communication style to better suit different audiences and situations."

4.  **Contradiction Check:**
    * **CRITICAL RULE:** The rewritten comments MUST NOT contradict the existing executive summary provided for context.
    * If a raw comment suggests a weakness in an area that the summary identified as a clear strength, you must **IGNORE** that raw comment. The score-based summary is the primary source of truth.

5.  **Handling No Developmental Feedback:**
    * If, after filtering, there are no valid developmental comments left, your entire output MUST be this exact sentence: "The panel did not provide any specific developmental feedback."

6.  **Language and Output Format:**
    * **Word Count:** The final rewritten paragraph must not exceed 50 words.
    * **Perspective:** Address the candidate directly in the 2nd person ("You could...", "You may benefit from...").
    * **Bilingual Output:** First, write the final paragraph in English. Then, use a clear separator '---ARABIC---' and provide a high-quality, native-level Arabic translation that follows all professional HR conventions.

## Final Instruction for {person_name}
Analyze the raw comments provided. Filter, synthesize, and rewrite them into a single, professional, and constructive paragraph of no more than 50 words. Ensure the output does not contradict the existing summary. Provide the output in both English and Arabic, separated by '---ARABIC---'. If no developmental comments exist, output the standard "no feedback" sentence.
"""

# --- API Call Function for Azure OpenAI ---
def generate_from_azure(prompt, api_key, endpoint, deployment_name):
    """
    A single function to call the Azure OpenAI API for both tasks.
    """
    try:
        client = openai.AzureOpenAI(api_key=api_key, azure_endpoint=endpoint, api_version="2024-02-01")
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a senior talent assessment consultant and HR communications specialist following British English standards."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2, max_tokens=800, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0
        )
        content = response.choices[0].message.content.strip()
        
        # Handle bilingual output for the comment rewriting task
        if '---ARABIC---' in content:
            english_part, arabic_part = content.split('---ARABIC---', 1)
            return english_part.strip(), arabic_part.strip()
        else:
            # For the summary task, the whole content is the English summary
            return content, None

    except Exception as e:
        st.error(f"An error occurred while contacting Azure OpenAI: {e}")
        return None, None

# --- Streamlit App Main UI ---
st.set_page_config(page_title="DGE Full Report Generator", layout="wide")
st.title("📄 DGE Full Report Generator")

# --- STEP 1: Score-Based Summary Generation ---
st.header("Step 1: Generate Executive Summaries from Scores")

with st.expander("Instructions & Sample File", expanded=True):
    st.markdown("""
    Upload an Excel file containing competency scores. The application will generate a professional executive summary for each person.
    """)
    # --- Create and provide a sample file for download ---
    sample_scores_data = {
        'email': ['jane.doe@example.com', 'john.roe@example.com'], 'first_name': ['Jane', 'John'], 'last_name': ['Doe', 'Roe'], 'level': ['Director', 'Manager'],
        'Strategic Thinker': [4, 2], 'Impactful Decision Maker': [5, 5], 'Effective Collaborator': [2, 3], 'Talent Nurturer': [4, 2],
        'Results Driver': [3, 4], 'Customer Advocate': [2, 4], 'Transformation Enabler': [3, 1], 'Innovation Catalyst': [1, 3]
    }
    sample_scores_df = pd.DataFrame(sample_scores_data)
    sample_scores_excel = to_excel(sample_scores_df)
    st.download_button(label="📥 Download Scores Template", data=sample_scores_excel, file_name="dge_scores_template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

scores_file = st.file_uploader("Upload your Scores Excel file here", type="xlsx", key="scores_uploader")

if scores_file is not None:
    if st.button("Generate Summaries from Scores", key="generate_summaries"):
        df_scores = pd.read_excel(scores_file)
        
        try:
            azure_api_key = st.secrets["azure_openai"]["api_key"]
            azure_endpoint = st.secrets["azure_openai"]["endpoint"]
            azure_deployment_name = st.secrets["azure_openai"]["deployment_name"]
        except (KeyError, FileNotFoundError):
            st.error("Azure OpenAI credentials not found. Please configure them in your Streamlit secrets.")
            st.stop()

        identifier_cols = ['email', 'first_name', 'last_name', 'level']
        competency_columns = [col for col in df_scores.columns if col not in identifier_cols]
        
        summaries_data = []
        progress_bar = st.progress(0)

        for i, row in df_scores.iterrows():
            first_name = row['first_name']
            person_data_str = "\n".join([f"- {comp}: {row[comp]}" for comp in competency_columns if comp in row and pd.notna(row[comp])])
            prompt = create_summary_prompt(first_name, person_data_str)
            summary_en, _ = generate_from_azure(prompt, azure_api_key, azure_endpoint, azure_deployment_name)
            
            if summary_en:
                summaries_data.append({'email': row['email'], 'Executive Summary': summary_en})
            else:
                summaries_data.append({'email': row['email'], 'Executive Summary': "Error generating summary."})
            
            progress_bar.progress((i + 1) / len(df_scores))
        
        # Merge summaries back into the original dataframe
        df_summaries = pd.DataFrame(summaries_data)
        output_df = pd.merge(df_scores, df_summaries, on='email')
        
        # Store results in session state for the next step
        st.session_state.summaries_df = output_df
        st.success("Step 1 Complete: Executive summaries have been generated successfully!")

# --- Display Summaries and Show Step 2 ---
if st.session_state.summaries_df is not None:
    st.subheader("Generated Summaries (Step 1 Output)")
    st.dataframe(st.session_state.summaries_df)
    st.divider()

    # --- STEP 2: Comment Rewriting and Appending ---
    st.header("Step 2: Rewrite and Append Panel Comments")
    
    with st.expander("Instructions & Sample File", expanded=True):
        st.markdown("""
        Now, upload the Excel file containing raw panel comments. The application will rewrite them professionally and append them to the summaries generated above. The file must contain an 'email' and a 'Panel Recommendation - English' column.
        """)
        sample_comments_data = {
            'email': ['jane.doe@example.com', 'jane.doe@example.com', 'john.roe@example.com'],
            'Panel Recommendation - English': ['She needs to be less direct.', 'Sometimes ignores feedback.', 'Amazing person, no feedback needed.']
        }
        sample_comments_df = pd.DataFrame(sample_comments_data)
        sample_comments_excel = to_excel(sample_comments_df)
        st.download_button(label="📥 Download Comments Template", data=sample_comments_excel, file_name="dge_comments_template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    comments_file = st.file_uploader("Upload your Comments Excel file here", type="xlsx", key="comments_uploader")

    if comments_file is not None:
        if st.button("Rewrite and Append Comments", key="rewrite_comments"):
            df_comments = pd.read_excel(comments_file)
            
            try:
                azure_api_key = st.secrets["azure_openai"]["api_key"]
                azure_endpoint = st.secrets["azure_openai"]["endpoint"]
                azure_deployment_name = st.secrets["azure_openai"]["deployment_name"]
            except (KeyError, FileNotFoundError):
                st.error("Azure OpenAI credentials not found.")
                st.stop()
            
            # Group comments by email
            comments_grouped = df_comments.groupby('email')['Panel Recommendation - English'].apply(lambda x: '\n- '.join(x.astype(str))).reset_index()
            
            final_results_df = st.session_state.summaries_df.copy()
            rewritten_en_list = []
            rewritten_ar_list = []

            progress_bar_2 = st.progress(0)
            
            for i, row in final_results_df.iterrows():
                email = row['email']
                first_name = row['first_name']
                score_summary = row['Executive Summary']
                
                # Find the comments for the current person
                person_comments_series = comments_grouped[comments_grouped['email'] == email]
                raw_comments = "- " + person_comments_series['Panel Recommendation - English'].iloc[0] if not person_comments_series.empty else "No comments provided."

                prompt = create_comment_rewriting_prompt(first_name, raw_comments, score_summary)
                comment_en, comment_ar = generate_from_azure(prompt, azure_api_key, azure_endpoint, azure_deployment_name)

                if comment_en and comment_ar:
                    rewritten_en_list.append(comment_en)
                    rewritten_ar_list.append(comment_ar)
                else:
                    rewritten_en_list.append("Error processing comments.")
                    rewritten_ar_list.append("Error processing comments.")
                
                progress_bar_2.progress((i + 1) / len(final_results_df))

            # Append the rewritten comments as new columns
            final_results_df['Rewritten Comment (EN)'] = rewritten_en_list
            final_results_df['Rewritten Comment (AR)'] = rewritten_ar_list
            
            st.balloons()
            st.subheader("Final Report with Appended Comments")
            st.dataframe(final_results_df)

            # Provide download for the final combined data
            final_excel_data = to_excel(final_results_df)
            st.download_button(label="📥 Download Final Report", data=final_excel_data, file_name="DGE_Final_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

