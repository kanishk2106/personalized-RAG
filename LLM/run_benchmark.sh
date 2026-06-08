RUN_ID="${RUN_ID:-run_$(date +%Y%m%d_%H%M%S)}"
BASE_URL="${BASE_URL:?set BASE_URL (vLLM endpoint, e.g. https://...modal.run)}"
MODEL="${MODEL:-qwen3-8b-vllm}"
CONCURRENCY="${CONCURRENCY:-12}"
N="${N:-50}"
MAX_TOKENS="${MAX_TOKENS:-512}"
TEMPERATURE="${TEMPERATURE:-0.0}"
WARMUP="${WARMUP:-2}"
SEED="${SEED:-42}"
SCRAPER_INTERVAL="${SCRAPER_INTERVAL:-1.0}"

OUT_DIR="runs/${RUN_ID}"
mkdir -p "${OUT_DIR}"

echo "[run_benchmark] RUN_ID=${RUN_ID}"
echo "[run_benchmark] OUT_DIR=${OUT_DIR}"
echo "[run_benchmark] BASE_URL=${BASE_URL}"
echo "[run_benchmark] CONCURRENCY=${CONCURRENCY} N=${N} MAX_TOKENS=${MAX_TOKENS}"
python3 -m collectors.vllm_scraper \
    --base-url "${BASE_URL}" \
    --run-id "${RUN_ID}" \
    --out "${OUT_DIR}/vllm_metrics.jsonl" \
    --interval "${SCRAPER_INTERVAL}" \
    > "${OUT_DIR}/vllm_scraper.log" 2>&1 &
SCRAPER_PID=$!
cleanup() {
    if kill -0 "${SCRAPER_PID}" 2>/dev/null; then
        kill -TERM "${SCRAPER_PID}" 2>/dev/null || true
        wait "${SCRAPER_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM
sleep 2
python3 benchmark_client.py \
    --base-url "${BASE_URL}" \
    --model "${MODEL}" \
    --concurrency "${CONCURRENCY}" \
    --n "${N}" \
    --max-tokens "${MAX_TOKENS}" \
    --temperature "${TEMPERATURE}" \
    --warmup "${WARMUP}" \
    --seed "${SEED}" \
    --run-id "${RUN_ID}" \
    --output "${OUT_DIR}/client.csv"
sleep 3