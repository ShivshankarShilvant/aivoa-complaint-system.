import { Provider } from "react-redux";
import { store } from "./store/store";
import ComplaintForm from "./components/ComplaintForm";
import AIAssistantPanel from "./components/AIAssistantPanel";

export default function App() {
  return (
    <Provider store={store}>
      <div style={{ display: "flex", fontFamily: "Inter, sans-serif" }}>
        <ComplaintForm />
        <AIAssistantPanel />
      </div>
    </Provider>
  );
}
