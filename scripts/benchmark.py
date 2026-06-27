import asyncio
import time
import random
import httpx

# Target Configuration
TOTAL_REQUESTS = 10000
CONCURRENCY_LIMIT = 100
BASE_URL = "http://127.0.0.1:8000"

# Mock Tenants & Metadata Pools
TENANTS = ["alpha-corp", "beta-labs", "gamma-tech", "delta-retail"]

async def send_request(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, worker_id: int):
    """Sends a request with randomized multi-tenant attributes and sizes."""
    # Select endpoints and tenants deterministically or randomly
    tenant = random.choice(TENANTS)
    
    if worker_id % 10 == 0:
        url = f"{BASE_URL}/error"
    elif worker_id % 5 == 0:
        url = f"{BASE_URL}/slow"
    else:
        url = f"{BASE_URL}/"

    # Generate custom headers representing our tenant and unique requests
    headers = {
        "x-tenant-id": tenant,
        "x-request-id": f"req-bench-{worker_id}",
        "content-length": str(random.randint(100, 5000)) if worker_id % 3 == 0 else "0"
    }

    async with semaphore:
        start = time.perf_counter()
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            latency = (time.perf_counter() - start) * 1000
            return response.status_code, latency, tenant
        except Exception:
            return "FAILED", 0.0, tenant

async def main():
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    print(f" Initializing multi-tenant stress-test engine...")
    print(f" Bombarding {BASE_URL} with {TOTAL_REQUESTS} multi-tenant requests...")
    
    limits = httpx.Limits(max_keepalive_connections=CONCURRENCY_LIMIT, max_connections=CONCURRENCY_LIMIT * 2)
    start_time = time.perf_counter()
    
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [send_request(client, semaphore, i) for i in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
    total_time = time.perf_counter() - start_time
    
    status_counts = {}
    tenant_counts = {}
    latencies = []
    
    for status, latency, tenant in results:
        status_counts[status] = status_counts.get(status, 0) + 1
        tenant_counts[tenant] = tenant_counts.get(tenant, 0) + 1
        if status != "FAILED":
            latencies.append(latency)
            
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    throughput = TOTAL_REQUESTS / total_time
    
    print("\n" + "="*40)
    print(" MULTI-TENANT BENCHMARK RESULTS")
    print("="*40)
    print(f" Total Time  : {total_time:.2f} seconds")
    print(f" Throughput  : {throughput:.2f} req/sec")
    print(f" Avg Latency : {avg_latency:.2f} ms")
    print("\n Tenant Request Distribution:")
    for t, c in tenant_counts.items():
        print(f"  • {t:<15} : {c} requests")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())