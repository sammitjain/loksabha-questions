import re
import pandas as pd
from py_pdf_parser.loaders import load_file
from thefuzz import process, fuzz
import pickle
import copy
from py_pdf_parser.visualise import visualise


def column_ordering_function(elements):
    """
    This function helps account for the ordering of text on the PDF.
    The first entry in the key is False for column 1, and True for column 2.
    The second and third keys just give left to right, top to bottom.
    """
    return sorted(elements, key=lambda elem: (elem.x0 > 300, -elem.y0, elem.x0))


def get_text(element_list):
    """
    Given a list of PDF elements, this function concatenates all the elements
    in sequence and outputs a string"
    """
    return " ".join(e.text() for e in element_list)


def clean_body_text(text):
    """
    Parsed question body text often needs to be cleaned. So far I'm removing
    footers, unnecessary metadata, non-ascii characters, newline characters,
    extra spaces and information that may not necessarily be a part of the
    body of the question
    """
    text = re.sub("_+", " ", text)          # remove footer line
    text = re.sub(" .*Hindi", " ", text)    # remove language notice text
    text = text.encode("ascii", "ignore").decode()  # remove non-ascii characters
    text = re.sub(r"\n", r" ", text)        # remove new-lines
    text = re.sub(" +", " ", text)  # remove extra spaces
    text = re.sub(r".*?(Will\s+)", r"\1", text, flags=re.DOTALL, count=1)
    return text


def identify_question_from(qc, question_topic):
    question_will_the = identify_will_the(qc)
    text = get_text(qc.before(question_will_the, inclusive=True))   # inclusive because of Issue: 01122021
    text = re.sub('\.', ' ', text)
    text = re.sub('(Will\s+the.*)|(\d{4})','',text)
    text = re.sub(question_topic, " ", text).strip()    # Remove topic leaks, Issue: 14122021 Lithium
    candidates = text.split(':')
    question_from = []
    for c in candidates:
        asking_member = re.search('([A-Za-z\(\) ]+)', c)
        if asking_member:
            asking_member_text = asking_member.group().strip()
            if asking_member_text:
                question_from.append(asking_member_text)
    return question_from


def identify_question_id(qc):
    question_id = re.search('\D*(\d+)\.', qc[0].text())
    if question_id is None:
        question_id = re.search('\D*(\d+)\.', qc[1].text()).groups()[0]
    else:
        question_id = question_id.groups()[0]
    return int(question_id)


def identify_question_to(qc):
    question_will_the = identify_will_the(qc)
    question_state = identify_pleased_to_state(qc)
    text = get_text(qc.after(question_will_the, inclusive=True).before(question_state, inclusive=True))
    # clean text to remove any text before will the                             # Issue: 01122021
    text = re.sub(r".*Will\s+the\s+", "", text, flags=re.DOTALL)
    question_to = re.search('([A-Z][A-Z ,]+)', text)
    if question_to is None:
        text = text.encode("ascii", "ignore").decode()
        question_to = re.search("Minister\s+of\s+(.*)\n", text).groups()[0]
    else:
        question_to = question_to.groups()[0]
    question_to = question_to.strip().replace(' ,', '')
    question_to = re.sub(r' +', ' ', question_to)
    return question_to.strip().replace(' ,', '')


def identify_question_body(qc):
    question_body = get_text(qc.after(identify_will_the(qc), inclusive=True))
    return clean_body_text(question_body)


def identify_question_date(question_session):
    dd = question_session[:2]
    mm = question_session[2:4]
    yyyy = question_session[4:8]
    return dd + "." + mm + "." + yyyy


def identify_question_topic(question_topic):
    return question_topic.replace("\n", " ").replace("\\", "").strip()


def identify_will_the(qc):
    """
    Identifies the section of the question that typically starts with "Will the"
    """
    question_will_the = qc.filter_by_regex("Will\s+the\s+Minister\s+of")
    if len(question_will_the) == 0:
        question_will_the = qc.filter_by_regex("Will\s+the\s+")
    if len(question_will_the) == 0:
        question_will_the = qc.filter_by_text_contains("Will the")
    if len(question_will_the) == 0:
        question_will_the = qc.filter_by_text_contains("Will  the")
    if len(question_will_the) == 0:
        question_will_the = qc.filter_by_regex("Will")
    return question_will_the[0]


def identify_pleased_to_state(qc):
    question_state = qc.filter_by_text_contains("pleased to state")
    if len(question_state) == 0:
        question_state = qc.filter_by_text_contains("state:")
    if len(question_state) == 0:
        question_state = qc.filter_by_text_contains("pleased  to  state")
    if len(question_state) == 0:
        question_state = qc.filter_by_text_contains("pleased  to state")    # Issue: Q4088
    if len(question_state) == 0:
        question_state = qc.before(qc.filter_by_text_contains("(a)")[0]).after(identify_will_the(qc))
    return question_state[0]


def print_element_list(element_list):
    for element in element_list:
        print(element.text())


