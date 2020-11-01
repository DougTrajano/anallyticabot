import pandas as pd
import streamlit as st
from app.helper_functions import *


def irrelevant_examples_page(state):
    st.title("Counter examples")
    st.markdown("""
    Os contra-exemplos (*counter examples*) no Watson Assistant são usados sempre que queremos evitar responder uma mensagem indesejada.

    Dentro do Watson Assistant não é possível acessar quais exemplos foram cadastrados como contra-exemplo.

    Por isso, disponibilizamos aqui essa página para você gerenciar isto.
    """)

    if not check_watson(state):
        not_connected_page(state)
    else:
        from src.connectors.watson_assistant import WatsonAssistant
        wa = WatsonAssistant(apikey=state.watson_args["apikey"],
                                service_endpoint=state.watson_args["endpoint"],
                                default_skill_id=state.watson_args["skill_id"])

        # Add new counter example
        counter_example = st.text_input("Novo exemplo irrelevante")

        if st.button("Cadastrar"):
            response = wa.add_counterexamples(counter_example)
            if response["success"]:
                st.success("Exemplo irrelevante adicionado.")
            else:
                st.error("Ops! Falha ao adicionar o exemplo irrelevante.")

        # Getting counter examples
        counter_examples = wa.get_counterexamples()
        counter_examples = counter_examples["counterexamples"]

        if len(counter_examples) > 0:
            col1, col2 = st.beta_columns(2)
            col1.header("Exemplos irrelevantes")
            col2.header("Ações")

            for i in range(len(counter_examples)):
                ckey = "counter_examples_{}".format(i)
                col1.write(counter_examples[i])
                cbutton = col2.button("Deletar", key=ckey)
                if cbutton:
                    pos = int(ckey.split("_")[-1])
                    response = wa.delete_counterexamples(counter_examples[pos])
                    if response["success"]:
                        st.success("Exemplo irrelevante deletado.")
                    else:
                        st.error("Falha ao deletar exemplo irrelevante.")

        else:
            st.markdown("Não encontramos exemplos irrelevantes treinados nessa skill do Watson Assistant.")