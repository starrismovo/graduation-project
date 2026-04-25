import unittest

from services.personality_scoring import (
    SCORING_MODEL_VERSION,
    resolve_personality_scores,
    score_big_five_from_abilities,
)


class TestPersonalityScoringModel(unittest.TestCase):
    def test_backend_mapping_returns_big_five_and_version(self):
        all_scores = {
            "专业能力": 8.0,
            "逻辑思维": 7.0,
            "表达能力": 9.0,
            "学习能力": 6.0,
            "团队合作": 8.0,
            "创新思维": 7.5,
        }
        scores, meta = score_big_five_from_abilities(all_scores)

        self.assertEqual(set(scores.keys()), {"外向性", "宜人性", "尽责性", "神经质", "开放性"})
        for value in scores.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 10.0)

        self.assertEqual(meta["model_version"], SCORING_MODEL_VERSION)
        self.assertEqual(meta["source"], "derived_from_all_scores")

    def test_resolve_prefers_explicit_personality_scores(self):
        all_scores = {"表达能力": 2.0}
        explicit = {
            "外向性": 7.2,
            "宜人性": 6.5,
            "尽责性": 8.1,
            "神经质": 3.3,
            "开放性": 7.8,
        }

        scores, meta = resolve_personality_scores(all_scores, explicit)

        self.assertEqual(meta["source"], "request_personality_scores")
        self.assertAlmostEqual(scores["外向性"], 7.2, places=2)
        self.assertAlmostEqual(scores["神经质"], 3.3, places=2)


if __name__ == "__main__":
    unittest.main()
