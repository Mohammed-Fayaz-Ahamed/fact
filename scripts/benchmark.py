import asyncio
import argparse
import random
import statistics
import time

import httpx

TENANTS = [
    "alpha-corp",
    "beta-labs",
    "gamma-tech",
    "delta-retail",
]


async def send_request(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    worker_id: int,
    base_url: str,
):
    tenant = random.choice(TENANTS)

    if worker_id % 10 == 0:
        url = f"{base_url}/error"
    elif worker_id % 5 == 0:
        url = f"{base_url}/slow"
    else:
        url = f"{base_url}/"
    

    headers = {
        "x-tenant-id": tenant,
        "x-request-id": f"req-bench-{worker_id}",
    }

    async with semaphore:
        start = time.perf_counter()

        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            latency = (time.perf_counter() - start) * 1000
            return response.status_code, latency, tenant

        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            print(f"{type(e).__name__}: {e}")
            return "FAILED", latency, tenant


def percentile(values, p):
    """Calculate percentile without external dependencies."""
    if not values:
        return 0

    values = sorted(values)

    index = int((len(values) - 1) * p / 100)

    return values[index]


async def main(args):
    semaphore = asyncio.Semaphore(args.concurrency)

    print("=" * 60)
    print("FACT Benchmark")
    print("=" * 60)
    print(f"Target        : {args.url}")
    print(f"Requests      : {args.requests}")
    print(f"Concurrency   : {args.concurrency}")
    print("=" * 60)

    limits = httpx.Limits(
        max_keepalive_connections=args.concurrency,
        max_connections=args.concurrency * 2,
    )

    start = time.perf_counter()

    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [
            send_request(client, semaphore, i, args.url)
            for i in range(args.requests)
        ]

        results = await asyncio.gather(*tasks)

    total_time = time.perf_counter() - start

    status_counts = {}
    tenant_counts = {}
    latencies = []

    success = 0          # HTTP 2xx
    server_error = 0     # HTTP 5xx
    client_failed = 0    # Transport errors

    for status, latency, tenant in results:
        status_counts[status] = status_counts.get(status, 0) + 1
        tenant_counts[tenant] = tenant_counts.get(tenant, 0) + 1

        latencies.append(latency)

        if status == "FAILED":
            client_failed += 1

        elif isinstance(status, int) and 200 <= status < 300:
            success += 1

        elif isinstance(status, int) and status >= 500:
            server_error += 1

    throughput = args.requests / total_time

    print()
    print("=" * 60)
    print("FACT BENCHMARK REPORT")
    print("=" * 60)

    print(f"Duration            : {total_time:.2f} sec")
    print(f"Throughput          : {throughput:.2f} req/sec")
    print()

    print("Latency")
    print("-" * 60)
    print(f"Average             : {statistics.mean(latencies):.2f} ms")
    print(f"Minimum             : {min(latencies):.2f} ms")
    print(f"Maximum             : {max(latencies):.2f} ms")
    print(f"P50                 : {percentile(latencies,50):.2f} ms")
    print(f"P95                 : {percentile(latencies,95):.2f} ms")
    print(f"P99                 : {percentile(latencies,99):.2f} ms")

    print()
    print("Request Results")
    print("-" * 60)
    print(f"HTTP Success (2xx)  : {success}")
    print(f"HTTP Server Error   : {server_error}")
    print(f"Transport Failed    : {client_failed}")
    print(f"HTTP Success Rate   : {(success/args.requests)*100:.2f}%")
    print(f"Server Error Rate   : {(server_error/args.requests)*100:.2f}%")
    print(f"Transport Fail Rate : {(client_failed/args.requests)*100:.2f}%")

    print("Status Codes")
    print("-" * 60)

    for status in sorted(status_counts, key=str):
        print(f"{status:<20}: {status_counts[status]}")

    print()
    print("Tenant Distribution")
    print("-" * 60)

    for tenant in sorted(tenant_counts):
        print(f"{tenant:<20}: {tenant_counts[tenant]}")

    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FACT Benchmark Tool")

    parser.add_argument(
        "--requests",
        type=int,
        default=10000,
        help="Total number of requests",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=100,
        help="Concurrent requests",
    )

    parser.add_argument(
        "--url",
        type=str,
        default="http://127.0.0.1:8000",
        help="Target URL",
    )

    args = parser.parse_args()

    asyncio.run(main(args))