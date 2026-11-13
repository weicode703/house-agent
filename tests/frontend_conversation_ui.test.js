const fs = require("fs");
const path = require("path");
const assert = require("assert");

const html = fs.readFileSync(
  path.join(__dirname, "..", "static", "house.html"),
  "utf8",
);

assert(html.includes("conversationSidebar"), "missing conversation sidebar");
assert(html.includes("newConversationBtn"), "missing new conversation button");
assert(html.includes("HOUSE_AGENT_CONVERSATIONS"), "missing localStorage key");
assert(html.includes("demoUserId"), "missing per-conversation demo user id");
assert(html.includes("createNewConversation"), "missing new conversation handler");
assert(html.includes("deleteConversation"), "missing delete conversation handler");
assert(!html.includes('user_id: "159"'), "fixed user_id should not be used");
assert(html.includes("del.title = '删除对话';"), "delete tooltip should use readable Chinese");
assert(!html.includes("鍒犻櫎瀵硅瘽"), "delete tooltip must not contain mojibake");

const sendMessageIndex = html.indexOf("async function sendMessage() {", html.indexOf("function createAssistantTurn()"));
const assistantTurnIndex = html.indexOf("turn = createAssistantTurn();", sendMessageIndex);
const requestIndex = html.indexOf("const response = await fetch(", assistantTurnIndex);
assert(assistantTurnIndex !== -1 && assistantTurnIndex < requestIndex, "thinking state should show before the request");
assert(html.includes("turn.thinkContent.textContent = '正在处理您的请求…';"), "missing immediate processing state");
const createThreadWaitIndex = html.indexOf("await createThread();", sendMessageIndex);
assert(assistantTurnIndex < createThreadWaitIndex && createThreadWaitIndex < requestIndex, "processing state should show before waiting for a new thread");

console.log("frontend conversation UI checks passed");
