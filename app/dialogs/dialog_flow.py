import streamlit as st
import datetime

def dialogflow_page(state):
    st.title("Dialog Flow")

    col1, col2 = st.beta_columns(2)
    col1.markdown("""
    The dialog flow visualization is an interactive tool for investigating user journeys, visits and abandonments within the steps of the dialog system.

    The visualization aggregates the temporal sequences of steps from Watson Assistant logs. The interaction allows to explore the distribution of visits across dialog steps and where abandonment takes place, and select the conversations that visit a certain step for further exploration and analysis.
    """)

    col2.image("https://camo.githubusercontent.com/0a581e6915e997c46ea7ccde0e94c380a3d8717e/68747470733a2f2f7261772e67697468756275736572636f6e74656e742e636f6d2f776174736f6e2d646576656c6f7065722d636c6f75642f617373697374616e742d6469616c6f672d666c6f772d616e616c797369732f6d61737465722f6e6f7465626f6f6b732f696d616765732f7475726e2d666c6f772e706e67")

    config = {"mode": "turn-based"}

    if len(state.watson_args.get('skill_name')) > 0:
        title_default = state.watson_args["skill_name"]
    else:
        title_default = 'Dialog Session'

    config['title'] = st.text_input('Title', value=title_default)

    config['commonRootPathName'] = config['title']
    config['maxChildrenInNode'] = st.number_input(
        'Max children in node', value=6)
    config['sortByAttribute'] = st.selectbox('Sort by attribute', options=(
        'flowRatio', 'dropped_offRatio', 'flows', 'dropped_off', 'rerouted'))
            
    with st.beta_expander('Advanced Settings'):
        config['nodeWidth'] = st.number_input('Node width', value=250)
        config['linkWidth'] = st.number_input('Link width', value=400)

        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=7)
        logs_date = st.date_input('Logs date', value=(start_date, end_date))
        
    if st.button("Generate report"):
        from src.dialogs.dialog_flow import prepare_data, generate_html_report
        from src.connectors.watson_assistant import WatsonAssistant
        from app.helper_functions import download_link

        wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                             service_endpoint=state.watson_args["endpoint"],
                             default_skill_id=state.watson_args["skill_id"])
        
        workspace = wa.get_workspace()

        query_logs = wa.define_query_by_date(logs_date[0], logs_date[1])
        logs = wa.get_logs(query=query_logs)

        skill_id = state.watson_args["skill_id"]
        
        data = prepare_data(logs, skill_id, workspace)
        html_report = generate_html_report(config, data)

        result = download_link(html_report, 'dialog_flow.html', 'Download Dialog Flow report')
        st.markdown(result, unsafe_allow_html=True)

    state.sync()
