import streamlit as st
import pandas as pd
import io

# --- Helper Functions ---

def get_sample_scores_df():
    """Creates a sample DataFrame for the scores file."""
    data = {
        'Person': ['Indicator Text', 'EO1'],
        'Adaptability': ['Adaptability', 4],
        'Adaptability 1': ["Effectively navigates and leads teams through changes...", 4],
        'Adaptability 2': ["Quickly learns from experiences and applies insights...", 4],
        'Adaptability 3': ["Welcomes diverse perspectives and ideas...", 4],
        'Adaptability 4': ["Displays personal resilience, remains calm...", 4],
        'Capability Development': ['Capability Development', 3],
        'Capability Development 1': ["Identifies current skills and competencies within the team...", 2.5],
        'Capability Development 2': ["Engages in coaching to develop team members' skills...", 3.5],
        'Capability Development 3': ["Delegates responsibilities effectively...", 3],
        'Capability Development 4': ["Proactively identifies and nurtures high-potential team members...", 3],
        'Decision Making and Takes Accountability': ['Decision Making and Takes Accountability', 4.8],
        'Decision Making and Takes Accountability 1': ["Show the ability to act assertively and take independent...", 4.5],
        'Decision Making and Takes Accountability 2': ["Displays confidence and credibility in decision-making...", 5],
        'Decision Making and Takes Accountability 3': ["Identifies potential risks associated with tactical decisions...", 4.5],
        'Decision Making and Takes Accountability 4': ["Utilizes critical thinking to assess options...", 5],
        'Effective Communication and Influence': ['Effective Communication and Influence', 3.5],
        'Effective Communication and Influence 1': ["Clearly articulates ideas and information...", 4],
        'Effective Communication and Influence 2': ["Seeks common ground and influences others...", 4],
        'Effective Communication and Influence 3': ["Demonstrates strong listening skills...", 2.5],
        'Effective Communication and Influence 4': ["Adjusts communication style and approach...", 3.5],
        'Initiative': ['Initiative', 3.8],
        'Initiative 1': ["Takes the initiative to identify and pursue opportunities...", 4],
        'Initiative 2': ["Sets ambitious objectives and consistently seeks ways to exceed...", 4],
        'Initiative 3': ["Displays grit in the achievement of challenging goals...", 3.5],
        'Initiative 4': ["Consistently takes action beyond immediate responsibilities...", 3.5],
        'Inspirational Leadership': ['Inspirational Leadership', 3.4],
        'Inspirational Leadership 1': ["Develops a sense of common vision and purpose...", 4],
        'Inspirational Leadership 2': ["Collaborates and works with others effectively...", 3.5],
        'Inspirational Leadership 3': ["Demonstrates awareness of one’s own emotions...", 3],
        'Inspirational Leadership 4': ["Recognizes the individual styles of each team member...", 3],
        'Strategic Thinking': ['Strategic Thinking', 4],
        'Strategic Thinking 1': ["Monitors and predicts key trends in the industry...", 4],
        'Strategic Thinking 2': ["Identifies and assesses potential disruptors...", 4],
        'Strategic Thinking 3': ["Proactively identifies new opportunities...", 4],
        'Strategic Thinking 4': ["Translates complex strategic organizational goals...", 4],
        'Systematic Analysis and Planning': ['Systematic Analysis and Planning', 2.8],
        'Systematic Analysis and Planning 1': ["Delivers high-quality results consistently...", 3],
        'Systematic Analysis and Planning 2': ["Creates detailed action plans that outline the steps...", 3],
        'Systematic Analysis and Planning 3': ["Effectively allocates resources (time, personnel, budget)...", 2.5],
        'Systematic Analysis and Planning 4': ["Establishes metrics and benchmarks to evaluate progress...", 2.5]
    }
    return pd.DataFrame(data)

def get_sample_comments_df():
    """Creates a sample DataFrame for the comments file."""
    data = {
        'Person Code': ['EO1', 'EO1', 'E32', 'E32'],
        'Comments': [
            'He needs to be more vocal in leadership meetings.',
            'His project planning documents are very detailed and helpful, but he sometimes misses the bigger picture on resource allocation.',
            'A bit quiet, but very reliable once a task is assigned.',
            'Would like to see him present his ideas with more confidence to senior stakeholders.'
        ]
    }
    return pd.DataFrame(data)


def df_to_excel_bytes(df):
    """Converts a DataFrame to an in-memory Excel file (bytes)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output.getvalue()


def get_score_summary_prompt():
    """Returns the prompt for generating the main summary from scores."""
    return """
