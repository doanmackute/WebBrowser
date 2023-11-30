from PyQt5.QtWidgets import QMainWindow, QApplication, QStyle, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QLineEdit, QPushButton, QToolBar, QWidget, QSizePolicy
from PyQt5.QtGui import QIcon
from urllib.parse import urlparse
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtCore import QEvent, QUrl, Qt, QTimer, QSize, pyqtSignal
import sys, os
from antiPhishing.URLBlocker import URLBlocker
from antiPhishing.URLLogger import URLLogger
from antiPhishing.UpdatePhishingTXT import TXTFileModificationChecker
from loadConfig import *
import pygame, math
from screeninfo import get_monitors

class MyWebEnginePage(QWebEnginePage):
    # Define a signal that will carry a URL as its argument
    urlChangedSignal = pyqtSignal(QUrl)

    def __init__(self, parent=None):
        super().__init__(parent)
        
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Ensure only modifying behavior for clicked links
        if _type == QWebEnginePage.NavigationTypeLinkClicked and isMainFrame:
            # Navigate to the url
            self.urlChangedSignal.emit(url)
            # Tell the view that handled this navigation request
            return False
        # Return True for all other navigation requests
        return True

    def createWindow(self, _type):
        # Create a new instance of MyWebEnginePage for the new window request
        new_page = MyWebEnginePage(self)
        new_page.urlChangedSignal.connect(self.urlChangedSignal.emit)
        return new_page
        
class GetHeightAndWidthFromScreen:
    def __init__(self):
        template_config = load_sweb_config_json()
        num_of_monitor = template_config["GlobalConfiguration"]["numOfScreen"]
        padding = template_config["GUI_template"]["padx_value"]
        height_divisor = template_config["GUI_template"]["height_divisor"]
        width_divisor = template_config["GUI_template"]["width_divisor"]
        num_option_on_frame = 5
        
        # Get monitor size
        # 0 = Get the first monitor
        monitor = get_monitors()[num_of_monitor]
        screen_width, screen_height = monitor.width, monitor.height
        self.button_height = screen_height / height_divisor
        # Number of button on menu = numberOfOptions + 1
        total_padding = (num_option_on_frame)*padding
        # Calculate width for button
        self.button_width = math.floor((screen_width-total_padding)/width_divisor) - padding*(1/2)
    
    def get_height_button(self):
        return self.button_height
    
    def get_width_button(self):
        return self.button_width

