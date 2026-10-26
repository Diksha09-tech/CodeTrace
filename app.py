
import streamlit as st
from analyzer import analyze_code

st.set_page_config(
    page_title="CodeTrace - Python Error Detective",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 CodeTrace")
st.subheader("Python Error Detective")
st.write(
    "Paste your Python code or upload a .py file. "
    "CodeTrace checks for common issues without executing your code."
)

st.sidebar.title("About CodeTrace")
st.sidebar.write(
    "CodeTrace is a beginner-friendly Python static analyzer."
)
st.sidebar.info(
    "It detects selected common issues. It cannot detect every possible error."
)

examples = {
    "Choose an example": "",
    "Syntax error": 'print("Hello"',
    "Division by zero": "total = 100\naverage = total / 0",
    "Undefined variable": "print(username)",
    "Correct code": 'student = "Diksha"\nprint(student)'
}

selected_example = st.selectbox(
    "Try an example",
    list(examples.keys())
)

input_method = st.radio(
    "Choose your input method",
    ["Write or paste code", "Upload a Python file"],
    horizontal=True
)

if input_method == "Upload a Python file":
    uploaded_file = st.file_uploader(
        "Upload a Python file",
        type=["py"]
    )

    if uploaded_file is not None:
        try:
            source_code = uploaded_file.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            source_code = ""
            st.error("The file must use UTF-8 text encoding.")

    else:
        source_code = ""

    st.text_area(
        "Uploaded Python code",
        value=source_code,
        height=300,
        disabled=True
    )

else:
    source_code = st.text_area(
        "Your Python code",
        value=examples[selected_example],
        height=300,
        placeholder="Write or paste your Python code here..."
    )

col1, col2 = st.columns(2)

with col1:
    analyze_clicked = st.button(
        "🔍 Analyze Code",
        use_container_width=True
    )

with col2:
    clear_clicked = st.button(
        "🗑️ Clear Code",
        use_container_width=True
    )

if clear_clicked:
    st.rerun()

if analyze_clicked:
    if not source_code.strip():
        st.warning("Please enter or upload Python code first.")

    else:
        result = analyze_code(source_code)

        st.subheader("Analysis Result")

        if result.startswith("Analysis completed successfully!"):
            st.success("No known issues detected!")
            st.code(result, language="text")

        elif result.startswith("Error type: SyntaxError"):
            st.error("Syntax error detected!")
            st.code(result, language="text")

        else:
            st.warning("Potential issue detected!")
            st.code(result, language="text")

st.caption(
    "Note: CodeTrace performs limited static analysis and does not run your code."
)
