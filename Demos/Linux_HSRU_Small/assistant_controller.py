import os
import sys
import ctypes
import numpy as np
import json
import time

def listen():
    '''Records audio and pipes to whisper.cpp for STT.'''
    print("\n[Ear] Listening... (Waiting for voice/text)")
    whisper_path = os.path.join(os.path.dirname(__file__), "bin", "whisper-cpp")
    if not os.path.exists(whisper_path):
        # Fallback if binaries are not installed yet
        return input("User: ")
        
    try:
        import subprocess
        print("[Ear] Recording 5 seconds...")
        # Record audio: arecord (Linux) or sox (macOS)
        record_cmd = ["arecord", "-d", "5", "-f", "S16_LE", "-r", "16000", "-c", "1", "temp.wav"]
        if sys.platform == "darwin":
            record_cmd = ["sox", "-d", "-r", "16000", "-b", "16", "-c", "1", "temp.wav", "trim", "0", "5"]
            
        subprocess.run(record_cmd, check=True, stderr=subprocess.DEVNULL)
        
        model_path = os.path.join(os.path.dirname(__file__), "models", "stt", "ggml-tiny.en.bin")
        stt_cmd = [whisper_path, "-m", model_path, "-f", "temp.wav", "-nt"]
        result = subprocess.check_output(stt_cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
        print(f"User: {result}")
        return result
    except Exception as e:
        print(f"[Ear] Failed to run STT: {e}")
        return input("User: ")

def speak(text):
    '''Pipes text to piper for TTS.'''
    print(f"\n[Mouth] Speaking: {text}")
    piper_path = os.path.join(os.path.dirname(__file__), "bin", "piper")
    if not os.path.exists(piper_path):
        return
        
    try:
        import subprocess
        model_path = os.path.join(os.path.dirname(__file__), "models", "tts", "en_US-lessac-low.onnx")
        echo_proc = subprocess.Popen(["echo", text], stdout=subprocess.PIPE)
        subprocess.run([piper_path, "--model", model_path, "--output_file", "out.wav"], 
                       stdin=echo_proc.stdout, stderr=subprocess.DEVNULL)
        
        play_cmd = ["aplay", "out.wav"]
        if sys.platform == "darwin":
            play_cmd = ["afplay", "out.wav"]
            
        subprocess.run(play_cmd, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[Mouth] Failed to run TTS: {e}")

def main():
    lib_name = "libhsru_llm.dll" if sys.platform == "win32" else "libhsru_llm.so"
    dll_path = os.path.join(os.path.dirname(__file__), lib_name)
    if not os.path.exists(dll_path):
        print(f"Error: {dll_path} not found.")
        return

    hsru = ctypes.CDLL(dll_path)
    
    hsru.hsru_llm_init_context.argtypes = [ctypes.c_char_p]
    hsru.hsru_llm_init_context.restype = ctypes.c_void_p
    hsru.hsru_llm_get_vocab_size.argtypes = [ctypes.c_void_p]
    hsru.hsru_llm_get_vocab_size.restype = ctypes.c_int
    hsru.hsru_llm_step.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_float)]
    hsru.hsru_save_state.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    hsru.hsru_load_state.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    weights_path = os.path.join(os.path.dirname(__file__), "models", "story_weights.bin")
    ctx = hsru.hsru_llm_init_context(weights_path.encode('utf-8'))
    
    # 1. LOAD PERSISTENT MEMORY
    history_file = os.path.join(os.path.dirname(__file__), "models", "history.bin")
    if os.path.exists(history_file):
        hsru.hsru_load_state(ctx, history_file.encode('utf-8'))
        print("[Brain] Woke up. Loaded persistent memory state from history.bin")
    else:
        print("[Brain] Woke up. Clean slate.")

    vocab_size = hsru.hsru_llm_get_vocab_size(ctx)
    logits_arr = np.zeros(vocab_size, dtype=np.float32)
    logits_ptr = logits_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from vocab.hf import HFTokenizerWrapper
        tokenizer_path = os.path.join(os.path.dirname(__file__), "vocab", "default.json")
        tokenizer = HFTokenizerWrapper(tokenizer_path)
    except Exception as e:
        print("Error loading tokenizer. Ensure vocab/ is deployed.")
        return

    print("--- HSRU Edge Assistant Active ---")
    while True:
        try:
            user_input = listen()
            if not user_input.strip(): continue
            if user_input.strip().lower() == "exit": break

            system_prompt = "You are a helpful smart home assistant with access to local network functions. Use them if required."
            prompt = f"SYSTEM: {system_prompt}\n<USER><INST> {user_input.strip()} </INST>\n<ASSISTANT>"
            
            prompt_ids = tokenizer.encode(prompt)
            if prompt_ids and prompt_ids[-1] == 50256:
                prompt_ids = prompt_ids[:-1]
                
            # CRITICAL: The model expects BOS at the beginning of the context
            prompt_ids = [50256] + prompt_ids
                
            # Feed prompt
            for token_id in prompt_ids:
                hsru.hsru_llm_step(ctx, token_id, logits_ptr)

            # Loop for recursive generation (in case of tool calls)
            while True:
                generated_tokens = []
                current_token = None
                
                for _ in range(200): # Max length
                    if current_token is not None:
                        hsru.hsru_llm_step(ctx, current_token, logits_ptr)
                        
                    logits_arr = np.ctypeslib.as_array(logits_ptr, shape=(vocab_size,))
                    # Greedy decode for function calls / commands
                    best_token = int(np.argmax(logits_arr))
                    generated_tokens.append(best_token)
                    current_token = best_token
                    
                    if current_token == 50256: # EOS
                        break

                response_text = tokenizer.decode(generated_tokens).strip()
                
                # 2. FUNCTION CALLING DETECTION & INJECTION
                if "<functioncall>" in response_text:
                    fn_str = response_text.split("<functioncall>")[-1].strip()
                    print("\n[Brain] Triggered API: " + fn_str)
                    try:
                        fn = json.loads(fn_str)
                        func_name = fn.get("name", fn.get("tool", "unknown_function"))
                        print(f"[Action] Executing function: {func_name}")
                        
                        # MOCK EXECUTION (User will replace this with real logic on the Pi)
                        result_msg = f"Function {func_name} executed successfully."
                        print(f"[Result] {result_msg}")
                        
                        # Feed the result back into the model context
                        system_prompt = f"\n<SYSTEM> {result_msg} </SYSTEM>\n<ASSISTANT>"
                        sys_ids = tokenizer.encode(system_prompt)
                        if sys_ids and sys_ids[-1] == 50256: sys_ids = sys_ids[:-1]
                        
                        for token_id in sys_ids:
                            hsru.hsru_llm_step(ctx, token_id, logits_ptr)
                            
                        # Loop continues to generate the spoken response...
                        continue

                    except json.JSONDecodeError:
                        print("[Error] Invalid JSON generated by model.")
                        speak("I encountered an error executing that command.")
                        break
                else:
                    speak(response_text)
                    break # Break inner loop, wait for next user input

            # 3. SAVE PERSISTENT MEMORY
            hsru.hsru_save_state(ctx, history_file.encode('utf-8'))
            print("[Brain] State saved to persistent memory.")

        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
