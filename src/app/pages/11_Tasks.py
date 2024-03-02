"""A page for managing the tasks."""
import requests
import pandas as pd
import streamlit as st
from utils.streamlit import app_init
from utils.settings import args

app_init()

st.title("Tasks")

response = requests.get(
    url=f"{args.API_INTERNAL_URL}/tasks",
    timeout=60
)

if response.status_code != 200:
    st.error("Failed to get the tasks.")
    st.stop()

tasks = response.json()

# Add output link to the tasks
for task in tasks:
    # task["progress"] = task["progress"] * 100 if task["progress"] is not None else None
    if task["status"] == "COMPLETED":
        task["output_link"] = (
            f"{args.API_EXTERNAL_URL}/tasks/{task['id']}/outputs?return_as_file=True"
        )

df = pd.DataFrame(tasks)
df["start_time"] = pd.to_datetime(df["start_time"])
df["end_time"] = pd.to_datetime(df["end_time"])

# Add filters
c1, c2, c3 = st.columns(3)

status = c1.multiselect(
    "Status",
    options=df.status.unique().tolist(),
    default=["COMPLETED"]
)

start_date = c2.date_input(
    "Start Date",
    value=df.start_time.min(),
    min_value=df.start_time.min(),
    max_value=df.start_time.max()
)

end_date = c3.date_input(
    "End Date",
    value=df.end_time.max(),
    min_value=df.end_time.min(),
    max_value=df.end_time.max()
)

df: pd.DataFrame = df[
    (df.status.isin(status)) &
    (df.start_time >= pd.to_datetime(start_date)) &
    (df.end_time <= pd.to_datetime(end_date).replace(hour=23, minute=59, second=59))
]

column_config = {
    "id": st.column_config.TextColumn(
        label="Task ID",
        help="The unique identifier of the task.",
    ),
    "name": st.column_config.TextColumn(
        label="Task Name",
        help="The name of the task.",
    ),
    "status": st.column_config.TextColumn(
        label="Status",
        help="The status of the task.",
    ),
    "status_desc": st.column_config.TextColumn(
        label="Status Description",
        help="The description of the status of the task."
    ),
    "progress": st.column_config.ProgressColumn(
        label="Progress",
        help="The progress of the task.",
    ),
    "start_time": st.column_config.DatetimeColumn(
        label="Start Date",
        help="The start datetime of the task.",
        format="D MMM YYYY, h:mm a"
    ),
    "end_time": st.column_config.DatetimeColumn(
        label="End Date",
        help="The end datetime of the task.",
        format="D MMM YYYY, h:mm a"
    ),
    "output_link": st.column_config.LinkColumn(
        label="Output",
        help="Download the output of the task.",
        validate=f"^{args.API_EXTERNAL_URL}/tasks/.*/outputs\\?return_as_file=True$",
        display_text="Download",
    )
}

st.data_editor(
    df[column_config.keys()],
    disabled=True,
    hide_index=True,
    column_config=column_config,
    use_container_width=True
)