**## Persona**
You are an expert talent management analyst and a master writer. Your style is formal, professional, objective, and constructive. You synthesize quantitative performance data into a rich, qualitative, behavioral-focused narrative. You are writing for a male individual, using the third person (`he`/`his`/`him`).

**## Core Objective**
Generate a sophisticated, multi-paragraph performance summary based on scores from 8 leadership competencies. The summary will have 2 or 3 paragraphs based on the logic below. The summary must be generated in both English and Arabic.

**## Input Data Profile**
You will receive a data set for one individual containing: 8 Competency Names and their average scores, plus 4 Indicator Scores and Texts for each competency.

**## Core Logic & Execution Flow**

**Step 1: Data Analysis & Categorization**
1.  Categorize each of the 8 competencies based on its average score:
    * **Clear Strength:** Average score >= 4.0
    * **Potential Strength:** Average score between 2.6 and 3.9
    * **Development Area:** Average score <= 2.5
2.  Count the number of distinct categories present for the candidate (1, 2, or 3).

**Step 2: Dynamic Summary Construction**
1.  **Mandatory Opening:** The English summary MUST begin with this exact text: "Your participation in the assessment center provided insight into how you demonstrate the leadership competencies in action. The feedback below highlights observed strengths and opportunities for development to support your continued growth."
2.  **Paragraphing Rules:** Follow this logic to structure the report:

    * **IF 3 Categories are present (Strengths, Potential, and Development):**
        * **Paragraph 1 (Clear Strengths):** Start with "You display clear strengths in several areas of leadership." Detail all "Clear Strength" competencies. Synthesize multiple high-scoring indicators into a narrative and add a concluding phrase about the impact.
        * **Paragraph 2 (Potential Strengths):** Start with "In addition, there are areas where you demonstrate potential strengths that can be further leveraged." Detail all "Potential Strength" competencies. Describe the positives, then transition ("However, there is room to...") to explain the development gap.
        * **Paragraph 3 (Development Areas):** Start with "In relation to the development areas..." Detail all "Development Area" competencies. **This paragraph must be purely developmental.** Focus only on what needs improvement based on the lowest-scoring indicators. Do not mix in positive framing.

    * **IF 2 Categories are present:**
        * **Paragraph 1:** Address the more positive of the two categories (Strengths > Potential Strengths).
        * **Paragraph 2:** Address the remaining category. The language must be purely developmental if it is the "Development Area" category.

    * **IF only 1 Category is present (e.g., all are 'Clear Strengths'):**
        * **Paragraph 1:** Address the top half of the competencies (those with the highest average scores).
        * **Paragraph 2:** Address the bottom half of the competencies. Even if they are still positive, frame this paragraph as covering competencies that, while strong, are not as pronounced as those in the first paragraph.
        * The same logic applies if all are 'Potential Strengths' or all are 'Development Areas'. This ensures a minimum of two paragraphs.

**## Writing Standards & Constraints**
* **Word Count:** Maximum 400 words total per language (excluding the mandatory opening).
* **Source Fidelity:** Base all statements *strictly* on the indicator language.
* **Behavioral Focus:** No technical or industry-specific jargon.

**## Bilingual Generation Mandate**
* Generate in **both English and Arabic**, following the same dynamic structure and professional tone.
* **Arabic Opening:** The first sentence thanking the participant MUST be in formal, written Arabic (`Lughat al-Fusha`), for example: "نشكرك على مشاركتك في مركز التقييم، مما أتاح لنا رؤية متعمقة لكيفية تجسيدك للكفاءات القيادية عمليًا."

---
**## TASK: GENERATE SCORE-BASED SUMMARY FOR THE FOLLOWING PERSON**
"""

def get_comment_summary_prompt():
    """Returns the new, specialized prompt for summarizing qualitative comments."""
    return """
**## Persona**
You are a discerning talent management analyst, skilled at synthesizing raw, unstructured feedback into a concise and professional summary. Your focus is purely on constructive, developmental themes.

**## Core Objective**
Analyze a list of raw comments for an individual and generate a single, final summary paragraph. This paragraph should be no more than 50 words. The summary must be in both English and Arabic.

**## Input Data Profile**
1.  **The Main Report:** The already-written, score-based summary.
2.  **Raw Comments:** A list of verbatim comments from colleagues.

**## Core Logic & Execution Flow**
1.  **Filter Comments:** First, you MUST filter the raw comments based on these rules:
    * **IGNORE:** Offensive, irrelevant, purely personal, or overly judgmental comments.
    * **FOCUS ON:** Developmental aspects, constructive criticism, and actionable feedback.
