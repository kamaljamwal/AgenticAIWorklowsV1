# 🤖 LLM Providers Guide - Open Source & Free Options

This guide explains how to use various LLM providers with the Agentic AI Workflows system, including many **free and open source options**.

## 🆓 **FREE & OPEN SOURCE OPTIONS**

### 1. **Google Gemini** (FREE with generous limits)

**Best for**: High-quality responses, multimodal capabilities, easy setup

**Setup**:
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Install: `pip install google-generativeai`

**Configuration**:
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro
```

**Available Models**:
- `gemini-1.5-flash` - Fast, efficient, FREE with generous limits
- `gemini-1.5-pro` - More capable, FREE tier available
- `gemini-pro` - Previous generation, still very capable

**Free Tier Limits**:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

**Pros**: ✅ FREE with high limits, ✅ Excellent quality, ✅ Fast responses, ✅ Multimodal
**Cons**: ❌ Requires internet, ❌ Google account needed

### 2. **Ollama** (Completely Free - Local Models)

**Best for**: Privacy, no API costs, works offline

**Setup**:
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama2`
3. Start Ollama service (usually auto-starts)

**Configuration**:
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2  # or mistral, codellama, vicuna, etc.
```

**Available Models**:
- `llama2` (7B) - General purpose, good quality
- `mistral` (7B) - Fast and capable
- `codellama` (7B) - Excellent for coding tasks
- `vicuna` (7B) - Good conversational model
- `phi` (3B) - Lightweight, faster inference

**Pros**: ✅ Completely free, ✅ Works offline, ✅ Privacy-focused
**Cons**: ❌ Requires local compute resources

---

### 2. **Hugging Face Transformers** (Completely Free - Local)

**Best for**: Custom models, research, complete control

**Setup**:
```bash
pip install transformers torch accelerate
```

**Configuration**:
```bash
LLM_PROVIDER=huggingface
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium
HUGGINGFACE_DEVICE=auto  # auto, cpu, cuda
HUGGINGFACE_CACHE_DIR=./hf_cache
```

**Recommended Models**:
- `microsoft/DialoGPT-medium` - Conversational AI
- `google/flan-t5-base` - Instruction following
- `EleutherAI/gpt-neo-2.7B` - General purpose
- `microsoft/CodeBERT-base` - Code understanding

**Pros**: ✅ Completely free, ✅ Huge model selection, ✅ Customizable
**Cons**: ❌ Requires technical setup, ❌ Resource intensive

---

### 3. **Together AI** (Free Tier Available)

**Best for**: Easy setup with free credits

**Setup**:
1. Sign up at https://together.ai/
2. Get free credits (usually $25-50)
3. Get API key from dashboard

**Configuration**:
```bash
LLM_PROVIDER=together
TOGETHER_API_KEY=your_api_key_here
TOGETHER_MODEL=togethercomputer/llama-2-7b-chat
```

**Available Models**:
- `togethercomputer/llama-2-7b-chat`
- `togethercomputer/falcon-7b-instruct`
- `NousResearch/Nous-Hermes-llama-2-7b`

**Pros**: ✅ Easy setup, ✅ Free credits, ✅ Good performance
**Cons**: ❌ Limited free usage

---

### 4. **Replicate** (Free Tier Available)

**Best for**: Trying different models easily

**Setup**:
1. Sign up at https://replicate.com/
2. Get free credits
3. Get API token from account settings

**Configuration**:
```bash
LLM_PROVIDER=replicate
REPLICATE_API_TOKEN=your_token_here
REPLICATE_MODEL=meta/llama-2-7b-chat
```

**Available Models**:
- `meta/llama-2-7b-chat`
- `mistralai/mistral-7b-instruct-v0.1`
- `togethercomputer/falcon-7b-instruct`

**Pros**: ✅ Easy to try different models, ✅ Free credits
**Cons**: ❌ Limited free usage, ❌ Can be slower

---

### 5. **Local OpenAI-Compatible Servers** (Completely Free)

**Best for**: Using existing local AI setups

**Compatible Software**:
- **LM Studio**: https://lmstudio.ai/ (GUI, easy setup)
- **text-generation-webui**: https://github.com/oobabooga/text-generation-webui
- **FastChat**: https://github.com/lm-sys/FastChat
- **vLLM**: https://github.com/vllm-project/vllm

**Configuration**:
```bash
LLM_PROVIDER=local_openai
LOCAL_OPENAI_BASE_URL=http://localhost:1234/v1  # LM Studio default
LOCAL_OPENAI_MODEL=local-model
LOCAL_OPENAI_API_KEY=not-needed
```

**Pros**: ✅ Use any local model, ✅ OpenAI-compatible API, ✅ Full control
**Cons**: ❌ Requires separate setup

---

## 💰 **PAID OPTIONS** (Already Supported)

### OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4
```

