import streamlit as st

def show_overview():
    st.title("Overview")
    st.markdown("""
        #### Titanic: Machine Learning from Disaster
        **Description**: The sinking of the RMS Titanic is one of the most infamous shipwrecks 
        in history. On April 15, 1912, during her maiden voyage, the Titanic sank after colliding 
        with an iceberg, killing 1502 out of 2224 passengers and crew. This sensational tragedy 
        shocked the international community and led to better safety regulations for ships.
        
        In this challenge, we ask you to complete the analysis of what sorts of people were likely 
        to survive. In particular, we ask you to apply the tools of machine learning to predict 
        which passengers survived the tragedy.
        
        **Prizes**: $50,000
    """)

def show_data():
    st.title("Data")
    st.write("## Data Overview")
    st.write("""
        ### Files
        - [train.csv](https://www.kaggle.com/c/titanic/download/train.csv) - The training set
        - [test.csv](https://www.kaggle.com/c/titanic/download/test.csv) - The test set
    """)

def show_submit():
    st.sidebar.title("Submit Your Entry")

    st.write("## Submission Form")

    # CSVファイルのアップロード
    st.write("### Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    # メールアドレスの入力
    st.write("### Enter Your Email Address")
    email = st.text_input("Email")

    # 登録名の入力
    st.write("### Enter Your Username")
    username = st.text_input("Username")

    # 提出ボタン
    if st.button("Submit"):
        if uploaded_file is not None and email != "" and username != "":
            # 提出処理を行う場合のコードをここに記述
            st.success("Your submission was successful!")
        else:
            st.error("Please fill in all the fields.")

def show_rules():
    st.title("Rules")
    st.write("Competition rules go here.")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Overview", "Data", "Submit", "Rules"))

    if page == "Overview":
        show_overview()
    elif page == "Data":
        show_data()
    elif page == "Submit":
        show_submit()
    elif page == "Rules":
        show_rules()

if __name__ == "__main__":
    main()