2.  **Check for Contradictions:** **This is the most important rule.** Compare the themes in the filtered comments with the main report provided. If a comment's theme directly contradicts a "Clear Strength" identified in the main report, you MUST ignore that comment. The main report is the primary source of truth.
3.  **Synthesize Themes:** From the remaining, non-contradictory comments, identify 1-2 key developmental themes. If the comments are varied, select the most impactful points.
4.  **Draft the Summary:** Write a single paragraph that summarizes these themes.
    * **Introduction:** Start with a phrase like "Additionally, feedback suggests..." or "Further feedback indicates...".
    * **Body:** Concisely state the key themes. Rephrase any judgmental language into professional, developmental terms (e.g., "He is too quiet" becomes "he would benefit from increasing his visibility in senior forums.").
5.  **Final Polish:** Ensure the paragraph flows naturally when appended to the main report.

**## Writing Standards & Constraints**
* **Word Count:** Maximum 50 words per language.
* **Tone:** Professional, constructive, and forward-looking.
* **Consistency:** The summary MUST NOT contradict the main report.

**## Bilingual Generation Mandate: English and Arabic**
* **Primary Task:** Generate the summary in **both English and Arabic**, following all rules above.
* **Arabic Language Standards:**
    * **Nuance and Professionalism:** The Arabic translation must not be a literal, word-for-word translation. It must be crafted with the nuance, formality, and flow of a native Arabic-speaking HR professional.
    * **Tone:** The tone should be formal, respectful, and constructive, using professional terminology appropriate for a corporate setting.
    * **Contextual Integrity:** Ensure the meaning and intent of the developmental feedback are preserved and culturally aligned.

