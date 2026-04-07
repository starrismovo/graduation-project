# -*- coding: utf-8 -*-
"""
从boss_raw_data表精选代表性数据到jobs表
用于论文演示系统，选择3000+条高质量职位
"""

import sys
from pathlib import Path
from datetime import datetime
import logging

# 设置日志
log_file = Path(__file__).parent / f"select_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

backend_path = str(Path(__file__).parent.parent)
sys.path.insert(0, backend_path)

from database import SessionLocal, engine, Base
from models.job_raw_data import JobRawData
from models.job import Job
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

def select_sample_jobs():
    """精选高质量职位数据"""
    
    db = SessionLocal()
    Base.metadata.create_all(engine)
    
    print("\n" + "="*70)
    print("精选代表性职位数据用于论文系统演示")
    print("="*70)
    
    try:
        # 1. 一级城市 + 热门职位 + 合理薪资 的组合筛选
        logger.info("开始筛选数据...")
        
        # 获取符合条件的原始数据，随机但均衡地选择
        raw_jobs = db.execute(text('''
            SELECT * FROM boss_raw_data 
            WHERE 
                is_processed = 0
                AND job_description IS NOT NULL
                AND salary_min > 5000
                AND position_name IS NOT NULL
                AND city IN ('北京', '上海', '深圳', '杭州', '广州', '成都', '武汉', '郑州')
                AND salary_min < 50000  -- 排除过高的职位
            ORDER BY RAND()
            LIMIT 5000
        ''')).fetchall()
        
        print(f"\n找到 {len(raw_jobs):,} 条精选优质记录\n")
        logger.info(f"精选了 {len(raw_jobs):,} 条记录")
        
        jobs_to_insert = []
        processed_ids = []
        
        for idx, raw in enumerate(raw_jobs, 1):
            # boss_raw_data 列索引映射：
            # [0] id, [1] company_name, [2] position_name, [3] city
            # [4] district, [5] salary_min, [6] salary_max, [7] job_description
            # [8] education, [9] experience, [10] recruit_count, [11] job_category
            # [12] job_type, [13] company_location, [14] work_location
            
            position_name = raw[2] if raw[2] else '其他'
            if len(position_name) > 100:
                position_name = position_name[:100]
            company_name = raw[1] if raw[1] else '其他公司'
            if len(company_name) > 100:
                company_name = company_name[:100]
            city = raw[3] if raw[3] else '全国'
            description = raw[7] if raw[7] else '职位描述'
            if len(description) > 2000:
                description = description[:2000]
            education = raw[8] if raw[8] else '其他'
            job_category = raw[11] if raw[11] and str(raw[11]).lower() != 'nan' else '其他'
            
            # 根据职位名称推断五大人格特征
            required_traits = extract_traits(position_name)
            
            # 处理薪资字段
            try:
                salary_min_val = float(raw[5]) if raw[5] else 0
                salary_max_val = float(raw[6]) if raw[6] else 0
                # 处理NaN值
                if salary_min_val != salary_min_val:
                    salary_min_val = 0
                if salary_max_val != salary_max_val:
                    salary_max_val = 0
            except (TypeError, ValueError):
                salary_min_val = 0
                salary_max_val = 0
            
            # 转换为K单位（原数据是元）
            salary_min_k = salary_min_val / 1000
            salary_max_k = salary_max_val / 1000
            
            # 确保薪资合理
            if salary_min_k <= 0:
                salary_min_k = 8
            if salary_max_k <= 0 or salary_max_k <= salary_min_k:
                salary_max_k = salary_min_k + 5
            
            job = Job(
                name=position_name,
                description=description,
                company=company_name,
                category=job_category or education,
                city=city,
                salary_min=round(salary_min_k, 1),
                salary_max=round(salary_max_k, 1),
                required_traits=required_traits,
            )
            
            jobs_to_insert.append(job)
            processed_ids.append(raw[0])  # id
            
            if idx % 500 == 0:
                print(f"  处理进度: {idx:,} / {len(raw_jobs):,}")
        
        # 分批插入到 jobs 表（每500条一批，避免单条错误全部回滚）
        batch_size = 500
        total_inserted = 0
        total_failed = 0
        
        for i in range(0, len(jobs_to_insert), batch_size):
            batch = jobs_to_insert[i:i+batch_size]
            batch_ids = processed_ids[i:i+batch_size]
            try:
                db.add_all(batch)
                db.commit()
                total_inserted += len(batch)
                print(f"  批次 {i//batch_size+1}: 插入 {len(batch)} 条成功")
            except Exception as batch_err:
                db.rollback()
                # 逐条插入容错
                for j, job in enumerate(batch):
                    try:
                        db.add(job)
                        db.commit()
                        total_inserted += 1
                    except Exception:
                        db.rollback()
                        total_failed += 1
                print(f"  批次 {i//batch_size+1}: 部分失败，成功/失败未知")
            
            # 标记原始记录为已处理
            if batch_ids:
                db.execute(
                    text('UPDATE boss_raw_data SET is_processed = 1 WHERE id IN :ids'),
                    {'ids': tuple(batch_ids)}
                )
                db.commit()
        
        print(f"\n[✓] 已插入 {total_inserted:,} 条精选职位到 jobs 表")
        if total_failed > 0:
            print(f"[!] 跳过 {total_failed:,} 条失败记录")
        logger.info(f"已插入 {total_inserted:,} 条，失败 {total_failed:,} 条")
        
        # 显示统计
        stats = db.execute(text('''
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT city) as cities,
                COUNT(DISTINCT name) as positions,
                ROUND(AVG(salary_min), 0) as avg_salary_min,
                ROUND(AVG(salary_max), 0) as avg_salary_max
            FROM jobs
        ''')).fetchone()
        
        if stats:
            print("="*70)
            print("精选后 jobs 表统计:")
            print(f"  总职位数: {stats[0]:,}")
            print(f"  城市数: {stats[1]:,}")
            print(f"  职位类型: {stats[2]:,}")
            print(f"  平均薪资: {stats[3]:.0f}k - {stats[4]:.0f}k")
            print("="*70 + "\n")
            
            logger.info(f"最终统计: {stats[0]:,}条职位，{stats[1]:,}个城市")
        
    except Exception as e:
        logger.error(f"错误: {e}")
        print(f"\n[✗] 出错: {e}\n")
    finally:
        db.close()