def resolve_topics(question_contents, question_topics):
    # Issue found in Q.113 (29112021) and Q.2613 (14122021)
    # identify malformed questions: questions with more than <threshold> elements
    threshold = 17
    malformed_idx = []
    for idx, qc in enumerate(question_contents):
        if len(qc) > threshold:
            malformed_idx.append(idx)

    bad_idx = []
    resolved = False
    for idx in malformed_idx:
        if not resolved:
            qc = question_contents[idx]
            q_id_1 = identify_question_id(qc)
            q_id_2 = str(q_id_1+1)
            qid2 = qc.filter_by_text_contains(q_id_2).extract_single_element()
            print("Malformed topic located!")
            qc1 = qc.before(qid2)
            qc2 = qc.after(qid2, inclusive=True)
            qc2_topic = get_text(qc2).split('\n')[0]
            qc2_topic = qc2_topic.replace(q_id_2+'.', "").strip()
            bad_idx = idx
            question_contents = question_contents[:bad_idx] + [qc1] + [qc2] + question_contents[bad_idx + 1:]
            question_topics = question_topics[:bad_idx + 1] + [qc2_topic] + question_topics[bad_idx + 1:]
            print("Resolved successfully")
            resolved = True

    return question_contents, question_topics


def collect_questions(question_elements, question_session, question_type):
    # Gather Question Topics
    question_topics_e = question_elements.after(question_elements.filter_by_regex('Total\s+Number').extract_single_element()).filter_by_font('CIDFont+F1,10.0')
    question_topics = []
    bad_topics = []
    # Use Topics to segregate all Question Contents
    question_contents = []
    for i in range(len(question_topics_e) - 1):
        qc = question_elements.after(question_topics_e[i]).before(question_topics_e[i + 1])
        if len(qc) == 0:
            bad_topics.append(i)
        else:
            question_topics.append(question_topics_e[i].text())
            question_contents.append(qc)

    # Collect final Topic till end of page after last topic
    question_contents.append(question_elements.after(question_topics_e[-1]))
    question_topics.append(question_topics_e[-1].text())

    # Clean bad topics
    for i, bt in enumerate(bad_topics):
        question_topics[bt-i] = question_topics_e[bt].text() + " " + question_topics[bt-i]

    # Validate number of questions          # First found in 14122021 - Lithium
    if (question_type == 'STARRED' and len(question_topics) == 20) or (question_type == 'UNSTARRED' and len(question_topics) == 230):
        print(f"Valid number of {question_type} questions")
    else:
        print("Possible mismatch in topics. Resolving...")
        question_contents, question_topics = resolve_topics(question_contents, question_topics)

    questions = []

    for idx, qc in enumerate(question_contents):
        question_topic = identify_question_topic(question_topics[idx])
        question_id = identify_question_id(qc)
        question_dict = {'id': question_id,
                         'topic': question_topic,
                         'from': identify_question_from(qc, question_topic),        # Check for topic leaks
                         'to': identify_question_to(qc),
                         'contents': identify_question_body(qc),
                         'date': identify_question_date(question_session),
                         'type': question_type}
        questions.append(question_dict)
        print(f"{idx}: {question_dict['id']}, {question_dict['topic']}")
        idx += 1
    return questions


def identify_indexes(document):
    index_elements = document.elements.filter_by_text_contains("INDEX")
    if len(index_elements) == 2:
        starred_index = index_elements[0].page_number
        unstarred_index = index_elements[1].page_number
    else:
        raise ValueError("Parse failed due to malformed indexes")
    return starred_index, unstarred_index


def identify_starred_unstarred_range(document):
    start_candidates = document.elements.filter_by_regex("Total\s+Number\s+of\s+Questions")
    index_candidates = document.elements.filter_by_text_contains("INDEX")
    corrigendum_elements = document.elements.filter_by_text_contains("CORRIGENDUM")
    corrigenda_elements = document.elements.filter_by_text_contains("CORRIGENDA")

    start_pages = [e.page_number for e in start_candidates]
    index_pages = [e.page_number for e in index_candidates]
    corrigendum_pages = [e.page_number for e in corrigendum_elements]
    corrigenda_pages = [e.page_number for e in corrigenda_elements]
    correction_pages = corrigenda_pages + corrigendum_pages

    # Remove correction pages from end page candidates
    for c in correction_pages:
        if c in index_pages:
            index_pages.remove(c)

    if len(start_pages) != 2 or len(index_pages) != 2:
        raise ValueError("Malformed Document Index")
    starred_start = start_pages[0]
    starred_index = index_pages[0]

    unstarred_start = start_pages[1]
    unstarred_index = index_pages[1]

    return range(starred_start, starred_index), range(unstarred_start, unstarred_index)


