import unittest

from services.personality_scoring import score_big_five_from_abilities


class TestPersonalityScoringStability(unittest.TestCase):
    def test_deterministic_for_same_input(self):
        all_scores = {
            "专业能力": 7.2,
            "逻辑思维": 7.4,
            "表达能力": 6.8,
            "学习能力": 7.0,
            "团队合作": 6.9,
            "创新思维": 7.3,
        }

        first, _ = score_big_five_from_abilities(all_scores)
        for _ in range(20):
            again, _ = score_big_five_from_abilities(all_scores)
            self.assertEqual(first, again)

    def test_small_input_perturbation_is_bounded(self):
        base = {
            "专业能力": 7.2,
            "逻辑思维": 7.4,
            "表达能力": 6.8,
            "学习能力": 7.0,
            "团队合作": 6.9,
            "创新思维": 7.3,
        }
        perturbed = dict(base)
        perturbed["表达能力"] = 7.0

        s1, _ = score_big_five_from_abilities(base)
        s2, _ = score_big_five_from_abilities(perturbed)

        max_delta = max(abs(s1[k] - s2[k]) for k in s1.keys())
        # Mapping weights ensure minor perturbation does not create large swings.
        self.assertLessEqual(max_delta, 1.0)


if __name__ == "__main__":
    unittest.main()
