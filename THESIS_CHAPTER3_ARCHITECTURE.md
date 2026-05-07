# 3 基于AI智能体的人岗匹配评估系统总体设计


3.1 系统目标与设计原则
3.1.1 系统目标
系统的总体目标是构建一个面向招聘评估场景的 AI 多智能体心理特质评估与人岗匹配系统。系统需要实现以下三个子目标：
1. 完整的多维评估：通过多个 AI 智能体的协同评估，从专业能力、沟通与稳定性、岗位适配与发展潜力等多个维度对候选人进行系统评估，克服传统单一面试官的主观性与维度不足问题。
2. 科学的心理特质刻画：基于大五人格理论构建分层人格模型，将候选人的人格特质分为基础人格（稳定特征）与场景人格（情境相关特征），为人岗匹配提供更精细的心理基础。
3. 精准的人岗匹配支持：通过岗位模板与岗位实例的双层建模，实现岗位需求的通用表示与个性化刻画，为候选人与企业提供基于多维特征的科学匹配建议。
3.1.2 设计原则
系统的设计遵循以下原则：
原则 1：可解释性优先：每一个关键决策都应该能够向用户清晰地说明理由。即使是复杂的人格推断或匹配计算，也应该能追溯到原始的面试证据。这不仅提升了系统的可信度，也便于用户对结果进行质证与反馈。
原则 2：一致性与稳定性保证：系统应该通过工程机制（如后端集中计算、会话隔离、统一标识）确保评估过程与结果的一致性。同一候选人的重复评估应该得到基本一致的结果，不同会话间的数据应该完全隔离，不存在污染或串扰。
原则 3：模块化与可扩展性:系统的各个模块（多 Agent 协同、人格评估、岗位建模、匹配计算）应该相对独立，便于后续的替换、升级或扩展。例如，大语言模型服务的升级不应影响人格计算逻辑；新的岗位类别的加入不应改变系统架构。
原则 4：用户导向:系统的设计应该从候选人与企业的实际需求出发。前端交互应该简洁直观，专业术语应该有清晰解释，最终的报告应该既有学术严谨性，也有实践可操作性。
3.2 功能需求分析
3.2.1 用户角色与需求
系统主要面向两类用户角色：候选人和企业HR。候选人侧关注岗位浏览、参与评估和查看报告；企业HR侧关注岗位管理、候选人管理、评估结果查看与招聘分析。
 
图3-4 系统用户角色与需求对照图
说明：本图展示了AITEJM系统的两类核心用户角色及其对应的功能需求。候选人主要关注自我评估与岗位适配信息获取；企业HR侧重于岗位管理、候选人评估与决策支持。两类用户的需求既相互独立，又通过评估流程紧密关联，共同支撑系统的业务闭环。
3.2.2 核心功能模块
本系统围绕人岗匹配评估流程，构建了六个核心功能模块，涵盖用户管理、岗位管理、面试评估、人格建模、匹配计算与结果输出等关键环节。各模块相互协同，共同支撑系统的完整业务闭环。
模块名称	主要功能
用户与身份管理	注册/登录/登出、身份验证、权限控制、个人信息管理
岗位与招聘管理	岗位实例发布、岗位需求结构化维护、招聘公告管理、岗位-候选人关联
多Agent协同面试引擎	评估会话创建管理、interviewer_agent/evaluator_agent/decision_agent 协同、问答历史记录、会话级数据隔离
人格特质评估与建模	基础人格推断与评分、场景人格推断、人格维度量化与可视化、评分历史管理
人岗匹配评估	候选人与岗位需求对标分析、多维度匹配度计算、候选人推荐与匹配可解释性生成
报告生成与展示	综合评估报告自动生成、心理特质画像可视化、匹配度图表展示、报告查看与管理
3.2.3 用户交互流程
候选人的评估流程和HR的评估流程

 
图3-5 用户交互流程图（候选人与HR）
说明：上图为候选人评估流程，涵盖从登录、岗位浏览、多Agent面试与评估（interviewer_agent → evaluator_agent → decision_agent）到报告查看的全过程；下图为HR招聘流程，涵盖岗位发布、候选人邀请、报告生成与结果分析。两流程通过“候选人参与评估”节点衔接，构成完整的业务闭环。
3.3 总体架构设计
3.3.1 架构风格与分层
 
图3-1 系统功能模块分层架构图
图3-2 系统总体架构图
系统采用三层架构：展示层提供用户交互界面；业务逻辑层封装核心服务（人格评估、人岗匹配、报告生成、文本分析）；数据层基于MySQL实现持久化存储。各层间通过RESTful API与ORM进行通信。






