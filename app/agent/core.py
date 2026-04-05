# ReAct agent core
import re
from typing import List, Any, Dict, Optional, Tuple, Generator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from infrastructure.logging.manager import logger
from app.middleware.callbacks import AgentBotCallbackHandler
from app.memory.session_manager import get_session_manager
from utils.prompt_loader import load_role_prompts

class BaseAgent:
    """
    智能体基类
    """
    def __init__(self, llm: BaseChatModel, tools: List[Any], callback_handler: Optional[AgentBotCallbackHandler] = None):
        self.llm = llm
        self.tools = tools
        self.callback_handler = callback_handler or AgentBotCallbackHandler()

    def run(self, query: str, **kwargs) -> Any:
        """执行智能体"""
        raise NotImplementedError("子类必须实现 run 方法")

class ReActAgent(BaseAgent):
    """
    极简 ReAct 智能体：手动管理推理循环，具备极高兼容性
    """
    def __init__(self, llm: BaseChatModel, tools: List[Any]):
        super().__init__(llm, tools)
        self.role_play = ""

    def build(self, prompt_template_str: str):
        """
        初始化提示词模板和工具描述
        """
        # 1. 手动准备工具描述
        self.tool_desc = "\n".join([f"{t.name}: {t.description}" for t in self.tools])
        self.tool_names = ", ".join([t.name for t in self.tools])
        
        # 2. 保存原始模板字符串 (我们将手动格式化，以获得最大灵活性并避免 PromptTemplate 的校验限制)
        self.prompt_template_str = prompt_template_str
        
        # 3. 初始化角色扮演提示词
        self.role_play = ""
        
        logger.info("极简 ReAct 智能体初始化完成")
        return self

    def _parse_action(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        增强版解析逻辑：支持中英文关键字，兼容全半角冒号，并处理模型伪造 Observation 的情况
        """
        # 1. 预处理：移除模型可能伪造的 Observation 及其之后的内容
        # 同时支持全角和半角冒号
        clean_text = re.split(r"观察[：:]|Observation:", text)[0].strip()

        # 2. 匹配最终答案 (支持 "最终答案:" / "最终答案：" / "Final Answer:" 以及变体如 "最终答案是:")
        final_match = re.search(r"(?:最终答案(?:是)?|Final Answer)[：:]\s*(.*)", clean_text, re.DOTALL)
        if final_match:
            return "finish", None, final_match.group(1).strip()
        
        # 3. 匹配行动和输入 (支持 "行动:"/"行动："/"Action:" 和 "行动输入:"/"行动输入："/"Action Input:")
        action_match = re.search(r"(?:行动|Action)[：:]\s*(.*)", clean_text)
        action_input_match = re.search(r"(?:行动输入|Action Input)[：:]\s*(.*)", clean_text)
        
        if action_match and action_input_match:
            return "call", action_match.group(1).strip(), action_input_match.group(1).strip()
        
        return None, None, None

    def run_stream(self, query: str, session_id: str = "default", max_iterations: int = 5) -> Generator[Dict[str, str], None, None]:
        """
        流式生成推理循环：Thought -> Action -> Observation
        每步 yield {"thought": "内容"} 或 {"output": "最终答案"}
        """
        # 1. 保存用户消息到记忆
        memory = get_session_manager()
        memory.save_message(session_id, "user", query)
        
        scratchpad = ""
        if not hasattr(self, 'role_play'):
            self.role_play = ""
        
        logger.info(f"Agent 开始运行 (流式模式)，Session: {session_id}, Query: {query}")
        
        # 获取并注入历史记录 (包含刚存入的 User 消息之前的历史)
        history_str = memory.get_history_str(session_id)
        
        for i in range(max_iterations):
            # 1. 构造当前轮次的完整 Prompt (手动替换，避免 .format() 解析用户输入中的大括号导致报错)
            formatted_prompt = self.prompt_template_str
            replacements = {
                "{input}": query,
                "{tools}": self.tool_desc,
                "{tool_names}": self.tool_names,
                "{agent_scratchpad}": scratchpad,
                "{history}": history_str,
                "{role_play}": self.role_play
            }
            for placeholder, value in replacements.items():
                formatted_prompt = formatted_prompt.replace(placeholder, str(value))
            
            # 2. 调用模型 (流式)
            try:
                full_response_text = ""
                # 绑定中英文停止词
                stop_words = ["\n观察:", "\nObservation:", "\n问题:", "\nQuestion:"]
                
                for chunk in self.llm.stream(
                    formatted_prompt, 
                    config={"callbacks": [self.callback_handler], "stop": stop_words}
                ):
                    content = chunk.content
                    full_response_text += content
                    # yield 当前 Token 用于 UI 展示
                    yield {"thought": content}
                
                response_text = full_response_text
            except Exception as e:
                logger.error(f"LLM 调用失败: {e}")
                yield {"error": f"模型调用出错: {str(e)}"}
                return

            # 3. 解析模型输出
            action_type, tool_name, tool_input = self._parse_action(response_text)
            logger.debug(f"解析结果: type={action_type}, tool={tool_name}, input={tool_input}")
            
            # 记录思考过程 (只保留到 Action 为止的部分，防止污染 scratchpad)
            current_thought = response_text.split("观察：")[0].split("Observation:")[0].strip()
            scratchpad += current_thought

            if action_type == "finish":
                # 保存助手消息到记忆
                memory.save_message(session_id, "assistant", tool_input)
                yield {"output": tool_input}
                return
            
            if action_type == "call":
                # 4. 执行工具
                # 鲁棒性：移除可能出现的反引号
                tool_name = tool_name.strip("`").strip()
                tool = next((t for t in self.tools if t.name == tool_name), None)
                
                if not tool:
                    observation = f"错误: 工具 '{tool_name}' 不存在。请从 [{self.tool_names}] 中选择。"
                else:
                    try:
                        logger.info(f"执行工具: {tool_name} | 参数: {tool_input}")
                        observation = tool.invoke(tool_input)
                    except Exception as e:
                        observation = f"工具执行异常: {str(e)}"
                
                # 5. 更新思考记录 (使用中文关键字，保持与提示词一致)
                obs_str = f"\n观察：{observation}\n思考："
                scratchpad += obs_str
                # yield 观察结果
                yield {"thought": f"\n观察：{observation}\n思考："}
                logger.debug(f"工具返回: {observation}")
                
                # 特殊处理：如果调用的是 inject_role_play，设置角色扮演提示词
                #if tool_name == "inject_role_play":
                    #self.role_play = load_role_prompts()

            else:
                # 解析失败，尝试强制引导
                logger.warning(f"无法解析模型输出，尝试修正... 输出原文: {response_text}")
                if "最终答案" in response_text or "Final Answer" in response_text:
                    # 如果模型没按格式写但确实给了答案，尝试二次提取
                    ans = response_text.split("答案")[-1].strip(":").strip()
                    yield {"output": ans}
                    return
                elif not ("行动" in response_text or "Action" in response_text):
                    # 如果不包含行动关键字，假设是直接回答
                    yield {"output": response_text}
                    return
                
                scratchpad += "\n思考：我刚才的输出格式可能有误。我必须严格按照“行动：[工具名]”和“行动输入：[参数]”的格式来调用工具，或者直接给出“最终答案：”。"
                yield {"thought": "\n思考：我刚才的输出格式可能有误。我必须严格按照“行动：[工具名]”和“行动输入：[参数]”的格式来调用工具，或者直接给出“最终答案：”。"}

        yield {"output": "抱歉，我尝试了多次但未能得出最终结论。"}

    def run(self, query: str, session_id: str = "default", max_iterations: int = 5) -> Dict[str, Any]:
        """
        非流式运行：是对 run_stream 的封装
        """
        output = ""
        thoughts = []
        current_thought = ""
        
        for step in self.run_stream(query, session_id, max_iterations):
            if "thought" in step:
                current_thought += step["thought"]
            if "output" in step:
                output = step["output"]
            if "error" in step:
                return {"output": step["error"], "thoughts": [current_thought]}
        
        # 简单切分 thoughts 以便展示
        thoughts = [current_thought]
        return {"output": output, "thoughts": thoughts}
