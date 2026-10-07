import ctypes
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
import numpy as np

import argparse

def test_api():
    parser = argparse.ArgumentParser(description="Test HSRU Edge API Generation")
    parser.add_argument("--temp", type=float, default=0.1, help="Temperature for sampling (default: 0.1)")
    parser.add_argument("--top_k", type=int, default=50, help="Top-K sampling (default: 50)")
    parser.add_argument("--rep_penalty", type=float, default=1.2, help="Repetition penalty (default: 1.2)")
    parser.add_argument("--gen_len", type=int, default=100, help="Number of tokens to generate (default: 100)")
    parser.add_argument("--chat", action="store_true", help="Start an interactive chat session")
    parser.add_argument("--rag_file", type=str, default="", help="Path to a text file to act as context (RAG)")
    parser.add_argument("--prompt", type=str, default="The neural network learns", help="Starting prompt for batch mode")
    args, _ = parser.parse_known_args()

    import sys
    lib_name = "libhsru_llm.dll" if sys.platform == "win32" else "libhsru_llm.so"
    dll_path = os.path.join(os.path.dirname(__file__), lib_name)
    if not os.path.exists(dll_path):
        print(f"Error: {dll_path} not found.")
        return

    print(f"Loading {dll_path}...")
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        # Python 3.8+ requires winmode=0 to search the system PATH for DLL dependencies (like MinGW libs)
        hsru = ctypes.CDLL(dll_path, winmode=0)
    else:
        hsru = ctypes.CDLL(dll_path)

    # API: void* hsru_llm_init_context(const char* weights_path);
    hsru.hsru_llm_init_context.argtypes = [ctypes.c_char_p]
    hsru.hsru_llm_init_context.restype = ctypes.c_void_p

    # API: int hsru_llm_get_vocab_size(void* ctx);
    hsru.hsru_llm_get_vocab_size.argtypes = [ctypes.c_void_p]
    hsru.hsru_llm_get_vocab_size.restype = ctypes.c_int

    # API: void hsru_llm_step(void* ctx, int current_token, float* out_logits);
    hsru.hsru_llm_step.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_float)]
    
    # API: void hsru_llm_free_context(void* ctx);
    hsru.hsru_llm_free_context.argtypes = [ctypes.c_void_p]

    # API: int hsru_save_state(void* ctx, const char* filepath);
    hsru.hsru_save_state.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    hsru.hsru_save_state.restype = ctypes.c_int
    
    # API: int hsru_load_state(void* ctx, const char* filepath);
    hsru.hsru_load_state.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    hsru.hsru_load_state.restype = ctypes.c_int

    weights_path = os.path.join(os.path.dirname(__file__), "models", "story_weights.bin")
    if not os.path.exists(weights_path):
        print(f"Error: {weights_path} not found. Ensure models are deployed.")
        return

    print("Initializing Opaque C-API Context...")
    ctx = hsru.hsru_llm_init_context(weights_path.encode('utf-8'))
    if not ctx:
        print("Failed to initialize context.")
        return

    vocab_size = hsru.hsru_llm_get_vocab_size(ctx)
    print(f"Context initialized successfully! Vocab Size: {vocab_size}")

    logits_arr = np.zeros(vocab_size, dtype=np.float32)
    logits_ptr = logits_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    try:
        # 1. Load Vocab for printing
        vocab_path = os.path.join(os.path.dirname(__file__), "models", "vocab.txt")
        vocab = []
        if os.path.exists(vocab_path):
            with open(vocab_path, "r", encoding="utf-8") as f:
                vocab = [line.strip('\n').replace('\\n', '\n') for line in f]
                
        # (existing context init logic goes above this, but since I am editing from line 63...)
        
        # 2. Tokenizer
        tokenizer = None
        try:
            current_dir = os.path.abspath(os.path.dirname(__file__))
            parent_dir = os.path.abspath(os.path.dirname(current_dir))
            
            if os.path.exists(os.path.join(current_dir, "vocab")):
                vocab_dir = current_dir
            elif os.path.exists(os.path.join(parent_dir, "vocab")):
                vocab_dir = parent_dir
            else:
                vocab_dir = current_dir
                
            if vocab_dir not in sys.path:
                sys.path.insert(0, vocab_dir)
                
            from vocab.hf import HFTokenizerWrapper
            tokenizer_path = os.path.join(vocab_dir, "vocab", "default.json")
            tokenizer = HFTokenizerWrapper(tokenizer_path)
        except Exception as e:
            print(f"Could not load python tokenizer ({e}). Chat mode requires the tokenizer.")
            if args.chat:
                return

        # Configure stdout for utf-8
        sys.stdout.reconfigure(encoding='utf-8')
        
        if args.chat:
            print("\n" + "="*50)
            print(" HSRU Edge Chat Mode (Type 'exit' or 'quit' to end)")
            print(" Commands: /save <path>, /load <path>, /context <path>, /new")
            print("="*50 + "\n")
            
            # Start with an initial context token
            current_token = 50256
            current_rag_context = ""
            conversation_history = []
            
            if args.rag_file and os.path.exists(args.rag_file):
                with open(args.rag_file, "r", encoding="utf-8") as f:
                    current_rag_context = f.read().strip()
                print(f"[System] Loaded RAG Context from {args.rag_file} ({len(current_rag_context)} chars)")
            
            while True:
                try:
                    user_input = input("\nUser: ")
                    if user_input.strip().lower() in ["exit", "quit"]:
                        break
                        
                    # Convert literal backticks or slashes to actual newlines
                    user_input = user_input.replace("`n", "\n").replace("\\n", "\n")
                    user_input = user_input.strip().strip('"').strip("'")
                    
                    if not user_input.strip():
                        continue
                        
                    if user_input.strip().lower().startswith("/save "):
                        filepath = user_input.strip().split(" ", 1)[1]
                        res = hsru.hsru_save_state(ctx, filepath.encode('utf-8'))
                        if res == 0:
                            print(f"[System] State saved successfully to {filepath}")
                        else:
                            print(f"[System] Failed to save state.")
                        continue
                        
                    if user_input.strip().lower().startswith("/load "):
                        filepath = user_input.strip().split(" ", 1)[1]
                        res = hsru.hsru_load_state(ctx, filepath.encode('utf-8'))
                        if res == 0:
                            print(f"[System] State loaded successfully from {filepath}")
                        else:
                            print(f"[System] Failed to load state.")
                        continue
                        
                    if user_input.strip().lower().startswith("/context "):
                        filepath = user_input.strip().split(" ", 1)[1]
                        if os.path.exists(filepath):
                            with open(filepath, "r", encoding="utf-8") as f:
                                current_rag_context = f.read().strip()
                            print(f"[System] RAG Context updated from {filepath} ({len(current_rag_context)} chars)")
                        else:
                            print(f"[System] Error: Context file {filepath} not found.")
                        continue
                        
                    if user_input.strip().lower() in ["/new", "/clear"]:
                        conversation_history = []
                        hsru.hsru_llm_free_context(ctx)
                        ctx = hsru.hsru_llm_init_context(weights_path.encode('utf-8'))
                        print("[System] Started a new chat. Context and History cleared.")
                        continue
                        
                    SPECIAL_TOKENS = {
                        "USER": "<USER>",
                        "INST": "<INST>",
                        "END_INST": "</INST>",
                        "ASSISTANT": "<ASSISTANT>"
                    }
                    
                    parts = []
                    
                    # If this is the first turn, we feed SYSTEM context and prepend BOS
                    is_first_turn = len(conversation_history) == 0
                    if is_first_turn:
                        if current_rag_context:
                            parts.append(f"SYSTEM: {current_rag_context}")
                    
                    # Current user turn ONLY (history is already in the RNN state!)
                    parts.append(f"{SPECIAL_TOKENS['USER']}{SPECIAL_TOKENS['INST']} {user_input.strip()} {SPECIAL_TOKENS['END_INST']}")
                    parts.append(SPECIAL_TOKENS['ASSISTANT'])
                        
                    prompt = "\n".join(parts)
                    
                    # If it's not the first turn, we need a newline before <USER> to match training format exactly
                    if not is_first_turn:
                        prompt = "\n" + prompt

                    prompt_ids = tokenizer.encode(prompt)
                    
                    if prompt_ids and prompt_ids[-1] == 50256:
                        prompt_ids = prompt_ids[:-1]
                        
                    if is_first_turn:
                        prompt_ids = [50256] + prompt_ids
                        
                    print("Assistant: ", end="", flush=True)
                    
                    # Step the prompt through
                    for i, token_id in enumerate(prompt_ids):
                        hsru.hsru_llm_step(ctx, token_id, logits_ptr)
                        
                    current_token = None
                    generated_tokens = []
                    
                    for t in range(args.gen_len):
                        # The logits_ptr already contains the predictions from the previous token.
                        # We only need to step if we have a newly generated token.
                        if current_token is not None:
                            hsru.hsru_llm_step(ctx, current_token, logits_ptr)
                        
                        logits_arr = np.ctypeslib.as_array(logits_ptr, shape=(vocab_size,))
                        for past_id in generated_tokens:
                            if logits_arr[past_id] > 0:
                                logits_arr[past_id] /= args.rep_penalty
                            else:
                                logits_arr[past_id] *= args.rep_penalty
                                
                        # Sampling
                        scaled = logits_arr / max(args.temp, 1e-8)
                        top_indices = np.argsort(scaled)[-args.top_k:]
                        top_logits = scaled[top_indices]
                        
                        exp_logits = np.exp(top_logits - np.max(top_logits))
                        probs = exp_logits / np.sum(exp_logits)
                        
                        best_token = np.random.choice(top_indices, p=probs)
                        generated_tokens.append(best_token)
                        current_token = best_token
                        
                        if current_token == 50256:
                            # CRITICAL: We MUST step the EOS token into the C++ context 
                            # so the model knows it finished speaking! Otherwise state corrupts.
                            hsru.hsru_llm_step(ctx, current_token, logits_ptr)
                            break
                            
                        if vocab:
                            print(vocab[current_token], end="", flush=True)
                        else:
                            print(f"[{current_token}] ", end="", flush=True)
                            
                    print() # newline after response
                    
                    # Save the exchange to history
                    assistant_response = tokenizer.decode(generated_tokens) if tokenizer else ""
                    conversation_history.append({"role": "user", "content": user_input.strip()})
                    conversation_history.append({"role": "assistant", "content": assistant_response.strip()})
                    
                except KeyboardInterrupt:
                    break
        else:
            # ORIGINAL BATCH MODE
            try:
                prompt = args.prompt
                prompt_ids = tokenizer.encode(prompt)
                if prompt_ids and prompt_ids[-1] == 50256:
                    prompt_ids = prompt_ids[:-1]
                print(f"Prompt: '{prompt}' -> {prompt_ids}")
            except Exception as e:
                print(f"Could not load python tokenizer ({e}). Falling back to <|endoftext|> (50256)")
                prompt_ids = [50256]
                
            print("\n--- Stepping through Prompt ---")
            
            for i, token_id in enumerate(prompt_ids):
                hsru.hsru_llm_step(ctx, token_id, logits_ptr)
                if vocab:
                    print(vocab[token_id], end="", flush=True)
                else:
                    print(f"[{token_id}] ", end="", flush=True)
                    
            print(f"\n\n--- Starting Full Generation (Temp: {args.temp}, Top-K: {args.top_k}) ---")
            
            current_token = prompt_ids[-1]
            generated_tokens = prompt_ids.copy()
            
            import time
            t0 = time.time()
            
            for t in range(args.gen_len):
                hsru.hsru_llm_step(ctx, current_token, logits_ptr)
                
                # Repetition Penalty
                for past_id in generated_tokens:
                    if logits_arr[past_id] > 0:
                        logits_arr[past_id] /= args.rep_penalty
                    else:
                        logits_arr[past_id] *= args.rep_penalty
                        
                # Sampling
                scaled = logits_arr / max(args.temp, 1e-8)
                
                top_indices = np.argsort(scaled)[-args.top_k:]
                top_logits = scaled[top_indices]
                
                # Softmax
                exp_logits = np.exp(top_logits - np.max(top_logits))
                probs = exp_logits / np.sum(exp_logits)
                
                best_token = np.random.choice(top_indices, p=probs)
                
                generated_tokens.append(best_token)
                current_token = best_token
                
                if current_token == 50256:
                    break
                    
                if vocab:
                    print(vocab[current_token], end="", flush=True)
                else:
                    print(f"[{current_token}] ", end="", flush=True)
                    
            t1 = time.time()
            print(f"\n\n[INFO] Generated {len(generated_tokens)} tokens in {t1-t0:.2f}s ({len(generated_tokens)/(t1-t0):.2f} tokens/sec)")

    except Exception as e:
        print(f"API Call Failed: {e}")
    finally:
        hsru.hsru_llm_free_context(ctx)
        print("Context freed safely.")

if __name__ == "__main__":
    test_api()
