import axios from "axios";
import { type AppType } from "next/dist/shared/lib/utils";
import { QueryClient, QueryClientProvider } from "react-query";
import useNotifyParentAboutDocumentSize from "../useNotifyParentAboutDocumentSize";

import "../styles/globals.css";

axios.defaults.baseURL = "https://timetable.mirea.ru";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
});

const MyApp: AppType = ({ Component, pageProps }) => {
  // Передаем родителю размеры документа. Используется, если приложение запущено в iframe
  useNotifyParentAboutDocumentSize();

  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
    </QueryClientProvider>
  );
};

export default MyApp;
