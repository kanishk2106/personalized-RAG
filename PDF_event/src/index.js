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
                    body: JSON.stringify({ filename: key })
                });

                if (!res.ok) {
                    throw new Error(`Processor returned ${res.status}`);
                }

                msg.ack();
            } catch (err) {
                console.error("Dispatch failed:", err);
                msg.retry();
            }
        }
    }
};