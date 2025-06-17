import streamlit as st
import pandas as pd
import io

# --- Helper Functions ---

def get_sample_df():
    """
    Creates a sample DataFrame that matches the required Excel format.
    This will be used to generate the downloadable template file.
    """
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
    # To ensure all columns are created, we can create an empty df with columns and then add data
    # This is a simplified example; a real one would have all 41 columns.
    # For this demonstration, we'll create a dataframe from the dictionary.
    return pd.DataFrame(data)

def df_to_excel_bytes(df):
    """Converts a DataFrame to an in-memory Excel file (bytes)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Template')
    output.seek(0)
    return output.getvalue()


def get_master_prompt():
    """
    Returns the final, calibrated master prompt architecture.
    This includes all rules, persona, logic, and exemplars.
    """
    return """
**## Persona**
You are an expert talent management analyst. Your writing style is formal, professional, objective, and constructive. You synthesize quantitative performance data into a qualitative, behavioral-focused narrative. You are writing for a male individual, using the third person (`he`/`his`/`him`).

**## Core Objective**
Generate a multi-paragraph performance summary based on scores from 8 leadership competencies. The summary must be generated in both English and Arabic.

**## Input Data Profile**
You will receive a data set for one individual containing:
1.  **8 Competency Names:** (e.g., Adaptability, Strategic Thinking, etc.).
2.  **Indicator Scores:** Each competency has 4 underlying indicators, each with a score from 1 to 5.
3.  **Indicator Text:** The specific behavioral description for each indicator.

**## Core Logic & Execution Flow**

**Step 1: Data Analysis & Categorization**
1.  For each of the 8 competencies, calculate the average score of its 4 indicators.
2.  Categorize each competency based on its average score:
    * **Clear Strength:** Average score >= 4.0
    * **Potential Strength:** Average score between 2.6 and 3.9
    * **Development Area:** Average score <= 2.5

**Step 2: Summary Construction**
1.  **Mandatory Opening:** The English summary MUST begin with this exact text: "Your participation in the assessment center provided insight into how you demonstrate the leadership competencies in action. The feedback below highlights observed strengths and opportunities for development to support your continued growth." The Arabic summary should use an equivalent professional opening.
2.  **Paragraph 1 (Clear Strengths):**
    * Start this paragraph with a sentence like "You display clear strengths in several areas of leadership."
    * Address ONLY the competencies categorized as "Clear Strength".
    * For each, introduce the competency using phrases like "In relation to **[Competency Name]**..." or "Similarly, your performance in **[Competency Name]** highlights...". **The competency name must be bolded.**
    * Describe the strength by paraphrasing the text of its highest-scoring indicators.
3.  **Paragraph 2 (Potential Strengths):**
    * Start this paragraph with a sentence like "In addition, there are areas where you demonstrate potential strengths that can be further leveraged."
    * Address ONLY the competencies categorized as "Potential Strength".
    * For each, introduce the competency (e.g., "In **[Competency Name]**..."). **The competency name must be bolded.**
    * First, describe the positive aspects by paraphrasing the higher-scoring indicators.
    * Then, introduce the growth area within that same competency using phrases like "However, there is room to enhance..." or "yet there is scope to more systematically...". Paraphrase the lower-scoring indicators.
4.  **Paragraph 3 (Development Areas):**
    * This paragraph should only be included if there are competencies in the "Development Area" category.
    * Start this paragraph with a sentence like "In relation to the development areas, **[Competency Name]** emerged as an area for improvement."
    * Address ONLY the "Development Area" competencies.
    * Describe the development need by paraphrasing the text of the lowest-scoring indicators.

**## Writing Standards & Constraints**
* **Word Count:** Maximum 400 words total per language (excluding the mandatory opening).
* **Source Fidelity:** Base all statements *strictly* on the indicator language. Do not add information or make assumptions.
* **Behavioral Focus:** Do not use technical or industry-specific jargon. The summary must be purely behavioral.
* **No Actions:** Describe the strengths and development areas only. DO NOT suggest specific development actions.

**## Bilingual Generation Mandate: English and Arabic**
* **Primary Task:** Generate the summary in **both English and Arabic**, following the same structure and tone.
* **Arabic Language Standards:**
    * **Nuance and Professionalism:** The Arabic translation must be crafted with the nuance and flow of a native Arabic-speaking HR professional, not a literal translation.
    * **Tone:** Formal, respectful, and constructive, using professional terminology appropriate for a corporate setting.
* **Output Format:** Provide the English summary first, followed by the Arabic summary.

---
**## TASK: GENERATE SUMMARY FOR THE FOLLOWING PERSON**
"""

def generate_summary_from_llm(person_data_prompt):
    """
    This is a placeholder function to simulate a call to a powerful Large Language Model (LLM).
    It returns a hardcoded example that matches the updated, more nuanced prompt format.
    """
    english_summary = """Your participation in the assessment center provided insight into how you demonstrate the leadership competencies in action. The feedback below highlights observed strengths and opportunities for development to support your continued growth.

You display clear strengths in several areas of leadership. In relation to **Decision Making and Takes Accountability**, you exhibit confidence in articulating your decisions and effectively evaluate risks. Another area of strength is **Adaptability**, where you consistently navigate teams through change and maintain resilience.

In addition, there are areas where you demonstrate potential strengths that can be further leveraged. In **Initiative**, you show a strong commitment to pursuing opportunities, yet there is potential to more consistently set ambitious objectives to exceed expectations. Similarly, in **Effective Communication and Influence**, you articulate ideas well, however, there is room to enhance your listening skills to ensure all team members feel fully heard. For **Inspirational Leadership**, you are effective at creating a sense of vision, but there is an opportunity to deepen your emotional awareness to better maximize your team's contributions.

