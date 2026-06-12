class PromptTemplates:

    TEST_POINT_ANALYZE = """你是一个专业的测试分析专家。请分析以下需求，提取出关键信息。

需求文本：
{requirement_text}

请从以下维度分析：
1. 核心功能点：该需求要实现什么功能？
2. 输入输出：涉及哪些输入和预期输出？
3. 约束条件：有哪些业务规则、限制条件？
4. 边界条件：有哪些边界值、极端情况需要考虑？
5. 关联依赖：是否依赖其他功能或外部系统？
6. 异常场景：可能出现的异常或错误情况？

请以JSON格式输出分析结果。"""

    TEST_POINT_ANALYZE_SCHEMA = """{
  "core_functions": ["功能1", "功能2"],
  "inputs_outputs": [{"input": "xxx", "output": "xxx"}],
  "constraints": ["约束1", "约束2"],
  "boundary_conditions": ["边界1", "边界2"],
  "dependencies": ["依赖1"],
  "exception_scenarios": ["异常1", "异常2"]
}"""

    TEST_POINT_GENERATE = """你是一个专业的测试设计专家。请根据以下需求分析和参考知识，生成测试点。

## 需求分析
{requirement_analysis}

## 参考知识
{knowledge_context}

## 原始需求
{requirement_text}

## 生成要求
1. 每个测试点应覆盖一个独立的测试维度
2. 测试点应包含：功能验证、边界条件、异常处理、兼容性等维度
3. 测试点名称应简洁明确，格式为"动词+对象+条件/场景"
4. 生成 3-7 个测试点
5. 如果有参考知识，请结合参考知识中的测试规范和领域经验"""

    TEST_POINT_GENERATE_SCHEMA = """{
  "test_points": [
    {
      "text": "测试点名称",
      "category": "功能验证|边界条件|异常处理|兼容性|性能|安全",
      "rationale": "为什么需要这个测试点（简述）"
    }
  ]
}"""

    TEST_POINT_REVIEW = """你是一个测试质量评审专家。请评审以下测试点列表的质量。

## 原始需求
{requirement_text}

## 需求分析
{requirement_analysis}

## 生成的测试点
{test_points_json}

## 评审维度（每项 1-5 分）
1. 完整性：是否覆盖了需求的所有关键功能点？
2. 独立性：测试点之间是否相互独立，无重复？
3. 可测性：每个测试点是否可以明确地设计测试用例？
4. 规范性：测试点命名是否规范，含义是否清晰？
5. 领域性：是否结合了领域知识（如有参考知识）？"""

    TEST_POINT_REVIEW_SCHEMA = """{
  "scores": {
    "completeness": 4,
    "independence": 5,
    "testability": 4,
    "standardization": 3,
    "domain_relevance": 4
  },
  "average_score": 4.0,
  "passed": true,
  "issues": [
    "缺少对并发场景的测试点"
  ],
  "suggestions": [
    "增加并发场景的测试点"
  ]
}"""

    TEST_POINT_REFINE = """你是一个专业的测试设计专家。请根据评审反馈优化以下测试点。

## 原始需求
{requirement_text}

## 当前测试点
{test_points_json}

## 评审反馈
- 评分：{average_score}/5
- 问题：{issues}
- 建议：{suggestions}

## 优化要求
1. 针对评审指出的问题逐一修正
2. 补充遗漏的测试维度
3. 合并或拆分重复/模糊的测试点
4. 保持测试点总数在 3-7 个"""

    TEST_POINT_REFINE_SCHEMA = """{
  "test_points": [
    {
      "text": "测试点名称",
      "category": "功能验证|边界条件|异常处理|兼容性|性能|安全",
      "rationale": "为什么需要这个测试点"
    }
  ]
}"""

    TEST_CASE_ANALYZE = """你是一个专业的测试用例设计专家。请分析以下测试点，确定用例设计方向。

## 需求上下文
{requirement_context}

## 测试点
- 名称：{test_point_text}
- 类别：{test_point_category}

请分析：
1. 测试意图：这个测试点要验证什么？
2. 需要的用例类型：需要哪些正例和反例？
3. 关键输入：测试需要哪些输入数据？
4. 预期行为：正常和异常情况下系统应如何响应？"""

    TEST_CASE_ANALYZE_SCHEMA = """{
  "test_intent": "测试意图描述",
  "case_types_needed": ["正例-正常流程", "正例-边界值", "反例-无效输入", "反例-异常中断"],
  "key_inputs": ["输入1", "输入2"],
  "expected_behaviors": ["正常行为", "异常行为"]
}"""

    TEST_CASE_GENERATE = """你是一个专业的测试用例设计专家。请根据测试点分析和参考知识，生成测试用例。

## 测试点分析
{test_point_analysis}

## 参考知识
{knowledge_context}

## 需求上下文
{requirement_context}

## 生成要求
1. 至少生成 2 个用例：1 个正例 + 1 个反例
2. 正例覆盖正常流程和主要边界值
3. 反例覆盖无效输入和异常场景
4. 每个用例包含完整的前置条件、步骤和预期结果
5. 步骤应具体可执行，预期结果应可验证
6. 如果有参考知识，请参考其中的用例编写规范和示例"""

    TEST_CASE_GENERATE_SCHEMA = """{
  "test_cases": [
    {
      "name": "用例名称",
      "property": "正例|反例",
      "pre_condition": "前置条件描述",
      "steps": [
        {
          "name": "步骤名称",
          "description": "具体操作描述",
          "stepExpectedResult": "该步骤的预期结果"
        }
      ]
    }
  ]
}"""

    TEST_CASE_QUALITY_CHECK = """你是一个测试用例质量校验专家。请校验以下测试用例的质量。

## 测试点
{test_point_text}

## 需求上下文
{requirement_context}

## 生成的测试用例
{test_cases_json}

## 校验维度（每项 1-5 分）
1. 完整性：每个用例是否有前置条件、步骤、预期结果？
2. 可执行性：步骤描述是否具体、可操作？
3. 可验证性：预期结果是否明确、可判定通过/失败？
4. 正反例均衡：是否包含正例和反例，比例是否合理？
5. 规范性：用例命名是否规范，步骤是否有逻辑顺序？"""

    TEST_CASE_QUALITY_CHECK_SCHEMA = """{
  "scores": {
    "completeness": 4,
    "executability": 4,
    "verifiability": 5,
    "balance": 4,
    "standardization": 4
  },
  "average_score": 4.2,
  "passed": true,
  "issues": [
    "反例缺少异常中断场景"
  ],
  "suggestions": [
    "增加一个异常中断的反例用例"
  ]
}"""

    TEST_CASE_SELF_CORRECT = """你是一个专业的测试用例设计专家。请根据质量校验反馈修正以下测试用例。

## 测试点
{test_point_text}

## 需求上下文
{requirement_context}

## 当前测试用例
{test_cases_json}

## 校验反馈
- 评分：{average_score}/5
- 问题：{issues}
- 建议：{suggestions}

## 修正要求
1. 针对校验指出的问题逐一修正
2. 补充遗漏的用例类型（如缺少反例则补充反例）
3. 完善前置条件和步骤描述
4. 确保预期结果明确可验证"""

    TEST_CASE_SELF_CORRECT_SCHEMA = """{
  "test_cases": [
    {
      "name": "用例名称",
      "property": "正例|反例",
      "pre_condition": "前置条件描述",
      "steps": [
        {
          "name": "步骤名称",
          "description": "具体操作描述",
          "stepExpectedResult": "该步骤的预期结果"
        }
      ]
    }
  ]
}"""

    EXPLORE_START = """你是一个专业的需求分析师。用户已经提交了原始需求描述，你需要先简要复述核心要点，然后基于选定的文档模板开始结构化提问。

用户原始需求：
{raw_content}

选定的文档模板：{template_name}

当前需要提问的维度：{dimension_label}
提问内容：{dimension_question}

请用友好专业的语气：
1. 先简要复述用户需求的核心要点（1-2句话）
2. 然后针对「{dimension_label}」维度提出问题
3. 问题应具体、有针对性，帮助用户补充该维度的信息
4. 如果用户原始需求中已包含该维度的部分信息，请确认并追问细节"""

    EXPLORE_CHAT = """你是一个专业的需求分析师。用户正在回答你关于需求的问题，请根据用户的回复继续探索。

用户原始需求：
{raw_content}

已收集的信息：
{explore_data}

当前维度：{dimension_label}（{dimension_key}）
维度提问：{dimension_question}

用户回复：{user_message}

请根据用户的回复：
1. 确认并总结用户在该维度提供的信息
2. 如果信息不够充分，可以追问细节
3. 如果信息已充分，提出下一个维度的提问

下一个待探索维度：{next_dimension_label}（{next_dimension_key}）
下一个维度提问：{next_dimension_question}

请以JSON格式输出：
{{
  "summary": "对用户回复的简要总结",
  "type": "question|followup|summary",
  "content": "你的回复内容（包含下一个维度的提问，或追问，或总结）",
  "dimension_key": "下一个维度标识",
  "dimension_label": "下一个维度名称",
  "quick_replies": ["快捷回复1", "快捷回复2"]
}}"""

    EXPLORE_CHAT_SCHEMA = """{
  "summary": "对用户回复的简要总结",
  "type": "question|followup|summary",
  "content": "回复内容",
  "dimension_key": "下一个维度标识",
  "dimension_label": "下一个维度名称",
  "quick_replies": ["快捷回复1", "快捷回复2"]
}"""

    STANDARDIZE_GENERATE = """你是一个专业的需求文档撰写专家。请根据以下信息，按照{template_name}模板结构，生成一份完整的标准化需求文档。

用户原始需求：
{raw_content}

探索收集的信息：
{explore_data}

模板章节结构：
{template_sections}

要求：
1. 严格按照模板章节结构组织文档，使用Markdown格式
2. 将探索收集的信息填充到对应章节
3. 对于信息不完整的章节，用"> 待补充：..."格式标注
4. 文档标题使用一级标题，章节使用二级标题，子章节使用三级标题
5. 内容专业、完整、可追溯
6. 每个章节应有实质内容，不要只写占位提示
7. 功能需求章节应详细描述输入、输出、业务规则
8. 非功能需求章节应包含量化指标

请直接输出Markdown格式的文档内容，不要包含其他说明文字。"""

    STANDARDIZE_ADJUST = """你是一个需求文档审核专家。用户希望调整标准化文档的内容。

用户调整请求：{user_message}
当前文档内容：
{current_content}

{context_info}

请分析用户的调整请求，给出具体的修改建议。你需要：
1. 理解用户的调整意图
2. 给出修改后的完整文档内容
3. 总结变更内容

请以JSON格式输出：
{{
  "content": "你的回复文本（说明修改了什么）",
  "type": "proposal|discussion|clarification",
  "pending_content": "修改后的完整文档内容（Markdown格式）",
  "change_summary": "变更摘要描述"
}}"""

    STANDARDIZE_ADJUST_SCHEMA = """{
  "content": "回复文本",
  "type": "proposal|discussion|clarification",
  "pending_content": "修改后的完整文档内容",
  "change_summary": "变更摘要"
}"""

    REQUIREMENT_SPLIT = """你是一个需求分析专家。请将以下标准化需求文档拆分为独立的、可执行的单个需求项。

标准化文档内容：
{standardized_content}

拆分规则：
1. 每个拆分项应是一个独立的功能需求或非功能需求
2. 拆分项应具有可测试性
3. 拆分粒度适中，不宜过大或过小
4. 保持需求项之间的逻辑关系
5. 按功能模块分组
6. 每个拆分项用简洁的一句话描述

请以JSON格式输出：
{{
  "splits": [
    {{
      "content": "拆分项内容描述"
    }}
  ]
}}"""

    REQUIREMENT_SPLIT_SCHEMA = """{
  "splits": [
    {
      "content": "拆分项内容描述"
    }
  ]
}"""

    TEST_DESIGN_ADJUST_SCHEMA = """{
  "content": "回复文本",
  "type": "proposal|discussion",
  "change_summary": "变更摘要，当type为proposal时必填",
  "pending_nodes": [
    {
      "action": "add|remove|modify",
      "id": "已有节点ID（删除和修改时必填，必须对应已有节点的ID）",
      "text": "节点文本（新增和修改时必填）",
      "description": "描述（仅测试点新增/修改时可选）",
      "case_property": "正例/反例（仅测试用例新增/修改时必填）",
      "pre_condition": "前置条件（仅测试用例新增/修改时可选）",
      "steps": [
        {
          "name": "步骤名称",
          "description": "步骤描述",
          "stepExpectedResult": "预期结果"
        }
      ]
    }
  ]
}"""

    TEMPLATE_RECOMMEND = """你是一个需求分析专家。请根据用户的需求内容，推荐最合适的需求文档模板。

用户需求内容：
{content}

可选模板：
1. SRS需求规格说明书 - 适用于瀑布式开发，基于IEEE 830标准，文档完整详细
2. 用户故事需求文档 - 适用于敏捷式开发，以用户故事为核心，文档简洁聚焦

推荐规则：
- 敏捷关键词（迭代、sprint、用户故事、敏捷、scrum、看板、backlog、MVP、增量）→ 推荐用户故事模板
- 瀑布关键词（规格、阶段、里程碑、评审、基线、配置管理、验收测试、SRS）→ 推荐SRS模板
- 两者得分相同时默认推荐SRS模板

请以JSON格式输出：
{{
  "recommended_template_id": "srs或user-story",
  "confidence": 0.0到1.0的置信度,
  "reason": "推荐理由"
}}"""

    TEMPLATE_RECOMMEND_SCHEMA = """{
  "recommended_template_id": "srs或user-story",
  "confidence": 0.85,
  "reason": "推荐理由"
}"""
