import csv
import io
import logging

from datetime import datetime

class CSVFormatter(logging.Formatter):

    def __init__(self):
        super().__init__()
        self.output = io.StringIO()
        self.writer = csv.writer(self.output, quoting=csv.QUOTE_ALL)

        self.writer.writerow(['timestamp', 'message'])

    def format(self, record):

        time_now = datetime.now()

        self.writer.writerow([time_now.isoformat(), record.msg])
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)

        return data.strip()


# logger 
logging.basicConfig(level=logging.DEBUG)

handler = logging.FileHandler('report.csv', 'a+')
handler.setFormatter(CSVFormatter())

customlogger = logging.getLogger('csvlogger')
customlogger.addHandler(handler)
