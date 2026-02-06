import pandas as pd
import re


def markdown_to_csv(md_content: str):
    lines = md_content.strip().split("\n")

    data = []

    for line in lines:
        if re.match(r"^\|?[\s\-:|]+\|$", line):
            continue

        if "|" in line:
            cells = [cell.strip() for cell in line.split("|")]
            cells = [c for c in cells if c]

            data.append(cells)

    df = pd.DataFrame(data[1:], columns=data[0])

    return df.to_csv(index=False, encoding="utf-8")
