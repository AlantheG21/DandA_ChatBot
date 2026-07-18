export default function TypingIndicator() {
  return (
    <div className="flex justify-start mb-3">
      <div className="bg-gray-600 px-4 py-3 rounded-2xl rounded-bl-sm flex gap-1 items-center">
        <span className="w-2 h-2 bg-gray-200 rounded-full animate-bounce [animation-delay:0ms]" />
        <span className="w-2 h-2 bg-gray-200 rounded-full animate-bounce [animation-delay:150ms]" />
        <span className="w-2 h-2 bg-gray-200 rounded-full animate-bounce [animation-delay:300ms]" />
      </div>
    </div>
  );
}
