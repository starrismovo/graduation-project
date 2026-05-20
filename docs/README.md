# 项目文档索引

本文档用于说明项目 Markdown 文件的整理规则。当前目录将文档分为“当前文档”“论文材料”和“历史归档”三类，便于后续开发、论文撰写与答辩准备。

## 当前文档

[current](current) 目录保留当前仍建议查阅的项目文档，包括系统概览、架构设计、接口说明、算法说明、环境配置、启动测试与关键模块说明。

建议优先阅读：

- [current/README_PROJECT.md](current/README_PROJECT.md)
- [current/START_HERE.md](current/START_HERE.md)
- [current/PROJECT_SUMMARY.md](current/PROJECT_SUMMARY.md)
- [current/SYSTEM_FUNCTIONAL_ARCHITECTURE.md](current/SYSTEM_FUNCTIONAL_ARCHITECTURE.md)
- [current/SYSTEM_IMPLEMENTATION_DESCRIPTION.md](current/SYSTEM_IMPLEMENTATION_DESCRIPTION.md)
- [current/BACKEND_API_SPECIFICATION.md](current/BACKEND_API_SPECIFICATION.md)
- [current/FRONTEND_BACKEND_INTEGRATION.md](current/FRONTEND_BACKEND_INTEGRATION.md)
- [current/TEST_AND_VALIDATION_GUIDE.md](current/TEST_AND_VALIDATION_GUIDE.md)

## 论文材料

[thesis](thesis) 目录保留本科毕业论文相关材料，包括章节草稿、整合稿、模块化改写稿与测试计划。该目录中的文档应保持本科工科论文风格，避免改写为 README、接口文档或软件说明书。

## 历史归档

[archive](archive) 目录用于保存项目迭代过程中产生的阶段性文档。这些文件不建议作为当前实现依据，但可用于追溯历史问题、修复过程和阶段交付记录。

归档目录说明：

- [archive/api-routes](archive/api-routes)：接口路由清单、核验与更新记录。
- [archive/backend](archive/backend)：后端、数据库与迁移相关历史记录。
- [archive/frontend](archive/frontend)：前端页面、集成、白屏调试与交互调整记录。
- [archive/jobs-and-hr](archive/jobs-and-hr)：候选人、HR、职位与投递流程相关迭代记录。
- [archive/resume-ocr](archive/resume-ocr)：简历解析、OCR 与 PaddleOCR 相关记录。
- [archive/fixes](archive/fixes)：错误诊断、快速修复和问题排查记录。
- [archive/reports](archive/reports)：阶段总结、完成报告、验证报告和交付报告。
- [archive/quick-guides](archive/quick-guides)：临时快速启动、快速参考和短期操作指南。
- [archive/implementation-notes](archive/implementation-notes)：其他实现说明、检查清单和后续计划。

## 维护规则

新增项目说明优先放入 `docs/current`。论文写作材料放入 `docs/thesis`。阶段性修复记录、一次性检查清单和临时操作指南放入 `docs/archive` 对应子目录。除 `README.md` 和 `AGENTS.md` 外，原则上不再向仓库根目录新增 Markdown 文件。