3.4 核心数据模型设计
3.4.1 核心实体设计
系统的核心数据模型包括以下七类实体。需要说明的是，本节描述的是论文层面的逻辑数据模型；在当前工程实现中，Role Template（岗位模板）尚未独立为物理数据表，岗位模板层信息主要由 Job（岗位实例）及其岗位需求、技能需求和人格需求等结构化字段承载。
（1）User 实体
User 实体用于描述系统中的用户信息，包括候选人和招聘人员。该实体不仅用于身份认证与权限控制，同时作为评估会话与岗位数据的关联基础。
字段	类型	说明
id	UUID	主键
username	String	用户名
email	String	邮箱
user_type	Enum	用户类型 (candidate/hr)
hashed_password	String	密码哈希
created_at	DateTime	创建时间
实体 2：Role Template（岗位模板）
字段	类型	说明
role_id	UUID	主键
role_name	String	岗位名称 (如"后端工程师")
role_category	String	岗位类别
required_skills	JSON	必需技能列表
personality_requirements	JSON	人格需求 (Big Five)
work_environment	JSON	工作环境特征
实体 3：Job（岗位实例）
字段	类型	说明
job_id	UUID	主键
role_id	FK	关联的岗位模板
company_name	String	公司名称
job_title	String	具体职位
job_description	Text	岗位描述
adjustments	JSON	相对模板的调整项
created_by	FK	HR 创建者
created_at	DateTime	发布时间
实体 4：AssessmentSession（评估会话）
字段	类型	说明
session_id	UUID	主键 (会话隔离)
candidate_id	FK	候选人
job_id	FK	岗位实例
status	Enum	会话状态 (ongoing/completed/abandoned)
created_at	DateTime	开始时间
completed_at	DateTime	完成时间
实体 5：DialogueHistory（对话历史）
字段	类型	说明
dialogue_id	UUID	主键
session_id	FK	关联的会话
agent_type	String	Agent 类型 (technical/hr/manager)
question	Text	问题
answer	Text	候选人回答
timestamp	DateTime	时间戳
实体 6：TraitScores（人格评分）
字段	类型	说明
score_id	UUID	主键
session_id	FK	关联的会话
candidate_id	FK	候选人
basic_traits	JSON	基础人格评分 {extroversion, agreeableness, ...}
scenario_traits	JSON	场景人格评分（针对特定岗位）
agent_source	String	来源 Agent
timestamp	DateTime	计算时间
实体 7：EvaluationResult（评估结果）
字段	类型	说明
result_id	UUID	主键
session_id	FK	关联的会话
candidate_id	FK	候选人
job_id	FK	岗位
match_score	Float	综合匹配度 (0-100)
ability_scores	JSON	各能力维度评分
trait_comparison	JSON	基础人格/场景人格 vs 岗位需求
strengths	Text	优势分析
gaps	Text	改进空间
recommendations	Text	个性化建议
report_content	JSON	完整报告内容
created_at	DateTime	生成时间
3.4.2 实体关系设计
系统各实体之间的关系如图 3-6 所示。
 
3.5 端到端评估流程设计
3.5.1 系统流程总览
系统整体评估流程如图 3-7 所示，核心阶段包括：岗位创建与发布、候选人参与、多Agent顺序面试、后端集中计算、报告生成与查看。
 
3.5.2 关键数据流说明
阶段1：初始化与会话创建
系统首先接收候选人 ID、岗位 ID 及其基本信息，然后创建一次评估会话（AssessmentSession），加载岗位实例及其结构化需求信息，并完成 Agent 对话上下文的初始化。岗位模板信息在当前实现中主要通过岗位通用字段与需求字段间接表达。
阶段2：多Agent顺序面试
按照“interviewer_agent → evaluator_agent → decision_agent”的协作链路组织多Agent面试与评估。各 Agent 根据当前岗位需求以及历史对话记录生成或分析问题，并将问答过程记录在对话历史（DialogueHistory）中。同时，系统提取候选人的能力与人格线索，并更新各维度的中间评分（TraitScores）。
阶段3：后端评分与匹配度计算
系统查询当前会话下所有 Agent 的评分结果，融合得到基础人格特征；再结合岗位要求推断出候选人在本岗位下的场景人格；进而计算能力匹配度、人格匹配度和期待匹配度，最终得出综合匹配度，并将所有结果写入评估结果（EvaluationResult）。
阶段4：报告生成与前端展示
基于 EvaluationResult 构建可解释性链路，包括决策依据、各维度得分解释、证据引用和综合建议。同时渲染雷达图、柱状图等可视化图表，生成最终匹配报告，供前端界面展示给候选人及 HR 查看。
