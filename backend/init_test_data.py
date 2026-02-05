"""
初始化测试数据脚本
用于开发和测试，填充示例岗位数据
"""

from sqlalchemy.orm import Session
from models.user import User
from models.job import Job
from models.interview import Interview
from database import SessionLocal, Base, engine
from routers.auth import get_password_hash

def init_test_data():
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 清空现有数据（可选）
    # db.query(Interview).delete()
    # db.query(Job).delete()
    # db.query(User).delete()
    
    # 创建测试用户
    # HR 用户
    hr_user = User(
        username="alice",
        email="alice@company.com",
        hashed_password=get_password_hash("password123"),
        is_hr=True
    )
    
    # 候选人用户
    candidate_user = User(
        username="bob",
        email="bob@example.com",
        hashed_password=get_password_hash("password123"),
        is_hr=False
    )
    
    db.add(hr_user)
    db.add(candidate_user)
    db.commit()
    
    print("✓ 创建用户成功")
    
    # 创建测试岗位
    jobs_data = [
        {
            "name": "前端开发工程师",
            "description": "负责React/Vue框架下的前端业务开发，参与产品迭代优化。",
            "company": "阿里巴巴",
            "category": "技术岗",
            "city": "杭州",
            "salary_min": 25,
            "salary_max": 35,
            "required_traits": {
                "openness": 8,
                "conscientiousness": 8,
                "extraversion": 7,
                "agreeableness": 6,
                "neuroticism": 3
            }
        },
        {
            "name": "后端开发工程师",
            "description": "开发高并发分布式后端系统，使用Go/Java技术栈。",
            "company": "字节跳动",
            "category": "技术岗",
            "city": "北京",
            "salary_min": 30,
            "salary_max": 50,
            "required_traits": {
                "openness": 7,
                "conscientiousness": 9,
                "extraversion": 5,
                "agreeableness": 6,
                "neuroticism": 2
            }
        },
        {
            "name": "Python数据分析师",
            "description": "使用Python进行数据分析和可视化，支撑业务决策。",
            "company": "腾讯",
            "category": "技术岗",
            "city": "深圳",
            "salary_min": 22,
            "salary_max": 32,
            "required_traits": {
                "openness": 8,
                "conscientiousness": 9,
                "extraversion": 4,
                "agreeableness": 5,
                "neuroticism": 3
            }
        },
        {
            "name": "产品经理",
            "description": "负责产品规划和迭代，与团队协作推进项目落地。",
            "company": "美团",
            "category": "产品岗",
            "city": "北京",
            "salary_min": 25,
            "salary_max": 40,
            "required_traits": {
                "openness": 9,
                "conscientiousness": 8,
                "extraversion": 8,
                "agreeableness": 7,
                "neuroticism": 3
            }
        },
        {
            "name": "视觉设计师",
            "description": "设计UI/UX界面，提升用户体验和视觉效果。",
            "company": "网易",
            "category": "设计岗",
            "city": "杭州",
            "salary_min": 18,
            "salary_max": 28,
            "required_traits": {
                "openness": 9,
                "conscientiousness": 7,
                "extraversion": 6,
                "agreeableness": 7,
                "neuroticism": 3
            }
        },
        {
            "name": "运营专员",
            "description": "负责社区运营和用户增长，分析数据优化策略。",
            "company": "快手",
            "category": "运营岗",
            "city": "上海",
            "salary_min": 15,
            "salary_max": 25,
            "required_traits": {
                "openness": 8,
                "conscientiousness": 7,
                "extraversion": 9,
                "agreeableness": 8,
                "neuroticism": 4
            }
        },
        {
            "name": "机器学习工程师",
            "description": "开发和优化机器学习模型，解决真实业务问题。",
            "company": "百度",
            "category": "技术岗",
            "city": "北京",
            "salary_min": 35,
            "salary_max": 60,
            "required_traits": {
                "openness": 9,
                "conscientiousness": 9,
                "extraversion": 4,
                "agreeableness": 5,
                "neuroticism": 2
            }
        },
        {
            "name": "市场营销经理",
            "description": "制定营销策略，管理营销团队，提升品牌影响力。",
            "company": "小米",
            "category": "市场岗",
            "city": "深圳",
            "salary_min": 20,
            "salary_max": 35,
            "required_traits": {
                "openness": 8,
                "conscientiousness": 7,
                "extraversion": 8,
                "agreeableness": 6,
                "neuroticism": 3
            }
        }
    ]
    
    for job_data in jobs_data:
        job = Job(
            **job_data,
            creator_id=hr_user.id
        )
        db.add(job)
    
    db.commit()
    print(f"✓ 创建 {len(jobs_data)} 个测试岗位成功")
    
    print("\n✅ 测试数据初始化完成！")
    print(f"HR用户: {hr_user.username} / password123")
    print(f"候选人: {candidate_user.username} / password123")
    
    db.close()

if __name__ == "__main__":
    init_test_data()
