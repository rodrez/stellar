<script lang="ts">
  import { onMount } from 'svelte';
  import { Terminal } from '@xterm/xterm';
  import { WebglAddon } from '@xterm/addon-webgl';
  import { FitAddon } from '@xterm/addon-fit';
  import { ClipboardAddon } from '@xterm/addon-clipboard';
  import '@xterm/xterm/css/xterm.css';
  import { invoke } from '@tauri-apps/api/core';
  import { listen } from '@tauri-apps/api/event';
  import { LigaturesAddon } from '@xterm/addon-ligatures';
  import fira from '../../../assets/fira_code/FiraCodeNerdFont-SemiBold.ttf';

  let terminalElement: HTMLDivElement;
  let terminal: Terminal;
  let fitAddon: FitAddon;
  
  const theme = {
    "background": "#1a1b26",
    "black": "#15161e",
    "blue": "#7aa2f7",
    "brightBlack": "#414868",
    "brightBlue": "#7aa2f7",
    "brightCyan": "#7dcfff",
    "brightGreen": "#9ece6a",
    "brightPurple": "#9d7cd8",
    "brightRed": "#f7768e",
    "brightWhite": "#c0caf5",
    "brightYellow": "#e0af68",
    "cursorColor": "#c0caf5",
    "cyan": "#7dcfff",
    "foreground": "#c0caf5",
    "green": "#9ece6a",
    "name": "Tokyo Night",
    "purple": "#bb9af7",
    "red": "#f7768e",
    "selectionBackground": "#283457",
    "white": "#a9b1d6",
    "yellow": "#e0af68"
  }

  onMount(async () => {
    terminal = new Terminal({
      cursorBlink: true,
      fontSize: 18,
      fontFamily: 'FiraCode, FiraCode Nerd Font Bold, Consolas, "Courier New", monospace',
      fontWeight: 600,
      theme: theme,
      allowProposedApi: true
    });

    terminal.open(terminalElement);

    const webglAddon = new WebglAddon();
    terminal.loadAddon(webglAddon);

    fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);

    const clipboardAddon = new ClipboardAddon();
    terminal.loadAddon(clipboardAddon);

    const ligaturesAddon = new LigaturesAddon();
    terminal.loadAddon(ligaturesAddon)

    fitAddon.fit();
    window.addEventListener('resize', handleResize);

    terminal.writeln('Welcome to Tauri + Svelte + xterm.js with PTY support!');

    // Create PTY
    await invoke('create_pty');

    // Listen for PTY output
    await listen('pty_output', (event: any) => {
      terminal.write(event.payload);
    });

    // Handle input
    terminal.onData((data) => {
      terminal.write(data);
      invoke('write_to_pty', { input: data });
    });
  });

  async function handleResize() {
    fitAddon.fit();
    const { rows, cols } = terminal;
    await invoke('resize_pty', { rows, cols });
  }
</script>

<div bind:this={terminalElement}></div>

<style>
  div {
    margin: 0;
    padding: 0;
    height: 100%;
    width: 100%;
  }
  :global(.xterm){
    cursor: text;
    position: relative;
    padding: 2px;
  }
</style>
