import pytest
from backend.app.agent import build_agent_graph
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_agent_availability_flow():
    # 1. Setup
    app = build_agent_graph()
    user_query = "Is Dr. Smith available on 2026-02-20?"
    
    # 2. Execution
    inputs = {"messages": [HumanMessage(content=user_query)]}
    # Use a thread_id so the checkpointer is tested too
    config = {"configurable": {"thread_id": "test_thread"}}
    
    result = await app.ainvoke(inputs, config=config)
    
    # 3. Assertions
    messages = result["messages"]
    
    # Check that the agent actually made a tool call
    has_tool_call = any(
        hasattr(m, "tool_calls") and len(m.tool_calls) > 0 
        for m in messages
    )
    assert has_tool_call, "Agent should have decided to call a tool."

    # Check that the final message is a response from the assistant
    assert messages[-1].content != "", "Assistant should have provided a final answer."
    print(f"Final Response: {messages[-1].content}")