"""
LLM Client Factory for multiple providers (OpenAI, AWS Bedrock, GROQ)
"""
import logging
from typing import Dict, Any, List
from config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """Unified LLM client interface for multiple providers"""
    
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider"""
        try:
            if self.provider == "openai":
                self._initialize_openai()
            elif self.provider == "aws":
                self._initialize_aws_bedrock()
            elif self.provider == "groq":
                self._initialize_groq()
            elif self.provider == "ollama":
                self._initialize_ollama()
            elif self.provider == "huggingface":
                self._initialize_huggingface()
            elif self.provider == "together":
                self._initialize_together()
            elif self.provider == "replicate":
                self._initialize_replicate()
            elif self.provider == "local_openai":
                self._initialize_local_openai()
            elif self.provider == "gemini":
                self._initialize_gemini()
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
            logger.info(f"LLM client initialized successfully for provider: {self.provider}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM client for {self.provider}: {str(e)}")
            raise
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def _initialize_aws_bedrock(self):
        """Initialize AWS Bedrock client"""
        try:
            import boto3
            
            # Use existing AWS credentials from environment or IAM role
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=settings.aws_bedrock_region,
                aws_access_key_id=settings.aws_access_key_id or None,
                aws_secret_access_key=settings.aws_secret_access_key or None
            )
            self.model = settings.aws_bedrock_model
            
        except ImportError:
            raise ImportError("Boto3 package not installed. Run: pip install boto3")
    
    def _initialize_groq(self):
        """Initialize GROQ client"""
        try:
            import groq
            if not settings.groq_api_key:
                raise ValueError("GROQ API key not configured")
            
            self.client = groq.Groq(api_key=settings.groq_api_key)
            self.model = settings.groq_model
            
        except ImportError:
            raise ImportError("GROQ package not installed. Run: pip install groq")
    
    def _initialize_ollama(self):
        """Initialize Ollama client for local models"""
        try:
            import requests
            
            # Test connection to Ollama server
            test_url = f"{settings.ollama_base_url}/api/tags"
            response = requests.get(test_url, timeout=5)
            
            if response.status_code != 200:
                raise ConnectionError(f"Cannot connect to Ollama server at {settings.ollama_base_url}")
            
            self.client = "ollama"  # We'll use requests directly
            self.model = settings.ollama_model
            self.base_url = settings.ollama_base_url
            
        except ImportError:
            raise ImportError("Requests package not installed. Run: pip install requests")
        except Exception as e:
            raise ConnectionError(f"Ollama server not available: {str(e)}. Make sure Ollama is running.")
    
    def _initialize_huggingface(self):
        """Initialize Hugging Face Transformers for local inference"""
        try:
            from transformers import pipeline
            import torch
            
            # Determine device
            if settings.huggingface_device == "auto":
                device = 0 if torch.cuda.is_available() else -1
            elif settings.huggingface_device == "cuda":
                device = 0
            else:
                device = -1
            
            # Initialize the pipeline
            self.client = pipeline(
                "text-generation",
                model=settings.huggingface_model,
                device=device,
                cache_dir=settings.huggingface_cache_dir
            )
            self.model = settings.huggingface_model
            
        except ImportError:
            raise ImportError("Transformers package not installed. Run: pip install transformers torch")
    
    def _initialize_together(self):
        """Initialize Together AI client"""
        try:
            import together
            
            if not settings.together_api_key:
                raise ValueError("Together AI API key not configured")
            
            together.api_key = settings.together_api_key
            self.client = together
            self.model = settings.together_model
            
        except ImportError:
            raise ImportError("Together package not installed. Run: pip install together")
    
    def _initialize_replicate(self):
        """Initialize Replicate client"""
        try:
            import replicate
            
            if not settings.replicate_api_token:
                raise ValueError("Replicate API token not configured")
            
            self.client = replicate.Client(api_token=settings.replicate_api_token)
            self.model = settings.replicate_model
            
        except ImportError:
            raise ImportError("Replicate package not installed. Run: pip install replicate")
    
    def _initialize_local_openai(self):
        """Initialize local OpenAI-compatible server (LM Studio, text-generation-webui, etc.)"""
        try:
            import openai
            
            self.client = openai.OpenAI(
                base_url=settings.local_openai_base_url,
                api_key=settings.local_openai_api_key
            )
            self.model = settings.local_openai_model
            
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def _initialize_gemini(self):
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            if not settings.gemini_api_key:
                raise ValueError("Gemini API key not configured")
            
            genai.configure(api_key=settings.gemini_api_key)
            self.client = genai.GenerativeModel(settings.gemini_model)
            self.model = settings.gemini_model
            
        except ImportError:
            raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using the configured provider"""
        try:
            if self.provider == "openai":
                return await self._openai_chat_completion(messages, **kwargs)
            elif self.provider == "aws":
                return await self._aws_chat_completion(messages, **kwargs)
            elif self.provider == "groq":
                return await self._groq_chat_completion(messages, **kwargs)
            elif self.provider == "ollama":
                return await self._ollama_chat_completion(messages, **kwargs)
            elif self.provider == "huggingface":
                return await self._huggingface_chat_completion(messages, **kwargs)
            elif self.provider == "together":
                return await self._together_chat_completion(messages, **kwargs)
            elif self.provider == "replicate":
                return await self._replicate_chat_completion(messages, **kwargs)
            elif self.provider == "local_openai":
                return await self._local_openai_chat_completion(messages, **kwargs)
            elif self.provider == "gemini":
                return await self._gemini_chat_completion(messages, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Chat completion failed for {self.provider}: {str(e)}")
            raise
    
    async def _openai_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """OpenAI chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000)
        )
        return response.choices[0].message.content
    
    async def _aws_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """AWS Bedrock chat completion"""
        import json
        
        # Convert messages to Claude format
        prompt = self._convert_messages_to_claude_prompt(messages)
        
        body = {
            "prompt": prompt,
            "max_tokens_to_sample": kwargs.get('max_tokens', 1000),
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": 0.9,
        }
        
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body.get('completion', '')
    
    async def _groq_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """GROQ chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000)
        )
        return response.choices[0].message.content
    
    async def _ollama_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Ollama chat completion"""
        import requests
        
        # Convert messages to a single prompt
        prompt = self._convert_messages_to_prompt(messages)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "num_predict": kwargs.get('max_tokens', 1000)
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        
        result = response.json()
        return result.get('response', '')
    
    async def _huggingface_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Hugging Face Transformers chat completion"""
        # Convert messages to a single prompt
        prompt = self._convert_messages_to_prompt(messages)
        
        # Generate response
        outputs = self.client(
            prompt,
            max_length=len(prompt) + kwargs.get('max_tokens', 200),
            temperature=kwargs.get('temperature', 0.7),
            do_sample=True,
            pad_token_id=self.client.tokenizer.eos_token_id
        )
        
        # Extract the generated text (remove the input prompt)
        generated_text = outputs[0]['generated_text']
        response = generated_text[len(prompt):].strip()
        return response
    
    async def _together_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Together AI chat completion"""
        # Convert messages to a single prompt
        prompt = self._convert_messages_to_prompt(messages)
        
        output = self.client.Complete.create(
            prompt=prompt,
            model=self.model,
            max_tokens=kwargs.get('max_tokens', 1000),
            temperature=kwargs.get('temperature', 0.7)
        )
        
        return output['output']['choices'][0]['text']
    
    async def _replicate_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Replicate chat completion"""
        # Convert messages to a single prompt
        prompt = self._convert_messages_to_prompt(messages)
        
        output = self.client.run(
            self.model,
            input={
                "prompt": prompt,
                "max_new_tokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7)
            }
        )
        
        # Replicate returns a generator, so we need to join the results
        return ''.join(output)
    
    async def _local_openai_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Local OpenAI-compatible server chat completion"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000)
        )
        return response.choices[0].message.content
    
    async def _gemini_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Google Gemini chat completion"""
        # Convert messages to Gemini format
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"Instructions: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts)
        
        # Generate response
        response = self.client.generate_content(
            prompt,
            generation_config={
                'temperature': kwargs.get('temperature', 0.7),
                'max_output_tokens': kwargs.get('max_tokens', 1000),
                'top_p': 0.8,
                'top_k': 10
            }
        )
        
        return response.text
    
    def _convert_messages_to_claude_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Claude prompt format"""
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"Human: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a simple prompt format for most open source models"""
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        return {
            'provider': self.provider,
            'model': getattr(self, 'model', 'unknown'),
            'available': self.client is not None
        }

# Global LLM client instance
llm_client = None

def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance"""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client

def initialize_llm_client() -> LLMClient:
    """Initialize and return a new LLM client instance"""
    return LLMClient()
