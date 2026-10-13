import os
from typing import Any, List, Optional, Sequence

# pyrefly: ignore [missing-import]
from tokenizers import Tokenizer
try:
    from transformers import AutoTokenizer, PreTrainedTokenizerBase
except ImportError:
    AutoTokenizer = None
    PreTrainedTokenizerBase = None


class HFTokenizerWrapper:
    def __init__(self, tokenizer_path_or_instance: Any):
        print(f"[TokenizerWrapper] Loading: {tokenizer_path_or_instance}")
        self._is_transformers = False
        
        if isinstance(tokenizer_path_or_instance, str):
            # Check if it's a local JSON file for the 'tokenizers' library
            if os.path.exists(tokenizer_path_or_instance) and tokenizer_path_or_instance.endswith(".json"):
                self.tokenizer = Tokenizer.from_file(tokenizer_path_or_instance)
            else:
                # Fallback to HuggingFace Transformers (e.g. "gpt2", "meta-llama/Llama-2-7b-hf")
                if AutoTokenizer is None:
                    raise ImportError("The 'transformers' library is required to load pretrained tokenizers from the Hub.")
                self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path_or_instance)
                self._is_transformers = True
                
        elif isinstance(tokenizer_path_or_instance, Tokenizer):
            self.tokenizer = tokenizer_path_or_instance
        elif PreTrainedTokenizerBase is not None and isinstance(tokenizer_path_or_instance, PreTrainedTokenizerBase):
            self.tokenizer = tokenizer_path_or_instance
            self._is_transformers = True
        else:
            raise TypeError("tokenizer_path_or_instance must be a path string, a tokenizers.Tokenizer, or a transformers Tokenizer.")

        # Extract special tokens
        if self._is_transformers:
            self.vocab_size = len(self.tokenizer)
            self.pad_token_id = self.tokenizer.pad_token_id
            self.bos_token_id = self.tokenizer.bos_token_id
            self.eos_token_id = self.tokenizer.eos_token_id
            self.unk_token_id = self.tokenizer.unk_token_id
        else:
            self.vocab_size = self.tokenizer.get_vocab_size()
            self.pad_token_id = self._get_special_token_id("<pad>", "padding")
            self.bos_token_id = self._get_special_token_id("<s>", "BOS")
            self.eos_token_id = self._get_special_token_id("</s>", "EOS")
            self.unk_token_id = self._get_special_token_id("<unk>", "unknown")

            # GPT-2 compatibility fallback
            if self.eos_token_id is None:
                self.eos_token_id = self._get_special_token_id("<|endoftext|>", "EOS (GPT-2 fallback)")
            if self.bos_token_id is None:
                self.bos_token_id = self._get_special_token_id("<|endoftext|>", "BOS (GPT-2 fallback)")
            if self.pad_token_id is None and self.eos_token_id is not None:
                self.pad_token_id = self.eos_token_id

        if self.pad_token_id is None:
            print("Warning: padding token not found. This might be an issue if padding is required.")

    def _get_special_token_id(self, token_str: str, token_name: str) -> Optional[int]:
        if self._is_transformers:
            return self.tokenizer.convert_tokens_to_ids(token_str)
        else:
            token_id = self.tokenizer.token_to_id(token_str)
            return token_id

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encodes text into a list of token IDs.
        If add_special_tokens is True, prepends BOS and appends EOS if they are defined.
        """
        if self._is_transformers:
            # Transformers automatically handles special tokens if requested
            token_ids = self.tokenizer.encode(text, add_special_tokens=add_special_tokens)
            return token_ids
        else:
            encoding = self.tokenizer.encode(text, add_special_tokens=False)
            token_ids = encoding.ids

            if add_special_tokens:
                final_ids = []
                if self.bos_token_id is not None:
                    final_ids.append(self.bos_token_id)
                final_ids.extend(token_ids)
                if self.eos_token_id is not None:
                    final_ids.append(self.eos_token_id)
                return final_ids
            else:
                return token_ids

    def decode(self, ids: Sequence[int], skip_special_tokens: bool = True) -> str:
        """
        Decodes a list of token IDs back to a string.
        """
        if not isinstance(ids, list):
            if hasattr(ids, 'tolist'):
                ids_list = ids.tolist()
            else:
                ids_list = list(ids)
        else:
            ids_list = ids

        return self.tokenizer.decode(ids_list, skip_special_tokens=skip_special_tokens)

    def tokenize_to_subwords(self, text: str) -> List[str]:
        """
        Tokenizes text into a list of subword strings (not IDs).
        """
        if self._is_transformers:
            return self.tokenizer.tokenize(text, add_special_tokens=False)
        else:
            encoding = self.tokenizer.encode(text, add_special_tokens=False)
            return encoding.tokens