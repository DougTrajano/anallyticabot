import streamlit as st
from src.helper_functions import setup_logger
from src.intents.utterance_generator import UtteranceGenerator

logger = setup_logger()


def utterances_gen_page(state):
    logger.info({"message": "Loading utterances_gen_page."})
    st.title("Utterance generator")
    st.markdown("""
    For any chatbot to be more useful to the end-user training plays an important role in making it more efficient. As you probably know, chatbots learn from varied grammatical samples.

    To help you to find valuable utterances we introducing our utterance generator based on [OpenAI](https://openai.com/) [GPT-3](https://openai.com/gpt-3/).""")

    # OpenAI key not set
    if not isinstance(state.openai, dict) or state.openai.get("apikey") in [None, ""]:
        st.markdown(
            "You need to set your [OpenAI](https://openai.com/) key on the settings page before using the utterance generator.")
        st.stop()

    with st.expander("OpenAI Settings"):
        st.warning("Be careful editing these settings. We have defined these to make the utterance generator more robust and more efficient. However, if you want to try out the utterance generator, you can change these settings.")

        c1, c2 = st.columns(2)
        
        state.openai["engine"] = c1.selectbox(label="Engine",
                                              options=["davinci", "curie", "babbage", "ada"],
                                              help="The engine to use for the API request. These engines provides a spectrum of capability, where davinci is the most capable and ada is the fastest.")
        
        state.openai["temp"] = c2.slider(label="Temperature",
                                         min_value=0.1, max_value=1.0, value=0.7,
                                         help="Controls randomness: Lowering results in less random completions. As the temperature approaches zero, the model will become deterministic and repetitive.")
        
        state.openai["max_tokens"] = c1.slider(label="Max tokens",
                                               min_value=1, max_value=2048, value=32,
                                               help="The maximum number of tokens to generate. Requests can use up to 2048 tokens shared between prompt and completion. (One token is roughly 4 characters for normal English text).")
        
        state.openai["top_p"] = c2.slider(label="Top P",
                                          min_value=0.1, max_value=1.0, value=1.0,
                                          help="Controls diversity via nucleus sampling: 0.5 means half of all likelihood-weighted options are considered.")
        
        state.openai["freq_p"] = c1.slider(label="Frequency penalty",
                                           min_value=0.1, max_value=1.0, value=0.2,
                                           help="How much to penalize new tokens based on their existing frequency in the text so far. Decreases the model's likelihood to repeat the same line verbatim.")
        
        state.openai["pres_p"] = c2.slider(label="Presence penalty",
                                           min_value=0.1, max_value=1.0, value=0.2,
                                           help="How much to penalize new tokens based on whether they appear in the text so far. Increases the model's likelihood to talk about new topics.")

    utt_gen = UtteranceGenerator(openai_api_key=state.openai.get("apikey"),
                                 engine=state.openai.get("engine"),
                                 temperature=state.openai.get("temp"),
                                 max_tokens=state.openai.get("max_tokens"),
                                 top_p=state.openai.get("top_p"),
                                 frequency_penalty=state.openai.get("freq_p"),
                                 presence_penalty=state.openai.get("pres_p"))

    with st.form("Sample utterances"):

        c1, c2 = st.columns(2)
        utts_qty = c1.number_input(label="Number of utterances to generate",
                                   min_value=1,
                                   max_value=100,
                                   value=10,
                                   help="The quantity of new generated utterances.")

        utts_increment = c1.checkbox(label="Increment with new utterances",
                                     value=True,
                                     help="Increment API calls with previously generated utterances.")

        utts_samples = st.text_area(label="Sample utterances", height=300,
                                    help="Please, give some sample utterances, each per line")

        submit_button = st.form_submit_button("Submit")

    if submit_button:
        with st.spinner("Calling GPT-3"):
            new_utts = utt_gen.generate(utts_samples, utts_qty, utts_increment)

        st.subheader("Generated utterances")

        for utt in new_utts:
            st.text(utt)

    state.sync()
