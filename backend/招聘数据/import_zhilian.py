# -*- coding: utf-8 -*-
"""
高性能导入脚本：1255万条智联招聘数据导入 MySQL
"""

import pandas as pd
import os
from datetime import datetime
from tqdm import tqdm
import sys
from pathlib import Path
import hashlib
import json
import logging
import time

# 设置日志
log_file = Path(__file__).parent / f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"日志文件: {log_file}")

# 加载项目配置
backend_path = str(Path(__file__).parent.parent)
sys.path.insert(0, backend_path)

from database import SessionLocal, engine, Base
from models.job_raw_data import JobRawData
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


def parse_salary(salary_str):
    """将字符串薪资转为浮点数（单位：元）"""
    if not salary_str or pd.isna(salary_str):
        return None
    try:
        return float(salary_str)
    except:
        return None


def parse_date(date_str):
    """解析日期字符串"""
    if not date_str or pd.isna(date_str):
        return None
    try:
        # 尝试不同的日期格式
        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d']:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except:
                pass
        return None
    except:
        return None


def import_zhilian_data(csv_path, batch_size=50000, start_row=0, max_rows=None):
    """
    分批导入智联招聘数据（带自动续断和错误恢复）
    
    Args:
        csv_path: CSV 文件路径
        batch_size: 每批处理行数（默认 5 万行）
        start_row: 从第几行开始（用于续断）
        max_rows: 最多导入多少行（None = 全部）
    """
    
    logger.info("\n" + "=" * 70)
    logger.info("开始导入智联招聘数据")
    logger.info("=" * 70)
    
    # 确保表存在
    Base.metadata.create_all(engine)
    logger.info("[OK] 表结构已创建")
    
    db = SessionLocal()
    total_imported = start_row
    total_duplicates = 0
    total_errors = 0
    total_fallback = 0  # 降级到逐条插入的数量
    
    try:
        # 预加载所有已有的source_id到内存（用于快速查询）
        logger.info("正在加载已导入的数据ID...")
        existing_ids = set()
        try:
            for (id_val,) in db.query(JobRawData.source_id).all():
                existing_ids.add(id_val)
        except Exception as e:
            logger.warning(f"加载已有ID出错: {e}，继续...")
        logger.info(f"已加载 {len(existing_ids):,} 条已有记录的ID")
        
        # 分批读取 CSV
        logger.info("开始读取CSV文件...")
        chunks = pd.read_csv(
            csv_path,
            encoding='utf-8',
            low_memory=False,
            chunksize=batch_size,
            skiprows=range(1, start_row + 1) if start_row > 0 else None,
            nrows=max_rows
        )
        
        pbar = tqdm(chunks, desc="导入进度", unit="批")
        for chunk_idx, df in enumerate(pbar):
            
            records_to_insert = []
            batch_ids = set()  # 当前批次的ID集合，用于检测批内重复
            
            for idx, row in df.iterrows():
                try:
                    # 生成唯一ID用于去重（MD5 哈希）
                    unique_str = f"{row.get('企业名称', '')}#{row.get('招聘岗位', '')}#{row.get('工作城市', '')}#{row.get('最低月薪', '')}#{row.get('招聘发布年份', 'na')}#{row.get('招聘发布日期', 'na')}"
                    source_id = hashlib.md5(unique_str.encode()).hexdigest()
                    
                    # 检查是否已存在（数据库或当前批次）
                    if source_id in existing_ids or source_id in batch_ids:
                        total_duplicates += 1
                        continue
                    
                    # 验证必要字段
                    company_name = str(row.get('企业名称', '')).strip()[:300]
                    position_name = str(row.get('招聘岗位', '')).strip()[:200]
                    city = str(row.get('工作城市', '')).strip()[:50]
                    
                    if not company_name or not position_name or not city:
                        total_errors += 1
                        continue
                    
                    # 构建记录
                    record = {
                        'company_name': company_name,
                        'position_name': position_name,
                        'city': city,
                        'district': str(row.get('工作区域', '')).strip()[:100] if row.get('工作区域') else None,
                        'salary_min': parse_salary(row.get('最低月薪')),
                        'salary_max': parse_salary(row.get('最高月薪')),
                        'job_description': str(row.get('职位描述', '')).strip() if row.get('职位描述') else None,
                        'education': str(row.get('学历要求', '')).strip()[:50] if row.get('学历要求') else None,
                        'experience': str(row.get('要求经验', '')).strip()[:100] if row.get('要求经验') else None,
                        'recruit_count': int(row.get('招聘人数', 0)) if row.get('招聘人数') and str(row.get('招聘人数')).isdigit() else None,
                        'job_category': str(row.get('招聘类别', '')).strip()[:100] if row.get('招聘类别') else None,
                        'job_type': str(row.get('初级分类', '')).strip()[:100] if row.get('初级分类') else None,
                        'company_location': str(row.get('公司地点', '')).strip()[:300] if row.get('公司地点') else None,
                        'work_location': str(row.get('工作地点', '')).strip()[:300] if row.get('工作地点') else None,
                        'publish_date': parse_date(row.get('招聘发布日期')),
                        'end_date': parse_date(row.get('招聘结束日期')),
                        'publish_year': int(row.get('招聘发布年份', 0)) if row.get('招聘发布年份') and str(row.get('招聘发布年份')).isdigit() else None,
                        'end_year': int(row.get('招聘结束年份', 0)) if row.get('招聘结束年份') and str(row.get('招聘结束年份')).isdigit() else None,
                        'source': 'zhilian',
                        'source_id': source_id,
                    }
                    
                    records_to_insert.append(record)
                    batch_ids.add(source_id)
                    
                except Exception as e:
                    total_errors += 1
                    if total_errors <= 5:  # 只显示前 5 条错误
                        logger.warning(f"行 {total_imported + idx} 构建失败: {str(e)[:80]}")
                    continue
            
            # 批量插入
            if records_to_insert:
                try:
                    db.bulk_insert_mappings(JobRawData, records_to_insert)
                    db.commit()
                    # 更新内存中的已有ID集合
                    existing_ids.update(batch_ids)
                    total_imported += len(records_to_insert)
                    pbar.update()
                except Exception as batch_err:
                    # 批量插入失败，降级到逐条插入
                    db.rollback()
                    logger.warning(f"批量插入失败（{len(records_to_insert)}条），切换到逐条模式")
                    
                    fallback_count = 0
                    for record in records_to_insert:
                        try:
                            db.bulk_insert_mappings(JobRawData, [record])
                            db.commit()
                            total_imported += 1
                            fallback_count += 1
                            existing_ids.add(record['source_id'])
                        except Exception as record_err:
                            db.rollback()
                            total_errors += 1
                            if total_errors <= 5:
                                logger.debug(f"单条插入失败: {str(record_err)[:80]}")
                    
                    total_fallback += fallback_count
                    logger.info(f"完成降级处理: {fallback_count}/{len(records_to_insert)} 条成功")
                    pbar.update()
                
                pbar.set_description(f"进度 (已入库: {total_imported:,}, 降级: {total_fallback:,})")
        
        logger.info("\n" + "=" * 70)
        logger.info("导入完成！")
        logger.info("=" * 70)
        logger.info(f"[OK] 成功导入: {total_imported:,} 条")
        logger.info(f"[DUP] 重复记录: {total_duplicates:,} 条")
        logger.info(f"[FALLBACK] 降级提交: {total_fallback:,} 条")
        logger.info(f"[ERR] 跳过错误: {total_errors:,} 条")
        logger.info(f"总计处理: {total_imported + total_duplicates + total_errors:,} 条\n")
        
        # 统计信息
        try:
            db_count = db.query(JobRawData).count()
            logger.info(f"数据库中现有记录: {db_count:,} 条")
        except Exception as e:
            logger.error(f"查询数据库记录数出错: {e}")
        
    except Exception as e:
        logger.error(f"导入过程异常: {e}")
        try:
            db.rollback()
        except:
            pass
    finally:
        try:
            db.close()
        except:
            pass


