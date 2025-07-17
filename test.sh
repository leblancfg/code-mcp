GCF_URL=https://us-central1-prd-s5y-librechat-f05a.cloudfunctions.net/code-interpreter \
npx @modelcontextprotocol/inspector@0.11.0 \
--cli uv run python main.py \
--method tools/call \
--tool-name run_code \
--tool-arg "code=print(1+1)" \
--tool-arg language=python \
| jq
