import pandas as pd
import plotly.express as px
import uuid
import os


def generate_graph(data: list) -> str | None:
    if not data or len(data) < 2:
        return None

    data_frame = pd.DataFrame(data)

    text_cols = data_frame.select_dtypes(include=['object']).columns
    numeric_cols = data_frame.select_dtypes(include=['number']).columns

    if len(text_cols) == 0 or len(numeric_cols) == 0:
        return None

    x_col = text_cols[0]
    y_col = numeric_cols[0]

    fig = px.bar(
        data_frame,
        x=x_col,
        y=y_col,
        title=f"Аналитика: {y_col} по {x_col}",
        color=x_col,
        template="plotly_white"
    )

    file_name = f"graph_{uuid.uuid4().hex[:8]}.html"
    file_path = os.path.join("output", file_name)
    fig.write_html(file_path)

    return file_path