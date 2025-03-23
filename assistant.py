import speech_recognition as sr
import pyttsx3
import nltk
from nltk.tokenize import word_tokenize
import pyautogui
import os
import requests
import json
from datetime import datetime
import webbrowser
import subprocess
import psutil
from datetime import date
import calendar
import wikipedia
import random
from dotenv import load_dotenv
import screen_brightness_control as sbc
import logging
import traceback
import time

# Set up logging
logging.basicConfig(
    filename='assistant.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Download required NLTK data
nltk.download('punkt')

class AIPersonalAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.is_active = True
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.weather_base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.debug_mode = False
        logging.info("AI Assistant initialized")

    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode = not self.debug_mode
        status = "enabled" if self.debug_mode else "disabled"
        logging.info(f"Debug mode {status}")
        return f"Debug mode {status}"

    def log_error(self, function_name, error):
        """Log errors with stack trace in debug mode"""
        if self.debug_mode:
            logging.error(f"Error in {function_name}: {str(error)}")
            logging.debug(f"Stack trace: {traceback.format_exc()}")
        return str(error)

    def get_weather(self, city="London"):
        """Get weather information for a city"""
        try:
            logging.info(f"Fetching weather for {city}...")
            params = {
                'q': city,
                'appid': self.weather_api_key,
                'units': 'metric'  # For Celsius
            }
            response = requests.get(self.weather_base_url, params=params)
            logging.debug(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                weather_data = response.json()
                temp = weather_data['main']['temp']
                description = weather_data['weather'][0]['description']
                weather_info = f"The temperature in {city} is {temp}°C with {description}"
                logging.info(f"Weather info: {weather_info}")
                return weather_info
            else:
                error_msg = "Sorry, I couldn't fetch the weather information"
                logging.error(f"Error: {error_msg} (Status code: {response.status_code})")
                return error_msg
        except Exception as e:
            error_msg = self.log_error("get_weather", e)
            return error_msg

    def clear_terminal(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_listening_animation(self):
        """Display a listening animation"""
        animation = "|/-\\"
        for i in range(10):
            print(f"\rListening {animation[i % len(animation)]}", end="", flush=True)
            time.sleep(0.1)

    def listen(self):
        """Listen to user's voice input"""
        with sr.Microphone() as source:
            # Clear terminal and show listening status
            self.clear_terminal()
            print("\n" + "="*50)
            print("🎤 LISTENING FOR YOUR COMMAND...")
            print("="*50 + "\n")
            
            self.recognizer.adjust_for_ambient_noise(source)
            self.display_listening_animation()
            
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio)
                # Clear terminal and show recognized text
                self.clear_terminal()
                print("\n" + "="*50)
                print("🗣️ You said:")
                print("="*50)
                print(f"\n\"{text}\"\n")
                print("="*50 + "\n")
                logging.info(f"Recognized text: {text}")
                return text.lower()
            except sr.UnknownValueError:
                print("\n❌ Sorry, I didn't catch that.\n")
                logging.warning("Speech not recognized")
                return ""
            except sr.RequestError as e:
                error_msg = self.log_error("listen", e)
                print(f"\n❌ Error: {error_msg}\n")
                return ""

    def speak(self, text):
        """Convert text to speech"""
        print(f"\n🤖 Assistant: {text}\n")  # Display assistant's response
        self.engine.say(text)
        self.engine.runAndWait()

    def take_screenshot(self):
        """Take a screenshot and save it to desktop"""
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            screenshot_name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = os.path.join(desktop_path, screenshot_name)
            
            # Ensure the desktop directory exists
            if not os.path.exists(desktop_path):
                os.makedirs(desktop_path)
                
            # Take the screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            logging.info(f"Screenshot saved to: {screenshot_path}")
            return True
        except Exception as e:
            error_msg = self.log_error("take_screenshot", e)
            return False

    def open_application(self, app_name):
        """Helper function to open applications"""
        try:
            if app_name == "calculator":
                os.system("calc")
            elif app_name == "paint":
                os.system("mspaint")
            elif app_name == "word":
                os.system("start winword")
            elif app_name == "excel":
                os.system("start excel")
            elif app_name == "powerpoint":
                os.system("start powerpnt")
            elif app_name == "cmd" or app_name == "command prompt":
                os.system("start cmd")
            elif app_name == "settings":
                os.system("start ms-settings:")
            elif app_name == "task manager":
                os.system("taskmgr")
            elif app_name == "edge" or app_name == "microsoft edge":
                os.system("start msedge")
            elif app_name == "whatsapp":
                os.system("start whatsapp:")  # Uses Windows 10/11 URI handler for WhatsApp
            else:
                return False
            logging.info(f"Opened application: {app_name}")
            return True
        except Exception as e:
            error_msg = self.log_error("open_application", e)
            return False

    def get_system_info(self):
        """Get system information"""
        try:
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            system_info = f"CPU usage is {cpu_usage}% and memory usage is {memory_usage}%"
            logging.info(system_info)
            return system_info
        except Exception as e:
            error_msg = self.log_error("get_system_info", e)
            return f"Error getting system information: {error_msg}"

    def get_date_info(self):
        """Get current date information"""
        try:
            today = date.today()
            day = calendar.day_name[today.weekday()]
            date_info = f"Today is {day}, {today.strftime('%B %d, %Y')}"
            logging.info(date_info)
            return date_info
        except Exception as e:
            error_msg = self.log_error("get_date_info", e)
            return f"Error getting date information: {error_msg}"

    def search_wikipedia(self, query):
        """Search Wikipedia for information"""
        try:
            result = wikipedia.summary(query, sentences=2)
            logging.info(f"Wikipedia result for '{query}': {result}")
            return result
        except Exception as e:
            error_msg = self.log_error("search_wikipedia", e)
            return "Sorry, I couldn't find that information on Wikipedia."

    def show_commands(self):
        """Display available commands from commands.txt"""
        try:
            with open('commands.txt', 'r') as file:
                commands = file.read()
                logging.info("Displaying available commands")
                print("\nAvailable Commands:")
                print("==================")
                print(commands)
                self.speak("I've displayed all available commands on the screen. You can ask me any of these commands.")
        except FileNotFoundError as e:
            error_msg = self.log_error("show_commands", e)
            self.speak("Sorry, I couldn't find the commands list.")

    def system_control(self, command):
        """Handle system shutdown and sleep commands"""
        try:
            if "shutdown" in command or "shut down" in command:
                self.speak("Shutting down the system in 10 seconds. Say 'cancel shutdown' to abort.")
                os.system("shutdown /s /t 10")
                logging.info("System shutdown initiated")
                return True
            elif "sleep" in command:
                self.speak("Putting the system to sleep")
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                logging.info("System sleep initiated")
                return True
            elif "cancel shutdown" in command:
                os.system("shutdown /a")
                self.speak("Shutdown cancelled")
                logging.info("System shutdown cancelled")
                return True
            return False
        except Exception as e:
            error_msg = self.log_error("system_control", e)
            return False

    def adjust_brightness(self, direction):
        """Adjust screen brightness up or down"""
        try:
            current = sbc.get_brightness()[0]
            change = 10 if direction == "up" else -10
            new_brightness = max(0, min(100, current + change))
            sbc.set_brightness(new_brightness)
            logging.info(f"Brightness adjusted to {new_brightness}%")
            return True
        except Exception as e:
            error_msg = self.log_error("adjust_brightness", e)
            return False

    def process_command(self, command):
        """Process the user's command"""
        try:
            logging.info(f"Processing command: {command}")
            tokens = word_tokenize(command)
            
            # Debug mode commands
            if "debug mode" in command:
                if "on" in command or "enable" in command:
                    self.debug_mode = True
                    self.speak("Debug mode enabled")
                    return
                elif "off" in command or "disable" in command:
                    self.debug_mode = False
                    self.speak("Debug mode disabled")
                    return
            
            if "run tests" in command:
                self.speak("Running unit tests")
                import unittest
                import test_assistant
                suite = unittest.TestLoader().loadTestsFromModule(test_assistant)
                result = unittest.TextTestRunner(verbosity=2).run(suite)
                if result.wasSuccessful():
                    self.speak("All tests passed successfully")
                else:
                    self.speak(f"Some tests failed. {len(result.failures)} failures, {len(result.errors)} errors")
                return
            
            # First check for system control commands
            if self.system_control(command):
                return
            
            if "help" in command or "commands" in command or "what can you do" in command:
                self.show_commands()
                
            elif "open" in tokens:
                if "chrome" in command or "browser" in command:
                    os.system("start chrome")
                    self.speak("Opening Chrome")
                elif "edge" in command or "microsoft edge" in command:
                    self.open_application("edge")
                    self.speak("Opening Microsoft Edge")
                elif "whatsapp" in command:
                    self.open_application("whatsapp")
                    self.speak("Opening WhatsApp")
                elif "notepad" in command:
                    os.system("start notepad")
                    self.speak("Opening Notepad")
                else:
                    # Check for other applications
                    for app in ["calculator", "paint", "word", "excel", "powerpoint", 
                              "cmd", "command prompt", "settings", "task manager"]:
                        if app in command.lower():
                            if self.open_application(app):
                                self.speak(f"Opening {app}")
                            else:
                                self.speak(f"Sorry, I couldn't open {app}")
                            break
                
            elif "weather" in command:
                # Extract city name from command
                city = "London"  # default city
                words = command.split()
                if "in" in words:
                    city_index = words.index("in") + 1
                    if city_index < len(words):
                        city = words[city_index].capitalize()
                
                weather_info = self.get_weather(city)
                self.speak(weather_info)
                
            elif "time" in command:
                current_time = datetime.now().strftime("%I:%M %p")
                self.speak(f"The current time is {current_time}")
                
            elif "date" in command:
                date_info = self.get_date_info()
                self.speak(date_info)
                
            elif "system" in command and ("status" in command or "info" in command):
                system_info = self.get_system_info()
                self.speak(system_info)
                
            elif "search" in command and "wikipedia" in command:
                # Extract search query
                query = command.lower().replace("search wikipedia for", "").replace("search on wikipedia", "").strip()
                if query:
                    result = self.search_wikipedia(query)
                    self.speak(result)
                else:
                    self.speak("What would you like me to search for on Wikipedia?")
                    
            elif "joke" in command:
                jokes = [
                    "Why don't programmers like nature? It has too many bugs!",
                    "Why did the computer keep freezing? Because it left its Windows open!",
                    "What do you call a computer that sings? A Dell!"
                ]
                self.speak(random.choice(jokes))
                
            elif "volume" in command:
                if "up" in command:
                    pyautogui.press("volumeup")
                    self.speak("Volume increased")
                elif "down" in command:
                    pyautogui.press("volumedown")
                    self.speak("Volume decreased")
                elif "mute" in command:
                    pyautogui.press("volumemute")
                    self.speak("Volume muted")
                    
            elif "brightness" in command:
                if "up" in command or "increase" in command:
                    if self.adjust_brightness("up"):
                        self.speak("Brightness increased")
                    else:
                        self.speak("Sorry, I couldn't adjust the brightness")
                elif "down" in command or "decrease" in command:
                    if self.adjust_brightness("down"):
                        self.speak("Brightness decreased")
                    else:
                        self.speak("Sorry, I couldn't adjust the brightness")
                    
            elif "screenshot" in command:
                if self.take_screenshot():
                    self.speak("Screenshot taken and saved to desktop")
                else:
                    self.speak("Sorry, I couldn't take the screenshot")
                    
            elif "stop" in command or "exit" in command:
                self.is_active = False
                self.speak("Goodbye!")
                
            else:
                self.speak("I'm not sure how to help with that. Say 'help' or 'what can you do' to see available commands.")
                
        except Exception as e:
            error_msg = self.log_error("process_command", e)
            self.speak(f"An error occurred: {error_msg}")

    def run(self):
        """Main loop for the assistant"""
        try:
            logging.info("Starting AI Assistant")
            self.speak("Hello! I'm your AI assistant. How can I help you?")
            
            while self.is_active:
                command = self.listen()
                if command:
                    self.process_command(command)
                    
        except Exception as e:
            error_msg = self.log_error("run", e)
            print(f"Critical error: {error_msg}")
            logging.critical(f"Assistant crashed: {error_msg}")

if __name__ == "__main__":
    assistant = AIPersonalAssistant()
    assistant.run()