def create_jobs_from_raw(batch_size=1000, min_salary=0):
    """
    从原始数据表筛选高质量记录放入 jobs 表
    
    条件：
    - 有完整的职位描述（job_description 不为空）
    - 薪资范围合理（salary_min > 0）
    - 不为空记录
    """
    from models.job import Job
    
    print("\n" + "=" * 70)
    print("从原始数据筛选到 jobs 表")
    print("=" * 70)
    
    Base.metadata.create_all(engine)
    db = SessionLocal()
    
    try:
        # 查询符合条件的记录
        raw_jobs = db.query(JobRawData).filter(
            JobRawData.is_processed == 0,
            JobRawData.job_description.isnot(None),
            JobRawData.salary_min > min_salary,
            JobRawData.position_name.isnot(None)
        ).all()
        
        print(f"找到 {len(raw_jobs):,} 条符合条件的记录\n")
        
        jobs_to_insert = []
        processed_ids = []
        
        for raw in raw_jobs:
            # 生成默认的 required_traits（从岗位类型推断）
            required_traits = {
                "外向性": 6,
                "宜人性": 6,
                "尽责性": 8,
                "神经质": 3,
                "开放性": 7
            }
            
            job = Job(
                name=raw.position_name,
                description=raw.job_description,
                company=raw.company_name,
                category=raw.job_type or '其他',
                city=raw.city or '全国',
                salary_min=raw.salary_min / 1000 if raw.salary_min else 0,  # 元转 K
                salary_max=raw.salary_max / 1000 if raw.salary_max else 0,
                required_traits=required_traits,
                salary_desc=f"{raw.salary_min/1000:.0f}k-{raw.salary_max/1000:.0f}k" if raw.salary_min and raw.salary_max else None,
                experience=raw.experience,
                degree=raw.education,
                industry=raw.job_category,
                address=raw.work_location,
                source='zhilian',
                source_id=raw.source_id,
            )
            
            jobs_to_insert.append(job)
            processed_ids.append(raw.id)
        
        # 批量插入到 jobs 表
        if jobs_to_insert:
            db.add_all(jobs_to_insert)
            db.commit()
            print(f"[OK] 已插入 {len(jobs_to_insert):,} 条到 jobs 表\n")
            
            # 标记原始记录为已处理
            db.query(JobRawData).filter(JobRawData.id.in_(processed_ids)).update(
                {JobRawData.is_processed: 1}
            )
            db.commit()
            print(f"[OK] 已标记 {len(processed_ids):,} 条为已处理\n")
        
    except Exception as e:
        print(f"[ERROR] 出错: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    csv_file = r"D:\Desktop\graduation-project\backend\招聘数据\save-data\智联招聘数据库2016-2025.7.csv"
    
    if not os.path.exists(csv_file):
        logger.error(f"文件不存在: {csv_file}")
        sys.exit(1)
    
    # 显示当前数据库状态
    try:
        from sqlalchemy import func
        db_temp = SessionLocal()
        current_count = db_temp.query(func.count(JobRawData.id)).scalar() or 0
        db_temp.close()
        logger.info(f"\n当前数据库状态: boss_raw_data 有 {current_count:,} 条记录")
    except Exception as e:
        logger.warning(f"无法查询数据库状态: {e}")
        current_count = 0
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        # 方案1：导入原始数据（第一次运行完整导入，或指定行号续断）
        logger.info("\n请选择操作:")
        logger.info("1. 导入原始数据（10万条测试）")
        logger.info("2. 导入原始数据（全量，从现有记录续断）")
        logger.info("3. 从原始数据筛选到 jobs 表")
        logger.info("4. 重新导入所有数据（清空后重新开始）")
        choice = input("\n请输入选择 (1/2/3/4): ").strip()
    
    if choice == '1':
        logger.info("\n执行: 导入10万条记录（测试）")
        import_zhilian_data(csv_file, batch_size=50000, max_rows=100000)
    elif choice == '2':
        logger.info(f"\n执行: 从现有 {current_count:,} 条记录后续断导入")
        import_zhilian_data(csv_file, batch_size=50000, start_row=current_count)
    elif choice == '3':
        logger.info("\n执行: 从原始数据筛选到 jobs 表")
        create_jobs_from_raw()
    elif choice == '4':
        logger.warning("\n清空 boss_raw_data 表...")
        db = SessionLocal()
        try:
            db.query(JobRawData).delete()
            db.commit()
            logger.info("[OK] 已清空所有数据")
        except Exception as e:
            logger.error(f"清空失败: {e}")
            db.rollback()
        finally:
            db.close()
        
        logger.info("\n重新开始完整导入...")
        import_zhilian_data(csv_file, batch_size=50000)
    else:
        logger.error("❌ 无效选择")
