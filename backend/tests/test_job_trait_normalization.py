import unittest

from routers.job import _build_personality_requirements, _normalize_job_traits


class TestJobTraitNormalization(unittest.TestCase):
    def test_normalize_job_traits_accepts_chinese_and_english_keys(self):
        traits = _normalize_job_traits({
            "开放性": 7.0,
            "conscientiousness": 8.0,
            "外向性": 6.0,
            "宜人性": 7.5,
            "neuroticism": 3.5,
            "无关字段": 9.0,
        })

        self.assertEqual(
            traits,
            {
                "openness": 7.0,
                "conscientiousness": 8.0,
                "extraversion": 6.0,
                "agreeableness": 7.5,
                "neuroticism": 3.5,
            },
        )

    def test_build_personality_requirements_deduplicates_generated_traits(self):
        required_traits, personality_requirements = _build_personality_requirements(
            {"psychological_focus": ["innovation", "detail"]},
            {
                "开放性": 7.0,
                "尽责性": 8.0,
                "外向性": 6.0,
                "宜人性": 7.5,
                "神经质": 3.5,
            },
        )

        self.assertEqual(
            set(required_traits.keys()),
            {"openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"},
        )
        self.assertEqual(required_traits["openness"], 6.8)
        self.assertEqual(required_traits["conscientiousness"], 7.2)
        self.assertEqual(required_traits["neuroticism"], 3.5)
        self.assertEqual(personality_requirements["input_mode"], "psychological_focus")


if __name__ == "__main__":
    unittest.main()