---
**## TASK: ANALYZE THE FOLLOWING COMMENTS AND GENERATE A 50-WORD SUMMARY PARAGRAPH TO APPEND TO THE MAIN REPORT PROVIDED.**
"""

def generate_summary_from_llm(prompt, is_comment_summary=False):
    """
    Placeholder function to simulate an LLM call.
    It returns a different hardcoded example based on the task.
    """
    if is_comment_summary:
        english_comment_summary = """Additionally, feedback suggests he could enhance his executive presence by projecting more confidence when presenting to senior stakeholders and increasing his visibility in key meetings. This will help ensure his valuable contributions are fully recognized."""
        arabic_comment_summary = """بالإضافة إلى ذلك، تشير الملاحظات إلى أنه يمكنه تعزيز حضوره التنفيذي من خلال إظهار المزيد من الثقة عند التقديم لكبار أصحاب المصلحة وزيادة حضوره في الاجتماعات الرئيسية. سيساعد ذلك في ضمان تقدير مساهماته القيمة بشكل كامل."""
        return english_comment_summary, arabic_comment_summary
    else:
        # Score-based summary
        english_summary = """Your participation in the assessment center provided insight into how you demonstrate the leadership competencies in action. The feedback below highlights observed strengths and opportunities for development to support your continued growth.\n\nYou display clear strengths in several areas of leadership. In relation to **Adaptability**, you consistently demonstrate the ability to navigate and lead teams through change, learn from experiences, and maintain resilience in challenging situations. This reflects your capacity to foster innovation and maintain team morale during periods of ambiguity. Similarly, your performance in **Decision Making and Takes Accountability** highlights your ability to make assertive, informed decisions, even under pressure. You exhibit confidence in articulating your decisions, evaluate risks effectively, and align your choices with organizational goals and values. Another area of strength is **Strategic Thinking**, where you excel in monitoring industry trends, identifying opportunities, and translating strategic goals into actionable plans. These behaviors underscore your ability to align organizational objectives with long-term success.\n\nIn addition, there are areas where you demonstrate potential strengths that can be further leveraged. In **Effective Communication and Influence**, you effectively articulate ideas and influence others toward collaborative outcomes. However, there is room to enhance your listening skills to ensure all team members feel fully heard and understood. Similarly, in **Initiative**, you show a strong commitment to pursuing opportunities and achieving results, but there is potential to push boundaries further and consistently exceed expectations. In **Inspirational Leadership**, you create a sense of vision and purpose for your team and adapt your leadership style to different situations. However, there is an opportunity to deepen your emotional awareness and proactively manage individual team dynamics to maximize contributions. In **Capability Development**, you engage in coaching and delegation effectively, yet there is scope to more systematically identify and nurture high-potential talent to meet future organizational needs.\n\nIn relation to the development areas, **Systematic Analysis and Planning** emerged as an area for improvement. There is a need to enhance resource allocation skills and establish more robust metrics to evaluate progress. Strengthening these aspects will help achieve greater consistency in delivering high-quality results and aligning plans with strategic priorities."""
        arabic_summary = """نشكرك على مشاركتك في مركز التقييم، مما أتاح لنا رؤية متعمقة لكيفية تجسيدك للكفاءات القيادية عمليًا. تسلط الملاحظات التالية الضوء على نقاط القوة التي تم رصدها وفرص التطوير المتاحة لدعم نموك المستمر.\n\nتُظهر نقاط قوة واضحة في عدة مجالات قيادية. فيما يتعلق بـ**القدرة على التكيف**، فإنك تبرهن باستمرار على قدرتك على قيادة الفرق خلال فترات التغيير، والتعلم من التجارب، والحفاظ على المرونة في المواقف الصعبة. وهذا يعكس قدرتك على تعزيز الابتكار والحفاظ على معنويات الفريق في أوقات الغموض. وبالمثل، يُبرز أداؤك في **اتخاذ القرار وتحمل المسؤولية** قدرتك على اتخاذ قرارات حاسمة ومستنيرة، حتى تحت الضغط. كما أنك تُظهر ثقة في التعبير عن قراراتك، وتقييم المخاطر بفعالية، ومواءمة خياراتك مع أهداف المنظمة وقيمها. ومن نقاط القوة الأخرى **التفكير الاستراتيجي**، حيث تتفوق في متابعة اتجاهات القطاع، وتحديد الفرص، وترجمة الأهداف الاستراتيجية إلى خطط قابلة للتنفيذ، مما يؤكد قدرتك على مواءمة أهداف المنظمة مع النجاح على المدى الطويل.\n\nبالإضافة إلى ذلك، هناك مجالات تُظهر فيها نقاط قوة كامنة يمكن تعزيزها. في **التواصل الفعال والتأثير**، تُعبر عن الأفكار بفعالية وتؤثر في الآخرين لتحقيق نتائج تعاونية، ولكن هناك مجال لتعزيز مهارات الاستماع لديك لضمان شعور جميع أعضاء الفريق بأنهم مسموعون ومفهومون تمامًا. وبالمثل، في **المبادرة**، تُظهر التزامًا قويًا باستثمار الفرص وتحقيق النتائج، ولكن هناك إمكانية لدفع الحدود إلى أبعد من ذلك وتجاوز التوقعات باستمرار. في **القيادة الملهمة**، تنجح في خلق رؤية وهدف لفريقك وتكييف أسلوب قيادتك مع المواقف المختلفة، ومع ذلك، هناك فرصة لتعميق وعيك العاطفي وإدارة ديناميكيات الفريق بشكل استباقي لتحقيق أقصى قدر من المساهمات. في **تطوير القدرات**، تمارس التدريب والتفويض بفعالية، ولكن هناك مجال لتحديد ورعاية المواهب الواعدة بشكل أكثر منهجية لتلبية احتياجات المنظمة المستقبلية.\n\nفيما يتعلق بمجالات التطوير، برز **التحليل المنهجي والتخطيط** كأحد الجوانب التي تتطلب تحسينًا. هناك حاجة لتعزيز مهاراتك في تخصيص الموارد ووضع مقاييس أكثر قوة لتقييم التقدم. إن تعزيز هذه الجوانب سيساعدك على تحقيق قدر أكبر من الاتساق في تقديم نتائج عالية الجودة ومواءمة الخطط مع الأولويات الاستراتيجية."""
        return english_summary, arabic_summary

def process_scores(df):
    """Processes the scores dataframe to generate initial summaries."""
    results = []
    indicator_definitions = df.iloc[0]
    people_data = df.iloc[1:]
    score_prompt_template = get_score_summary_prompt()

    for _, row in people_data.iterrows():
        person_name = row.iloc[0]
        if pd.isna(person_name) or 'ERROR' in str(row.iloc[1]): continue

        person_data_prompt = f"**Person's Name:** {person_name}\n\n**Competency Data:**\n"
        for i in range(8):
            comp_col_index = 1 + (i * 5)
            person_data_prompt += f"\n**- Competency: {df.columns[comp_col_index]}** (Average Score: {row[comp_col_index]})\n"
            for j in range(4):
                ind_col_index = comp_col_index + 1 + j
                person_data_prompt += f"  - Indicator: '{indicator_definitions[ind_col_index]}' | Score: {row[ind_col_index]}\n"

        full_prompt = score_prompt_template + person_data_prompt
        eng_summary, ar_summary = generate_summary_from_llm(full_prompt, is_comment_summary=False)
        results.append({"Person": person_name, "English Summary": eng_summary, "Arabic Summary": ar_summary})
    return pd.DataFrame(results)

def process_comments_and_append(results_df, comments_df):
    """Processes comments and appends them to the existing summaries."""
    comment_prompt_template = get_comment_summary_prompt()
    
    for i, row in results_df.iterrows():
        person_code = row['Person']
        main_eng_summary = row['English Summary']
        
        # Filter comments for the current person
        person_comments = comments_df[comments_df['Person Code'] == person_code]['Comments'].tolist()

        if person_comments:
            # Construct the prompt for comment summarization
            comment_data_prompt = f"**Main Report:**\n{main_eng_summary}\n\n**Raw Comments to Summarize:**\n- {'\n- '.join(person_comments)}"
            full_prompt = comment_prompt_template + comment_data_prompt
            
            # Generate comment summary
            eng_comment_summary, ar_comment_summary = generate_summary_from_llm(full_prompt, is_comment_summary=True)

            # Append the new paragraph
            results_df.at[i, 'English Summary'] += f"\n\n{eng_comment_summary}"
            results_df.at[i, 'Arabic Summary'] += f"\n\n{ar_comment_summary}"
            
    return results_df

# --- Streamlit App UI ---

st.set_page_config(layout="wide")
st.title("📄 Integrated Performance Summary Generator")

# --- Step 1: Score File ---
st.markdown("### 1. Upload Quantitative Scores File")
with st.expander("Show Score File Instructions"):
    st.write("Upload an Excel file with competency scores. The first row should be headers, the second row must contain indicator definitions, and subsequent rows should have person IDs and scores.")
    sample_scores_df = get_sample_scores_df()
    st.download_button(
        label="📥 Download Scores Template",
        data=df_to_excel_bytes(sample_scores_df),
        file_name="sample_scores_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

uploaded_scores_file = st.file_uploader("Choose a scores file", type="xlsx", key="scores_uploader")

if uploaded_scores_file:
    try:
        scores_df = pd.read_excel(uploaded_scores_file, engine='openpyxl')
        if st.button("Generate Summaries from Scores", key="generate_scores"):
            with st.spinner("Analyzing scores and generating summaries..."):
                results_df = process_scores(scores_df)
                st.session_state['results_df'] = results_df
                st.success("Score-based summaries generated successfully!")
    except Exception as e:
        st.error(f"Error processing scores file: {e}")

# --- Step 2: Display initial results and offer comment upload ---
if 'results_df' in st.session_state:
    st.markdown("---")
    st.markdown("### 2. Score-Based Summaries (Preview)")
    st.dataframe(st.session_state['results_df'].head())

    st.markdown("---")
    st.markdown("### 3. (Optional) Upload Qualitative Comments File")
    with st.expander("Show Comments File Instructions"):
        st.write("To enrich the report, upload an Excel file with raw comments. It should have two columns: 'Person Code' and 'Comments'.")
        sample_comments_df = get_sample_comments_df()
        st.download_button(
            label="📥 Download Comments Template",
            data=df_to_excel_bytes(sample_comments_df),
            file_name="sample_comments_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    uploaded_comments_file = st.file_uploader("Choose a comments file", type="xlsx", key="comments_uploader")

    if uploaded_comments_file:
        try:
            comments_df = pd.read_excel(uploaded_comments_file, engine='openpyxl')
            if st.button("Incorporate Comments into Summaries", key="generate_comments"):
                with st.spinner("Analyzing comments and updating summaries..."):
                    # Make a copy to avoid modifying the session state directly during processing
                    current_results = st.session_state['results_df'].copy()
                    final_df = process_comments_and_append(current_results, comments_df)
                    st.session_state['final_df'] = final_df
                    st.success("Comments incorporated successfully!")
        except Exception as e:
            st.error(f"Error processing comments file: {e}")

# --- Step 3: Display final results and download ---
if 'final_df' in st.session_state:
    st.markdown("---")
    st.markdown("### 4. Final Integrated Report")
    st.dataframe(st.session_state['final_df'])
    st.download_button(
        label="📥 Download Final Integrated Report",
        data=df_to_excel_bytes(st.session_state['final_df']),
        file_name="final_integrated_summaries.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
elif 'results_df' in st.session_state and 'final_df' not in st.session_state:
    # Offer download for score-based summary if comments are not added
    st.markdown("---")
    st.markdown("### 4. Download Score-Based Report")
    st.download_button(
        label="📥 Download Score-Based Report",
        data=df_to_excel_bytes(st.session_state['results_df']),
        file_name="score_based_summaries.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
