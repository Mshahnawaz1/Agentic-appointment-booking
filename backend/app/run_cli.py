from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
import asyncio
from agent import build_agent_graph, SYS_PROMPT

async def run_cli():
    # 1. Compile the graph ONCE outside the loop for speed
    app = build_agent_graph().compile()
    
    # 2. Maintain a history of messages for memory during this session
    # We start with the System Message
    chat_history = [SystemMessage(content=SYS_PROMPT)]

    print("--- 🩺 Medical Assistant CLI ---")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        # Get user input
        user_query = input("You: ")
        
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Append user message to history
        chat_history.append(HumanMessage(content=user_query))
        
        # 3. Stream the response
        # We pass the entire history so the agent remembers previous context
        inputs = {"messages": chat_history}
        
        async for event in app.astream(inputs, stream_mode="updates"):
            for node_name, output in event.items():
                # Check for messages in the node output
                if "messages" in output:
                    new_msg = output["messages"][-1]
                    
                    # Update local history so the next turn knows what happened
                    chat_history.append(new_msg)

                    # Display based on message type
                    if hasattr(new_msg, "tool_calls") and new_msg.tool_calls:
                        for tc in new_msg.tool_calls:
                            print(f"  [System]: 🛠️  Calling {tc['name']}...")
                    elif isinstance(new_msg, ToolMessage):
                        print(f"  [System]: ✅ Tool returned data.")
                    else:
                        print(f"Assistant: {new_msg.content}")

if __name__ == "__main__":
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\nInterrupted by user. Closing...")