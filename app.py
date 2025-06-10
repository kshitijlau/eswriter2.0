import streamlit as st
import pandas as pd
import openai
import io

# --- Helper Function to convert DataFrame to Excel in memory ---
def to_excel(df):
    """
    Converts a pandas DataFrame to an Excel file in memory (bytes).
    This function is used to prepare the final output for download.
    """
    output = io.BytesIO()
    # Use 'xlsxwriter' engine for better compatibility and features.
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Summaries')
    processed_data = output.getvalue()
    return processed_data

# --- The Master Prompt Template ---
# This is the heart of the application. It's a comprehensive, expert-level prompt
# that instructs the AI on exactly how to perform the summarization task.
def create_master_prompt(person_name, person_data):
    """
    Dynamically creates the detailed, expert-level prompt for the Azure OpenAI API.
    This function structures all the rules, examples, and data into a single request.

    Args:
        person_name (str): The name of the person being evaluated.
        person_data (str): A string representation of the person's scores and indicators.

    Returns:
        str: A fully constructed prompt ready to be sent to the AI model.
    """
    return f"""
You are an expert HR and organizational development analyst. Your specialization is synthesizing quantitative leadership assessment data into a formal, professional, and purely behavioral performance summary. You must adhere to the highest standards of professional HR writing, ensuring the output is constructive, balanced, and directly tied to the provided evidence.

## Core Objective
Your task is to process a set of scores for an individual named {person_name} across 8 core leadership competencies and their underlying behavioral indicators. You will then generate a two-paragraph summary (one for strengths, one for development) in both English and Arabic.

## Input Data for {person_name}
{person_data}

## Primary Directives & Rules

1.  **Two-Paragraph Structure:**
    * **Paragraph 1 (Strengths & Potential):** This paragraph MUST ONLY discuss strengths. It will first address all competencies with scores of 4 or 5. After that, it will address all competencies with a score of 3.
    * **Paragraph 2 (Development Areas):** This paragraph MUST ONLY discuss development areas, which are any competencies with scores of 1 or 2. If there are no scores of 1 or 2, this paragraph should not be generated.

2.  **Score Interpretation Logic:**
    * **Scores 4 & 5:** Frame these as clear, definitive strengths. Use confident and affirming language based on the indicator's definition.
    * **Score 3:** Frame these as "potential strengths" or areas that can be "further leveraged." You must follow a balanced structure: state the emerging positive behavior, then describe the scope for improvement using the indicator's language.
    * **Scores 1 & 2:** Frame these as "development areas" or "areas for improvement." The language must be constructive and forward-looking (e.g., "He would benefit from focusing on..." or "There is an opportunity to develop...").

3.  **Writing and Content Standards:**
    * **Perspective:** 3rd person, male gender (he/his/him), addressing {person_name}.
    * **Tone:** Formal, professional, objective, and constructive.
    * **Evidence-Based:** Adhere strictly to the language of the provided indicators. DO NOT invent behaviors or make assumptions beyond the scope of the indicator's definition.
    * **No Actions:** Identify the development area, but DO NOT prescribe solutions or development actions.
    * **Structure:** For each point, state the **Competency** name first, then elaborate using the synthesized language from the **Indicator**.
    * **Behavioral Focus:** Keep all feedback purely behavioral. Omit any technical or industry-specific references.
    * **Length:** The total summary should not exceed 400 words.

4.  **Language and Output Format:**
    * First, generate the complete, final summary in English.
    * Then, use a clear separator like '---ARABIC---'.
    * After the separator, provide an accurate and professional Arabic translation of the English summary.

## Detailed Analysis of Required Output (Internalizing Examples for High-Quality Generation)

**Analyze and learn from these two examples showing the transformation from scores to summary.**

### Example 1: Primarily Strengths (Like Subject E01)
* **Key Input Scores:** High scores (4s, 5s).
* **Correct Output Structure:** A single, comprehensive strengths paragraph. No development paragraph.
* **Reasoning to Emulate:** The summary should start with the highest-rated competencies. It must synthesize multiple high-scoring indicators into a fluid narrative for each competency. The sentence structure must be "Competency + Elaboration."

### Example 2: Potential Strengths & Development Needs (Like Subject E32)
* **Key Input Scores:** Scores of 3 and some scores of 1 or 2.
* **Correct Output Structure:** A first paragraph detailing "potential strengths," and a second paragraph for development areas.
* **Reasoning to Emulate:**
    * **Paragraph 1 (Score 3):** The summary must identify scores of 3 as "potential strengths." It must use balanced phrasing like, *"He shows potential in [positive aspect], there is room for him to improve [area for leverage]."* This exact structure must be replicated for all score 3 indicators.
    * **Paragraph 2 (Scores 1-2):** The summary must transition cleanly to development. It must use constructive phrases like "was observed as potential area of improvement" and "is another area of development." It must correctly translate the low-scoring indicator language into a developmental need without prescribing an action.

## Final Instruction for {person_name}
Now, process the new set of competency scores provided for {person_name} and generate the two-paragraph summary, first in English and then in Arabic, adhering strictly to all the rules and learned examples above. The English and Arabic text should be separated by '---ARABIC---'.
"""

