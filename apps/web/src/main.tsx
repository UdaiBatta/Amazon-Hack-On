import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
// Vendored locally so the demo runs fully offline (no CDN dependency).
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import "leaflet/dist/leaflet.css";
import "./index.css";
import App from "./App";
import OpsDashboard from "./flows/ops/OpsDashboard";
import BuyerView from "./flows/buyer/BuyerView";

const router = createBrowserRouter([
  { path: "/", element: <App /> },
  { path: "/buyer", element: <BuyerView /> },
  { path: "/ops", element: <OpsDashboard /> },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
