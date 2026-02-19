import type { GameStateDTO, ValidMovesDTO, MoveDTO } from "../types";

const BASE_URL = "http://localhost:8000";


async function safeJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const message = err?.detail ?? `Request failed: ${res.status}`;
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export async function getState(): Promise<GameStateDTO> {
  const res = await fetch(`${BASE_URL}/state`);
  return safeJson<GameStateDTO>(res);
}

export async function getValidMoves(pieceId: number): Promise<ValidMovesDTO> {
  const res = await fetch(`${BASE_URL}/valid-moves/${pieceId}`);
  return safeJson<ValidMovesDTO>(res);
}

export async function makeMove(move: MoveDTO): Promise<GameStateDTO> {
  const res = await fetch(`${BASE_URL}/move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(move),
  });
  return safeJson<GameStateDTO>(res);
}

export async function resetGame(): Promise<void> {
  // Backend must have POST /reset
  const res = await fetch(`${BASE_URL}/reset`, { method: "POST" });
  await safeJson(res);
}
