from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import uuid
from typing import Dict

app = FastAPI()

# Store active SSE streams (simulating user-specific streams)
active_streams: Dict[str, asyncio.Queue] = {}

# Pydantic model for input data
class UserInput(BaseModel):
    username: str

# SSE endpoint to stream results for a specific session
@app.get("/stream/{session_id}")
async def sse_stream(request: Request, session_id: str):
    async def event_stream():
        if session_id not in active_streams:
            yield f"data: {json.dumps({'error': 'Invalid session ID'})}\n\n"
            return

        queue = active_streams[session_id]
        try:
            while True:
                if await request.is_disconnected():
                    print(f"Client disconnected for session {session_id}")
                    break
                
                # Get data from the queue (non-blocking)
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Send keep-alive to prevent connection timeout
                    yield ": keep-alive\n\n"
        
        finally:
            # Clean up when client disconnects
            if session_id in active_streams:
                del active_streams[session_id]
                print(f"Cleaned up session {session_id}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

# Endpoint to receive user input and create SSE stream
@app.post("/submit")
async def submit_data(user_input: UserInput):
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Create a queue for this session
    active_streams[session_id] = asyncio.Queue()
    
    # Simulate processing and pushing results to the queue
    asyncio.create_task(simulate_processing(session_id, user_input.username))
    
    return {"session_id": session_id}

# Simulate processing user input and pushing results
async def simulate_processing(session_id: str, username: str):
    queue = active_streams.get(session_id)
    if not queue:
        return
    
    # Simulate 5 updates related to the username
    for i in range(5):
        data = {
            "username": username,
            "update": f"Update {i+1} for {username}",
            "timestamp": asyncio.get_event_loop().time()
        }
        await queue.put(data)
        await asyncio.sleep(2)  # Simulate delay between updates
    
    # Send completion message
    await queue.put({"username": username, "update": "Processing complete", "status": "done"})

# HTML frontend to send data and display SSE results
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSE with User Input</title>
    </head>
    <body>
        <h1>SSE with User Input</h1>
        <form id="inputForm">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <button type="submit">Submit</button>
        </form>
        <h2>Updates:</h2>
        <div id="output"></div>
        <script>
            const form = document.getElementById('inputForm');
            const output = document.getElementById('output');
            let source = null;

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('username').value;

                // Close existing SSE connection if any
                if (source) {
                    source.close();
                }

                // Send POST request to submit username
                try {
                    const response = await fetch('/submit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username })
                    });
                    const { session_id } = await response.json();

                    // Start SSE stream
                    source = new EventSource(`/stream/${session_id}`);
                    output.innerHTML = ''; // Clear previous output

                    source.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        const p = document.createElement('p');
                        p.textContent = `Update for ${data.username}: ${data.update} (Time: ${data.timestamp})`;
                        output.appendChild(p);
                        if (data.status === 'done') {
                            source.close();
                            p.textContent += ' [Stream Closed]';
                        }
                    };

                    source.onopen = () => {
                        console.log('SSE connection opened');
                    };

                    source.onerror = () => {
                        console.log('SSE error, connection may have closed');
                        source.close();
                        const p = document.createElement('p');
                        p.textContent = 'Error occurred, stream closed.';
                        output.appendChild(p);
                    };
                } catch (error) {
                    console.error('Error:', error);
                    const p = document.createElement('p');
                    p.textContent = `Error: ${error.message}`;
                    output.appendChild(p);
                }
            });
        </script>
    </body>
    </html>
    """