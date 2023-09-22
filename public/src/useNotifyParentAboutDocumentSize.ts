import { useEffect } from "react";

function useNotifyParentAboutDocumentSize() {
    return useEffect(() => {
        const sizeSender = () => {
            window.parent.postMessage(
                {
                    messageType: "resize",
                    size: {
                        width: document.body.scrollWidth,
                        height: document.body.scrollHeight,
                    },
                },
                "*"
            );
        };

        const resizeObserver = new ResizeObserver(() => {
            sizeSender();
        });
        resizeObserver.observe(window.document.body);

        const messageEventListener = (message: MessageEvent) => {
            if (message.data.messageType == "get_initial_size") {
                sizeSender();
            }
        };

        window.addEventListener("message", messageEventListener);

        return () => {
            resizeObserver.unobserve(window.document.body);
            resizeObserver.disconnect();
            window.removeEventListener("message", messageEventListener);
        };
    }, []);
}

export default useNotifyParentAboutDocumentSize;