def parse_pdf_questions(session_date):
    questions = []
    path_to_questions_pdf = f"../data/loksabha-questions/{session_date}.pdf"
    document = load_file(path_to_questions_pdf, element_ordering=column_ordering_function)

    # starred_index, unstarred_index = identify_indexes(document)
    starred_pages, unstarred_pages = identify_starred_unstarred_range(document)
    starred_question_elements = document.elements.filter_by_pages(*starred_pages)
    starred_questions = collect_questions(starred_question_elements,
                                          question_session=session_date, question_type='STARRED')

    unstarred_question_elements = document.elements.filter_by_pages(*unstarred_pages)
    unstarred_questions = collect_questions(unstarred_question_elements,
                                            question_session=session_date, question_type='UNSTARRED')

    questions = starred_questions + unstarred_questions
    return questions


def augment_member_data(questions):
    members_list_curated_file = "../data/loksabha_members_curated.p"
    f = open(members_list_curated_file, 'rb')
    members_list_curated = pickle.load(f)
    f.close()

    fuzzy_choices = [member[0] for member in members_list_curated]

    members_list_fuzzy_file = "../data/loksabha_members_fuzzy.p"
    f = open(members_list_fuzzy_file, 'rb')
    members_fuzzy_dict = pickle.load(f)
    f.close()

    members_info_dict_file = "../data/member_info_lookup.p"
    f = open(members_info_dict_file, 'rb')
    members_info_dict = pickle.load(f)
    f.close()

    i = 0
    for question_idx, question in enumerate(questions):
        members = []
        member_constituency = []
        member_party = []
        member_state = []
        member_constituency_type = []
        for member_idx, member in enumerate(question['from']):
            compressed_member = "".join(member.split())
            if compressed_member in members_fuzzy_dict:
                # print(f"Found: {compressed_member :<35} -> {members_fuzzy_dict[compressed_member]}")
                lookedup_member = members_fuzzy_dict[compressed_member]
                if lookedup_member:     # Ignore stop-members
                    member_name = members_fuzzy_dict[compressed_member]
                    members.append(member_name)
                    member_party.append(members_info_dict[member_name][0])
                    member_constituency.append(members_info_dict[member_name][1])
                    member_state.append(members_info_dict[member_name][2])
                    member_constituency_type.append(members_info_dict[member_name][3])
            else:
                mapped_member = process.extractOne(member, fuzzy_choices, scorer=fuzz.token_set_ratio)
                if mapped_member[1] > 50:
                    members_fuzzy_dict[compressed_member] = mapped_member[0]
                    member_name = mapped_member[0]
                    members.append(member_name)
                    member_party.append(members_info_dict[member_name][0])
                    member_constituency.append(members_info_dict[member_name][1])
                    member_state.append(members_info_dict[member_name][2])
                    member_constituency_type.append(members_info_dict[member_name][3])
                else:
                    print(f"Dropped: {member :>35} - > {mapped_member}")
        questions[question_idx]['from'] = members
        questions[question_idx]['party'] = member_party
        questions[question_idx]['state'] = member_state
        questions[question_idx]['constituency'] = member_constituency
        questions[question_idx]['constituency_type'] = member_constituency_type

    return questions, members_fuzzy_dict


def clean_ministry_info(questions):
    ministries_cleanup_dict = {'MICRO,SMALL AND MEDIUM ENTERPRISES': 'MICRO, SMALL AND MEDIUM ENTERPRISES',
                               'Communications': 'COMMUNICATIONS',
                               'ROAD TRANSPORT AND HIGH': 'ROAD TRANSPORT AND HIGHWAYS'}
    for idx, question in enumerate(questions):
        if question['to'] in ministries_cleanup_dict:
            questions[idx]['to'] = ministries_cleanup_dict[question['to']]
    return questions


def flatten_questions(questions):
    flattened_questions = []
    for question in questions:
        for idx, member in enumerate(question['from']):
            question_copy = copy.deepcopy(question)
            question_copy['from'] = member
            question_copy['party'] = question['party'][idx]
            question_copy['state'] = question['state'][idx]
            question_copy['constituency'] = question['constituency'][idx]
            question_copy['constituency_type'] = question['constituency_type'][idx]
            flattened_questions.append(question_copy)
    return flattened_questions


def finalize_datasets(questions_raw):
    questions = clean_ministry_info(questions_raw)
    questions, members_fuzzy_dict = augment_member_data(questions)
    questions_df = pd.DataFrame(questions)
    questions_df['date'] = pd.to_datetime(questions_df['date'], format="%d.%m.%Y")
    questions_flattened = flatten_questions(questions)
    questions_flattened_df = pd.DataFrame(questions_flattened)
    questions_flattened_df['date'] = pd.to_datetime(questions_flattened_df['date'], format="%d.%m.%Y")
    return questions_df, questions_flattened_df


if __name__ == '__main__':
    questions_raw = []
    session_dates = ["29112021", "30112021", "01122021", "02122021", "03122021",
                     "06122021", "07122021", "08122021", "09122021", "10122021",
                     "13122021", "14122021", "15122021", "16122021", "17122021",
                     "20122021", "21122021", "22122021", "23122021"]

    for date in session_dates:
        questions_raw += parse_pdf_questions(date)
    raw_questions = questions_raw
    q_df, q_f_df = finalize_datasets(questions_raw)

