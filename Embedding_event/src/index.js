export default {
    async queue(batch, env) {
        for (const msg of batch.messages) {
            const key = msg.body.object?.key;

            if (!key) {
                msg.ack();
                continue;
            }

            try {
                const res = await fetch(env.PROCESSOR_URL, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ json_filenames: [key] })
                });

                if (!res.ok) {
                    throw new Error(`Embedding service returned ${res.status}`);
                }

                msg.ack();
            } catch (err) {
                console.error("Dispatch failed:", err);
                msg.retry();
            }
        }
    }
};
