import pandas as pd

questions_file = "data/questions.csv"


def print_question_summary(question):
    # Question_Date, Question_Type
    # Question_From
    # To
    # Question_To
    # Question_ID : Topic
    # Question_Contents
    print(f"Date: {question['date']},\t Type: {question['type']}")
    print(f"From: {question['from']}")
    print(f"To: {question['to']}")
    print(f"{question['id']} : {question['topic']}")
    print(f"{question['contents']}")


def prepare_df(questions_file):
    return pd.read_csv(questions_file)


def filter_by_topic(questions, topic):
    return questions[questions['topic'].str.contains(topic, case=False)]


def filter_by_question_from(questions, question_from):
    return questions[questions['from'].str.contains(question_from, case=False)]
