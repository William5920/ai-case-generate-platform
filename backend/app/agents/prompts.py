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
