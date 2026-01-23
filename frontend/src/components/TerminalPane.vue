<template>
  <div ref="terminalRef" class="terminal-container"></div>
</template>

<script lang="ts" setup>
import { onMounted, onBeforeUnmount, ref } from "vue";
import { Terminal } from "xterm";
import { FitAddon } from 'xterm-addon-fit';
import "xterm/css/xterm.css";

const props = defineProps<{
  hostId: number;
  sessionId: string;
}>();

const terminalRef = ref<HTMLElement | null>(null);
let term: Terminal;
let fitAddon: FitAddon;
let ws: WebSocket;

onMounted(() => {
  term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    fontFamily: 'Consolas, "Courier New", monospace'
  });
  fitAddon = new FitAddon();
  term.loadAddon(fitAddon);
  
  term.open(terminalRef.value!);
  fitAddon.fit();

  // Determine WebSocket protocol
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  // If running in dev with proxy, use window.location.host which goes to vite proxy
  // But vite proxy config forwards /ws to ws://localhost:8000
  // So we connect to /ws/terminal/ws
  
  // Note: Vite proxy rewrites /ws to root, so if we call /ws/terminal/ws, 
  // it goes to target/terminal/ws.
  const wsUrl = `${protocol}//${window.location.host}/ws/terminal/ws?host_id=${props.hostId}&session_id=${props.sessionId}&cols=${term.cols}&rows=${term.rows}`;
  
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    term.write('\r\n*** Connected to SSH ***\r\n');
  };

  ws.onmessage = (ev) => {
    term.write(ev.data);
  };

  ws.onclose = (ev) => {
    term.write(`\r\n*** Disconnected (Code: ${ev.code}) ***\r\n`);
  };

  ws.onerror = () => {
    term.write('\r\n*** Connection Error ***\r\n');
  };

  term.onData((data) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    }
  });
  
  // Handle resize
  window.addEventListener('resize', () => {
      fitAddon.fit();
      if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
              type: 'resize',
              cols: term.cols,
              rows: term.rows
          }));
      }
  });
});

onBeforeUnmount(() => {
  ws?.close();
  term?.dispose();
});
</script>

<style scoped>
.terminal-container {
  width: 100%;
  height: 100%;
  background-color: #000;
  padding: 5px;
  box-sizing: border-box;
}
</style>
