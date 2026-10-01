import unittest
from EmotionDetection.emotion_detection import emotion_detector


class TestEmotionDetector(unittest.TestCase):

    def test_joy(self):
        result = emotion_detector("I am glad this happened")
        self.assertEqual(result["dominant_emotion"], "joy")

    def test_anger(self):
        result = emotion_detector("I am really angry about this")
        self.assertEqual(result["dominant_emotion"], "anger")

    def test_disgust(self):
        result = emotion_detector("This is disgusting")
        self.assertEqual(result["dominant_emotion"], "disgust")

    def test_fear(self):
        result = emotion_detector("I am afraid of this")
        self.assertEqual(result["dominant_emotion"], "fear")

    def test_sadness(self):
        result = emotion_detector("I am feeling very sad")
        self.assertEqual(result["dominant_emotion"], "sadness")


if __name__ == "__main__":
    unittest.main()
