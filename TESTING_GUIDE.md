# VocalNode Testing Guide

## Automated Tests Completed ✅

All core component tests have been completed and passed. See `TEST_RESULTS.md` for details.

## Manual Testing Required

The following tests require manual/interactive testing:

### 1. Hotkey Functionality
**Steps:**
1. Start the application
2. Open Settings → Hotkey tab
3. Click "Click here and press your hotkey"
4. Press a key combination (e.g., `Ctrl+Shift+V`)
5. Verify it's displayed correctly
6. Save settings
7. Test the hotkey in different applications
8. Verify it starts/stops dictation

**Expected:** Hotkey works globally, starts/stops recording correctly

### 2. Audio Recording
**Steps:**
1. Ensure microphone is connected
2. Press configured hotkey to start recording
3. Speak clearly into microphone
4. Press hotkey again to stop
5. Check console/log for "Audio capture started" messages
6. Verify audio chunks are collected

**Expected:** Recording starts, audio is captured, no errors

### 3. Speech Transcription
**Steps:**
1. Record a short phrase (2-3 seconds)
2. Wait for processing
3. Check console for "Transcribed text" message
4. Verify text appears in overlay (if enabled)
5. Verify text is accurate

**Expected:** Speech is transcribed correctly, text appears

### 4. Text Insertion
**Steps:**
1. Open a text editor (gedit, nano, etc.)
2. Place cursor in text field
3. Record speech using hotkey
4. Wait for processing
5. Verify text appears at cursor position
6. Test in different applications (browser, terminal, etc.)

**Expected:** Text is inserted correctly in all applications

### 5. Overlay Display
**Steps:**
1. Enable overlay in Settings
2. Start recording
3. Verify overlay appears
4. Verify it shows "Listening..." with animation
5. Stop recording
6. Verify it shows "Processing..."
7. Verify transcribed text appears (if enabled)
8. Verify overlay hides after completion

**Expected:** Overlay displays correctly, animations work, text shows

### 6. Settings Persistence
**Steps:**
1. Change hotkey to something new
2. Change audio device
3. Change language
4. Save settings
5. Quit application
6. Restart application
7. Verify all settings persisted

**Expected:** All settings are saved and restored

### 7. Error Handling
**Steps:**
1. Disconnect microphone
2. Try to start recording
3. Verify error message appears
4. Reconnect microphone
5. Try again
6. Verify it works

**Expected:** Graceful error handling, clear error messages

### 8. Performance
**Steps:**
1. Record short audio (< 2 seconds)
2. Record long audio (> 30 seconds)
3. Record multiple times rapidly
4. Monitor CPU/memory usage
5. Verify no crashes or hangs

**Expected:** Good performance, no crashes, reasonable resource usage

## Test Checklist

Print this and check off as you test:

- [ ] Application starts successfully
- [ ] Tray icon appears
- [ ] Settings window opens
- [ ] Hotkey can be configured (any key combination)
- [ ] Hotkey works globally
- [ ] Recording starts when hotkey pressed
- [ ] Recording stops when hotkey pressed again
- [ ] Audio is captured
- [ ] Speech is transcribed
- [ ] Text is inserted into active window
- [ ] Overlay displays correctly
- [ ] Settings persist after restart
- [ ] Error handling works
- [ ] Performance is acceptable
- [ ] No crashes or critical errors

## Reporting Issues

If you find issues during testing:

1. Note the exact steps to reproduce
2. Check console/log output for errors
3. Note your system configuration
4. Report with:
   - What you were doing
   - What you expected
   - What actually happened
   - Error messages (if any)

## Quick Test Script

Run this to verify basic functionality:

```bash
cd /home/jb/dev/VocalNode
source venv/bin/activate
python3 run.py
```

Then:
1. Right-click tray icon → Settings
2. Configure hotkey
3. Open text editor
4. Press hotkey → speak → press hotkey
5. Verify text appears


