(function (global) {
    function createSseParser(onEvent) {
        let buffer = '';
        let eventName = '';
        let dataLines = [];

        function dispatchEvent() {
            if (dataLines.length > 0) {
                onEvent(eventName || 'message', dataLines.join('\n'));
            }
            eventName = '';
            dataLines = [];
        }

        function consumeLine(line) {
            if (line.endsWith('\r')) {
                line = line.slice(0, -1);
            }
            if (line === '') {
                dispatchEvent();
                return;
            }
            if (line.startsWith(':')) {
                return;
            }

            const separator = line.indexOf(':');
            const field = separator === -1 ? line : line.slice(0, separator);
            let value = separator === -1 ? '' : line.slice(separator + 1);
            if (value.startsWith(' ')) {
                value = value.slice(1);
            }

            if (field === 'event') {
                eventName = value;
            } else if (field === 'data') {
                dataLines.push(value);
            }
        }

        return {
            push(chunk) {
                buffer += chunk;
                const lines = buffer.split('\n');
                buffer = lines.pop();
                lines.forEach(consumeLine);
            },
            end() {
                if (buffer) {
                    consumeLine(buffer);
                    buffer = '';
                }
                dispatchEvent();
            },
        };
    }

    global.createSseParser = createSseParser;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = createSseParser;
    }
})(typeof window === 'undefined' ? globalThis : window);
