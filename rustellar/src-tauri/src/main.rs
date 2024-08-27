// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use portable_pty::{native_pty_system, CommandBuilder, PtyPair, PtySize};
use std::io::{BufRead, BufReader, Write};
use tauri::{Emitter, Manager};

use std::sync::{Arc, Mutex};
use tauri::State;

struct PtyState {
    pty_pair: Arc<Mutex<Option<PtyPair>>>,
    writer: Arc<Mutex<Option<Box<dyn Write + Send>>>>,
}

#[tauri::command]
async fn create_pty(window: tauri::Window, state: State<'_, PtyState>) -> Result<(), String> {
    let pty_system = native_pty_system();

    let size = PtySize {
        rows: 24,
        cols: 80,
        pixel_width: 0,
        pixel_height: 0,
    };

    let pair = pty_system.openpty(size).map_err(|e| e.to_string())?;

    let cmd = CommandBuilder::new("bash");
    let _child = pair.slave.spawn_command(cmd).map_err(|e| e.to_string())?;

    let reader = pair.master.try_clone_reader().map_err(|e| e.to_string())?;
    let writer = pair.master.take_writer().map_err(|e| e.to_string())?;

    let pty_pair_clone = Arc::clone(&state.pty_pair);
    let writer_clone = Arc::clone(&state.writer);

    // Store the PtyPair and writer in the state
    *state.pty_pair.lock().unwrap() = Some(pair);
    *state.writer.lock().unwrap() = Some(writer);

    // Read from the PTY
    tauri::async_runtime::spawn(async move {
        let mut reader = BufReader::new(reader);
        loop {
            let mut line = String::new();
            match reader.read_line(&mut line) {
                Ok(0) => break, // EOF
                Ok(_) => {
                    window
                        .emit("pty_output", line)
                        .expect("failed to emit event");
                }
                Err(_) => break,
            }
        }
        // Clean up when the PTY is closed
        let mut pty_pair = pty_pair_clone.lock().unwrap();
        *pty_pair = None;
        let mut writer = writer_clone.lock().unwrap();
        *writer = None;
    });

    Ok(())
}

#[tauri::command]
async fn write_to_pty(input: String, state: State<'_, PtyState>) -> Result<(), String> {
    let mut writer_guard = state.writer.lock().unwrap();
    if let Some(writer) = writer_guard.as_mut() {
        writer
            .write_all(input.as_bytes())
            .map_err(|e| e.to_string())?;
        writer.flush().map_err(|e| e.to_string())?;
        Ok(())
    } else {
        Err("PTY writer not initialized".to_string())
    }
}

#[tauri::command]
async fn resize_pty(rows: u16, cols: u16, state: State<'_, PtyState>) -> Result<(), String> {
    let pty_pair = state.pty_pair.lock().unwrap();
    if let Some(pair) = pty_pair.as_ref() {
        pair.master
            .resize(PtySize {
                rows,
                cols,
                pixel_width: 0,
                pixel_height: 0,
            })
            .map_err(|e| e.to_string())?;
        Ok(())
    } else {
        Err("PTY not initialized".to_string())
    }
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }
            Ok(())
        })
        .manage(PtyState {
            pty_pair: Arc::new(Mutex::new(None)),
            writer: Arc::new(Mutex::new(None)),
        })
        .invoke_handler(tauri::generate_handler![
            create_pty,
            write_to_pty,
            resize_pty
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
