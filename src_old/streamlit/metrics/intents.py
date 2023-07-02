import streamlit as st
import logging
import datetime

def intents_metrics_page(state):
    logging.info({"message": "Loading Metrics - Intents page."})
    st.title(":bar_chart: Metrics - Intents")
    st.markdown("""
    In this page you can generate intents-based metrics for your Watson Assistant.

    You need to select a date range to get logs.
    """)
    args = {}

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7)

    st.subheader("Parameters")
    col1, col2 = st.beta_columns(2)
    args['logs_date'] = col1.date_input('Logs date', value=(start_date, end_date))
    args['Date'] = col2.selectbox('Datetime variable', ('request_timestamp', 'response_timestamp'))

    args['threshold'] = st.slider('Threshold', min_value=0.01, max_value=1.0, value=(0.6, 1.0), step=0.01)

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
        from src.metrics.intents import gen_plotly_intents, filter_df
        df_logs = state.logs

        try:
            # Filter intents
            columns = [col for col in df_logs.columns if 'response.intents' in col]
            columns = columns + ['Date', 'request.input.text']
            main_intent = 'response.intents.0.intent'
            df_logs = df_logs[df_logs[main_intent].notnull()]
            df_logs = df_logs[columns]

            # Top 20 intents
            fig = gen_plotly_intents(df_logs, args["threshold"])
            st.plotly_chart(fig, use_container_width=True)
        except Exception as error:
            logging.error({"message": "Failed to generate graph.", "exception": error})
            st.error("Failed to generate graph.")

        # Intents export
        df_intents = filter_df(df_logs, args["threshold"])
        for intent in df_intents["intent"].unique():
            try:
                with st.expander(intent):
                    for row in df_intents[df_intents["intent"] == intent].to_dict(orient="records"):
                        c1, c2 = st.columns(2)
                        c1.text(row["input"])
                        c2.text(row["confidence"])
            except Exception as error:
                logging.error({"message": "Failed to generate export.", "exception": error})
                st.error("Failed to generate export.")

    state.sync()