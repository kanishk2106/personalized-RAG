import { MAX_CONCURRENT, MAX_QUEUE, QUEUE_TIMEOUT_MS } from "../config.js";


let inflight = 0;

const queue: Array<{
  resolve: () => void;
  reject: (err: Error) => void;
  timer: ReturnType<typeof setTimeout>;
}> = [];

export function acquire(): Promise<void> {
  if (inflight < MAX_CONCURRENT) {
    inflight++;
    return Promise.resolve();
  }
  if (queue.length >= MAX_QUEUE) {
    return Promise.reject(new Error("queue_full"));
  }
  return new Promise<void>((resolve, reject) => {
    const timer = setTimeout(() => {
      const idx = queue.findIndex((e) => e.resolve === resolve);
      if (idx !== -1) queue.splice(idx, 1);
      reject(new Error("queue_timeout"));
    }, QUEUE_TIMEOUT_MS);
    queue.push({ resolve, reject, timer });
  });
}

export function release(): void {
  inflight--;
  if (queue.length > 0) {
    const next = queue.shift()!;
    clearTimeout(next.timer);
    inflight++;
    next.resolve();
  }
}

export function getInflight(): number {
  return inflight;
}

export function getQueueLength(): number {
  return queue.length;
}
