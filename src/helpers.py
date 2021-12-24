import textwrap

def pprint_question(question, width=80):
    if question.type=='STARRED':
        print(f"*Q.{question['id']}", end="")
    else:
        print(f"Q.{question['id']}", end="")
    print(question['date'].rjust(width, ' '))
    print(f"By: {question['from']}")
    print("")
    print(question['topic'].center(width, ' '))
    print("")
    contents = question['contents']
    contents = contents.replace('(a)','\n(a)').replace('(b)','\n(b)').replace('(c)','\n(c)').replace('(d)','\n(d)').replace('(e)','\n(e)').replace('(f)','\n(f)').replace('(g)','\n(g)').replace('(h)','\n(h)')
    contents_lines = contents.splitlines()
    for line in contents_lines:
        print(textwrap.fill(line, width=width))


def filter_by_topic(questions, topic):
    return questions[questions['topic'].str.contains(topic, case=False)]


def filter_by_question_from(questions, question_from):
    return questions[questions['from'].str.contains(question_from, case=False)]