In relation to the development areas, **Systematic Analysis and Planning** emerged as an area for improvement. There is room to enhance your resource allocation skills and establish more robust metrics to evaluate progress, which will help in delivering high-quality results more consistently.
"""

    arabic_summary = """نود أن نشكرك على مشاركتك في مركز التقييم، والتي أتاحت لنا فرصة الاطلاع على كيفية تطبيقك للكفاءات القيادية على أرض الواقع. تستعرض الملاحظات أدناه نقاط القوة التي لوحظت وفرص التطوير المتاحة، وذلك بهدف دعم مسيرتك المهنية المستمرة.

تُظهر نقاط قوة واضحة في عدة مجالات قيادية. فيما يتعلق بـ**اتخاذ القرار وتحمل المسؤولية**، فإنك تُبدي ثقة في التعبير عن قراراتك وتقييم المخاطر بفاعلية. كما أن **القدرة على التكيف** تمثل إحدى نقاط قوتك، حيث تقود الفرق بنجاح خلال فترات التغيير وتحافظ على مرونتك.

بالإضافة إلى ذلك، هناك مجالات تُظهر فيها نقاط قوة كامنة يمكن تعزيزها. في مجال **المبادرة**، تُظهر التزامًا قويًا باستثمار الفرص، ولكن هناك إمكانية لوضع أهداف أكثر طموحًا بشكل مستمر لتجاوز التوقعات. وبالمثل، في **التواصل الفعال والتأثير**، تُعبر عن أفكارك بوضوح، ولكن هناك مجال لتحسين مهارات الاستماع لديك لضمان شعور جميع أعضاء الفريق بأن أصواتهم مسموعة. أما بالنسبة لـ**القيادة الملهمة**، فأنت فعال في خلق رؤية مشتركة، ولكن هناك فرصة لتعميق وعيك العاطفي لتحقيق أقصى استفادة من مساهمات فريقك.

فيما يتعلق بمجالات التطوير، برز **التحليل المنهجي والتخطيط** كأحد الجوانب التي تتطلب تحسينًا. هناك مجال لتعزيز مهاراتك في تخصيص الموارد ووضع مقاييس أكثر دقة لتقييم التقدم، مما سيساعد في تحقيق نتائج عالية الجودة بشكل أكثر اتساقًا.
"""
    return english_summary, arabic_summary


def process_data(df):
    """
    Processes the uploaded dataframe to generate summaries for each person.
    """
    master_prompt = get_master_prompt()
    results = []

    # The second row contains the indicator text definitions
    indicator_definitions = df.iloc[0] 
    
    # Data for actual people starts from the third row
    people_data = df.iloc[1:]

    progress_bar = st.progress(0)
    total_people = len(people_data)
    for i, (index, row) in enumerate(people_data.iterrows()):
        person_name = row.iloc[0]
        
        if pd.isna(person_name) or 'ERROR' in str(row.iloc[1]):
            continue

        st.write(f"Generating summary for {person_name}...")
        
        person_data_prompt = f"**Person's Name:** {person_name}\n\n**Competency Data:**\n"
        
        for comp_idx in range(8):
            comp_col_index = 1 + (comp_idx * 5)
            competency_name = df.columns[comp_col_index]
            person_data_prompt += f"\n**- Competency: {competency_name}** (Average Score: {row[comp_col_index]})\n"
            for ind_idx in range(4):
                indicator_col_index = comp_col_index + 1 + ind_idx
                indicator_text = indicator_definitions[indicator_col_index]
                indicator_score = row[indicator_col_index]
                person_data_prompt += f"  - Indicator: '{indicator_text}' | Score: {indicator_score}\n"
        
        full_prompt = master_prompt + person_data_prompt
        english_summary, arabic_summary = generate_summary_from_llm(full_prompt)

        results.append({
            "Person": person_name,
            "English Summary": english_summary,
            "Arabic Summary": arabic_summary
        })
        progress_bar.progress((i + 1) / total_people)

    return pd.DataFrame(results)

# --- Streamlit App UI ---

st.set_page_config(layout="wide")
st.title("📄 Performance Summary Generator")

# --- ADDED: Sample File Download Section ---
st.markdown("### 1. Download Sample Template")
st.write("If you're unsure about the file format, download this sample template.")
sample_df = get_sample_df()
sample_excel_bytes = df_to_excel_bytes(sample_df)
st.download_button(
    label="📥 Download Sample Excel Template",
    data=sample_excel_bytes,
    file_name="sample_summary_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# --- END: Sample File Download Section ---

st.markdown("---")
st.markdown("### 2. Upload Your Data File")
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("File uploaded successfully! Here's a preview:")
        st.dataframe(df.head())

        st.markdown("### 3. Generate Summaries")
        if st.button("Generate Summaries", key="generate"):
            with st.spinner("Analyzing data and generating summaries... This may take a moment."):
                results_df = process_data(df)
                st.success("Summaries generated successfully!")
                st.session_state['results_df'] = results_df

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error("Please ensure the file is a valid Excel file and the format matches the sample template.")

if 'results_df' in st.session_state:
    results_df = st.session_state['results_df']
    if not results_df.empty:
        st.markdown("---")
        st.markdown("### 4. View and Download Results")
        st.dataframe(results_df)

        results_excel_bytes = df_to_excel_bytes(results_df)
        st.download_button(
            label="📥 Download All Results as Excel",
            data=results_excel_bytes,
            file_name="generated_summaries.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
