import unittest
import os
from unittest.mock import patch, MagicMock
from assistant import AIPersonalAssistant

class TestAIPersonalAssistant(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.assistant = AIPersonalAssistant()
        # Disable speak functionality during tests
        self.assistant.speak = MagicMock()

    def test_weather_functionality(self):
        """Test weather information retrieval"""
        # Mock the requests.get response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'main': {'temp': 20},
                'weather': [{'description': 'clear sky'}]
            }
            mock_get.return_value = mock_response

            result = self.assistant.get_weather("London")
            self.assertIn("20°C", result)
            self.assertIn("clear sky", result)

    def test_system_info(self):
        """Test system information retrieval"""
        info = self.assistant.get_system_info()
        self.assertIsInstance(info, str)
        self.assertIn("CPU usage", info)
        self.assertIn("memory usage", info)

    def test_date_info(self):
        """Test date information retrieval"""
        info = self.assistant.get_date_info()
        self.assertIsInstance(info, str)
        self.assertIn("Today is", info)

    def test_brightness_control(self):
        """Test brightness control"""
        with patch('screen_brightness_control.get_brightness') as mock_get:
            with patch('screen_brightness_control.set_brightness') as mock_set:
                mock_get.return_value = [50]  # Current brightness
                
                # Test increasing brightness
                result = self.assistant.adjust_brightness("up")
                self.assertTrue(result)
                mock_set.assert_called_with(60)  # Should increase by 10

                # Test decreasing brightness
                result = self.assistant.adjust_brightness("down")
                self.assertTrue(result)
                mock_set.assert_called_with(40)  # Should decrease by 10

    def test_open_application(self):
        """Test application opening functionality"""
        with patch('os.system') as mock_system:
            # Test valid application
            result = self.assistant.open_application("calculator")
            self.assertTrue(result)
            mock_system.assert_called_with("calc")

            # Test invalid application
            result = self.assistant.open_application("invalid_app")
            self.assertFalse(result)

    def test_screenshot(self):
        """Test screenshot functionality"""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_image = MagicMock()
            mock_screenshot.return_value = mock_image
            
            result = self.assistant.take_screenshot()
            self.assertTrue(result)
            self.assertTrue(mock_screenshot.called)
            self.assertTrue(mock_image.save.called)

    def test_wikipedia_search(self):
        """Test Wikipedia search functionality"""
        with patch('wikipedia.summary') as mock_summary:
            mock_summary.return_value = "Test summary"
            result = self.assistant.search_wikipedia("test")
            self.assertEqual(result, "Test summary")

            # Test error handling
            mock_summary.side_effect = Exception("Not found")
            result = self.assistant.search_wikipedia("nonexistent")
            self.assertIn("Sorry", result)

if __name__ == '__main__':
    unittest.main()