def extract_traits(position_name):
    """根据职位名称推断五大人格特征"""
    
    traits = {
        "外向性": 5,  # 默认中等水平
        "宜人性": 5,
        "尽责性": 6,
        "神经质": 4,
        "开放性": 5
    }
    
    pos_lower = position_name.lower()
    
    # 销售/市场相关 -> 高外向性
    if any(x in pos_lower for x in ['销售', '市场', '商务', '客户', 'sales', 'marketing']):
        traits["外向性"] = 8
        traits["宜人性"] = 7
    
    # 管理/领导相关 -> 高外向性、高尽责性
    elif any(x in pos_lower for x in ['经理', '主管', '总监', '副总', 'manager', 'director']):
        traits["外向性"] = 7
        traits["尽责性"] = 8
        
    # 财务/会计 -> 高尽责性、低神经质
    elif any(x in pos_lower for x in ['财务', '会计', '出纳', 'finance', 'accounting']):
        traits["尽责性"] = 8
        traits["神经质"] = 3
        traits["开放性"] = 4
    
    # 技术/工程相关 -> 高开放性、高尽责性、低外向性
    elif any(x in pos_lower for x in ['工程师', '技术', '开发', '程序', 'engineer', 'developer', 'tech']):
        traits["开放性"] = 8
        traits["尽责性"] = 7
        traits["外向性"] = 4
    
    # HR/行政 -> 宜人性高
    elif any(x in pos_lower for x in ['人力', 'hr', '行政', '招聘']):
        traits["宜人性"] = 8
        traits["尽责性"] = 7
    
    # 产品/设计 -> 开放性高
    elif any(x in pos_lower for x in ['产品', '设计', '产品经理', 'product', 'design']):
        traits["开放性"] = 8
        traits["尽责性"] = 7
    
    return traits


if __name__ == '__main__':
    select_sample_jobs()
    print("\n✓ 精选完成！系统已准备好进行演示\n")
