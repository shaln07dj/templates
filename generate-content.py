from datetime import datetime

with open("report.txt", "w") as f:
    f.write(f"Report generated on {datetime.now()}\n")
