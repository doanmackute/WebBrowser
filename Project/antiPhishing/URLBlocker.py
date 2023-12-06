# Go through all domain in the file
# If the domain is match, take a blocking
class URLBlocker:
    def __init__(self, paths_to_db):
        self.blocked_urls = set()
        # Load file from file path
        #for filepath in paths_to_db:
        self.load_urls_from_txt(paths_to_db)
        
    # Read all member in that Domain file
    def load_urls_from_txt(self,path):
        with open(path,"r") as txtfile:
             # Real all member from the file until the file is None
                if txtfile is not None:
                    content  = txtfile.read()
                    urls = content.strip().split('\n')
                    self.blocked_urls.update(urls)

    # Control that if the url is Block
    def is_url_blocked(self, url):
        print(f"URL {url}")
        for blocked_url in self.blocked_urls:
            if blocked_url == "login.microsoft":
                return False
            if blocked_url == "microsoft365.com":
                return False
            if blocked_url in url:
                return True
        return False