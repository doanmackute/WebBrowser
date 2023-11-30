import os, time, tarfile, requests
from datetime import datetime, timedelta

# This method will check if the .txt file is up to date
class TXTFileModificationChecker:
    def __init__(self,my_config_data,logger):
        self.logger = logger
        # Get path to file SWEB_PHISH_1.txt
        path_to_txt = my_config_data["phishing_database"]["path"]
        url_to_tar_github = my_config_data["phishing_database"]["path_to_tar_github"]
        self.file_path_to_txt = path_to_txt
        

        # Create update file
        self.updater = FileUpdater(url_to_tar_github, self.file_path_to_txt)
    
    # Get the last modified time of the .txt file
    def get_last_modification_time(self):
        # Returns as a datetime object.
        # Check if the file is existed
        if not os.path.exists(self.file_path_to_txt):
            raise FileNotFoundError(self.logger.log_blocked_url('WEBBROWSER', 2, 'UpdatePhishingTXT', f'File path not found {self.file_path_to_txt}'))
        else:
            # Get the last modificated time of .txt file
            timestamp_of_txt = os.path.getmtime(self.file_path_to_txt)
            
            # Using fromtimestamp to change it to Calender
            return datetime.fromtimestamp(timestamp_of_txt)
    
    # This methoud check if the file has been modified since the given check_time.
    # compared_time should be a datetime object.
    # Returns True if modified after check_time, False otherwise.
    def file_has_been_modified_since(self, compared_time):
        return self.get_last_modification_time() > compared_time

    # This methoud check if the file was last modified more than 2 weeks ago
    def check_and_update_if_needed(self):
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        if not self.file_has_been_modified_since(two_weeks_ago):
            self.updater.download_and_extract()

class FileUpdater:
    def __init__(self, github_url, txt_path):
        self.github_url = github_url
        self.txt_path = txt_path
        self.max_attempts = 2
        # Set delay after redirect HTTP
        self.delay_betwween_attempts = 0.1

    # This method will download the .gz file from GitHub and extract its contents to a .txt file.
    def download_and_extract(self):
        for attempt in range(self.max_attempts):
            try:
                # Connect to file_github and download
                response = requests.get(self.github_url, stream=True)
                # HTTPError object if an error has occurred during the process.
                response.raise_for_status()
                
                # Set file temp
                temp_gz_filename = "downloaded_file.tar.gz"
                # Write to file temp (WriteBinary)
                with open(temp_gz_filename, "wb") as temp_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        temp_file.write(chunk)
                
                # Extract file to .txt
                try:
                    with tarfile.open(temp_gz_filename, "r") as tar_file:
                        for member in tar_file.getmembers():
                            extracted_file = tar_file.extractfile(member)
                            if extracted_file:
                                with open(self.txt_path, "wb") as txt_file:
                                    txt_file.write(extracted_file.read())
                    # Remove file temp
                    os.remove(temp_gz_filename)
                    # Break for if the first HTTP is succeed
                    break
                except tarfile.ReadError:
                    self.logger.log_blocked_url('WEBBROWSER', 2, 'UpdatePhishingTXT', f'Can not open and write file tar {temp_gz_filename}')
            except (requests.ConnectionError, requests.HTTPError) as excep:
                if attempt < self.max_attempts -1:
                    # Wait for the specified delay before retrying
                    time.sleep(self.delay_betwween_attempts)  
                else:
                    self.logger.log_blocked_url("WEBBROWSER",2,"UpdatePhishingTXT",f'Can not update SWEB_PHISHING_1.txt')
