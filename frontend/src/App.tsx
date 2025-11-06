import { useCallback, useMemo, useState } from "react";
import axios from "axios";

type SDLCPhase =
  | "intake"
  | "analysis"
  | "design"
  | "implementation"
  | "testing"
  | "deployment"
  | "retrospective";

interface AgentMessage {
  sender: string;
  phase: SDLCPhase;
  content: string;
  metadata: Record<string, unknown>;
}

interface AgentResult {
  agent: string;
  phase: SDLCPhase;
  output: string;
  artifacts: Record<string, unknown>;
  requires_confirmation: boolean;
  suggested_next_phase?: SDLCPhase;
}

interface WorkflowState {
  workflow_id: string;
  current_phase?: SDLCPhase;
  pending_confirmation: boolean;
  history: AgentMessage[];
  artifacts: Record<string, unknown>;
  last_result?: AgentResult;
}

const api = axios.create({ baseURL: "/api" });

function App() {
  const [workflow, setWorkflow] = useState<WorkflowState | null>(null);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const startDisabled = !input.trim() || loading;

  const handleStart = useCallback(async () => {
    try {
      setLoading(true);
      setStatus(null);
      const response = await api.post<WorkflowState>("/workflows", {
        prompt: input.trim()
      });
      setWorkflow(response.data);
      setInput("");
    } catch (error) {
      setStatus(
        error instanceof Error ? error.message : "Error iniciando el flujo"
      );
    } finally {
      setLoading(false);
    }
  }, [input]);

  const handleConfirm = useCallback(async () => {
    if (!workflow) return;
    try {
      setLoading(true);
      setStatus(null);
      const response = await api.post<WorkflowState>(
        `/workflows/${workflow.workflow_id}/confirm`,
        { message: input.trim() || undefined }
      );
      setWorkflow(response.data);
      setInput("");
    } catch (error) {
      setStatus(
        error instanceof Error
          ? error.message
          : "Error al confirmar el siguiente paso"
      );
    } finally {
      setLoading(false);
    }
  }, [workflow, input]);

  const phaseLabel = useMemo(() => {
    if (!workflow?.current_phase) return "completado";
    const labels: Record<SDLCPhase, string> = {
      intake: "Captura de requerimientos",
      analysis: "Análisis",
      design: "Diseño",
      implementation: "Implementación",
      testing: "Pruebas",
      deployment: "Despliegue",
      retrospective: "Retrospectiva"
    };
    return labels[workflow.current_phase];
  }, [workflow?.current_phase]);

  return (
    <div className="app">
      <header>
        <h1>Plataforma de ciclo de vida de desarrollo</h1>
        <p>
          Orquestación multi-agente basada en LangChain, LangGraph y LangFuse.
          Cada agente espera confirmación antes de continuar con la siguiente fase.
        </p>
      </header>

      <section className="control-panel">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder={
            workflow
              ? "Agrega contexto adicional antes de confirmar la siguiente fase"
              : "Describe tu necesidad, objetivos o adjunta notas de las reuniones"
          }
          rows={4}
        />
        <div className="actions">
          {workflow ? (
            <button
              onClick={handleConfirm}
              disabled={!workflow.pending_confirmation || loading}
            >
              {loading ? "Procesando..." : "Confirmar y continuar"}
            </button>
          ) : (
            <button onClick={handleStart} disabled={startDisabled}>
              {loading ? "Iniciando..." : "Iniciar flujo"}
            </button>
          )}
        </div>
        {status && <span className="status">{status}</span>}
        {workflow && (
          <div className="workflow-status">
            <strong>Estado actual:</strong>
            <span>
              {workflow.pending_confirmation
                ? "Esperando tu confirmación"
                : "En ejecución"}
            </span>
            <strong>Siguiente fase:</strong>
            <span>{phaseLabel}</span>
          </div>
        )}
      </section>

      <section className="history">
        <h2>Historial de agentes</h2>
        {!workflow && <p>Comienza un flujo para ver el trabajo de los agentes.</p>}
        {workflow &&
          (workflow.history.length ? (
            <ul>
              {workflow.history.map((message, index) => (
                <li key={`${message.sender}-${index}`}>
                  <div className="phase">{message.phase}</div>
                  <div className="sender">{message.sender}</div>
                  <p>{message.content}</p>
                  {Object.keys(message.metadata || {}).length > 0 && (
                    <details>
                      <summary>Ver artefactos</summary>
                      <pre>{JSON.stringify(message.metadata, null, 2)}</pre>
                    </details>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p>Sin mensajes todavía.</p>
          ))}
      </section>
    </div>
  );
}

export default App;
