import os
from glob import glob
import datetime
import pandas as pd
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
    st.write("Data Description goes here.")

    st.write("### Download Data")
    st.write("You can download the files here:")

    # Display the download buttons
    st.download_button(
        label="Download train.csv",
        data=open("./src/train.csv", "rb"),
        file_name="train.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Download test.csv",
        data=open("./src/test.csv", "rb"),
        file_name="test.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Download sample-submission.csv",
        data=open("./src/sample-submission.csv", "rb"),
        file_name="sample-submission.csv",
        mime="text/csv"
    )


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
            # ファイルの保存先ディレクトリ
            upload_dir = "submits/"
            t_delta = datetime.timedelta(hours=9)
            JST = datetime.timezone(t_delta, 'JST')
            now = datetime.datetime.now(JST)
            # ファイルの保存
            os.makedirs(os.path.join(upload_dir, username), exist_ok=True)
            with open(os.path.join(upload_dir, f"{username}/{now.strftime('%Y%m%d%H%M%S')}-{uploaded_file.name}"), "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 提出処理を行う場合のコードをここに記述
            st.success("Your submission was successful!")
            # リーダーボードにリダイレクトしてほしいがStreamlitではリダイレクトができない
        else:
            st.error("Please fill in all the fields.")


def show_rules():
    st.title("Rules")
    st.write("Competition rules go here.")


def calc_score(true_df, submit_df):    
    # 両方のデータフレームが同じ形式か確認
    if not all(true_df.columns == submit_df.columns):
        raise ValueError("Both CSV files must have the same columns.")
    
    # Survivedカラムの値を比較し、一致する数を計算
    num_correct = sum(true_df['Survived'] == submit_df['Survived'])
    total = len(true_df)
    
    # 精度を計算
    accuracy = num_correct / total
    return accuracy


def make_leaderboard():
    submission_files = glob("submits/**/*.csv")
    true_df = pd.read_csv("./src/truth.csv")
    scoredict = dict()
    for submit_file in submission_files:
        submit_df = pd.read_csv(submit_file)
        score = calc_score(true_df, submit_df)
        username = os.path.basename(os.path.dirname(submit_file))
        scoredict[username] = max(score, scoredict.get(username, -9999))
    leaderboard_df = pd.DataFrame(scoredict.items(), columns=["Username", "Score"])
    leaderboard_df.to_csv("./src/leaderboard.csv", index=False)


def show_leaderboard():
    st.title("Leaderboard")
    make_leaderboard()
    leaderboard_df = pd.read_csv("./src/leaderboard.csv")
    st.write(leaderboard_df)


def main():
    st.sidebar.title("Grani Competition")
    page = st.sidebar.radio("Go to", ("Overview", "Data", "Submit", "Rules", "Leaderboard"))

    if page == "Overview":
        show_overview()
    elif page == "Data":
        show_data()
    elif page == "Submit":
        show_submit()
    elif page == "Rules":
        show_rules()
    elif page == "Leaderboard":
        show_leaderboard()

if __name__ == "__main__":
    main()
