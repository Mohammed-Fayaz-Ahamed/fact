import asyncio
import time
import httpx

# Target Configuration
TOTAL_REQUESTS = 10000
CONCURRENCY_LIMIT = 100  # Number of concurrent workers hitting the server simultaneously
BASE_URL = "http://127.0.0.1:8000"
ENDPOINTS = ["/", "/slow", "/error"]

async def send_request(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, worker_id: int):
    """Sends a request to a rotating target endpoint using a semaphore to limit concurrency."""
    # Rotate through targets: 70% root, 20% slow, 10% error
    if worker_id % 10 == 0:
        url = f"{BASE_URL}/error"
    elif worker_id % 5 == 0:
        url = f"{BASE_URL}/slow"
    else:
        url = f"{BASE_URL}/"

    async with semaphore:
        start = time.perf_counter()
        try:
            response = await client.get(url, timeout=10.0)
            latency = (time.perf_counter() - start) * 1000
            return response.status_code, latency
        except Exception as e:
            return "FAILED", 0.0

async def main():
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    print(f" Initializing stress-test engine...")
    print(f" Bombarding {BASE_URL} with {TOTAL_REQUESTS} requests (Max Concurrency: {CONCURRENCY_LIMIT})...")
    
    # Configure connection pooling limits inside HTTPX to support high concurrency
    limits = httpx.Limits(max_keepalive_connections=CONCURRENCY_LIMIT, max_connections=CONCURRENCY_LIMIT * 2)
    
    start_time = time.perf_counter()
    
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [send_request(client, semaphore, i) for i in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
    total_time = time.perf_counter() - start_time
    
    # Analyze metrics
    status_counts = {}
    latencies = []
    
    for status, latency in results:
        status_counts[status] = status_counts.get(status, 0) + 1
        if status != "FAILED":
            latencies.append(latency)
            
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    throughput = TOTAL_REQUESTS / total_time
    
    print("\n" + "="*40)
    print(" BENCHMARK PERFORMANCE RESULTS")
    print("="*40)
    print(f" Total Execution Time : {total_time:.2f} seconds")
    print(f" Throughput            : {throughput:.2f} requests/sec")
    print(f" Avg HTTP Round-trip  : {avg_latency:.2f} ms")
    print("\n Response Distribution Summary:")
    for status, count in status_counts.items():
        print(f"  • Status {status} : {count} requests")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())