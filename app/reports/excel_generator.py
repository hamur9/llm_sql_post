import pandas as pd
import uuid
import os


def generate_excel(data: list) -> str | None:
    if not data:
        return None

    data_frame = pd.DataFrame(data)
    file_name = f"report_{uuid.uuid4().hex[:8]}.xlsx"
    file_path = os.path.join("output", file_name)
    data_frame.to_excel(file_path, index=False)

    return file_path