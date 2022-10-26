import streamlit as st
from bill import Bill


# with st.sidebar:
#     st.header("Our Mission")
#     st.write("With democracy being questioned everyday more and more here in the United States, it is essential that as many are involved with politics as possible.")
#
#     st.header("Bills")
#     st.write("What are bills?")
#
#     st.header("Resolutions")
#     st.write("What are resolutions?")
st.title("Welcome to Resolve")

search_number = st.number_input("Search by Bill Number", min_value = 0, max_value=10000, value=0)

st.write("OR Search by Most Recent")







col1, col2, col3 = st.columns(3)

with col1:
    congress = st.selectbox(
        'Select a Congress session',
        (range(117, 81, -1))
        )

    type_of_legislation = st.selectbox(
    'Select a type of bill',
    (item for key, item in Bill.types_of_legislation.items())
    )


with col2:
    limit = st.number_input("Results per page", min_value = 1, max_value = 250, value = 20)
    sort_by = st.selectbox(
        'Sort By',
        (key for key, item in Bill.types_of_sort.items())
    )


with col3:
    st.markdown("#")

    def previous_page_click(*, limit):
        st.session_state.offset -= limit

    previous_page = st.button("Previous Page", on_click=previous_page_click, kwargs={"limit": limit})

    st.markdown("#")

    def next_page_click(*, limit):
        st.session_state.offset += limit

    next_page = st.button("Next Page", on_click=next_page_click, kwargs={"limit": limit})









def renderRecent():
    if 'offset' not in st.session_state:
        st.session_state.offset = 0


    try:
        recentBills = Bill.recentBills(congress, Bill.types_of_legislation_display[type_of_legislation], limit = limit, offset = st.session_state.offset, sort=Bill.types_of_sort[sort_by])
    except Exception as error:
        st.error(error)
        st.stop()


    key1 = 0
    key2 = len(recentBills)
    key3 = len(recentBills) * 2

    for bill in recentBills:
        renderBill(bill, key1=key1, key2=key2, key3=key3)
        key1 += 1
        key2 += 1
        key3 += 1


def renderBill(bill, **kwargs):
    key1 = kwargs.get('key1')
    key2 = kwargs.get('key2')
    key3 = kwargs.get('key3')
    try:
        with st.expander(f"{bill.type.upper()} {bill.number}: {bill.title}"):

            tab1, tab2, tab3 = st.tabs(["Info", "Text", "Summary"])

            with tab1:

                spacing = "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;"

                if st.button("More Information", key=kwargs.get('key1')):
                    bill.getInfo()

                    st.markdown(f"Congress Session: **{bill.congress}**")

                    st.markdown(f"Number: **{bill.type.upper()} {bill.number}**")

                    st.markdown(f"Introduced on: **{bill.introducedDate}**")

                    st.markdown(f"Originated In: **{bill.originChamber}**")

                    st.markdown(f"Actions:")
                    actions = bill.getActions()
                    for action in actions:
                        st.markdown(f"{spacing}Date: **{action['actionDate']}**")
                        st.markdown(f"{spacing}**{action['type']}**: **{action['text']}**")
                        st.markdown("##")

                    st.markdown("Sponsors:")
                    for sponsor in bill.sponsors:
                        st.markdown(f"{spacing}{sponsor['fullName']}")

                else:
                    st.markdown(f"Congress Session: **{bill.congress}**")

                    st.markdown(f"Number: **{bill.type.upper()} {bill.number}**")




            with tab2:
                if st.button("Fetch Text", key=kwargs.get('key2')):
                    text = bill.getText()

                    if text:
                        section = []
                        header = []
                        subheader = []
                        textList = text.split()

                        for index in range(0, len(textList)):
                            word = textList[index]

                            if word.isupper() and (word.startswith("SECTION") or word.startswith("SEC.")):
                                if section:
                                    st.write(" ".join(section))
                                    section = []

                                header.append(word)

                                header.append(textList[index + 1])

                            elif word.isupper() and header:
                                subheader.append(word)

                            else:
                                if header:
                                    st.header(" ".join(header))
                                    header = []

                                elif subheader:
                                    st.subheader(" ".join(subheader))
                                    subheader = []

                                section.append(word)
                        st.write(" ".join(section))

                    else:
                        st.error("The text of this bill has not yet been made avaiable by Congress.")



            with tab3:
                if st.button("Summarize", key=kwargs.get('key3')):

                    summary, tuned = bill.generateSummary()

                    if not tuned:
                        st.info('Text was too large to be summarized with a fine-tuned model')

                    st.write(summary)


    except Exception as error:
        st.error(error)







if search_number == 0:
    renderRecent()
else:
    try:
        bill = Bill(congress, Bill.types_of_legislation_display[type_of_legislation], search_number)
    except Exception as error:
        st.error(error)

    bill.title = bill.getTitle()
    renderBill(bill)
