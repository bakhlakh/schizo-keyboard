# Keyboard Randomizer

Every key you press leaks information. An observer with line-of-sight to your hands, a camera feed, or a device capturing electromagnetic emissions from your keyboard can reconstruct what you typed — even without ever seeing your screen. Your muscle memory and hand positions are a side channel.

Keyboard Randomizer breaks that side channel. It shuffles your key layout into a random mapping before each session, so the physical keys you press carry no predictable relationship to the characters being produced. Someone watching your hands — or intercepting the electromagnetic signals from your keystrokes — sees a sequence of physical movements that maps to nothing meaningful without knowing the current layout. Only you do.

A visual keyboard on screen shows the live mapping, so you can type accurately while the physical-to-character relationship stays opaque to anyone observing from the outside.

## Also useful if

Someone has a directed energy device reconstructing a full 3D live model of your room and watching your every move. You know, just in case.

## Features

- Visual QWERTY keyboard display showing the current key mapping
- Randomize and Reset buttons
- In-app typing test with key flash on press
- **Settings:**
  - Key scope: Letters only / Letters + Numbers / All printable
  - OS-level remapping (system-wide, via a global keyboard hook)

## Requirements

- Python 3.11+
- PyQt6
- pynput

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Building an executable

```bash
pip install pyinstaller

# Windows
pyinstaller --onefile --windowed main.py

# Linux
pyinstaller --onefile main.py
```

The executable will be in `dist/`.

## OS-level remapping notes

- **Windows:** works without admin rights
- **Linux X11:** requires the user to be in the `input` group, or run with `sudo`
- **Linux Wayland:** not supported
- **macOS:** partially supported. No OS-level remapping.
