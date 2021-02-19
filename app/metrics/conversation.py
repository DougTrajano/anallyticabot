import logging
import datetime
import streamlit as st

def conversation_metrics_page(state):
    logging.info({"message": "Loading Metrics - Conversations page."})
    st.title(":bar_chart: Metrics - Conversations")

    st.markdown("""
    In this page you can generate conversation-based metrics for your Watson Assistant.

    You need to select a date range to get logs.
    """)

    st.subheader("Parameters")
    col1, col2 = st.beta_columns(2)

    args = {}

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7)

    args['logs_date'] = col1.date_input('Logs date', value=(start_date, end_date))
    args['Date'] = col1.selectbox('Datetime variable', ('request_timestamp', 'response_timestamp'))    
    args['Sessions'] = col2.text_input('Conversation id', value='response.context.conversation_id')
    args['Active users'] = col2.text_input('User variable', value='response.context.global.system.user_id')

    if st.button("Get logs"):
        with st.spinner("Getting logs..."):
            from src.metrics.conversation import logs_to_dataframe
            from src.connectors.watson_assistant import WatsonAssistant
            wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                                    service_endpoint=state.watson_args["endpoint"],
                                    default_skill_id=state.watson_args["skill_id"])
            
            query_logs = wa.define_query_by_date(args['logs_date'][0], args['logs_date'][1])
            logs = wa.get_logs(query=query_logs)
            state.logs = logs_to_dataframe(logs, args['Date'])

    if state.logs is not None:
        from src.metrics.conversation import get_metrics, gen_plotly_datetime
        
        df_logs = state.logs
        
        metrics = get_metrics(df_logs, args)

        col1, col2, col3, col4 = st.beta_columns(4)
        
        col1.write("# {}".format(metrics["sessions_count"]))
        col1.write("Sessions count")
        
        col2.write("# {}".format(metrics["messages_count"]))
        col2.write("Msgs count")
        
        col3.write("# {}".format(metrics["avg_messages"]))
        col3.write("Avg. msgs per session")

        col4.write("# {}".format(metrics["active_users"]))
        col4.write("Active Users")

        # Plotly Datetime per day
        fig_date_options = list(args.keys())
        fig_date_options = [e for e in fig_date_options if e not in ['logs_date', 'Date']]
        fig_date_option = st.selectbox('Options', fig_date_options)
        fig_date = gen_plotly_datetime(df_logs, args, fig_date_option)
        st.plotly_chart(fig_date, use_container_width=True)

    state.sync()