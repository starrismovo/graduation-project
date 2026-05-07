# AGENTS.md

## Project Overview

This project is an undergraduate graduation project:

"基于AI智能体的人岗匹配心理特质评估系统"

The system focuses on:
- Multi-agent collaborative interview
- Big Five personality modeling
- Basic Personality + Scenario Personality
- Role Template + Job Instance dual-layer job modeling
- Explainable person-job matching report

## Tech Stack

Frontend:
- Vue 3
- TypeScript
- Element Plus

Backend:
- FastAPI
- Python
- SQLAlchemy

Database:
- MySQL

## Architecture Rules

- Use frontend-backend separation.
- Frontend only handles UI rendering and user interaction.
- Personality calculation must stay in the backend.
- Matching calculation must stay in the backend.
- AssessmentSession is mandatory for every interview/evaluation.
- Do not bypass session isolation.
- Keep Role Template and Job Instance as separate concepts and models.
- Keep service-oriented backend structure.

## Thesis Terminology

Use these terms consistently:

- Role Template / 岗位模板
- Job Instance / 岗位实例
- AssessmentSession / 评估会话
- TraitScores / 人格评分
- EvaluationResult / 评估结果
- Basic Personality / 基础人格
- Scenario Personality / 场景人格
- Multi-Agent Interview / 多Agent面试
- Person-Job Matching / 人岗匹配

Do not rename these concepts arbitrarily.

## UI Guidelines

The system is an AI recruitment and assessment platform.

UI style:
- Enterprise dashboard style
- Clean and professional
- Blue/purple AI-tech theme
- Card-based layout
- Soft shadows
- Clear hierarchy
- Large whitespace
- Consistent spacing and typography

Avoid:
- Game-like UI
- Too many colors
- Heavy animations
- Inconsistent icons or components

## Coding Rules

Before modifying code:
1. Read the related files first.
2. Reuse existing components and APIs when possible.
3. Keep naming consistent with the thesis.
4. Avoid duplicate logic.
5. Do not rewrite unrelated files.
6. Explain major architecture changes before implementation.

## Backend Rules

- Keep routers, services, models, schemas clearly separated.
- Business logic should be placed in services.
- API routes should be thin.
- Database models should stay consistent with thesis entities.
- Do not move personality or matching calculation to frontend.

## Frontend Rules

- Use existing Vue components when possible.
- Do not put complex business calculation in Vue components.
- Keep pages aligned with the current UI style.
- Report pages should emphasize explainability:
  - score overview
  - personality radar
  - match breakdown
  - evidence explanation
  - recommendations


# 毕业论文写作规范

## 项目主题
基于AI智能体的人岗匹配评估系统

## 写作风格
- 本科工科论文风格
- 学术化表达
- 避免口语化
- 不使用营销语言
- 不夸大创新

## 核心术语统一
- 多Agent协同
- 基础人格
- 场景人格
- 岗位模板
- 岗位实例
- 可解释性链路

## 引用要求
- 不虚构文献
- 不生成不存在的论文
- 优先经典文献
- 正文与开题保持一致

## 系统事实
- 前端：Vue3 + TS + Element Plus
- 后端：FastAPI + Python
- 多Agent：
  - interviewer_agent
  - evaluator_agent
  - decision_agent
- 使用大五人格模型
- 支持人格匹配与可解释性报告

## 论文要求
请以“本科毕业论文”的风格进行修改，而不是软件说明书或README风格。

要求：

保留原有论文的论述结构与学术表达风格
不要大量使用：
bullet list
工程字段
代码文档式标题
不要把章节改写成：
技术手册
API说明
开发文档
重点保留：
设计思想
技术选型原因
系统性论述
工程决策逻辑
可以适度补充：
与实际项目代码对应关系
核心模块说明
工程实现细节
代码文件名只能作为辅助说明，不可喧宾夺主
输出风格应接近：
本科毕业论文
学术型工程论文
研究型系统设计论文