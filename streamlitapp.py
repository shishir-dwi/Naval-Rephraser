import streamlit as st
from langchain_openai import ChatOpenAI
import json

from loguru import logger
import traceback

logger.add('rephraser.log', format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")


def parse_Response(response):
    # print(response)
    start_index = response.find("{")
    end_index = response.rfind("}")
    if start_index != -1 and end_index != -1:
        valid_json_content = response[start_index : end_index + 1]
        try:
            JSON_response = json.loads(valid_json_content.replace("\n", ""))
            # append_list_to_file(JSON_response)
            return JSON_response
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response: {e.__class__.__name__} - {e}\n\n Still trying to work on particular exceptions ...")
            logger.debug(f"Actual Content:  {valid_json_content}")
    else:
        logger.warning("No valid JSON content found in the response.")
        # time.sleep(50)
        return None



def style_selection(selected_style_str):
    styles = {
        "Simple/less technical terms": 1,
        "Include Analogy": 2,
        "Include Examples": 3,
    }
    return styles.get(selected_style_str, None)


def get_OpenAI_response(prompt, model_name="gpt-4o-mini", temperature=0.3 ):
    
    model = ChatOpenAI(model=model_name, temperature=temperature)
    
    try:
        response = model.invoke(prompt)
 
        try :
            parsed_output = parse_Response(response.content)
            if parsed_output:
                return parsed_output['rephrased_text']
            else:
                raise Exception ("NONE RETURNED FROM PARSER")
        except Exception as e:
            logger.error(f"Error with PARSING : COULD NOT PARSE THE MODEL OUTPUT {type(e).__name__} - {e}\n{traceback.format_exc()}")
            return None
    except Exception as e:
        logger.error(f"Error with invocation: {type(e).__name__} –, {e} \n {traceback.format_exc()}")
        return None




def get_prompt(style_no: int, summary: str, answer="") -> str:
    REPHRASING_STYLES_DICT = {
        1: "should be simpler and use fewer technical terms compared to the original input",
       
    }
    
        #instructions dictionary
    REPHRASING_INSTRUCTIONS_DICT = {
        1: (
        "Rephrase the provided text such that it is Concise while retaining its original meaning. \n"
        "The generated rephrased answer word length should be around that of the given content. \n"
        "Ensure the rephrased response remains in the context of the provided content without introducing unrelated information. \n"
    ),
    
    }

    REPHRASED_TEXT_OUTPUT_FORMAT_DICT = {
        1: """
            {
                "rephrased_text": "The rephrased version of the input text."
            }
            """,

        2: """
            {
                "rephrased_text": "{summary} \n{response generated}"
            }
            """,
        3: """
            {
            "rephrased_text": "{summary} \n{response generated}"
            }
            """,
    }

    REPHRASING_PROMPT_TEMPLATE_STRING_DICT = {
        1: (
            "You're an Educational AI model designed to Rephrase text, which has all the knowledge of the undergraduate Bachelors of Technology Course."
            "Your task is rephrase the given text based on the your style, the context, and the given guidelines. \n\n"
            "Your writing style : {style}. \n\n"
            "Follow these instructions to generate a good quality rephrased answer: {instructions}\n"
            "Given content to be used for rephrasing: ```{text}```\n\n"

            "Return your output as json in the following format:"
            "{output_format} \n\n"
            
            "Ensure that you follow all the above guidelines and rules to generate the rephrased content. Any deviation from these guidelines \
            will result in rephrased content not meeting the education standards required for this exercise."
        ),
        
        2: (
            "You are an AI specializing in creating relatable analogies. "
            "Given the following explanation, provide a short, real-world analogy that is "
            "easy to understand and relatable for most people.\n\n"
            "Answer: {answer}\n\n"
            "Analogy: "
            "Ensure that the analogy does not exceed more than 50 words.\n\n"

            "And concatenate these result after the given {summary} text"
            "Ensure the {summary} followed by the **analogy** generated is included in the output."

            "Format Your Output: "
            "Return your response in the given format:\n"
            "{output_format}"
        ),
        3: (
            "You are an Educational AI assistant who excels in Bachelors of Technology course. "
            "You have all the knowledge about every subject and its whole content. "
            "Given the following answer, generate three concise examples that relate to the content. "
            "Each example must be brief and to the point.\n\n"
            "Answer: {answer}\n\n"
            "Ensure that the word length of each example does not exceed 15 words.\n\n"

            "And concatenate these result after the given {summary} text"
            "Ensure the {summary} followed by the **examples** generated is included in the output."

            "Format Your Output: "
            "Return your response in the given format:\n"
            "{output_format}"
        ),
    }

    output_format = REPHRASED_TEXT_OUTPUT_FORMAT_DICT[style_no]
     
    # Validate style number
    if style_no not in REPHRASING_PROMPT_TEMPLATE_STRING_DICT:
        return "Invalid style number"

    # define prompt
    if style_no == 1:
        style = REPHRASING_STYLES_DICT[style_no]
        instructions = REPHRASING_INSTRUCTIONS_DICT[style_no]
        prompt = REPHRASING_PROMPT_TEMPLATE_STRING_DICT[style_no].format(text = summary, style=style, instructions=instructions, output_format=output_format)
    else:
        prompt = REPHRASING_PROMPT_TEMPLATE_STRING_DICT[style_no].format(answer = answer, summary = summary, output_format=output_format)
    
    return prompt
    
    
def get_rephrased_content(selected_style: str, summary: str, answer="") :
    style_no = style_selection(selected_style)
    if not style_no:
        return "Invalid style selected."
    
    prompt = get_prompt(style_no, summary, answer )
    
    
    # rephrasing the styles 1 
    if style_no == 1 :
        parsed_output = get_OpenAI_response(prompt, model_name="gpt-4", temperature=0.3 ) # calling the rephrasing function and getting a parsed output      
    # rephrasing for style 2 or 3
    else:  
        parsed_output = get_OpenAI_response(prompt, model_name="gpt-4", temperature=0.7 ) # getting the 3.analogy / 4.example
        
    return parsed_output




# # Streamlit App
# st.title("Rephraser App")

# # Inputs
# summary = st.text_area("Summary:")
# answer = st.text_area("Answer (Optional):")
# style = st.selectbox(
#     "Select Style:", ["Simple/less technical terms", "Include Analogy", "Include Examples"]
# )

# if st.button("Rephrase"):
#     if not summary:
#         st.error("Summary is required!")
#     else:
#         rephrased_text = get_rephrased_content(style, summary, answer)
#         st.text_area("Rephrased Text:", rephrased_text, height=200)
        
# Inject custom CSS
custom_css = """
<style>
.st-emotion-cache-yw8pof {
    width: 100%; /* Adjust width to your preference */
    padding: 4rem 2rem 6rem; /* Customize padding as needed */
    max-width: 80rem; /* Adjust the max-width */
}

.st-emotion-cache-yw8pof {
    width: 100%;
    padding: 4rem 2rem 6rem;
    max-width: 80rem;
}

.st-emotion-cache-1u4fkce{
    max-height: 20px;
}


.stAppHeader img {
    height: 80px; /* Adjust image height */
    margin: auto;
}


.stAppHeader-naval {
    background-color: #DEDEDE; /* Optional: Set a background color */
    color: black; /* Text color, if any */
    height: 80px; /* Adjust height */
    min-width: 100%;
}

.stAppHeader-naval img {
    height: 80px; /* Adjust image height */
    margin: auto;
}

.st-emotion-cache-1v0mbdj{
    max-height: 15px;
    z-index: 2000000;
    position: fixed;
    top: 15px;
    left: 15px;
}

.st-emotion-cache-1v0mbdj{
    
        gap: 9px;
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        align-content: normal;
        justify-content: normal;
        align-items: center;
}

</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
        
# st.markdown("<div class='stAppHeader-naval'><img src='logo.png' alt='Logo'></div>", unsafe_allow_html=True)
# st.image('logo.png', width=100)
# st.logo('logo.png', size="large")
st.image('logo.png', width=70, caption="NAVAL Innovators")

# Streamlit App
# st.set_page_config(page_title="Rephraser App", page_icon="✍️")
st.title("Rephraser App - NAVAL Innovators")
# st.markdown("""<h1 style='text-align: center;'>Rephraser App - NAVAL Innovators</h1>""", unsafe_allow_html=True)


# Inputs
col1, col2 = st.columns([4, 4])  # Adjust the ratio as needed
with col1:
    summary = st.text_area("**Summary:**", height=200)
with col2:
    answer = st.text_area("**Answer (Optional):**", height=200)

style = st.selectbox(
    "Select Style:", ["Simple/less technical terms", "Include Analogy", "Include Examples"]
)

if st.button("Rephrase"):
    if not summary:
        st.error("Summary is required!")
    else:
        rephrased_text = get_rephrased_content(style, summary, answer)
        st.text_area("Rephrased Text:", rephrased_text, height=200)
