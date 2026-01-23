from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from ..ssh_manager import ssh_manager
from ..db import get_db
from ..models import Host
import asyncio
import json

router = APIRouter(prefix="/terminal", tags=["terminal"])

@router.websocket("/ws")
async def terminal_ws(
    websocket: WebSocket,
    host_id: int = Query(...),
    session_id: str = Query(...),
    cols: int = Query(80),
    rows: int = Query(24),
    db: Session = Depends(get_db) # Note: Depends in websocket works in newer FastAPI
):
    await websocket.accept()
    
    # In WebSocket, Depends might not work exactly as in HTTP endpoints for session management depending on version/setup
    # Re-creating session manually if needed or trusting Depends
    
    try:
        host = db.query(Host).filter(Host.id == host_id).first()
        if not host:
            await websocket.close(code=1008, reason="Host not found")
            return

        conn, process = await ssh_manager.create_session(session_id, host, cols=cols, rows=rows)

        async def ws_to_ssh():
            try:
                while True:
                    data = await websocket.receive_text()
                    # Check for resize event (custom protocol or just raw data)
                    # For xterm.js default, it sends raw text. 
                    # If we want resize, we usually send JSON or specific prefix.
                    # Here we assume raw text for shell input.
                    # To support resize, we could try to parse JSON if it looks like one, or use a separate endpoint.
                    # For simplicity, let's check if it starts with '{'
                    if data.startswith('{'):
                        try:
                            msg = json.loads(data)
                            if msg.get('type') == 'resize':
                                await ssh_manager.resize(session_id, msg['cols'], msg['rows'])
                                continue
                        except:
                            pass
                    
                    await ssh_manager.write(session_id, data)
            except WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"ws_to_ssh error: {e}")

        async def ssh_to_ws():
            try:
                while True:
                    # asyncssh process.stdout is an SSHReader
                    chunk = await process.stdout.read(1024)
                    if not chunk:
                        break
                    # Ensure chunk is string if xterm expects string
                    # asyncssh default encoding is utf-8, returns str
                    await websocket.send_text(chunk)
            except Exception as e:
                print(f"ssh_to_ws error: {e}")

        task1 = asyncio.create_task(ws_to_ssh())
        task2 = asyncio.create_task(ssh_to_ws())
        
        done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
        
        for task in pending:
            task.cancel()

    except Exception as e:
        print(f"Terminal error: {e}")
        await websocket.close(code=1011, reason=str(e))
    finally:
        await ssh_manager.close_session(session_id)
        # Check if websocket is still open before closing?
        # It might be closed by WebSocketDisconnect
        try:
            await websocket.close()
        except:
            pass