# --- API Call Function for Azure OpenAI ---
def generate_summary_azure(prompt, api_key, endpoint, deployment_name):
    """
    Calls the Azure OpenAI API to generate a summary.
    This function handles the specific client initialization required for Azure.
    """
    try:
        # Initialize the AzureOpenAI client with credentials from secrets
        client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version="2024-02-01"  # A common, stable API version
        )
        
        # Make the API call to the chat completions endpoint
        response = client.chat.completions.create(
            model=deployment_name,  # Use the deployment name for the model
            messages=[
                {"role": "system", "content": "You are an expert HR and organizational development analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        content = response.choices[0].message.content
        
        # Split the response into English and Arabic parts using the custom separator
        if '---ARABIC---' in content:
            english_summary, arabic_summary = content.split('---ARABIC---', 1)
        else:
            # Fallback if the separator is not found in the AI's response
            english_summary = content
            arabic_summary = "Translation not generated."
            
        return english_summary.strip(), arabic_summary.strip()
        
    except Exception as e:
        st.error(f"An error occurred while contacting Azure OpenAI: {e}")
        return None, None

# --- Streamlit App Main UI ---
st.set_page_config(page_title="HR Summary Generator (Azure)", layout="wide")

st.title("📄 Professional Performance Summary Generator (Azure OpenAI)")
st.markdown("""
This application uses AI to generate professional, behavioral summaries from assessment data.
1.  **Set up your secrets file**. Create a `.streamlit/secrets.toml` file with your Azure OpenAI credentials.
2.  **Download the Sample Template** to see the required Excel format.
3.  **Upload your completed Excel file**.
4.  **Click 'Generate Summaries'** to process the file and download the results.
""")

# --- Create and provide a sample file for download ---
sample_data = {
    'Name': ['John Doe', 'John Doe', 'John Doe', 'Jane Smith', 'Jane Smith', 'Jane Smith'],
    'Competency': ['Decision Making', 'Strategic Thinking', 'Capability Development', 'Adaptability Towards Change', 'Communication', 'Inspirational Leadership'],
    'Indicator': ['Makes decisions with confidence and gains buy-in', 'Thinks long-term and strategically', 'Delegates responsibilities effectively to others', 'Navigates through change and learns from experience', 'Communicates clearly and displays listening skills', 'Fails to recognize each team member\'s unique style'],
    'Score': [5, 4, 2, 4, 3, 1]
}
sample_df = pd.DataFrame(sample_data)
sample_excel_data = to_excel(sample_df)

st.download_button(
    label="📥 Download Sample Template File",
    data=sample_excel_data,
    file_name="summary_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload your completed Excel file here", type="xlsx")

if uploaded_file is not None:
    try:
        # Read the uploaded Excel file into a pandas DataFrame
        df = pd.read_excel(uploaded_file)
        
        # Validate that the necessary columns exist in the uploaded file
        required_columns = ['Name', 'Indicator', 'Score', 'Competency']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Error: The uploaded file is missing one or more required columns. Please ensure it contains: {', '.join(required_columns)}")
        else:
            st.success("Excel file loaded successfully. Ready to generate summaries.")
            st.dataframe(df.head())

            # The main action button to start the generation process
            if st.button("Generate Summaries", key="generate"):
                try:
                    # Securely access the Azure credentials from Streamlit's secrets
                    azure_api_key = st.secrets["azure_openai"]["api_key"]
                    azure_endpoint = st.secrets["azure_openai"]["endpoint"]
                    azure_deployment_name = st.secrets["azure_openai"]["deployment_name"]
                except (KeyError, FileNotFoundError):
                    # Provide a clear error if the secrets file is missing or misconfigured
                    st.error("Azure OpenAI credentials not found. Please create a `.streamlit/secrets.toml` file with your `api_key`, `endpoint`, and `deployment_name`.")
                    st.stop() # Stop execution if credentials are not found

                # Group the DataFrame by 'Name' to process each person individually
                grouped = df.groupby('Name')
                results = []
                
                # Initialize a progress bar for user feedback
                progress_bar = st.progress(0)
                total_people = len(grouped)
                
                # Iterate through each person's data
                for i, (name, group) in enumerate(grouped):
                    st.write(f"Processing summary for: {name}...")
                    
                    # Format the person's data into a string for the prompt
                    person_data_str = group[['Competency', 'Indicator', 'Score']].to_string(index=False)
                    # Create the master prompt with the person's specific data
                    prompt = create_master_prompt(name, person_data_str)
                    
                    # Call the Azure-specific function to get the summary
                    english_summary, arabic_summary = generate_summary_azure(
                        prompt, 
                        azure_api_key, 
                        azure_endpoint, 
                        azure_deployment_name
                    )
                    
                    # If the summary is successfully generated, add it to the results list
                    if english_summary and arabic_summary:
                        results.append({
                            'Name': name,
                            'English Summary': english_summary,
                            'Arabic Summary': arabic_summary
                        })
                        st.success(f"Successfully generated summary for {name}.")
                    else:
                        st.error(f"Failed to generate summary for {name}.")

                    # Update the progress bar
                    progress_bar.progress((i + 1) / total_people)
                
                # --- Display and Download Final Results ---
                if results:
                    st.balloons()
                    st.subheader("Generated Summaries")
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df) # Display results in a table
                    
                    # Convert the results DataFrame to an Excel file in memory
                    excel_data = to_excel(results_df)
                    
                    # Create a download button for the generated Excel file
                    st.download_button(
                        label="📥 Download Summaries as Excel",
                        data=excel_data,
                        file_name="generated_summaries_azure.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