### AWS Bedrock
```bash
LLM_PROVIDER=aws
AWS_BEDROCK_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
```

### GROQ (Fast Inference)
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama3-8b-8192
```

---

## 🚀 **Quick Start Guide**

### Option 1: Ollama (Recommended for Beginners)
```bash
# 1. Install Ollama from https://ollama.ai/
# 2. Pull a model
ollama pull llama2

# 3. Configure your .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2

# 4. Start your application
python main_working.py
```

### Option 2: Together AI (Easiest Cloud Option)
```bash
# 1. Sign up at https://together.ai/ and get free credits
# 2. Get your API key
# 3. Configure your .env
LLM_PROVIDER=together
TOGETHER_API_KEY=your_key_here

# 4. Start your application
python main_working.py
```

---

## 📊 **Comparison Table**

| Provider | Cost | Setup Difficulty | Performance | Privacy | Offline |
|----------|------|------------------|-------------|---------|---------|
| Ollama | Free | Easy | Good | High | Yes |
| Hugging Face | Free | Medium | Variable | High | Yes |
| Together AI | Free Tier | Easy | Good | Medium | No |
| Replicate | Free Tier | Easy | Good | Medium | No |
| Local OpenAI | Free | Hard | Variable | High | Yes |
| OpenAI | Paid | Easy | Excellent | Low | No |
| AWS Bedrock | Paid | Medium | Excellent | Medium | No |
| GROQ | Paid | Easy | Fast | Medium | No |

---

## 🔧 **Installation Commands**

```bash
# For Ollama (after installing Ollama)
ollama pull llama2

# For Hugging Face
pip install transformers torch accelerate

# For Together AI
pip install together

# For Replicate
pip install replicate

# Install all optional dependencies
pip install -r requirements_llm_providers.txt
```

---

## 🎯 **Recommendations by Use Case**

- **🏠 Home/Personal Use**: Ollama with llama2 or mistral
- **💼 Small Business**: Together AI or Replicate free tier
- **🏢 Enterprise**: OpenAI GPT-4 or AWS Bedrock
- **🔬 Research/Development**: Hugging Face Transformers
- **⚡ Need Speed**: GROQ or local vLLM setup
- **🔒 Privacy Critical**: Ollama or Hugging Face (local only)
- **💻 Coding Tasks**: Ollama with codellama or OpenAI GPT-4

---

## ❓ **Troubleshooting**

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve
```

### Hugging Face Issues
```bash
# Clear cache if models fail to load
rm -rf ./hf_cache
```

### Connection Issues
- Check firewall settings for local providers
- Verify API keys for cloud providers
- Ensure sufficient disk space for local models

---

## 📈 **Performance Tips**

1. **For Local Models**: Use GPU if available (set `HUGGINGFACE_DEVICE=cuda`)
2. **For Ollama**: Use smaller models (phi, mistral) for faster responses
3. **For Cloud APIs**: Adjust temperature and max_tokens for better responses
4. **Memory**: Local models require 4-16GB RAM depending on model size

---

**🎉 You now have access to multiple free and open source LLM options!**

Choose the option that best fits your needs, budget, and technical requirements.
