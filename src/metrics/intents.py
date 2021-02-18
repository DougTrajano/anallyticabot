import logging
import plotly_express as px


def gen_plotly_intents(df, threshold=(0.6, 1.0)):
    df_temp = df[["response.intents.0.intent",
                  "response.intents.0.confidence"]]
    df_temp.columns = ["intent", "confidence"]
    df_temp = df_temp[(df_temp["confidence"] >= threshold[0]) & (df_temp["confidence"] <= threshold[1])]
    
    df_temp = df_temp.groupby("intent").count().sort_values(by="confidence")
    df_temp.reset_index(inplace=True)
    df_temp.columns = ["intent", "quantity"]
    df_temp = df_temp.head(20)
    return px.bar(df_temp, x="quantity", y="intent",
                  title="Top 20 intents", height=600)

def filter_df(df, threshold=(0.6, 1.0)):
    df_temp = df[["response.intents.0.intent", "response.intents.0.confidence", "request.input.text", "Date"]]
    df_temp.columns = ["intent", "confidence", "input", "date"]
    df_temp = df_temp[(df_temp["confidence"] >= threshold[0]) & (df_temp["confidence"] <= threshold[1])]
    df_temp.sort_values(by="confidence", inplace=True, ascending=False)
    df_temp.sort_values(by="intent", inplace=True)
    return df_temp