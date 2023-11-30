from datetime import datetime

# Call class URL Logger for logging Phishing url to file
# Cisco log: seq no:timestamp: %facility-severity-MNEMONIC:description
class URLLogger:
    def __init__(self, log_file="logPhishing.txt"):
        self.severity_log = ["EMERGENCY","ALERT","CRITICAL","ERROR","WARNING","NOTICE","INFORMATIONAL","DEBUGGING"]
        self.log_file = log_file
        # Ensure the name for log file
        # If the name of file does not exist, create the new file
        # Ensure that the file is exist
        self._init_txt()

    # Method for creating and opening file .txt
    def _init_txt(self):
        try:
            # Read file with file name
            with open(self.log_file, 'r') as f:
                f.readline()
        except FileNotFoundError:
            # If file does not exist, show use w to create new and write parameter
            with open(self.log_file, 'w') as f:
                f.write("Logging phishing URL from Browser\n")
                
    # Show the the block message to window
    def log_blocked_url(self, facility, level_of_severity, mnemonic, description):
        self.log_to_txt(facility, self.severity_log[level_of_severity], mnemonic, description)

    # When the URL is blocked from log_blocked_url, save to file .txt
    def log_to_txt(self, facility, severity, mnemonic, description):
        # Set current time 
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # seq no:timestamp: %facility-severity-MNEMONIC:description
        log_entry = f"{current_time} : {facility}-{severity} -> {mnemonic} : {description}\n"
        # Write to exising file txt
        with open(self.log_file, 'a') as f:
            f.write(log_entry)