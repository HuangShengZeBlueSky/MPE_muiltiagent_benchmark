# Game Prompt & Obs 标准化流程

面向后续任意环境/game代码，使用以下步骤完成标准化。

## 输入
- 一份环境的API/game代码，包含：
  - 内联提示词
  - 观测解析逻辑（raw obs → structured obs）
  - 运行入口

## 目标产物
1) 提示词模块化为4类（参考 prompt/My_requirement.md）：
   - `get_task_and_reward` (B 任务/奖励)
   - `get_action_and_response_format` (C 动作空间/输出格式)
   - `get_physics_rules` (D 物理规则)
   - `get_navigation_hints` (E 导航/策略)
   - `__all__` 仅导出上述4个函数
   - 注意：观测语义(obs_semantics)直接在主文件的 obs formatter 中处理
2) 观测解析函数抽取到 obs/ 下独立文件（如 `obs/parse_xxx_obs.py`），可单独运行；同时提供样例测试，打印 raw obs 与 struct obs。
3) 游戏主文件仅调用已模块化的提示词与解析器，使用统一的 LLM 引擎接口 `get_api_engine(provider, **kwargs)`。

## 操作步骤
1) **提示词梳理**
   - 从原 game 文件提取全部提示文本，按 My_requirement 四类分组。
   - 放入 `prompt/prompt_for_<env>.py`，只保留四个函数与 `__all__`。
   - 观测语义不需要单独提取，在主文件的 obs formatter 中处理。

2) **观测解析抽取**
   - 将 `parse_<env>_obs` 从 game 文件移到 `obs/parse_<env>_obs.py`。
   - 保留维度校验、距离计算、碰撞风险等逻辑，输出结构化 dict。
   - 在同文件 `if __name__ == "__main__":` 下写测试：
     - 构造最小 raw obs 样例（长度匹配公式）
     - 打印 raw obs 长度与 struct obs 字段
     - 演示维度错误的兜底提示

3) **主流程对接**
   - 在 game 主文件：
     - `from prompt.prompt_for_<env> import ...`（4类函数）
     - `from obs.parse_<env>_obs import parse_<env>_obs`
     - `from utils_api import get_api_engine, get_unique_filename`
     - 使用统一 LLM 引擎：`llm_engine = get_api_engine(provider, **kwargs)`
     - `user_prompt(...)` 仅拼接4类提示 + 当前 struct obs（obs 格式化在 formatter 函数中）
     - 运行时使用 `parse_<env>_obs` 生成 struct，再传入模型
     - 确保视频和日志保存使用 `get_unique_filename`

4) **测试与验证**
   - 单独运行解析器：`python obs/parse_<env>_obs.py`，确认样例输出正确。
   - 运行主程序数步，确认提示调用正常、动作向量可 clip。

## 输出要求
- 所有新增/改动文件默认 ASCII。
- 提示词文件仅包含4个函数与 `__all__`，无额外 helper。
- 解析器测试打印：raw obs 长度、各字段、错误分支。
- 主文件不再内联提示词与解析逻辑。
- 统一使用 `get_api_engine(provider, **kwargs)` 初始化模型。
- 文件保存统一使用 `get_unique_filename` 防止覆盖。

## 交付清单（每个环境）
- `prompt/prompt_for_<env>.py`（4类提示词）
- `obs/parse_<env>_obs.py`（解析 + 样例测试）
- `<env>_API.py` 或主入口（调用上面两个模块）

按照以上流程，后续可对其他 game 代码快速做同样的标准化。
