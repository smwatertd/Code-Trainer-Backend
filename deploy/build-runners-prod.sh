#!/usr/bin/env bash
# Сборка раннеров на слабом VPS: по одному, с очисткой кэша перед C#.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

RUNNERS=(python cpp pascal csharp)
BUILD_FLAGS=(--provenance=false --sbom=false)

echo "==> Очистка build cache (освобождает место под C#)"
docker builder prune -af || true

for runner in "${RUNNERS[@]}"; do
  img="${runner}_runner"
  if docker image inspect "${img}" >/dev/null 2>&1; then
    echo "==> ${img} уже есть, пропуск"
    continue
  fi
  echo "==> Сборка ${img}"
  docker build "${BUILD_FLAGS[@]}" \
    -f "docker/runners/Dockerfile.${runner}" \
    -t "${img}" .
done

echo "==> C# runner (Alpine SDK, пересборка)"
docker build "${BUILD_FLAGS[@]}" \
  -f docker/runners/Dockerfile.csharp \
  -t csharp_runner .

echo "==> Запуск prod-раннеров (без Java)"
docker compose -f docker/docker-compose.runners.prod.yml up -d --force-recreate --remove-orphans --no-build

docker image ls --format 'table {{.Repository}}\t{{.Size}}' | grep _runner || true
df -h /