# My main browser contains all GUI in this class (Toolbar, Buttons, URLbar)
class MyBrowser(QMainWindow):
    # Define the contructor for initialization 
    def __init__(self,my_config_data):
        super(MyBrowser,self).__init__()
        # Set window flags to customize window behavior
        # Remove standard window controls
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.browser = QWebEngineView()
        # Set cutstom page to open in the same browser
        self.custom_page = MyWebEnginePage(self.browser)
        self.custom_page.urlChangedSignal.connect(self.on_url_changed_my_custom_page)
        # Set page for page
        self.browser.setPage(self.custom_page)
        self.setCentralWidget(self.browser)
        self.browser.setUrl(QUrl("https://edition.cnn.com"))
        self.get_height_and_width = GetHeightAndWidthFromScreen()

        # Load URL blocker and logger
        file_to_phishing = my_config_data["phishing_database"]["path"]
        self.url_blocker = URLBlocker(file_to_phishing)
        self.logger = URLLogger()
        
        # Check if SWEB_PHISH_1.txt is up to date
        phishing_checker = TXTFileModificationChecker(my_config_data,self.logger)
        phishing_checker.check_and_update_if_needed()
        
        # Initialization pygame mixer 
        pygame.mixer.init()
        # Sound control attribute
        self.sound_for_button = None
        
        self.path_to_alert_phishing_music = my_config_data["audio"]["sweb_en_alert_phishing"]
        
        # Get parameter from file sconf/TEMPLATE.json
        self.font_family_info = my_config_data["GlobalConfiguration"]["fontFamily"]
        self.font_size_info = my_config_data["GlobalConfiguration"]["fontSize"]
        self.font_weight_info = my_config_data["GlobalConfiguration"]["fontThickness"]
        self.button_value_padd_info = my_config_data["GUI_template"]["padx_value"]
        self.time_hover_button = my_config_data["GlobalConfiguration"]["soundDelay"] * 1000
        
        # Get height and width from class GetHeightAndWidthInfo
        self.buttons_width_info = self.get_height_and_width.get_width_button()
        self.buttons_height_info = self.get_height_and_width.get_height_button()
        
        # Get my parametr from file
        self.color_info_menu = my_config_data["colors_info"]["menu_frame"]
        self.color_info_app = my_config_data["colors_info"]["app_frame"]
        self.color_info_button_unselected = my_config_data["colors_info"]["buttons_unselected"]
        self.color_info_button_selected = my_config_data["colors_info"]["buttons_selected"]
        
        # Get path for images
        self.path_to_image_exit = my_config_data["image"]["sweb_image_exit"]
        self.path_to_image_reload = my_config_data["image"]["sweb_image_reload"]
        self.path_to_image_home = my_config_data["image"]["sweb_image_home"]
        
        # Create toolbar for saving URL
        self.url_toolbar = QToolBar("URL Navigation")
        self.addToolBar(self.url_toolbar)
        self.url_toolbar.setMovable(False)
        
        self.addToolBarBreak()
        
        # Create a toolbar for saving menu and buttons
        self.menu_1_toolbar = QToolBar("Menu 1")
        self.addToolBar(self.menu_1_toolbar)
        self.menu_1_toolbar.setMovable(False)
        
        self.toolbarSpacer = QToolBar("Spacer")
        # Set the spacer height
        self.toolbarSpacer.setFixedHeight(int(self.buttons_height_info))
        self.toolbarSpacer.setStyleSheet(f"""
        QToolBar {{
                background-color: #fff;
        }}
        """)
        self.addToolBar(self.toolbarSpacer)
        self.toolbarSpacer.setMovable(False)
        self.toolbarSpacer.setVisible(False)
        self.addToolBarBreak()
        
        # Set a style for Menu 1 toolbar
        self.menu_1_toolbar.setStyleSheet(self.default_style_toolbar())
        self.setup_initial_menu_1()
        
        # Create a URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setAlignment(Qt.AlignCenter)
        # Change the parameter of URL bar
        self.url_bar.setStyleSheet(f"""
        QToolBar {{
                background-color: {self.color_info_menu};
        }}
        QLineEdit {{
            font-family: {self.font_family_info};
            font-size: {int(self.buttons_height_info/8)}px;
            font-weight: {self.font_weight_info};
            background-color: {self.color_info_app};
            padding: {self.button_value_padd_info}px;
            border-radius: {self.button_value_padd_info}px;
            border: 2px solid black;         
        }}        
        """)
        
        # When text of URL is changed, check for URL Phishing
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_toolbar.addWidget(self.url_bar)
        
        # Configure audio and for hovering buttons, menus and options
        # Run this methods for the set Current language in Translator
        #self.update_ui_text()
        #self.update_ui_audio()
        self.browser.urlChanged.connect(self.security_again_phishing)
        self.browser.loadFinished.connect(self.onLoadFinished)
    
    def on_url_changed_my_custom_page(self, url):
        # Load the new URL in the existing browser window
        self.browser.setUrl(url)
        
    def onLoadFinished(self, success):
        url_in_browser = self.browser.url()
        print()
        if success:
            if "homepage" not in url_in_browser.toString():
                self.browser.setZoomFactor(1)
            else:
                return
        
    def setup_initial_menu_1(self):
        # Create button back
        self.menu1Back = QPushButton(self)
        menu1Back_layout = QVBoxLayout(self.menu1Back)
        # QStyle.SP_ArrowBack to setting icon for back button
        menu1Back_icon = self.style().standardIcon(QStyle.SP_ArrowBack)
        menu1Back_label = QLabel(self.menu1Back)
        menu1Back_label.setPixmap(menu1Back_icon.pixmap(QSize(int(self.buttons_width_info/(1.5)),int(self.buttons_height_info/(1.5)))))
        menu1Back_layout.addWidget(menu1Back_label)
        # Set text for back_btn
        self.menu1Back_text_label = QLabel("Back",self.menu1Back)
        menu1Back_layout.addWidget(self.menu1Back_text_label)
        # Align text and icon in the center
        menu1Back_layout.setAlignment(menu1Back_label,Qt.AlignCenter)
        menu1Back_layout.setAlignment(self.menu1Back_text_label,Qt.AlignCenter)
        self.menu1Back.clicked.connect(self.browser.back)
        self.menu1Back.setCursor(Qt.PointingHandCursor) 
        self.menu_1_toolbar.addWidget(self.menu1Back)
        
        # Add a bliak space between two button
        spacer1 = QWidget()
        spacer1.setFixedWidth(self.button_value_padd_info)
        self.menu_1_toolbar.addWidget(spacer1)

        # Create forward button
        self.menu1Forward = QPushButton(self)
        menu1Forward_layout = QVBoxLayout(self.menu1Forward)
        # Setting icon for forward button
        menu1Forward_icon = self.style().standardIcon(QStyle.SP_ArrowForward)
        menu1Forward_label = QLabel(self.menu1Forward)
        menu1Forward_label.setPixmap(menu1Forward_icon.pixmap(QSize(int(self.buttons_width_info/(1.5)),int(self.buttons_height_info/(1.5)))))
        menu1Forward_layout.addWidget(menu1Forward_label)
        # Set text for forward_btn
        self.menu1Forward_text_label = QLabel("Forward",self.menu1Forward)
        menu1Forward_layout.addWidget(self.menu1Forward_text_label)
        # Align text and icon in the center
        menu1Forward_layout.setAlignment(menu1Forward_label,Qt.AlignCenter)
        menu1Forward_layout.setAlignment(self.menu1Forward_text_label,Qt.AlignCenter)
        self.menu1Forward.clicked.connect(self.browser.forward)
        self.menu1Forward.setCursor(Qt.PointingHandCursor) 
        self.menu_1_toolbar.addWidget(self.menu1Forward)
        
        # Add a bliak space between two button
        spacer2 = QWidget()
        spacer2.setFixedWidth(self.button_value_padd_info)
        self.menu_1_toolbar.addWidget(spacer2)
        
        # Create reload button
        self.menu1Reload = QPushButton(self)
        menu1Reload_layout = QVBoxLayout(self.menu1Reload)
        # Setting icon for reload button
        menu1Reload_icon = QIcon(self.path_to_image_reload)
        menu1Reload_label = QLabel(self.menu1Reload)
        menu1Reload_label.setPixmap(menu1Reload_icon.pixmap(QSize(int(self.buttons_width_info/(1.8)),int(self.buttons_height_info/(1.8)))))
        menu1Reload_layout.addWidget(menu1Reload_label)
        # Set text for reload_btn
        self.menu1Reload_text_label = QLabel("Reload",self.menu1Reload)
        menu1Reload_layout.addWidget(self.menu1Reload_text_label)
        # Align text and icon in the center
        menu1Reload_layout.setAlignment(menu1Reload_label,Qt.AlignCenter)
        menu1Reload_layout.setAlignment(self.menu1Reload_text_label,Qt.AlignCenter)
        self.menu1Reload.clicked.connect(self.browser.reload)
        self.menu1Reload.setCursor(Qt.PointingHandCursor) 
        self.menu_1_toolbar.addWidget(self.menu1Reload)
        
        # Add a blank space between two button
        spacer3 = QWidget()
        spacer3.setFixedWidth(self.button_value_padd_info)
        self.menu_1_toolbar.addWidget(spacer3)
        
        # Create Home button
        self.menu1Home = QPushButton(self)
        menu1Home_layout = QVBoxLayout(self.menu1Home)
        # Setting icon for Home button
        menu1Home_icon = QIcon(self.path_to_image_home)
        menu1Home_label = QLabel(self.menu1Home)
        menu1Home_label.setPixmap(menu1Home_icon.pixmap(QSize(int(self.buttons_width_info/(1.8)),int(self.buttons_height_info/(1.8)))))
        menu1Home_layout.addWidget(menu1Home_label)
        # Set text for home_btn
        self.menu1Home_text_label = QLabel("Home",self.menu1Home)
        menu1Home_layout.addWidget(self.menu1Home_text_label)
        # Align text and icon in the center
        menu1Home_layout.setAlignment(menu1Home_label,Qt.AlignCenter)
        menu1Home_layout.setAlignment(self.menu1Home_text_label,Qt.AlignCenter)
        self.menu1Home.clicked.connect(self.navigate_home)
        self.menu1Home.setCursor(Qt.PointingHandCursor) 
        self.menu_1_toolbar.addWidget(self.menu1Home)
        
        # Add a blank space between two button
        spacer4 = QWidget()
        spacer4.setFixedWidth(self.button_value_padd_info)
        self.menu_1_toolbar.addWidget(spacer4)
        
        # Add Exit button
        self.menu1Exit = QPushButton(self)
        # Create Home QvBoxLayout
        menu1Exit_layout = QVBoxLayout(self.menu1Exit)
        # Set Icon for Exit
        menu1Exit_icon = QIcon(self.path_to_image_exit)
        menu1Exit_label = QLabel(self.menu1Exit)
        menu1Exit_label.setPixmap(menu1Exit_icon.pixmap(QSize(int(self.buttons_width_info/(1.6)),int(self.buttons_height_info/(1.6)))))
        menu1Exit_layout.addWidget(menu1Exit_label)
        # Set text for exit_btn
        self.menu1Exit_text_label = QLabel("Exit",self.menu1Home)
        menu1Exit_layout.addWidget(self.menu1Exit_text_label)
        # Align text and icon in the center
        menu1Exit_layout.setAlignment(menu1Exit_label,Qt.AlignCenter)
        menu1Exit_layout.setAlignment(self.menu1Exit_text_label,Qt.AlignCenter)
        self.menu1Exit.clicked.connect(self.close)
        self.menu1Exit.setCursor(Qt.PointingHandCursor)
        self.menu_1_toolbar.addWidget(self.menu1Exit)
    
    # Set default style for Toolbar
    def default_style_toolbar(self):
        style_string = f"""
             QToolBar {{
                background-color: {self.color_info_menu};
            }}
            
            /* Changes parameters for button in Toolbar*/
            QPushButton {{
                border: 1px solid black;
                background-color: {self.color_info_button_unselected};                   
                font-size: {self.font_size_info}px;
                font-weight: {self.font_weight_info};
                font-family: {self.font_family_info};
                width: {self.buttons_width_info}px;
                height: {self.buttons_height_info}px;
                border-radius: {self.button_value_padd_info}px;
            }}
            
            QPushButton:hover {{
                background-color: {self.color_info_button_selected}; 
            }}
            
            QPushButton QLabel {{
                font-size: {self.font_size_info}px;
                font-weight: {self.font_weight_info};
                font-family: {self.font_family_info};
            }}
        """
        
        return style_string
    
    # Set default style for Toolbar
    def phishing_style_toolbar(self):
        alert_style_string = f"""
             QToolBar {{
                background-color: {self.color_info_menu};
            }}
            
            /* Changes parameters for button in Toolbar*/
            QPushButton {{
                border: 1px solid black;
                background-color: red;                   
                font-size: {self.font_size_info}px;
                font-weight: {self.font_weight_info};
                font-family: {self.font_family_info};
                width: {self.buttons_width_info}px;
                height: {self.buttons_height_info}px;
                border-radius: {self.button_value_padd_info}px;
            }}
            
            QPushButton:hover {{
                background-color: {self.color_info_button_selected}; 
            }}
            
            QPushButton QLabel {{
                font-size: {self.font_size_info}px;
                font-weight: {self.font_weight_info};
                font-family: {self.font_family_info};
            }}
        """
        
        return alert_style_string
        
    # Show full screen without Minimizing or Moving
    def show_app_fullscreen(self):
        self.showFullScreen()

    # QpushButton can be set HoverLeave and HoverEnter event with "widget"
    def setup_hover_sound(self, widget, hover_time,path_to_sound):
        # Using Qtimer to set clock
        widget.hover_timer = QTimer()
        widget.hover_timer.setInterval(hover_time)
        # Run only one times when hover
        widget.hover_timer.setSingleShot(True)
        widget.hover_timer.timeout.connect(lambda: self.play_sound_for_button(path_to_sound))
        # Install event to widget -> Event is comefrom eventFilter
        widget.installEventFilter(self)
    
    # Set event for leave and enter button -> Using only with QpushButton
    def eventFilter(self, watched, event):
        if event.type() == QEvent.HoverEnter:
            watched.hover_timer.start()
        elif event.type() == QEvent.HoverLeave:
            watched.hover_timer.stop()
            # Stop sound immediately
            self.stop_sound_for_button()
        return super().eventFilter(watched, event)
    
    # Play a sound, which is stored on SWEB_config.json
    def play_sound_for_button(self, path_to_sound):
        # Ensure the file exists before playing it
        if not os.path.exists(path_to_sound):
            print(f"Sound file not found: {path_to_sound}")
            return
        try:
            # Load and play the sound file
            self.sound_for_button = pygame.mixer.Sound(path_to_sound)
            self.sound_for_button.play()
        except Exception as exc:
            print(f"Failed to play sound: {str(exc)}")
            
    # Stop sound immediately when button is leaved hover
    def stop_sound_for_button(self):
        if self.sound_for_button:
            self.sound_for_button.stop()
            self.sound_for_button = None
        
    # This method is set for visible and invisible URL bar
    def toggle_url_toolbar(self):
        # Toggle visibility of the URL toolbar
        self.play_sound_for_button(self.path_to_url_music)
        self.browser.setUrl(QUrl("about:blank"))
        self.url_toolbar.setVisible(not self.url_toolbar.isVisible())
        self.toolbarSpacer.setVisible(not self.toolbarSpacer.isVisible())

    # This method is used for navigation URL bar
    def navigate_to_url(self):
        # Get url from URL toobal
        url_in_bar = self.url_bar.text().strip()
        #If "." is not contained in URL
        if "." not in url_in_bar:
            url_in_bar = "https://www.google.com/search?q=" + url_in_bar
        # If in URl not http or https, connect with HTTPS
        if "://" not in url_in_bar:
            url_in_bar = "https://" + url_in_bar
        if url_in_bar.endswith("/"):
            url_in_bar = url_in_bar[:-1]
        
        # Set default style for toolbar
        self.menu_1_toolbar.setStyleSheet(self.default_style_toolbar())
        # Connect to URL after entering
        self.browser.setUrl(QUrl(url_in_bar))
        
    def security_again_phishing(self,qurl):
        # Get url from QURL
        url_in_browser = qurl.toString()
        if not url_in_browser.endswith('/'):
            #url_in_browser = url_in_browser[:-1]
            if "about:blank" in url_in_browser:
                return
            elif "google.com" not in url_in_browser:
                # Check that if URL is from URL
                if self.url_blocker.is_url_blocked(url_in_browser):
                    self.show_blocked_message(url_in_browser)
                    # Log with level 5 when connected to phishing
                    self.logger.log_blocked_url('WEBBROWSER', 5, 'main <security>', f'Connection to Phishing server {url_in_browser}')
                    
                    # Set red colour for connect to phishing
                    self.menu_1_toolbar.setStyleSheet(self.phishing_style_toolbar())
                    # Connect to URL after entering
                    self.browser.setUrl(QUrl(url_in_browser))
                else:
                    self.menu_1_toolbar.setStyleSheet(self.default_style_toolbar())
                    # Log with level 6 INFORMATIONAL
                    self.logger.log_blocked_url('WEBBROWSER', 6, 'main <security>', f'Connection to {url_in_browser}')
                    # Connect to URL after entering
                    self.browser.setUrl(QUrl(url_in_browser))
            else:
                self.menu_1_toolbar.setStyleSheet(self.default_style_toolbar())
                # Log with LEVEL 6 INFORMATIONAL
                self.logger.log_blocked_url('WEBBROWSER', 6, 'main <security>', f'Connection to {url_in_browser}')
                # Connect to URL after entering
                self.browser.setUrl(QUrl(url_in_browser))
        else:
            self.url_bar.setText(url_in_browser)
            self.url_bar.setCursorPosition(0)
            return
        self.url_bar.setText(url_in_browser)
        self.url_bar.setCursorPosition(0)
        
    # Show block message when User connect to web from Phishing list
    def show_blocked_message(self, url):
        #msg = QMessageBox()
        #msg.setIcon(QMessageBox.Warning)
        #msg.setText(f"Blocked Phishing URL: {url}")
        #msg.setWindowTitle("Blocked URL Warning")
        #msg.exec_()
        self.play_sound_for_button(self.path_to_alert_phishing_music)
        
    # Method for connect to edition.cnn.com.com
    def navigate_home(self):
        self.browser.setUrl(QUrl("https://edition.cnn.com"))
    
# Definuje funkci Main
if __name__ == "__main__":
    try:
        qApplication = QApplication(sys.argv)
        # Load config data from JSON file
        sweb_config = load_sweb_config_json()
        mainWindow = MyBrowser(sweb_config)
        mainWindow.show_app_fullscreen()
        sys.exit(qApplication.exec_())
    except Exception as excep:
        # Load URL blocker and logger
        sweb_config = load_sweb_config_json()
        file_to_phishing = sweb_config["phishing_database"]["path"]
        url_blocker = URLBlocker(file_to_phishing)
        logger = URLLogger()
        # Log with level 2
        logger.log_blocked_url('WEBBROWSER', 2, 'main <security>', f'Application did not work')
        # Exit with an error code
        sys.exit(1)
