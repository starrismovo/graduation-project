"""
简化的数据库初始化脚本 - 使用纯 SQL
"""
import mysql.connector
import json

# 数据库连接配置
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='hr_matching'
    )
    cursor = connection.cursor()
    
    # 清空表（保持表结构）
    print("清空现有数据...")
    cursor.execute("DELETE FROM interviews")
    cursor.execute("DELETE FROM jobs")
    cursor.execute("DELETE FROM users")
    
    # 插入用户
    print("插入用户...")
    cursor.execute("""
        INSERT INTO users (username, email, hashed_password, is_hr) 
        VALUES 
        (%s, %s, %s, %s),
        (%s, %s, %s, %s)
    """, (
        'alice', 'alice@company.com', 'hashed_password_alice', True,
        'bob', 'bob@example.com', 'hashed_password_bob', False
    ))
    
    # 获取HR用户ID
    cursor.execute("SELECT id FROM users WHERE username = 'alice'")
    hr_user_id = cursor.fetchone()[0]
    
    # 插入岗位
    print("插入岗位...")
    jobs_data = [
        ('前端开发工程师', '负责React/Vue框架下的前端业务开发，参与产品迭代优化。', '阿里巴巴', '技术岗', '杭州', 25, 35, json.dumps({"openness": 8, "conscientiousness": 8, "extraversion": 7, "agreeableness": 6, "neuroticism": 3})),
        ('后端开发工程师', '开发高并发分布式后端系统，使用Go/Java技术栈。', '字节跳动', '技术岗', '北京', 30, 50, json.dumps({"openness": 7, "conscientiousness": 9, "extraversion": 5, "agreeableness": 6, "neuroticism": 2})),
        ('Python数据分析师', '使用Python进行数据分析和可视化，支撑业务决策。', '腾讯', '技术岗', '深圳', 22, 32, json.dumps({"openness": 8, "conscientiousness": 9, "extraversion": 4, "agreeableness": 5, "neuroticism": 3})),
        ('产品经理', '负责产品规划和迭代，与团队协作推进项目落地。', '美团', '产品岗', '北京', 25, 40, json.dumps({"openness": 9, "conscientiousness": 8, "extraversion": 8, "agreeableness": 7, "neuroticism": 3})),
        ('视觉设计师', '设计UI/UX界面，提升用户体验和视觉效果。', '网易', '设计岗', '杭州', 18, 28, json.dumps({"openness": 9, "conscientiousness": 7, "extraversion": 6, "agreeableness": 7, "neuroticism": 3})),
        ('运营专员', '负责社区运营和用户增长，分析数据优化策略。', '快手', '运营岗', '上海', 15, 25, json.dumps({"openness": 8, "conscientiousness": 7, "extraversion": 9, "agreeableness": 8, "neuroticism": 4})),
        ('机器学习工程师', '开发和优化机器学习模型，解决真实业务问题。', '百度', '技术岗', '北京', 35, 60, json.dumps({"openness": 9, "conscientiousness": 9, "extraversion": 4, "agreeableness": 5, "neuroticism": 2})),
        ('市场营销经理', '制定营销策略，管理营销团队，提升品牌影响力。', '小米', '市场岗', '深圳', 20, 35, json.dumps({"openness": 8, "conscientiousness": 7, "extraversion": 8, "agreeableness": 6, "neuroticism": 3})),
    ]
    
    for name, description, company, category, city, salary_min, salary_max, traits in jobs_data:
        cursor.execute("""
            INSERT INTO jobs (name, description, company, category, city, salary_min, salary_max, required_traits, creator_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, description, company, category, city, salary_min, salary_max, traits, hr_user_id))
    
    connection.commit()
    print("✅ 数据初始化成功！")
    print(f"✅ 创建 {len(jobs_data)} 个岗位")
    print("✅ 测试用户:")
    print("  - alice (HR) / password: hashed_password_alice")
    print("  - bob (候选人) / password: hashed_password_bob")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    print("\n提示: 确保MySQL已启动，且存在hr_matching数据库")
    print("创建数据库的SQL: CREATE DATABASE hr_matching DEFAULT CHARSET=utf8mb4")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
