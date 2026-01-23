import asyncssh
from typing import Dict, Tuple, Optional
import asyncio

class SSHManager:
    def __init__(self):
        # key: session_id, value: (ssh_conn, ssh_process)
        self.sessions: Dict[str, Tuple[asyncssh.SSHClientConnection, asyncssh.SSHClientProcess]] = {}
        self.lock = asyncio.Lock()

    async def create_session(self, session_id: str, host, term_type="xterm", cols=80, rows=24):
        async with self.lock:
            if session_id in self.sessions:
                return self.sessions[session_id]

            try:
                conn = await asyncssh.connect(
                    host.ip,
                    port=host.ssh_port,
                    username=host.username,
                    password=host.password if host.auth_type == "password" else None,
                    known_hosts=None # Insecure for demo, in prod use known_hosts
                )
                process = await conn.create_process(term_type=term_type, term_size=(cols, rows))
                self.sessions[session_id] = (conn, process)
                return conn, process
            except Exception as e:
                print(f"SSH Connection failed: {e}")
                raise e

    async def close_session(self, session_id: str):
        async with self.lock:
            conn, process = self.sessions.pop(session_id, (None, None))
        if process:
            try:
                process.terminate()
            except:
                pass
        if conn:
            conn.close()

    async def write(self, session_id: str, data: str):
        if session_id not in self.sessions:
            return
        conn, process = self.sessions[session_id]
        process.stdin.write(data)

    async def resize(self, session_id: str, cols: int, rows: int):
        if session_id not in self.sessions:
            return
        conn, process = self.sessions[session_id]
        process.terminal_size = (cols, rows)
        # asyncssh might handle resize automatically if supported, 
        # otherwise we might need to send signal, but term_size property setter should work

ssh_manager = SSHManager()
