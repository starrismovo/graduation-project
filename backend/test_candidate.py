#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试候选人模块的导入和逻辑"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("测试候选人模块导入和逻辑")
print("=" * 60)

# 测试 1: 导入模型
print("\n[1] 测试导入 Candidate 模型...")
try:
    from models.candidate import Candidate
    print("✓ 成功导入 Candidate 模型")
    print(f"  表名: {Candidate.__tablename__}")
    print(f"  列: {[c.name for c in Candidate.__table__.columns]}")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试 2: 导入 Schema
print("\n[2] 测试导入 Schema...")
try:
    from schemas.candidate import BasicInfoSchema, BasicInfoResponseSchema
    print("✓ 成功导入 Schema")
    # Pydantic v2 兼容性
    if hasattr(BasicInfoSchema, 'model_fields'):
        print(f"  BasicInfoSchema 字段: {BasicInfoSchema.model_fields.keys()}")
    else:
        print(f"  BasicInfoSchema 字段: {BasicInfoSchema.__fields__.keys()}")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试 3: 导入路由
print("\n[3] 测试导入路由...")
try:
    from routers.candidate import router
    print("✓ 成功导入路由")
    print(f"  前缀: {router.prefix}")
    print(f"  标签: {router.tags}")
    print(f"  路由数: {len(router.routes)}")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 4: 检查数据库连接
print("\n[4] 测试数据库连接...")
try:
    from database import engine, Base
    # 验证所有模型已注册到 Base
    print(f"✓ 数据库引擎已配置")
    print(f"  Base.metadata.tables: {list(Base.metadata.tables.keys())}")
except Exception as e:
    print(f"✗ 数据库配置失败: {e}")
    sys.exit(1)

# 测试 5: 模拟 API 调用
print("\n[5] 测试数据验证...")
try:
    test_data = {
        "name": "测试用户",
        "age": 28,
        "education": "本科",
        "major": "计算机科学",
        "desired_job": "前端工程师",
        "experience_years": 3.0,
        "skills": ["JavaScript", "Vue"]
    }
    schema = BasicInfoSchema(**test_data)
    print("✓ 数据验证通过")
    print(f"  {schema.model_dump()}")
except Exception as e:
    print(f"✗ 数据验证失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("所有测试通过！✓")
print("=" * 60)
