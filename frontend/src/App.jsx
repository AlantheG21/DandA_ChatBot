import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { messages, isLoading, sendQuery } = useChat();

  return (
    <div className="h-screen bg-white flex flex-col">
      <Header />
      <ChatWindow messages={messages} isLoading={isLoading} />
      <ChatInput onSend={sendQuery} disabled={isLoading} />
    </div>
  );
}
