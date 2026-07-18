import { useState } from "react";

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      handleSubmit(e);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="shrink-0 border-t border-yellow-400 bg-blue-800 px-4 py-3 flex gap-3 items-end"
    >
      <textarea
        className="flex-1 bg-gray-100 text-black placeholder-gray-500 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px] max-h-32"
        placeholder="Type your message..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={!value.trim() || disabled}
        className="bg-yellow-400 text-black font-semibold text-sm px-5 py-3 rounded-xl hover:bg-yellow-300 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shrink-0"
      >
        Send
      </button>
    </form>
  );
}
