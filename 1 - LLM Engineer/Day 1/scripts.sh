# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Install Gemma
ollama run gemma3:270m

# Install phi3
ollama run phi3:latest

# stop ollama
systemctl stop ollama

# start ollama
systemctl start ollama

sudo systemctl disable ollama