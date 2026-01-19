Challenges while working on this assignment
1. What should be schema of the datas . [intent, registration]
2. Should i directly use mcp or with fastapi
 - going with fastapi as it will expose the endpoint to user frontend



3. Connecting MCP with fast was very bad, most of the server was not connected, and then debug console wont open.
- Solved this using to debug, [direct, sse(for https service), other one is for LLMS like claude etc.]
`npx @modelcontextprotocol/inspector http://localhost:8000/mcp/`

or use client.py, 
- make the CORS available
- uvicorn app:app --reload : does not run the __main__, that was also causing error(i was running mcp in this)


-------
fast api creates a server, which is invoked by a client. 
- these clients are used to create tools for llm to use. 
- The 

`NotImplementedError: StructuredTool does not support sync invocation.
During task with name 'tools' and id '792e7f9b-6855-f0d6-2a4b-592c54226ddf'`
- LLMs expects synchronous calling because they need to perform tasks in sequential manner. 
so our api endpoints needs to be synchronous, 
- asynchronous endpoints can handle multiple requests/sec and are better for use cases such as database reading.

4. The output of the intent agent is not maching the tools use.

```
    raise self._make_status_error_from_response(err.response) from None
groq.BadRequestError: Error code: 400 - {'error': {'message': "Failed to call a function. Please adjust your prompt. See 'failed_generation' for more details.", 'type': 'invalid_request_error', 'code': 'tool_use_failed', 'failed_generation': '<function=book_appointment>{"appointment_date":"2024-01-22","appointment_time":"10:00","doctor_name":"Dr. Smith","reason":"General consultation"}'}}
During task with name 'agent' and id 'edeb74b8-752b-48fe-6a76-aacf44d9c688'
```

This is the issue: 
`INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 200 OK"
Booking appointment with payload: {'doctor_name': 'Dr. Smith', 'date': 'this week\'s date + 7 days + 1 days + "2024-01-15" or "the next  Monday'}
INFO:httpx:HTTP Request: POST http://localhost:8000/doctor_availablity "HTTP/1.1 422 Unprocessable Content"`


### DATABASE
- Using postgresql with docker, 
    `docker-compose up -d`

Enter the container's PostgreSQL shell
- `docker exec -it school_db psql -U postgres -d school_db`
```
docker-compose down          # Stops container, keeps data
docker-compose down -v       # stop and remove data
```
3. When creating the model for database, *enum* is used to create a new type of column as String, Date etc. It should be named otherwise db will randomly generate the name.
