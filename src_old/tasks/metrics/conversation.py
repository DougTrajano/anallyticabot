import pandas as pd
import streamlit as st
import plotly_express as px
from src.helper_functions import flatten, setup_logger

logger = setup_logger()


def logs_to_dataframe(logs, datetime_var):
    lst = []

    for log in logs:
        lst.append(flatten(log))
    
    # Create DataFrame
    df = pd.DataFrame(lst)

    # Add Date
    df[datetime_var] = pd.to_datetime(df[datetime_var])
    df['Date'] = [each.date() for each in df[datetime_var]]

    return df

def get_metrics(df, args):
    metrics = {}

    # Session count
    try:
        metrics['sessions_count'] = len(df[args['Sessions']].unique())
    except Exception as error:
        metrics['sessions_count'] = None
        logger.error({"message": "Failed to get session counts.", "exception": error})
        st.error("Failed to get session counts.")

    # Messages count
    try:
        metrics["messages_count"] = len(df)
    except Exception as error:
        metrics["messages_count"] = None
        logger.error({"message": "Failed to get messages count.", "exception": error})
        st.error("Failed to get messages count.")

    # Avg messages
    try:
        metrics['avg_messages'] = len(df) / len(df[args['Sessions']].unique())
        metrics['avg_messages'] = round(metrics['avg_messages'], 1)
    except Exception as error:
        metrics['avg_messages'] = None
        logger.error({"message": "Failed to get average messages.", "exception": error})
        st.error("Failed to get average messages.")

    # Active users
    try:
        metrics['active_users'] = len(df[args['Active users']].unique())
    except Exception as error:
        metrics['active_users'] = None
        logger.error({"message": "Failed to get active users. Please, check User variable.", "exception": error})
        st.error('Failed to get active users. Please, check "User variable" on advanced options.')

    return metrics

def filter_columns(df, args):
    columns = []
    for arg in args.values():
        if arg in df.columns:
            columns.append(arg)
            
    # Add datetime column
    columns.append('Date')
    return columns

def gen_plotly_datetime(df, args, var):
    columns = filter_columns(df, args)
    df_temp = df[columns]
    df_temp = df_temp[df_temp[args[var]].notnull()]
    df_temp = df_temp[['Date', args[var]]]
    df_temp.drop_duplicates(inplace=True)
    df_temp = pd.DataFrame(df_temp['Date'].value_counts())
    df_temp.sort_index(inplace=True)
    df_temp.reset_index(inplace=True)
    df_temp.columns = ['Date', args.get(var)]
    df_temp.rename(columns={args[var]: var}, inplace=True)
    
    fig = px.bar(df_temp, x='Date', y=var,
                 title="{} per day".format(var))
    fig.update_xaxes(tickformat="%Y-%m-%d", type="category")
    fig.update_layout(showlegend=False)
    
    return fig