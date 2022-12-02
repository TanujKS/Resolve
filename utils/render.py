import sys
sys.path.insert(0, "..")
import streamlit as st
import traceback
from bill import Bill
from utils import exceptions

def writeSections(sections: dict):
    for key, item in sections.items():
        if key != "intro":
            st.header(key)

        subheader = item.get('subheader')
        if subheader:
            st.subheader(subheader)

        st.write(item.get('text'))


def renderBills(bills):
    if 'offset' not in st.session_state:
        st.session_state.offset = 0


    key1 = 0
    key2 = len(bills) * (2**0)
    key3 = len(bills) * (2**1)
    key4 = len(bills) * (2**2)
    key5 = len(bills) * (2**3)

    for bill in bills:
        renderBill(bill, key1=key1, key2=key2, key3=key3, key4=key4, key5=key5)
        key1 += 1
        key2 += 1
        key3 += 1
        key4 += 1
        key5 += 1


def renderBill(bill, **kwargs):
    if not getattr(bill, "title", None):
        bill.title = bill.getTitle()

    if not getattr(st.session_state, f'{bill.type}_{str(bill.number)}', False):
        st.session_state[f"{bill.type}_{str(bill.number)}"] = {
        "feedback_received": False,
        }

    key1 = kwargs.get('key1')
    key2 = kwargs.get('key2')
    key3 = kwargs.get('key3')
    key4 = kwargs.get('key4')
    key5 = kwargs.get('key5')

    try:
        with st.expander(f"{bill.type.upper()} {bill.number}: {bill.title}"):

            tab1, tab2, tab3, tab4 = st.tabs(["Info", "Text", "Summary", "Brief"])

            with tab1:

                spacing = "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;"

                if st.button("More Information", key=key1):
                    bill.getInfo()

                    st.markdown(f"**Congress Session:** {bill.congress}")

                    st.markdown(f"**Number:** {bill.type.upper()} {bill.number}")

                    actions = bill.getActions()
                    action = actions[0]
                    st.markdown(f"**Latest Action:** {action['actionDate']} {action['type']}: {action['text']}")


                    st.markdown(f"**Introduced on:** {bill.introducedDate}")

                    st.markdown(f"**Originated In:** {bill.originChamber}")

                    st.markdown("**Sponsors:**")
                    for sponsor in bill.sponsors:
                        st.markdown(f"{spacing}{sponsor['fullName']}")

                    #st.markdown(f"Summary: {bill.getSummary()}")

                    st.markdown("#")

                    st.markdown("**Also known as:**")
                    titles = bill.getTitles()
                    titles.remove(bill.title)
                    for title in titles:
                        st.markdown(f"{spacing}{title}")

                    st.markdown("#")
                    st.markdown("#")

                    st.markdown("**Actions:**")
                    for action in actions:
                        st.markdown(f"{spacing}{action['actionDate']} {action['type']}: {action['text']}")
                        st.markdown("#")




                else:
                    st.markdown(f"**Congress Session**: {bill.congress}")

                    st.markdown(f"**Number:** {bill.type.upper()} {bill.number}")

                    search_score = getattr(bill, 'search_score', False)
                    if search_score:
                        st.markdown(f"**Search Confidence:** {search_score}")

                    relevancy_score = getattr(bill, 'relevancy_score', False)
                    if relevancy_score:
                        st.markdown(f"**Relevancy Score:** {relevancy_score}")

                    action = getattr(bill, 'latestAction', None)
                    if action:
                        st.markdown(f"**Latest Action:** {action['actionDate']}: {action['text']}")


            with tab2:
                if st.button("Fetch Text", key=key2):
                    sections = bill.getSections()

                    if not sections:
                        st.error("The text of this bill has not yet been made available by Congress.")

                    writeSections(sections)


            with tab3:
                #user_data = getattr(st.session_state, str(bill.number), None)
                user_data = st.session_state[f"{bill.type}_{str(bill.number)}"]

                summarized = user_data.get('feedback_received', False)
                summarized_section = getattr(st.session_state, f"{bill.type}_{str(bill.number)}_section", None)

                summarize_button = st.button("Summarize", key=key3)

                if summarize_button:
                    st.session_state[f"{bill.type}_{str(bill.number)}"]['feedback_received'] = False

                    try:
                        summary = bill.generateSummary()

                        st.write(summary)

                        def good_summary_click(bill, completion):

                            data = {
                            "prompt": bill.getText(),
                            "completion": completion
                            }

                            with open("congress_data/human_feedback.jsonl", "a") as file:
                                file.write("\n")
                                file.write(json.dumps(data))

                            number = str(bill.number)
                            st.session_state[f"{bill.type}_{str(bill.number)}"]['feedback_received'] = True
                            #st.session_state[number]['feedback_received'] = True

                        st.button("I Like This!", on_click=good_summary_click, args=(bill, summary), key=key4)

                    except exceptions.TextTooLarge:
                        st.write("Bill is too large to summarize entirely, please select a section to summarize instead")

                        section = st.selectbox(
                            'Select a section too summarize',
                            (content.get('subheader', section) for section, content in bill.getSections().items()),
                            key=f"{bill.type}_{str(bill.number)}_section"
                            )

                        #st.session_state[str(bill.number)]['summarized_section'] = section

                if summarized:
                    st.subheader("Thanks for your feedback!")

                if summarized_section:
                    st.write(summarized_section)

                    st.markdown("#")

                    sections = bill.getSections()
                    section = bill.getSectionFromSubheader(summarized_section, sections=sections)

                    if not section:
                        raise exceptions.SectionNotAvailable("Section is not available or has been redacted.")

                    st.write(bill.generateSummary(text=sections[section]['text']))

            with tab4:
                briefed_section = getattr(st.session_state, f"{bill.type}_{str(bill.number)}_brief", None)

                brief_button = st.button("Get Brief", key=key5)

                if brief_button:

                    try:
                        key_points = bill.generateBrief()

                        for point in key_points:
                            st.write(point)
                    except exceptions.TextTooLarge:
                        st.write("Bill is too large to brief entirely, please select a section to brief instead")

                        brief = st.selectbox(
                        "Select a section too brief",
                        (content.get('subheader', section) for section, content in bill.getSections().items()),
                        key=f"{bill.type}_{str(bill.number)}_brief"
                        )



                if briefed_section:
                    st.write(briefed_section)
                    st.markdown("#")

                    sections = bill.getSections()
                    section = bill.getSectionFromSubheader(briefed_section, sections=sections)
                    if not section:
                        raise exceptions.SectionNotAvailable("Section is not available or has been redacted.")

                    key_points = bill.generateBrief(text=sections[section]['text'])

                    for point in key_points:
                        st.write(point)

    except Exception as error:
        st.error(error)
        traceback.print_exc()
