const assert = require("assert");
const createSseParser = require("../static/sse_parser.js");

const events = [];
const parser = createSseParser((event, data) => events.push({ event, data }));
const frame = 'event: messages/partial\r\ndata: [{"type":"ai","content":"北京房源"}]\r\n\r\n';

for (let index = 0; index < frame.length; index += 3) {
  parser.push(frame.slice(index, index + 3));
}
parser.end();

assert.deepStrictEqual(events, [
  {
    event: "messages/partial",
    data: '[{"type":"ai","content":"北京房源"}]',
  },
]);

const multipleEvents = [];
const secondParser = createSseParser((event, data) => multipleEvents.push({ event, data }));
secondParser.push("event: updates\ndata: {\"ok\":true}\n\nevent: messages/metadata\ndata: {\"node\":\"generate_query\"}\n\n");
secondParser.end();
assert.deepStrictEqual(multipleEvents.map((item) => item.event), ["updates", "messages/metadata"]);

console.log("frontend SSE parser checks passed");
