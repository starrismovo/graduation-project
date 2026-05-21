from types import SimpleNamespace

from services.job_requirement_service import matching_engine


def _skill(name, priority=10, must_have=True):
    return SimpleNamespace(
        skill_name=name,
        priority_score=priority,
        is_must_have=must_have,
    )


def test_product_skill_aliases_match_must_have_requirements():
    score, matched, missing = matching_engine.calculate_skill_match(
        ["产品规划", "用户调研", "需求管理"],
        [
            _skill("产品思维", 10),
            _skill("用户研究", 8),
            _skill("需求分析", 9),
        ],
    )

    assert score == 100.0
    assert matched == ["产品思维", "用户研究", "需求分析"]
    assert missing == []
