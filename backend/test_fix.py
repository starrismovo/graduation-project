#!/usr/bin/env python3
"""测试JobResponse验证器修复"""

from schemas.schemas import JobResponse
import json

# 模拟数据库返回的字符串化 JSON
job_data = {
    'id': 1,
    'name': '后端工程师',
    'description': 'Some description',
    'company': 'Company',
    'category': '技术岗',
    'city': '北京',
    'salary_min': 25.0,
    'salary_max': 35.0,
    'required_traits': '{"openness": 7.0, "conscientiousness": 8.0, "extroversion": 5.0, "agreeableness": 6.5, "neuroticism": 4.0}',
    'creator_id': 1
}

try:
    response = JobResponse(**job_data)
    print('✅ JobResponse validation PASSED!')
    print(f'required_traits type: {type(response.required_traits)}')
    print(f'required_traits value: {response.required_traits}')
    print(f'\nModel JSON: {response.model_dump_json()}')
except Exception as e:
    print(f'❌ FAILED: {e}')
    import traceback
    traceback.print_exc()
